from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import models, schemas, database, workflow_engine, voice_parser, audit_logger
from database import engine
from pydantic import BaseModel

from fastapi.middleware.cors import CORSMiddleware

# Drop all tables to force recreation with new schema
models.Base.metadata.drop_all(bind=engine)
# Recreate all tables with current schema
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="VoiceFlow - Kitchenware Industry Management",
    description="AI-powered voice control for complete industrial management",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============= ROOT =============
@app.get("/")
def read_root():
    return {
        "message": "VoiceFlow - Kitchenware Industry Management System",
        "status": "Active",
        "features": ["Tasks", "Workers", "Inventory", "Voice Commands", "Audit Logging"],
        "endpoints": {
            "tasks": "/tasks",
            "workers": "/workers",
            "inventory": "/inventory",
            "voice": "/voice/process",
            "docs": "/docs"
        }
    }

# ============= TASK ENDPOINTS =============
@app.post("/tasks", response_model=schemas.Task)
def create_task(task: schemas.TaskCreate, db: Session = Depends(database.get_db)):
    """Create a new production task"""
    db_task = models.Task(**task.dict())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    audit_logger.log_task_created(db, db_task, source="api")
    workflow_engine.check_and_trigger_workflows(db_task.id, db_task.status, db)
    
    return db_task

@app.get("/tasks", response_model=List[schemas.Task])
def read_tasks(skip: int = 0, limit: int = 100, status: Optional[str] = None, db: Session = Depends(database.get_db)):
    """Get all tasks, optionally filtered by status"""
    query = db.query(models.Task)
    if status:
        query = query.filter(models.Task.status == status)
    return query.offset(skip).limit(limit).all()

@app.get("/tasks/{task_id}", response_model=schemas.Task)
def read_task(task_id: int, db: Session = Depends(database.get_db)):
    """Get a specific task"""
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task

@app.put("/tasks/{task_id}", response_model=schemas.Task)
def update_task(task_id: int, task: schemas.TaskUpdate, db: Session = Depends(database.get_db)):
    """Update a task"""
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    update_data = task.dict(exclude_unset=True)
    for key, value in update_data.items():
        old_value = getattr(db_task, key, None)
        if old_value != value:
            audit_logger.log_task_field_change(db, task_id, key, old_value, value, source="api")
        setattr(db_task, key, value)
    
    db.commit()
    db.refresh(db_task)
    workflow_engine.check_and_trigger_workflows(db_task.id, db_task.status, db)
    
    return db_task

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(database.get_db)):
    """Delete a task"""
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.query(models.WorkflowTrigger).filter(models.WorkflowTrigger.task_id == task_id).delete()
    audit_logger.log_task_deleted(db, task_id, db_task.title, source="api")
    db.delete(db_task)
    db.commit()
    
    return {"status": "success", "message": "Task deleted"}

# ============= WORKER ENDPOINTS =============
@app.post("/workers", response_model=schemas.Worker)
def create_worker(worker: schemas.WorkerCreate, db: Session = Depends(database.get_db)):
    """Add a new worker to the system"""
    db_worker = models.Worker(**worker.dict())
    db.add(db_worker)
    db.commit()
    db.refresh(db_worker)
    
    audit_logger.log_audit(
        db, 
        action="create", 
        entity_type="worker",
        entity_id=db_worker.id,
        description=f"Added worker: {db_worker.name} ({db_worker.position})",
        source="api"
    )
    
    return db_worker

@app.get("/workers", response_model=List[schemas.Worker])
def read_workers(skip: int = 0, limit: int = 100, department: Optional[str] = None, status: Optional[str] = None, db: Session = Depends(database.get_db)):
    """Get all workers, optionally filtered"""
    query = db.query(models.Worker)
    if department:
        query = query.filter(models.Worker.department == department)
    if status:
        query = query.filter(models.Worker.status == status)
    return query.offset(skip).limit(limit).all()

