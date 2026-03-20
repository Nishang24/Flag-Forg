"""
Audit logging utility for task changes
"""
import models
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, Any, Dict


def log_task_audit(
    db: Session,
    task_id: int,
    action: str,
    field_name: Optional[str] = None,
    old_value: Optional[str] = None,
    new_value: Optional[str] = None,
    source: str = "api",
    details: Optional[str] = None
):
    """
    Log a task change to the audit log.
    
    Args:
        db: Database session
        task_id: ID of the task being changed
        action: Type of action (created, updated, deleted, voice_command)
        field_name: Name of field that changed
        old_value: Previous value
        new_value: New value
        source: Source of change (voice, api, workflow, ui)
        details: Additional context/details
    """
    try:
        audit_log = models.TaskAuditLog(
            task_id=task_id,
            action=action,
            field_name=field_name,
            old_value=str(old_value) if old_value is not None else None,
            new_value=str(new_value) if new_value is not None else None,
            source=source,
            details=details,
            timestamp=datetime.utcnow()
        )
        db.add(audit_log)
        db.commit()
        print(f"✅ Audit logged: {action} on task {task_id} ({field_name})")
    except Exception as e:
        print(f"⚠️ Failed to log audit: {e}")
        # Don't fail the main operation if logging fails
        pass


def log_task_created(db: Session, task: models.Task, source: str = "api", details: Optional[str] = None):
    """Log task creation"""
    log_task_audit(
        db,
        task.id,
        "created",
        field_name="task",
        old_value=None,
        new_value=task.title,
        source=source,
        details=details or f"Task created via {source}"
    )


def log_task_deleted(db: Session, task_id: int, task_title: str, source: str = "api", details: Optional[str] = None):
    """Log task deletion"""
    log_task_audit(
        db,
        task_id,
        "deleted",
        field_name="task",
        old_value=task_title,
        new_value=None,
        source=source,
        details=details or f"Task deleted via {source}"
    )


def log_task_field_change(
    db: Session,
    task_id: int,
    field_name: str,
    old_value: Any,
    new_value: Any,
    source: str = "api"
):
    """Log a field change on a task"""
    log_task_audit(
        db,
        task_id,
        "updated",
        field_name=field_name,
        old_value=old_value,
        new_value=new_value,
        source=source,
        details=f"{field_name} changed from '{old_value}' to '{new_value}'"
    )


def get_task_history(db: Session, task_id: int, limit: int = 100) -> list:
    """Get audit history for a task"""
    logs = db.query(models.TaskAuditLog).filter(
        models.TaskAuditLog.task_id == task_id
    ).order_by(
        models.TaskAuditLog.timestamp.desc()
    ).limit(limit).all()
    return logs


def get_recent_activity(db: Session, limit: int = 50) -> list:
    """Get recent activity across all tasks"""
    logs = db.query(models.TaskAuditLog).order_by(
        models.TaskAuditLog.timestamp.desc()
    ).limit(limit).all()
    return logs


def clear_task_history(db: Session, task_id: int) -> int:
    """Clear audit history for a task (use cautiously!)"""
    deleted = db.query(models.TaskAuditLog).filter(
        models.TaskAuditLog.task_id == task_id
    ).delete()
    db.commit()
    return deleted
