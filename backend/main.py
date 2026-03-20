from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import models, schemas, database, workflow_engine, voice_parser, audit_logger
from database import engine
from pydantic import BaseModel

from fastapi.middleware.cors import CORSMiddleware

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="VoiceFlow API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to VoiceFlow API"}

@app.post("/tasks/", response_model=schemas.Task)
def create_task(task: schemas.TaskCreate, db: Session = Depends(database.get_db)):
    db_task = models.Task(**task.dict())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    # Log task creation
    audit_logger.log_task_created(db, db_task, source="api")
    
    # Trigger workflow engine check
    workflow_engine.check_and_trigger_workflows(db_task.id, db_task.status, db)
    
    return db_task

@app.get("/tasks/", response_model=List[schemas.Task])
def read_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    tasks = db.query(models.Task).offset(skip).limit(limit).all()
    return tasks

@app.put("/tasks/{task_id}", response_model=schemas.Task)
def update_task(task_id: int, task: schemas.TaskUpdate, db: Session = Depends(database.get_db)):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    update_data = task.dict(exclude_unset=True)
    
    # Log each field change
    for key, value in update_data.items():
        old_value = getattr(db_task, key)
        if old_value != value:
            audit_logger.log_task_field_change(db, task_id, key, old_value, value, source="api")
        setattr(db_task, key, value)
    
    db.commit()
    db.refresh(db_task)
    
    # Trigger workflow engine
    workflow_engine.check_and_trigger_workflows(db_task.id, db_task.status, db)
    
    return db_task

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(database.get_db)):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task_title = db_task.title
    
    # Delete associated workflows first
    db.query(models.WorkflowTrigger).filter(models.WorkflowTrigger.task_id == task_id).delete()
    
    # Log deletion before deleting
    audit_logger.log_task_deleted(db, task_id, task_title, source="api")
    
    db.delete(db_task)
    db.commit()
    return {"message": "Task deleted successfully"}

@app.post("/workflows/", response_model=schemas.WorkflowTrigger)
def create_workflow(workflow: schemas.WorkflowTriggerCreate, db: Session = Depends(database.get_db)):
    db_workflow = models.WorkflowTrigger(**workflow.dict())
    db.add(db_workflow)
    db.commit()
    db.refresh(db_workflow)
    return db_workflow

class VoiceRequest(BaseModel):
    transcription: str

@app.post("/voice/process")
def process_voice_command(request: VoiceRequest, db: Session = Depends(database.get_db)):
    """
    🎤 Main voice processing endpoint.
    Takes voice transcription, parses intent with GPT-4o, and executes action.
    """
    try:
        intent = voice_parser.parse_intent(request.transcription)
        
        if intent["action"] == "create":
            db_task = models.Task(
                title=intent.get("title", "New Voice Task"),
                description=intent.get("description"),
                priority=intent.get("priority", "Medium"),
                status=intent.get("status", "Todo"),
                due_date=intent.get("due_date")
            )
            db.add(db_task)
            db.commit()
            db.refresh(db_task)
            
            # Log voice command
            audit_logger.log_task_created(
                db, 
                db_task, 
                source="voice",
                details=f"Created via voice: '{request.transcription}'"
            )
            
            # Trigger workflows
            workflow_engine.check_and_trigger_workflows(db_task.id, db_task.status, db)
            
            return {
                "status": "success",
                "message": f"✅ Created task: {db_task.title}",
                "task": db_task,
                "audio_response": f"Task created: {db_task.title}"
            }
        
        elif intent["action"] == "delete":
            # Find task by title and delete it
            db_task = db.query(models.Task).filter(
                models.Task.title.ilike(f"%{intent.get('title', '')}%")
            ).first()
            if db_task:
                task_title = db_task.title
                # Log voice deletion
                audit_logger.log_task_deleted(
                    db,
                    db_task.id,
                    task_title,
                    source="voice",
                    details=f"Deleted via voice: '{request.transcription}'"
                )
                db.delete(db_task)
                db.commit()
                return {
                    "status": "success",
                    "message": f"❌ Deleted task: {task_title}",
                    "audio_response": f"Task deleted: {task_title}"
                }
            return {"status": "error", "message": "Task not found"}
        
        else:
            return {
                "status": "success",
                "message": "Intent recognized",
                "intent": intent,
                "audio_response": f"I understood: {intent.get('title', 'your command')}"
            }
    
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error processing voice: {str(e)}",
            "audio_response": "Sorry, I couldn't process that command"
        }

