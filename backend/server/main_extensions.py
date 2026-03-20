# ============= SHIFT MANAGEMENT ENDPOINTS (NEW FEATURE) =============
@app.post("/shifts", response_model=dict)
def create_shift(
    name: str,
    start_time: str,  # HH:MM format
    end_time: str,    # HH:MM format
    date: str,        # YYYY-MM-DD format
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
    """List all shifts, optionally filtered by date or status"""
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
            "shifts": [{"id": s.id, "name": s.name, "date": s.date, "start_time": s.start_time, "end_time": s.end_time} for s in shifts]
        }
    except Exception as e:
        return {"status": "❌ error", "message": str(e)}

@app.post("/shifts/{shift_id}/assign-worker")
def assign_worker_to_shift(
    shift_id: int,
    worker_id: int,
    db: Session = Depends(database.get_db)
):
    """Assign a worker to a shift"""
    try:
        shift = db.query(models.Shift).filter(models.Shift.id == shift_id).first()
        worker = db.query(models.Worker).filter(models.Worker.id == worker_id).first()
        
        if not shift or not worker:
            raise HTTPException(status_code=404, detail="Shift or worker not found")
        
        assignment = models.ShiftAssignment(
            shift_id=shift_id,
            worker_id=worker_id,
            status="Assigned"
        )
        db.add(assignment)
        db.commit()
        
        audit_logger.log_audit(
            db,
            action="create",
            entity_type="shift_assignment",
            entity_id=assignment.id,
            description=f"Assigned {worker.name} to shift {shift.name}",
            source="api"
        )
        
        return {
            "status": "✅ success",
            "message": f"Worker {worker.name} assigned to shift {shift.name}"
        }
    except Exception as e:
        return {"status": "❌ error", "message": str(e)}

# ============= ATTENDANCE ENDPOINTS (NEW FEATURE) =============
@app.post("/attendance/check-in")
def check_in_worker(
    worker_id: int,
    db: Session = Depends(database.get_db)
):
    """Record worker check-in"""
    try:
        worker = db.query(models.Worker).filter(models.Worker.id == worker_id).first()
        if not worker:
            raise HTTPException(status_code=404, detail="Worker not found")
        
        from datetime import datetime, date
        today = date.today().isoformat()
        
        # Check if already checked in today
        existing = db.query(models.AttendanceRecord).filter(
            models.AttendanceRecord.worker_id == worker_id,
            models.AttendanceRecord.date == today
        ).first()
        
        if existing and existing.check_in_time:
            return {
                "status": "⚠️ warning",
                "message": f"{worker.name} already checked in at {existing.check_in_time}"
            }
        
        record = models.AttendanceRecord(
            worker_id=worker_id,
            date=today,
            check_in_time=datetime.now().strftime("%H:%M:%S"),
            status="Present"
        )
        db.add(record)
        db.commit()
        
        audit_logger.log_audit(
            db,
            action="create",
            entity_type="attendance",
            entity_id=record.id,
            description=f"{worker.name} checked in",
            source="api"
        )
        
        return {
            "status": "✅ success",
            "message": f"{worker.name} checked in successfully",
            "check_in_time": record.check_in_time
        }
    except Exception as e:
        return {"status": "❌ error", "message": str(e)}

