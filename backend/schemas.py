from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: str = "Todo"
    priority: str = "Medium"
    due_date: Optional[datetime] = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(TaskBase):
    title: Optional[str] = None

class TaskAuditLogBase(BaseModel):
    action: str
    field_name: Optional[str] = None
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    source: str = "api"
    details: Optional[str] = None

class TaskAuditLog(TaskAuditLogBase):
    id: int
    task_id: int
    timestamp: datetime

    class Config:
        from_attributes = True

class Task(TaskBase):
    id: int
    owner_id: Optional[int] = None
    audit_logs: Optional[List[TaskAuditLog]] = []

    class Config:
        from_attributes = True

class TaskWithHistory(Task):
    """Task with full audit history"""
    audit_logs: List[TaskAuditLog] = []

class WorkflowTriggerBase(BaseModel):
    task_id: int
    condition: str
    action: str

class WorkflowTriggerCreate(WorkflowTriggerBase):
    pass

class WorkflowTrigger(WorkflowTriggerBase):
    id: int

    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    role: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