@app.get("/workflows/{task_id}")
def get_workflows(task_id: int, db: Session = Depends(database.get_db)):
    """Get all workflows for a specific task"""
    workflows = db.query(models.WorkflowTrigger).filter(
        models.WorkflowTrigger.task_id == task_id
    ).all()
    return workflows

@app.get("/workflows/")
def list_workflows(db: Session = Depends(database.get_db)):
    """List all workflows"""
    return db.query(models.WorkflowTrigger).all()

@app.delete("/workflows/{workflow_id}")
def delete_workflow(workflow_id: int, db: Session = Depends(database.get_db)):
    """Delete a workflow"""
    workflow = db.query(models.WorkflowTrigger).filter(
        models.WorkflowTrigger.id == workflow_id
    ).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    db.delete(workflow)
    db.commit()
    return {"message": "Workflow deleted"}

@app.post("/seed-demo-data")
def seed_demo_data(db: Session = Depends(database.get_db)):
    """
    Seed database with demo data for presentation/testing.
    Creates realistic tasks and workflows.
    """
    # Clear existing data
    db.query(models.WorkflowTrigger).delete()
    db.query(models.Task).delete()
    db.query(models.User).delete()
    db.commit()

    # Create demo user
    demo_user = models.User(username="demo")
    db.add(demo_user)
    db.flush()

    # Create demo tasks
    demo_tasks = [
        models.Task(
            title="Website Redesign Landing Page",
            description="Create modern landing page with glassmorphism design",
            status="InProgress",
            priority="High",
            owner_id=demo_user.id
        ),
        models.Task(
            title="Fix Navigation Bug",
            description="Users report dropdown menu not responding on mobile",
            status="Todo",
            priority="High",
            owner_id=demo_user.id
        ),
        models.Task(
            title="Implement Voice Analytics",
            description="Track voice command success rates and patterns",
            status="Todo",
            priority="Medium",
            owner_id=demo_user.id
        ),
        models.Task(
            title="Database Migration to PostgreSQL",
            description="Migrate from SQLite to PostgreSQL for production",
            status="Done",
            priority="Medium",
            owner_id=demo_user.id
        ),
        models.Task(
            title="Setup CI/CD Pipeline",
            description="Configure GitHub Actions for automated testing and deployment",
            status="Done",
            priority="High",
            owner_id=demo_user.id
        ),
        models.Task(
            title="Slack Integration Testing",
            description="Verify all workflow actions trigger correctly",
            status="InProgress",
            priority="Medium",
            owner_id=demo_user.id
        ),
    ]

    db.add_all(demo_tasks)
    db.flush()

    # Create demo workflows
    demo_workflows = [
        models.WorkflowTrigger(
            task_id=demo_tasks[0].id,
            condition="Status Changed to Done",
            action="Send Slack Notification - Task Completed"
        ),
        models.WorkflowTrigger(
            task_id=demo_tasks[1].id,
            condition="Status Changed to Done",
            action="Send Discord Notification - Bug Fixed"
        ),
        models.WorkflowTrigger(
            task_id=demo_tasks[5].id,
            condition="Status Changed to InProgress",
            action="Send Slack Notification - Testing Started"
        ),
    ]

    db.add_all(demo_workflows)
    db.commit()

    return {
        "status": "success",
        "message": "Demo data seeded successfully",
        "tasks_created": len(demo_tasks),
        "workflows_created": len(demo_workflows)
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "VoiceFlow API"}