@app.post("/attendance/check-out")
def check_out_worker(
    worker_id: int,
    db: Session = Depends(database.get_db)
):
    """Record worker check-out"""
    try:
        worker = db.query(models.Worker).filter(models.Worker.id == worker_id).first()
        if not worker:
            raise HTTPException(status_code=404, detail="Worker not found")
        
        from datetime import datetime, date
        today = date.today().isoformat()
        
        record = db.query(models.AttendanceRecord).filter(
            models.AttendanceRecord.worker_id == worker_id,
            models.AttendanceRecord.date == today
        ).first()
        
        if not record:
            raise HTTPException(status_code=400, detail="No check-in record found for today")
        
        record.check_out_time = datetime.now().strftime("%H:%M:%S")
        
        # Calculate hours worked
        from datetime import datetime as dt
        check_in = dt.strptime(record.check_in_time, "%H:%M:%S")
        check_out = dt.strptime(record.check_out_time, "%H:%M:%S")
        hours = (check_out - check_in).total_seconds() / 3600
        record.hours_worked = round(hours, 2)
        
        db.commit()
        
        audit_logger.log_audit(
            db,
            action="update",
            entity_type="attendance",
            entity_id=record.id,
            description=f"{worker.name} checked out ({hours:.1f} hours)",
            source="api"
        )
        
        return {
            "status": "✅ success",
            "message": f"{worker.name} checked out",
            "hours_worked": record.hours_worked
        }
    except Exception as e:
        return {"status": "❌ error", "message": str(e)}

@app.get("/attendance/daily")
def get_daily_attendance(
    date: Optional[str] = None,
    db: Session = Depends(database.get_db)
):
    """Get daily attendance report"""
    try:
        from datetime import date as dt_date
        if not date:
            date = dt_date.today().isoformat()
        
        records = db.query(models.AttendanceRecord).filter(
            models.AttendanceRecord.date == date
        ).all()
        
        present = len([r for r in records if r.status == "Present"])
        absent = len([r for r in records if r.status == "Absent"])
        
        return {
            "status": "✅ success",
            "date": date,
            "present": present,
            "absent": absent,
            "total": present + absent,
            "records": [{"worker_id": r.worker_id, "status": r.status, "check_in": r.check_in_time} for r in records]
        }
    except Exception as e:
        return {"status": "❌ error", "message": str(e)}

