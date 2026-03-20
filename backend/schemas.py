from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# ============= WORKER SCHEMAS =============
class WorkerBase(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    position: str
    department: str
    status: str = "Active"
    salary: Optional[float] = None

class WorkerCreate(WorkerBase):
    pass

class WorkerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    position: Optional[str] = None
    department: Optional[str] = None
    status: Optional[str] = None
    salary: Optional[float] = None

class Worker(WorkerBase):
    id: int
    hire_date: datetime
    user_id: Optional[int] = None

    class Config:
        from_attributes = True

# ============= INVENTORY SCHEMAS =============
class InventoryItemBase(BaseModel):
    name: str
    category: str
    sku: str
    quantity: int = 0
    min_quantity: int = 10
    unit: str
    price_per_unit: float
    supplier: Optional[str] = None
    location: Optional[str] = None

class InventoryItemCreate(InventoryItemBase):
    pass

class InventoryItemUpdate(BaseModel):
    name: Optional[str] = None
    quantity: Optional[int] = None
    min_quantity: Optional[int] = None
    price_per_unit: Optional[float] = None
    supplier: Optional[str] = None
    location: Optional[str] = None
    status: Optional[str] = None

class InventoryItem(InventoryItemBase):
    id: int
    last_updated: datetime

    class Config:
        from_attributes = True

class InventoryTransactionBase(BaseModel):
    item_id: int
    transaction_type: str
    quantity: int
    reference: Optional[str] = None
    notes: Optional[str] = None

class InventoryTransaction(InventoryTransactionBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True

# ============= TASK SCHEMAS =============
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: str = "Todo"
    priority: str = "Medium"
    due_date: Optional[datetime] = None
    task_type: str = "production"
    estimated_hours: Optional[float] = None
    batch_id: Optional[str] = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[datetime] = None
    actual_hours: Optional[float] = None

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
    actual_hours: Optional[float] = None
    audit_logs: Optional[List[TaskAuditLog]] = []

    class Config:
        from_attributes = True

class WorkerAssignmentBase(BaseModel):
    worker_id: int
    task_id: Optional[int] = None

class WorkerAssignment(WorkerAssignmentBase):
    id: int
    assigned_date: datetime
    status: str

    class Config:
        from_attributes = True

class WorkflowTriggerBase(BaseModel):
    task_id: int
    condition: str
    action: str

class WorkflowTriggerCreate(WorkflowTriggerBase):
    pass

class WorkflowTrigger(WorkflowTriggerBase):
    id: int
    is_active: bool = True

    class Config:
        from_attributes = True

# ============= AUDIT LOG SCHEMA =============
class AuditLogBase(BaseModel):
    action: str
    entity_type: str
    entity_id: int
    description: str
    source: str = "api"

class AuditLog(AuditLogBase):
    id: int
    user_id: Optional[int] = None
    worker_id: Optional[int] = None
    task_id: Optional[int] = None
    inventory_id: Optional[int] = None
    timestamp: datetime

    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    username: str
    email: str
    role: str = "worker"

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str

    class Config:
        from_attributes = True

# ============= VOICE COMMAND RESPONSE =============
class VoiceCommandRequest(BaseModel):
    transcription: str

class VoiceCommandResponse(BaseModel):
    action: str
    entity_type: str
    data: dict
    confidence: float = 0.95