# ==================== AUDIT LOG ENDPOINTS ====================

@app.get("/tasks/{task_id}/history", response_model=List[schemas.TaskAuditLog])
def get_task_history(task_id: int, limit: int = 100, db: Session = Depends(database.get_db)):
    """
    Get complete audit history for a specific task.
    Shows all changes: creation, status updates, deletions, etc.
    """
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return audit_logger.get_task_history(db, task_id, limit)

@app.get("/audit/recent", response_model=List[schemas.TaskAuditLog])
def get_recent_activity(limit: int = 50, db: Session = Depends(database.get_db)):
    """
    Get recent activity across all tasks.
    Useful for activity dashboard/feed.
    """
    return audit_logger.get_recent_activity(db, limit)

@app.get("/audit/stats")
def get_audit_stats(db: Session = Depends(database.get_db)):
    """
    Get audit statistics:
    - Total events
    - By action type
    - By source (voice, api, workflow, ui)
    - Recent changes
    """
    try:
        total_events = db.query(models.TaskAuditLog).count()
        
        # Count by action
        actions = {}
        for action_type in ["created", "updated", "deleted", "voice_command"]:
            count = db.query(models.TaskAuditLog).filter(
                models.TaskAuditLog.action == action_type
            ).count()
            if count > 0:
                actions[action_type] = count
        
        # Count by source
        sources = {}
        for source_type in ["voice", "api", "workflow", "ui"]:
            count = db.query(models.TaskAuditLog).filter(
                models.TaskAuditLog.source == source_type
            ).count()
            if count > 0:
                sources[source_type] = count
        
        # Most active field
        most_changed_field = db.query(
            models.TaskAuditLog.field_name
        ).filter(
            models.TaskAuditLog.field_name != None
        ).group_by(
            models.TaskAuditLog.field_name
        ).order_by(
            "count DESC"
        ).first()
        
        return {
            "total_events": total_events,
            "by_action": actions,
            "by_source": sources,
            "most_changed_field": most_changed_field[0] if most_changed_field else "status"
        }
    except Exception as e:
        return {
            "error": str(e),
            "total_events": 0,
            "by_action": {},
            "by_source": {}
        }

@app.get("/audit/export")
def export_audit_logs(task_id: Optional[int] = None, db: Session = Depends(database.get_db)):
    """
    Export audit logs as JSON for analysis or compliance.
    Optionally filter by task_id.
    """
    if task_id:
        logs = audit_logger.get_task_history(db, task_id, limit=1000)
    else:
        logs = audit_logger.get_recent_activity(db, limit=10000)
    
    return {
        "export_date": datetime.utcnow().isoformat(),
        "total_records": len(logs),
        "records": [
            {
                "id": log.id,
                "task_id": log.task_id,
                "action": log.action,
                "field_name": log.field_name,
                "old_value": log.old_value,
                "new_value": log.new_value,
                "source": log.source,
                "timestamp": log.timestamp.isoformat(),
                "details": log.details
            }
            for log in logs
        ]
    }

@app.delete("/audit/clear/{task_id}")
def clear_audit_logs(task_id: int, db: Session = Depends(database.get_db)):
    """
    Clear audit logs for a specific task.
    WARNING: This is permanent and cannot be undone!
    """
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    deleted_count = audit_logger.clear_task_history(db, task_id)
    
    return {
        "message": f"Cleared {deleted_count} audit log entries for task {task_id}",
        "deleted_count": deleted_count
    }


if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting VoiceFlow Backend Server...")
    print("📊 API Documentation: http://localhost:8000/docs")
    print("🎤 Voice Processing: POST http://localhost:8000/voice/process")
    uvicorn.run(app, host="0.0.0.0", port=8000)

