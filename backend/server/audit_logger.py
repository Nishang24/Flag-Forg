from sqlalchemy.orm import Session
from datetime import datetime
import models

def log_audit(db: Session, action: str, entity_type: str, entity_id: int, description: str, 
              source: str = "api", user_id: int = None, worker_id: int = None, 
              task_id: int = None, inventory_id: int = None):
    """
    Unified audit logging for all entities (workers, inventory, tasks).
    """
    audit_log = models.AuditLog(
        user_id=user_id,
        worker_id=worker_id if entity_type == "worker" else None,
        task_id=task_id if entity_type == "task" else None,
        inventory_id=inventory_id if entity_type == "inventory" else None,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        description=description,
        source=source,
        timestamp=datetime.utcnow()
    )
    db.add(audit_log)
    db.commit()
    return audit_log

def log_task_created(db: Session, task: models.Task, source: str = "api", details: str = None):
    """Log task creation"""
    log_audit(
        db,
        action="created",
        entity_type="task",
        entity_id=task.id,
        description=f"Task created: {task.title}",
        source=source,
        task_id=task.id
    )

def log_task_updated(db: Session, task_id: int, task_title: str, changes: str, source: str = "api"):
    """Log task update"""
    log_audit(
        db,
        action="updated",
        entity_type="task",
        entity_id=task_id,
        description=f"Task updated: {task_title} - {changes}",
        source=source,
        task_id=task_id
    )

def log_task_field_change(db: Session, task_id: int, field_name: str, old_value, new_value, source: str = "api"):
    """Log individual field change for tasks"""
    task_audit = models.TaskAuditLog(
        task_id=task_id,
        action="updated",
        field_name=field_name,
        old_value=str(old_value),
        new_value=str(new_value),
        source=source,
        timestamp=datetime.utcnow()
    )
    db.add(task_audit)
    db.commit()

def log_task_deleted(db: Session, task_id: int, task_title: str, source: str = "api", details: str = None):
    """Log task deletion"""
    log_audit(
        db,
        action="deleted",
        entity_type="task",
        entity_id=task_id,
        description=f"Task deleted: {task_title}" + (f" - {details}" if details else ""),
        source=source,
        task_id=task_id
    )

def log_worker_created(db: Session, worker: models.Worker, source: str = "api"):
    """Log worker creation"""
    log_audit(
        db,
        action="created",
        entity_type="worker",
        entity_id=worker.id,
        description=f"Worker created: {worker.name} ({worker.position})",
        source=source,
        worker_id=worker.id
    )

def log_worker_updated(db: Session, worker_id: int, worker_name: str, changes: str, source: str = "api"):
    """Log worker update"""
    log_audit(
        db,
        action="updated",
        entity_type="worker",
        entity_id=worker_id,
        description=f"Worker updated: {worker_name} - {changes}",
        source=source,
        worker_id=worker_id
    )

def log_worker_deleted(db: Session, worker_id: int, worker_name: str, source: str = "api"):
    """Log worker deletion"""
    log_audit(
        db,
        action="deleted",
        entity_type="worker",
        entity_id=worker_id,
        description=f"Worker deleted: {worker_name}",
        source=source,
        worker_id=worker_id
    )

def log_inventory_created(db: Session, item: models.InventoryItem, source: str = "api"):
    """Log inventory item creation"""
    log_audit(
        db,
        action="created",
        entity_type="inventory",
        entity_id=item.id,
        description=f"Inventory created: {item.name} (SKU: {item.sku})",
        source=source,
        inventory_id=item.id
    )

def log_inventory_transaction(db: Session, item_id: int, transaction_type: str, quantity: int, 
                             item_name: str, source: str = "api"):
    """Log inventory transaction"""
    log_audit(
        db,
        action=transaction_type,
        entity_type="inventory",
        entity_id=item_id,
        description=f"Inventory {transaction_type}: {item_name} ({quantity} units)",
        source=source,
        inventory_id=item_id
    )

def get_audit_trail(db: Session, entity_type: str, entity_id: int):
    """Get full audit trail for an entity"""
    return db.query(models.AuditLog).filter(
        models.AuditLog.entity_type == entity_type,
        models.AuditLog.entity_id == entity_id
    ).order_by(models.AuditLog.timestamp.desc()).all()