# ============= QUALITY CONTROL ENDPOINTS (NEW FEATURE) =============
@app.post("/quality-checks")
def record_quality_check(
    item_id: int,
    result: str,  # Pass or Fail
    notes: str = "",
    db: Session = Depends(database.get_db)
):
    """Record a quality check for inventory item"""
    try:
        item = db.query(models.InventoryItem).filter(models.InventoryItem.id == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        
        from datetime import datetime
        check = models.QualityCheck(
            item_id=item_id,
            result=result,
            notes=notes,
            checked_at=datetime.utcnow()
        )
        db.add(check)
        db.commit()
        
        audit_logger.log_audit(
            db,
            action="create",
            entity_type="quality_check",
            entity_id=check.id,
            description=f"Quality check for {item.name}: {result}",
            source="api"
        )
        
        return {
            "status": "✅ success",
            "message": f"Quality check recorded: {result}",
            "check_id": check.id
        }
    except Exception as e:
        return {"status": "❌ error", "message": str(e)}

@app.get("/quality-reports")
def get_quality_report(
    days: int = 7,
    db: Session = Depends(database.get_db)
):
    """Get quality report for past N days"""
    try:
        from datetime import datetime, timedelta
        since = datetime.utcnow() - timedelta(days=days)
        
        checks = db.query(models.QualityCheck).filter(
            models.QualityCheck.checked_at >= since
        ).all()
        
        passed = len([c for c in checks if c.result == "Pass"])
        failed = len([c for c in checks if c.result == "Fail"])
        pass_rate = (passed / len(checks) * 100) if checks else 0
        
        return {
            "status": "✅ success",
            "period_days": days,
            "total_checks": len(checks),
            "passed": passed,
            "failed": failed,
            "pass_rate": round(pass_rate, 2)
        }
    except Exception as e:
        return {"status": "❌ error", "message": str(e)}

# ============= EQUIPMENT MANAGEMENT ENDPOINTS (NEW FEATURE) =============
@app.post("/equipment")
def register_equipment(
    name: str,
    equipment_type: str,
    location: str,
    purchase_date: str = None,
    db: Session = Depends(database.get_db)
):
    """Register new equipment"""
    try:
        equipment = models.Equipment(
            name=name,
            equipment_type=equipment_type,
            location=location,
            purchase_date=purchase_date,
            status="Active"
        )
        db.add(equipment)
        db.commit()
        db.refresh(equipment)
        
        audit_logger.log_audit(
            db,
            action="create",
            entity_type="equipment",
            entity_id=equipment.id,
            description=f"Registered equipment: {name} ({equipment_type})",
            source="api"
        )
        
        return {
            "status": "✅ success",
            "message": f"Equipment {name} registered",
            "equipment_id": equipment.id
        }
    except Exception as e:
        return {"status": "❌ error", "message": str(e)}

@app.get("/equipment")
def list_equipment(db: Session = Depends(database.get_db)):
    """List all equipment"""
    try:
        equipment = db.query(models.Equipment).all()
        return {
            "status": "✅ success",
            "count": len(equipment),
            "equipment": [{"id": e.id, "name": e.name, "type": e.equipment_type, "status": e.status} for e in equipment]
        }
    except Exception as e:
        return {"status": "❌ error", "message": str(e)}

@app.post("/equipment/{equipment_id}/maintenance")
def schedule_maintenance(
    equipment_id: int,
    maintenance_type: str,
    scheduled_date: str,
    db: Session = Depends(database.get_db)
):
    """Schedule maintenance for equipment"""
    try:
        equipment = db.query(models.Equipment).filter(models.Equipment.id == equipment_id).first()
        if not equipment:
            raise HTTPException(status_code=404, detail="Equipment not found")
        
        schedule = models.MaintenanceSchedule(
            equipment_id=equipment_id,
            maintenance_type=maintenance_type,
            scheduled_date=scheduled_date,
            status="Scheduled"
        )
        db.add(schedule)
        db.commit()
        
        audit_logger.log_audit(
            db,
            action="create",
            entity_type="maintenance",
            entity_id=schedule.id,
            description=f"Maintenance scheduled for {equipment.name} on {scheduled_date}",
            source="api"
        )
        
        return {
            "status": "✅ success",
            "message": f"Maintenance scheduled for {equipment.name}"
        }
    except Exception as e:
        return {"status": "❌ error", "message": str(e)}

# ============= SAFETY MANAGEMENT ENDPOINTS (NEW FEATURE) =============
@app.post("/safety-incidents")
def report_safety_incident(
    incident_type: str,
    severity: str,
    description: str,
    worker_id: Optional[int] = None,
    db: Session = Depends(database.get_db)
):
    """Report a safety incident"""
    try:
        from datetime import datetime
        incident = models.SafetyIncident(
            incident_type=incident_type,
            severity=severity,
            description=description,
            worker_id=worker_id,
            reported_at=datetime.utcnow(),
            status="Open"
        )
        db.add(incident)
        db.commit()
        
        audit_logger.log_audit(
            db,
            action="create",
            entity_type="safety_incident",
            entity_id=incident.id,
            description=f"Safety incident reported: {incident_type} ({severity})",
            source="api"
        )
        
        return {
            "status": "✅ success",
            "message": f"Safety incident reported ({severity})",
            "incident_id": incident.id
        }
    except Exception as e:
        return {"status": "❌ error", "message": str(e)}

@app.get("/safety-incidents")
def list_safety_incidents(
    severity: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(database.get_db)
):
    """List safety incidents"""
    try:
        query = db.query(models.SafetyIncident)
        if severity:
            query = query.filter(models.SafetyIncident.severity == severity)
        if status:
            query = query.filter(models.SafetyIncident.status == status)
        
        incidents = query.order_by(models.SafetyIncident.reported_at.desc()).all()
        
        return {
            "status": "✅ success",
            "count": len(incidents),
            "incidents": [
                {"id": i.id, "type": i.incident_type, "severity": i.severity, "status": i.status}
                for i in incidents
            ]
        }
    except Exception as e:
        return {"status": "❌ error", "message": str(e)}

# ============= ORDER MANAGEMENT ENDPOINTS (NEW FEATURE) =============
@app.post("/orders")
def create_order(
    customer_name: str,
    items: dict,  # {"item_id": quantity, ...}
    delivery_date: str = None,
    db: Session = Depends(database.get_db)
):
    """Create new customer order"""
    try:
        from datetime import datetime
        order = models.Order(
            customer_name=customer_name,
            items=items,
            status="Pending",
            created_at=datetime.utcnow(),
            delivery_date=delivery_date
        )
        db.add(order)
        db.commit()
        db.refresh(order)
        
        audit_logger.log_audit(
            db,
            action="create",
            entity_type="order",
            entity_id=order.id,
            description=f"Order created for {customer_name}",
            source="api"
        )
        
        return {
            "status": "✅ success",
            "message": f"Order created",
            "order_id": order.id
        }
    except Exception as e:
        return {"status": "❌ error", "message": str(e)}

@app.get("/orders")
def list_orders(
    status: Optional[str] = None,
    db: Session = Depends(database.get_db)
):
    """List all orders"""
    try:
        query = db.query(models.Order)
        if status:
            query = query.filter(models.Order.status == status)
        
        orders = query.all()
        
        return {
            "status": "✅ success",
            "count": len(orders),
            "orders": [
                {"id": o.id, "customer": o.customer_name, "status": o.status}
                for o in orders
            ]
        }
    except Exception as e:
        return {"status": "❌ error", "message": str(e)}

@app.post("/complaints")
def record_complaint(
    order_id: Optional[int] = None,
    customer_name: str = None,
    complaint_type: str = None,
    description: str = None,
    db: Session = Depends(database.get_db)
):
    """Record a customer complaint"""
    try:
        from datetime import datetime
        complaint = models.Complaint(
            order_id=order_id,
            customer_name=customer_name,
            complaint_type=complaint_type,
            description=description,
            reported_at=datetime.utcnow(),
            status="Open"
        )
        db.add(complaint)
        db.commit()
        
        audit_logger.log_audit(
            db,
            action="create",
            entity_type="complaint",
            entity_id=complaint.id,
            description=f"Complaint recorded: {complaint_type}",
            source="api"
        )
        
        return {
            "status": "✅ success",
            "message": "Complaint recorded",
            "complaint_id": complaint.id
        }
    except Exception as e:
        return {"status": "❌ error", "message": str(e)}

# ============= TRAINING MANAGEMENT ENDPOINTS (NEW FEATURE) =============
@app.post("/training")
def record_training(
    worker_id: int,
    training_title: str,
    training_date: str,
    duration_hours: int = 1,
    db: Session = Depends(database.get_db)
):
    """Record worker training"""
    try:
        worker = db.query(models.Worker).filter(models.Worker.id == worker_id).first()
        if not worker:
            raise HTTPException(status_code=404, detail="Worker not found")
        
        training = models.TrainingRecord(
            worker_id=worker_id,
            training_title=training_title,
            training_date=training_date,
            duration_hours=duration_hours,
            status="Completed"
        )
        db.add(training)
        db.commit()
        
        audit_logger.log_audit(
            db,
            action="create",
            entity_type="training",
            entity_id=training.id,
            description=f"Recorded training for {worker.name}: {training_title}",
            source="api"
        )
        
        return {
            "status": "✅ success",
            "message": f"Training recorded for {worker.name}",
            "training_id": training.id
        }
    except Exception as e:
        return {"status": "❌ error", "message": str(e)}

# ============= REPORTING ENDPOINTS (NEW FEATURE) =============
@app.get("/reports/daily")
def get_daily_report(
    date: Optional[str] = None,
    db: Session = Depends(database.get_db)
):
    """Get daily activity report"""
    try:
        from datetime import date as dt_date
        if not date:
            date = dt_date.today().isoformat()
        
        # Get daily stats
        tasks = db.query(models.Task).filter(models.Task.created_at.ilike(f"{date}%")).count()
        attendance_records = db.query(models.AttendanceRecord).filter(
            models.AttendanceRecord.date == date
        ).count()
        quality_checks = db.query(models.QualityCheck).filter(
            models.QualityCheck.checked_at.ilike(f"{date}%")
        ).count()
        
        return {
            "status": "✅ success",
            "date": date,
            "tasks_created": tasks,
            "workers_present": attendance_records,
            "quality_checks": quality_checks
        }
    except Exception as e:
        return {"status": "❌ error", "message": str(e)}

@app.get("/reports/performance")
def get_performance_report(
    worker_id: Optional[int] = None,
    db: Session = Depends(database.get_db)
):
    """Get performance metrics report"""
    try:
        if worker_id:
            worker = db.query(models.Worker).filter(models.Worker.id == worker_id).first()
            if not worker:
                raise HTTPException(status_code=404, detail="Worker not found")
            
            training_count = db.query(models.TrainingRecord).filter(
                models.TrainingRecord.worker_id == worker_id
            ).count()
            
            assignments = db.query(models.WorkerAssignment).filter(
                models.WorkerAssignment.worker_id == worker_id
            ).count()
            
            return {
                "status": "✅ success",
                "worker_id": worker_id,
                "worker_name": worker.name,
                "tasks_assigned": assignments,
                "trainings_completed": training_count
            }
        else:
            total_workers = db.query(models.Worker).count()
            total_trainings = db.query(models.TrainingRecord).count()
            
            return {
                "status": "✅ success",
                "total_workers": total_workers,
                "total_trainings_recorded": total_trainings
            }
    except Exception as e:
        return {"status": "❌ error", "message": str(e)}

# ============= COST & ANALYTICS ENDPOINTS (NEW FEATURE) =============
@app.post("/cost-tracking")
def track_cost(
    entity_type: str,
    entity_id: int,
    amount: float,
    description: str,
    db: Session = Depends(database.get_db)
):
    """Track costs for various operations"""
    try:
        from datetime import datetime
        cost = models.CostTracking(
            entity_type=entity_type,
            entity_id=entity_id,
            amount=amount,
            description=description,
            recorded_at=datetime.utcnow()
        )
        db.add(cost)
        db.commit()
        
        return {
            "status": "✅ success",
            "message": f"Cost recorded: {description}",
            "amount": amount
        }
    except Exception as e:
        return {"status": "❌ error", "message": str(e)}

@app.get("/cost-analysis")
def get_cost_analysis(
    days: int = 30,
    db: Session = Depends(database.get_db)
):
    """Get cost analysis for past N days"""
    try:
        from datetime import datetime, timedelta
        since = datetime.utcnow() - timedelta(days=days)
        
        costs = db.query(models.CostTracking).filter(
            models.CostTracking.recorded_at >= since
        ).all()
        
        total_cost = sum(c.amount for c in costs)
        by_type = {}
        for cost in costs:
            if cost.entity_type not in by_type:
                by_type[cost.entity_type] = 0
            by_type[cost.entity_type] += cost.amount
        
        return {
            "status": "✅ success",
            "period_days": days,
            "total_cost": round(total_cost, 2),
            "by_type": {k: round(v, 2) for k, v in by_type.items()}
        }
    except Exception as e:
        return {"status": "❌ error", "message": str(e)}

# ============= SYSTEM STATUS ENDPOINTS =============
@app.get("/system-status")
def system_status(db: Session = Depends(database.get_db)):
    """Get complete system status and statistics"""
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
                "unresolved_complaints": db.query(models.Complaint).filter(models.Complaint.status == "Open").count() if hasattr(models, 'Complaint') else 0,
                "safety_incidents": db.query(models.SafetyIncident).filter(models.SafetyIncident.status == "Open").count() if hasattr(models, 'SafetyIncident') else 0
            },
            "features": [
                "Tasks Management",
                "Worker Management",
                "Inventory Management",
                "Shift Scheduling",
                "Attendance Tracking",
                "Quality Control",
                "Equipment Management",
                "Safety Management",
                "Order Processing",
                "Training Management",
                "Cost Tracking",
                "Voice Commands",
                "Reporting & Analytics"
            ]
        }
    except Exception as e:
        return {"status": "❌ error", "message": str(e)}