@app.get("/workers/{worker_id}", response_model=schemas.Worker)
def read_worker(worker_id: int, db: Session = Depends(database.get_db)):
    """Get a specific worker"""
    db_worker = db.query(models.Worker).filter(models.Worker.id == worker_id).first()
    if not db_worker:
        raise HTTPException(status_code=404, detail="Worker not found")
    return db_worker

@app.put("/workers/{worker_id}", response_model=schemas.Worker)
def update_worker(worker_id: int, worker: schemas.WorkerUpdate, db: Session = Depends(database.get_db)):
    """Update worker information"""
    db_worker = db.query(models.Worker).filter(models.Worker.id == worker_id).first()
    if not db_worker:
        raise HTTPException(status_code=404, detail="Worker not found")
    
    update_data = worker.dict(exclude_unset=True)
    changes = []
    for key, value in update_data.items():
        old_value = getattr(db_worker, key, None)
        if old_value != value:
            changes.append(f"{key}: {old_value} → {value}")
        setattr(db_worker, key, value)
    
    db.commit()
    db.refresh(db_worker)
    
    audit_logger.log_audit(
        db,
        action="update",
        entity_type="worker",
        entity_id=worker_id,
        description=f"Updated worker {db_worker.name}: {', '.join(changes)}",
        source="api"
    )
    
    return db_worker

@app.delete("/workers/{worker_id}")
def delete_worker(worker_id: int, db: Session = Depends(database.get_db)):
    """Remove a worker from the system"""
    db_worker = db.query(models.Worker).filter(models.Worker.id == worker_id).first()
    if not db_worker:
        raise HTTPException(status_code=404, detail="Worker not found")
    
    worker_name = db_worker.name
    db.delete(db_worker)
    db.commit()
    
    audit_logger.log_audit(
        db,
        action="delete",
        entity_type="worker",
        entity_id=worker_id,
        description=f"Removed worker: {worker_name}",
        source="api"
    )
    
    return {"status": "success", "message": f"Worker {worker_name} removed"}

# ============= WORKER ASSIGNMENT ENDPOINTS =============
@app.post("/assignments", response_model=schemas.WorkerAssignment)
def create_assignment(assignment: schemas.WorkerAssignmentBase, db: Session = Depends(database.get_db)):
    """Assign a worker to a task"""
    db_assignment = models.WorkerAssignment(**assignment.dict())
    db.add(db_assignment)
    db.commit()
    db.refresh(db_assignment)
    
    audit_logger.log_audit(
        db,
        action="create",
        entity_type="assignment",
        entity_id=db_assignment.id,
        description=f"Assigned worker {db_assignment.worker_id} to task {db_assignment.task_id}",
        source="api"
    )
    
    return db_assignment

@app.get("/assignments", response_model=List[schemas.WorkerAssignment])
def read_assignments(skip: int = 0, limit: int = 100, worker_id: Optional[int] = None, db: Session = Depends(database.get_db)):
    """Get all assignments"""
    query = db.query(models.WorkerAssignment)
    if worker_id:
        query = query.filter(models.WorkerAssignment.worker_id == worker_id)
    return query.offset(skip).limit(limit).all()

@app.put("/assignments/{assignment_id}", response_model=schemas.WorkerAssignment)
def update_assignment(assignment_id: int, status: str, db: Session = Depends(database.get_db)):
    """Update assignment status"""
    db_assignment = db.query(models.WorkerAssignment).filter(models.WorkerAssignment.id == assignment_id).first()
    if not db_assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    db_assignment.status = status
    db.commit()
    db.refresh(db_assignment)
    
    return db_assignment

# ============= INVENTORY ENDPOINTS =============
@app.post("/inventory", response_model=schemas.InventoryItem)
def create_inventory_item(item: schemas.InventoryItemCreate, db: Session = Depends(database.get_db)):
    """Add a new item to inventory"""
    db_item = models.InventoryItem(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    
    audit_logger.log_audit(
        db,
        action="create",
        entity_type="inventory",
        entity_id=db_item.id,
        description=f"Added inventory: {db_item.name} (SKU: {db_item.sku}, Qty: {db_item.quantity})",
        source="api"
    )
    
    return db_item

@app.get("/inventory", response_model=List[schemas.InventoryItem])
def read_inventory(skip: int = 0, limit: int = 100, category: Optional[str] = None, db: Session = Depends(database.get_db)):
    """Get all inventory items, optionally filtered by category"""
    query = db.query(models.InventoryItem)
    if category:
        query = query.filter(models.InventoryItem.category == category)
    return query.offset(skip).limit(limit).all()

@app.get("/inventory/{item_id}", response_model=schemas.InventoryItem)
def read_inventory_item(item_id: int, db: Session = Depends(database.get_db)):
    """Get a specific inventory item"""
    db_item = db.query(models.InventoryItem).filter(models.InventoryItem.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return db_item

@app.put("/inventory/{item_id}", response_model=schemas.InventoryItem)
def update_inventory_item(item_id: int, item: schemas.InventoryItemUpdate, db: Session = Depends(database.get_db)):
    """Update inventory item"""
    db_item = db.query(models.InventoryItem).filter(models.InventoryItem.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    
    update_data = item.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_item, key, value)
    
    db_item.last_updated = datetime.utcnow()
    db.commit()
    db.refresh(db_item)
    
    audit_logger.log_audit(
        db,
        action="update",
        entity_type="inventory",
        entity_id=item_id,
        description=f"Updated inventory: {db_item.name}",
        source="api"
    )
    
    return db_item

@app.post("/inventory/{item_id}/transaction")
def add_inventory_transaction(item_id: int, transaction: schemas.InventoryTransactionBase, db: Session = Depends(database.get_db)):
    """Record an inventory transaction (add, remove, usage, waste)"""
    db_item = db.query(models.InventoryItem).filter(models.InventoryItem.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    
    # Update quantity based on transaction type
    if transaction.transaction_type == "add":
        db_item.quantity += transaction.quantity
    elif transaction.transaction_type in ["remove", "usage", "waste"]:
        if db_item.quantity < transaction.quantity:
            raise HTTPException(status_code=400, detail="Insufficient quantity")
        db_item.quantity -= transaction.quantity
    
    db_transaction = models.InventoryTransaction(
        item_id=item_id,
        **transaction.dict()
    )
    db.add(db_transaction)
    db_item.last_updated = datetime.utcnow()
    db.commit()
    
    audit_logger.log_audit(
        db,
        action=transaction.transaction_type,
        entity_type="inventory",
        entity_id=item_id,
        description=f"{transaction.transaction_type}: {db_item.name} ({transaction.quantity} {db_item.unit})",
        source="api"
    )
    
    return {"status": "success", "message": f"Recorded {transaction.transaction_type} transaction", "new_quantity": db_item.quantity}

# ============= VOICE COMMAND ENDPOINT =============
class VoiceRequest(BaseModel):
    transcription: str

@app.post("/voice/process")
def process_voice_command(request: VoiceRequest, db: Session = Depends(database.get_db)):
    """
    🎤 Process voice commands for workers, inventory, and tasks
    Examples:
    - "Add inventory of 50 kg flour"
    - "Create a new worker named John in kitchen"
    - "Create a high priority task for cleanup"
    - "List all workers in kitchen"
    - "Update inventory flour to 30"
    """
    try:
        intent = voice_parser.parse_intent(request.transcription)
        entity_type = intent.get("entity_type", "task")
        action = intent.get("action", "create")
        
        # ===== WORKER COMMANDS =====
        if entity_type == "worker":
            if action == "create":
                primary_name = intent.get("primary_input", "New Worker")
                department = voice_parser.extract_department(request.transcription.lower()) or "Kitchen"
                new_worker = models.Worker(
                    name=primary_name,
                    email=f"{primary_name.lower().replace(' ', '')}@company.com",
                    position=intent.get("category", "Kitchen Staff"),
                    department=department,
                    status=intent.get("status", "Active")
                )
                db.add(new_worker)
                db.commit()
                db.refresh(new_worker)
                
                audit_logger.log_audit(
                    db,
                    action="create",
                    entity_type="worker",
                    entity_id=new_worker.id,
                    description=f"Voice command: Added {new_worker.name} to {new_worker.department}",
                    source="voice"
                )
                
                return {
                    "status": "✅ success",
                    "message": f"Added {new_worker.name} as {new_worker.position} in {new_worker.department}",
                    "worker": new_worker,
                    "audio_response": f"Worker {new_worker.name} added to {new_worker.department}"
                }
            
            elif action == "list":
                department = voice_parser.extract_department(request.transcription.lower())
                workers = db.query(models.Worker)
                if department:
                    workers = workers.filter(models.Worker.department == department)
                workers = workers.all()
                
                return {
                    "status": "✅ success",
                    "message": f"Found {len(workers)} workers",
                    "workers": workers,
                    "audio_response": f"Found {len(workers)} workers in {department or 'the system'}"
                }
            
            elif action == "update":
                worker = db.query(models.Worker).filter(
                    models.Worker.name.ilike(f"%{intent.get('primary_input')}%")
                ).first()
                if not worker:
                    raise HTTPException(status_code=404, detail="Worker not found")
                
                if intent.get("status"):
                    worker.status = intent.get("status")
                department = voice_parser.extract_department(request.transcription.lower())
                if department:
                    worker.department = department
                
                db.commit()
                return {
                    "status": "✅ success",
                    "message": f"Updated {worker.name}",
                    "worker": worker,
                    "audio_response": f"Updated {worker.name}"
                }
        
        # ===== INVENTORY COMMANDS =====
        elif entity_type == "inventory":
            if action == "create":
                primary_name = intent.get("primary_input", "New Item")
                new_item = models.InventoryItem(
                    name=primary_name,
                    category=intent.get("category", "Supplies"),
                    sku=primary_name.upper()[:8],
                    quantity=intent.get("quantity", 0),
                    unit="kg" if "kg" in request.transcription.lower() else "pieces",
                    price_per_unit=0.0
                )
                db.add(new_item)
                db.commit()
                db.refresh(new_item)
                
                audit_logger.log_audit(
                    db,
                    action="create",
                    entity_type="inventory",
                    entity_id=new_item.id,
                    description=f"Voice command: Added {new_item.name} ({intent.get('quantity', 0)} {new_item.unit})",
                    source="voice"
                )
                
                return {
                    "status": "✅ success",
                    "message": f"Added {new_item.name} ({intent.get('quantity', 0)} {new_item.unit})",
                    "item": new_item,
                    "audio_response": f"Inventory added: {new_item.name}"
                }
            
            elif action == "list":
                category = intent.get("category")
                items = db.query(models.InventoryItem)
                if category:
                    items = items.filter(models.InventoryItem.category == category)
                items = items.all()
                
                return {
                    "status": "✅ success",
                    "message": f"Found {len(items)} items",
                    "items": items,
                    "audio_response": f"Found {len(items)} items in inventory"
                }
            
            elif action == "update":
                item = db.query(models.InventoryItem).filter(
                    models.InventoryItem.name.ilike(f"%{intent.get('primary_input')}%")
                ).first()
                if not item:
                    raise HTTPException(status_code=404, detail="Inventory item not found")
                
                if intent.get("quantity"):
                    item.quantity = intent.get("quantity")
                db.commit()
                
                return {
                    "status": "✅ success",
                    "message": f"Updated {item.name} to {item.quantity} {item.unit}",
                    "item": item,
                    "audio_response": f"Updated {item.name}"
                }
        
        # ===== TASK COMMANDS =====
        else:
            if action == "create":
                db_task = models.Task(
                    title=intent.get("primary_input", "New Task"),
                    priority=intent.get("priority", "Medium"),
                    status="Todo",
                    task_type="production"
                )
                db.add(db_task)
                db.commit()
                db.refresh(db_task)
                
                audit_logger.log_audit(
                    db,
                    action="create",
                    entity_type="task",
                    entity_id=db_task.id,
                    description=f"Voice command: Created {db_task.title} ({db_task.priority} priority)",
                    source="voice"
                )
                
                workflow_engine.check_and_trigger_workflows(db_task.id, db_task.status, db)
                
                return {
                    "status": "✅ success",
                    "message": f"Created task: {db_task.title}",
                    "task": db_task,
                    "audio_response": f"Task created: {db_task.title}"
                }
            
            elif action == "list":
                tasks = db.query(models.Task).all()
                return {
                    "status": "✅ success",
                    "message": f"Found {len(tasks)} tasks",
                    "tasks": tasks,
                    "audio_response": f"Found {len(tasks)} tasks"
                }
    
    except Exception as e:
        return {
            "status": "❌ error",
            "message": str(e),
            "audio_response": f"Error processing command: {str(e)}"
        }

# ============= AUDIT LOG ENDPOINTS =============
@app.get("/audit-logs", response_model=List[schemas.AuditLog])
def read_audit_logs(skip: int = 0, limit: int = 100, entity_type: Optional[str] = None, db: Session = Depends(database.get_db)):
    """Get audit logs"""
    query = db.query(models.AuditLog)
    if entity_type:
        query = query.filter(models.AuditLog.entity_type == entity_type)
    return query.order_by(models.AuditLog.timestamp.desc()).offset(skip).limit(limit).all()

@app.get("/task-audit/{task_id}")
def read_task_audit(task_id: int, db: Session = Depends(database.get_db)):
    """Get audit logs for a specific task"""
    logs = db.query(models.TaskAuditLog).filter(models.TaskAuditLog.task_id == task_id).order_by(models.TaskAuditLog.timestamp.desc()).all()
    return logs

# ============= SHIFT MANAGEMENT ENDPOINTS (NEW FEATURE) =============
@app.post("/shifts", response_model=dict)
def create_shift(
    name: str,
    start_time: str,
    end_time: str,
    date: str,
    db: Session = Depends(database.get_db)
):
    """Create a new work shift"""
    try:
        db_shift = models.Shift(
            name=name,
            start_time=start_time,
            end_time=end_time,
            date=date,
            status="Open"
        )
        db.add(db_shift)
        db.commit()
        db.refresh(db_shift)
        
        audit_logger.log_audit(
            db,
            action="create",
            entity_type="shift",
            entity_id=db_shift.id,
            description=f"Created shift {name} on {date} ({start_time}-{end_time})",
            source="api"
        )
        
        return {
            "status": "✅ success",
            "message": f"Shift {name} created",
            "shift": {"id": db_shift.id, "name": name, "date": date}
        }
    except Exception as e:
        return {"status": "❌ error", "message": str(e)}

@app.get("/shifts")
def list_shifts(
    date: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(database.get_db)
):
    """List all shifts"""
    try:
        query = db.query(models.Shift)
        if date:
            query = query.filter(models.Shift.date == date)
        if status:
            query = query.filter(models.Shift.status == status)
        shifts = query.all()
        
        return {
            "status": "✅ success",
            "count": len(shifts),
            "shifts": [{"id": s.id, "name": s.name, "date": s.date} for s in shifts]
        }
    except Exception as e:
        return {"status": "❌ error", "message": str(e)}

@app.post("/shifts/{shift_id}/assign-worker")
def assign_worker_to_shift(shift_id: int, worker_id: int, db: Session = Depends(database.get_db)):
    """Assign worker to shift"""
    try:
        shift = db.query(models.Shift).filter(models.Shift.id == shift_id).first()
        worker = db.query(models.Worker).filter(models.Worker.id == worker_id).first()
        if not shift or not worker:
            raise HTTPException(status_code=404, detail="Shift or worker not found")
        assignment = models.ShiftAssignment(shift_id=shift_id, worker_id=worker_id, status="Assigned")
        db.add(assignment)
        db.commit()
        return {"status": "✅ success", "message": f"Worker assigned to shift"}
    except Exception as e:
        return {"status": "❌ error", "message": str(e)}

# ============= ATTENDANCE ENDPOINTS (NEW FEATURE) =============
@app.post("/attendance/check-in")
def check_in_worker(worker_id: int, db: Session = Depends(database.get_db)):
    """Record worker check-in"""
    try:
        worker = db.query(models.Worker).filter(models.Worker.id == worker_id).first()
        if not worker:
            raise HTTPException(status_code=404, detail="Worker not found")
        
        from datetime import date as dt_date
        today = dt_date.today().isoformat()
        
        record = models.AttendanceRecord(
            worker_id=worker_id,
            date=today,
            check_in_time=datetime.utcnow().strftime("%H:%M:%S"),
            status="Present"
        )
        db.add(record)
        db.commit()
        
        return {"status": "✅ success", "message": f"{worker.name} checked in"}
    except Exception as e:
        return {"status": "❌ error", "message": str(e)}

@app.post("/attendance/check-out")
def check_out_worker(worker_id: int, db: Session = Depends(database.get_db)):
    """Record worker check-out"""
    try:
        worker = db.query(models.Worker).filter(models.Worker.id == worker_id).first()
        if not worker:
            raise HTTPException(status_code=404, detail="Worker not found")
        
        from datetime import date as dt_date
        today = dt_date.today().isoformat()
        
        record = db.query(models.AttendanceRecord).filter(
            models.AttendanceRecord.worker_id == worker_id,
            models.AttendanceRecord.date == today
        ).first()
        
        if not record:
            raise HTTPException(status_code=400, detail="No check-in found")
        
        record.check_out_time = datetime.utcnow().strftime("%H:%M:%S")
        db.commit()
        
        return {"status": "✅ success", "message": f"{worker.name} checked out"}
    except Exception as e:
        return {"status": "❌ error", "message": str(e)}

# ============= QUALITY CONTROL ENDPOINTS (NEW FEATURE) =============
@app.post("/quality-checks")
def record_quality_check(item_id: int, result: str, notes: str = "", db: Session = Depends(database.get_db)):
    """Record quality check"""
    try:
        item = db.query(models.InventoryItem).filter(models.InventoryItem.id == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        
        check = models.QualityCheck(item_id=item_id, result=result, notes=notes, checked_at=datetime.utcnow())
        db.add(check)
        db.commit()
        
        return {"status": "✅ success", "message": f"Quality check recorded: {result}"}
    except Exception as e:
        return {"status": "❌ error", "message": str(e)}

@app.get("/quality-reports")
def get_quality_report(days: int = 7, db: Session = Depends(database.get_db)):
    """Get quality report"""
    try:
        from datetime import timedelta
        since = datetime.utcnow() - timedelta(days=days)
        checks = db.query(models.QualityCheck).filter(models.QualityCheck.checked_at >= since).all()
        passed = len([c for c in checks if c.result == "Pass"])
        failed = len([c for c in checks if c.result == "Fail"])
        pass_rate = (passed / len(checks) * 100) if checks else 0
        return {"status": "✅ success", "total": len(checks), "passed": passed, "failed": failed, "pass_rate": round(pass_rate, 2)}
    except Exception as e:
        return {"status": "❌ error", "message": str(e)}

# ============= EQUIPMENT MANAGEMENT ENDPOINTS (NEW FEATURE) =============
@app.post("/equipment")
def register_equipment(name: str, equipment_type: str, location: str, db: Session = Depends(database.get_db)):
    """Register new equipment"""
    try:
        equipment = models.Equipment(name=name, equipment_type=equipment_type, location=location, status="Active")
        db.add(equipment)
        db.commit()
        db.refresh(equipment)
        return {"status": "✅ success", "message": f"Equipment {name} registered", "equipment_id": equipment.id}
    except Exception as e:
        return {"status": "❌ error", "message": str(e)}

@app.get("/equipment")
def list_equipment(db: Session = Depends(database.get_db)):
    """List all equipment"""
    try:
        equipment = db.query(models.Equipment).all()
        return {"status": "✅ success", "count": len(equipment), "equipment": [{"id": e.id, "name": e.name, "type": e.equipment_type} for e in equipment]}
    except Exception as e:
        return {"status": "❌ error", "message": str(e)}

@app.post("/equipment/{equipment_id}/maintenance")
def schedule_maintenance(equipment_id: int, maintenance_type: str, scheduled_date: str, db: Session = Depends(database.get_db)):
    """Schedule maintenance"""
    try:
        equipment = db.query(models.Equipment).filter(models.Equipment.id == equipment_id).first()
        if not equipment:
            raise HTTPException(status_code=404, detail="Equipment not found")
        schedule = models.MaintenanceSchedule(equipment_id=equipment_id, maintenance_type=maintenance_type, scheduled_date=scheduled_date, status="Scheduled")
        db.add(schedule)
        db.commit()
        return {"status": "✅ success", "message": f"Maintenance scheduled for {equipment.name}"}
    except Exception as e:
        return {"status": "❌ error", "message": str(e)}

# ============= SAFETY MANAGEMENT ENDPOINTS (NEW FEATURE) =============
@app.post("/safety-incidents")
def report_safety_incident(incident_type: str, severity: str, description: str, worker_id: Optional[int] = None, db: Session = Depends(database.get_db)):
    """Report safety incident"""
    try:
        incident = models.SafetyIncident(incident_type=incident_type, severity=severity, description=description, worker_id=worker_id, reported_at=datetime.utcnow(), status="Open")
        db.add(incident)
        db.commit()
        return {"status": "✅ success", "message": f"Safety incident reported ({severity})", "incident_id": incident.id}
    except Exception as e:
        return {"status": "❌ error", "message": str(e)}

@app.get("/safety-incidents")
def list_safety_incidents(severity: Optional[str] = None, db: Session = Depends(database.get_db)):
    """List safety incidents"""
    try:
        query = db.query(models.SafetyIncident)
        if severity:
            query = query.filter(models.SafetyIncident.severity == severity)
        incidents = query.order_by(models.SafetyIncident.reported_at.desc()).all()
        return {"status": "✅ success", "count": len(incidents), "incidents": [{"id": i.id, "type": i.incident_type, "severity": i.severity} for i in incidents]}
    except Exception as e:
        return {"status": "❌ error", "message": str(e)}

# ============= ORDER MANAGEMENT ENDPOINTS (NEW FEATURE) =============
@app.post("/orders")
def create_order(customer_name: str, items: dict, db: Session = Depends(database.get_db)):
    """Create order"""
    try:
        order = models.Order(customer_name=customer_name, items=items, status="Pending", created_at=datetime.utcnow())
        db.add(order)
        db.commit()
        db.refresh(order)
        return {"status": "✅ success", "message": f"Order created", "order_id": order.id}
    except Exception as e:
        return {"status": "❌ error", "message": str(e)}

@app.get("/orders")
def list_orders(status: Optional[str] = None, db: Session = Depends(database.get_db)):
    """List orders"""
    try:
        query = db.query(models.Order)
        if status:
            query = query.filter(models.Order.status == status)
        orders = query.all()
        return {"status": "✅ success", "count": len(orders), "orders": [{"id": o.id, "customer": o.customer_name, "status": o.status} for o in orders]}
    except Exception as e:
        return {"status": "❌ error", "message": str(e)}

@app.post("/complaints")
def record_complaint(order_id: Optional[int] = None, customer_name: str = None, complaint_type: str = None, description: str = None, db: Session = Depends(database.get_db)):
    """Record complaint"""
    try:
        complaint = models.Complaint(order_id=order_id, customer_name=customer_name, complaint_type=complaint_type, description=description, reported_at=datetime.utcnow(), status="Open")
        db.add(complaint)
        db.commit()
        return {"status": "✅ success", "message": "Complaint recorded", "complaint_id": complaint.id}
    except Exception as e:
        return {"status": "❌ error", "message": str(e)}

# ============= TRAINING MANAGEMENT ENDPOINTS (NEW FEATURE) =============
@app.post("/training")
def record_training(worker_id: int, training_title: str, training_date: str, db: Session = Depends(database.get_db)):
    """Record training"""
    try:
        worker = db.query(models.Worker).filter(models.Worker.id == worker_id).first()
        if not worker:
            raise HTTPException(status_code=404, detail="Worker not found")
        training = models.TrainingRecord(worker_id=worker_id, training_title=training_title, training_date=training_date, status="Completed")
        db.add(training)
        db.commit()
        return {"status": "✅ success", "message": f"Training recorded for {worker.name}", "training_id": training.id}
    except Exception as e:
        return {"status": "❌ error", "message": str(e)}

# ============= REPORTING ENDPOINTS (NEW FEATURE) =============
@app.get("/reports/daily")
def get_daily_report(date: Optional[str] = None, db: Session = Depends(database.get_db)):
    """Get daily report"""
    try:
        from datetime import date as dt_date
        if not date:
            date = dt_date.today().isoformat()
        tasks = db.query(models.Task).filter(models.Task.created_at.ilike(f"{date}%")).count()
        return {"status": "✅ success", "date": date, "tasks_created": tasks}
    except Exception as e:
        return {"status": "❌ error", "message": str(e)}

@app.get("/reports/performance")
def get_performance_report(worker_id: Optional[int] = None, db: Session = Depends(database.get_db)):
    """Get performance report"""
    try:
        if worker_id:
            worker = db.query(models.Worker).filter(models.Worker.id == worker_id).first()
            if not worker:
                raise HTTPException(status_code=404, detail="Worker not found")
            return {"status": "✅ success", "worker_id": worker_id, "worker_name": worker.name}
        return {"status": "✅ success", "total_workers": db.query(models.Worker).count()}
    except Exception as e:
        return {"status": "❌ error", "message": str(e)}

# ============= COST & ANALYTICS (NEW FEATURE) =============
@app.get("/cost-analysis")
def get_cost_analysis(days: int = 30, db: Session = Depends(database.get_db)):
    """Get cost analysis"""
    try:
        from datetime import timedelta
        since = datetime.utcnow() - timedelta(days=days)
        costs = db.query(models.CostTracking).filter(models.CostTracking.recorded_at >= since).all()
        total = sum(c.amount for c in costs)
        return {"status": "✅ success", "period_days": days, "total_cost": round(total, 2)}
    except Exception as e:
        return {"status": "❌ error", "message": str(e)}

# ============= SYSTEM STATUS =============
@app.get("/system-status")
def system_status(db: Session = Depends(database.get_db)):
    """Get system status and statistics"""
    try:
        return {
            "status": "✅ Active",
            "timestamp": datetime.utcnow().isoformat(),
            "statistics": {
                "total_workers": db.query(models.Worker).count(),
                "total_tasks": db.query(models.Task).count(),
                "total_inventory_items": db.query(models.InventoryItem).count(),
                "total_shifts": db.query(models.Shift).count() if hasattr(models, 'Shift') else 0,
                "open_orders": db.query(models.Order).filter(models.Order.status == "Pending").count() if hasattr(models, 'Order') else 0,
            },
            "features": ["Tasks", "Workers", "Inventory", "Shifts", "Attendance", "Quality", "Equipment", "Safety", "Orders", "Training", "Reporting", "Voice Commands"]
        }
    except Exception as e:
        return {"status": "❌ error", "message": str(e)}

# ============= HEALTH CHECK =============
@app.get("/health")
def health_check():
    return {
        "status": "✅ Healthy",
        "timestamp": datetime.utcnow(),
        "service": "VoiceFlow Kitchenware Management API v1.0"
    }

if __name__ == "__main__":
    import uvicorn
    print("Starting VoiceFlow Industrial Management System...")
    print("Dashboard: http://localhost:3000")
    print("Backend API: http://localhost:8001")
    print("Documentation: http://localhost:8001/docs")
    uvicorn.run(app, host="127.0.0.1", port=8001)
