from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Text, Float, Boolean, Date, Time
from sqlalchemy.orm import relationship
from database import Base
import datetime

# ============= USER & ACCESS =============
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    role = Column(String, default="worker")  # manager, supervisor, worker, admin
    tasks = relationship("Task", back_populates="owner")
    workers = relationship("Worker", back_populates="user")
    audits = relationship("AuditLog", back_populates="user")

# ============= SHIFT MANAGEMENT =============
class Shift(Base):
    __tablename__ = "shifts"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)  # Morning, Evening, Night
    start_time = Column(Time)
    end_time = Column(Time)
    workers = relationship("ShiftAssignment", back_populates="shift")
    
class ShiftAssignment(Base):
    __tablename__ = "shift_assignments"
    id = Column(Integer, primary_key=True, index=True)
    worker_id = Column(Integer, ForeignKey("workers.id"))
    shift_id = Column(Integer, ForeignKey("shifts.id"))
    date = Column(Date, default=datetime.date.today)
    status = Column(String, default="Assigned")  # Assigned, Attended, Absent, Late
    shift = relationship("Shift", back_populates="workers")
    worker = relationship("Worker")

# ============= WORKER MANAGEMENT (Enhanced) =============
class Worker(Base):
    __tablename__ = "workers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String, nullable=True)
    position = Column(String)
    department = Column(String)
    status = Column(String, default="Active")
    salary = Column(Float, nullable=True)
    hire_date = Column(DateTime, default=datetime.datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user = relationship("User", back_populates="workers")
    assignments = relationship("WorkerAssignment", back_populates="worker")
    audit_logs = relationship("AuditLog", back_populates="worker", cascade="all, delete-orphan")
    performance = relationship("PerformanceMetric", back_populates="worker")
    training = relationship("TrainingRecord", back_populates="worker")
    attendance = relationship("AttendanceRecord", back_populates="worker")
    leave_requests = relationship("LeaveRequest", back_populates="worker")

# ============= ATTENDANCE & TIME TRACKING =============
class AttendanceRecord(Base):
    __tablename__ = "attendance_records"
    id = Column(Integer, primary_key=True, index=True)
    worker_id = Column(Integer, ForeignKey("workers.id"))
    date = Column(Date, index=True)
    check_in_time = Column(DateTime, nullable=True)
    check_out_time = Column(DateTime, nullable=True)
    hours_worked = Column(Float, nullable=True)
    overtime_hours = Column(Float, default=0)
    status = Column(String, default="Present")  # Present, Absent, Late, Early Leave
    notes = Column(Text, nullable=True)
    worker = relationship("Worker", back_populates="attendance")

class LeaveRequest(Base):
    __tablename__ = "leave_requests"
    id = Column(Integer, primary_key=True, index=True)
    worker_id = Column(Integer, ForeignKey("workers.id"))
    leave_type = Column(String)  # Sick, Vacation, Personal, Unpaid
    start_date = Column(Date)
    end_date = Column(Date)
    reason = Column(Text, nullable=True)
    status = Column(String, default="Pending")  # Pending, Approved, Rejected
    approved_by = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    worker = relationship("Worker", back_populates="leave_requests")

# ============= PERFORMANCE & TRAINING =============
class PerformanceMetric(Base):
    __tablename__ = "performance_metrics"
    id = Column(Integer, primary_key=True, index=True)
    worker_id = Column(Integer, ForeignKey("workers.id"))
    rating = Column(Float, default=0)  # 0-5
    tasks_completed = Column(Integer, default=0)
    quality_score = Column(Float, default=0)  # 0-100
    punctuality_score = Column(Float, default=0)  # 0-100
    teamwork_score = Column(Float, default=0)  # 0-100
    month = Column(String)  # YYYY-MM format
    notes = Column(Text, nullable=True)
    worker = relationship("Worker", back_populates="performance")

class TrainingRecord(Base):
    __tablename__ = "training_records"
    id = Column(Integer, primary_key=True, index=True)
    worker_id = Column(Integer, ForeignKey("workers.id"))
    training_name = Column(String)  # Food Safety, Equipment Operation, etc.
    trainer = Column(String, nullable=True)
    date = Column(Date)
    duration_hours = Column(Float)
    certification = Column(String, nullable=True)
    expiry_date = Column(Date, nullable=True)
    status = Column(String, default="Completed")  # Completed, Pending, Failed
    worker = relationship("Worker", back_populates="training")

# ============= INVENTORY MANAGEMENT (Enhanced) =============
class InventoryItem(Base):
    __tablename__ = "inventory_items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    category = Column(String)
    sku = Column(String, unique=True, index=True)
    quantity = Column(Integer, default=0)
    min_quantity = Column(Integer, default=10)
    max_quantity = Column(Integer, nullable=True)
    unit = Column(String)
    price_per_unit = Column(Float)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=True)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow)
    location = Column(String, nullable=True)
    expiry_date = Column(Date, nullable=True)
    batch_number = Column(String, nullable=True)
    audit_logs = relationship("AuditLog", back_populates="inventory", cascade="all, delete-orphan")

class InventoryTransaction(Base):
    __tablename__ = "inventory_transactions"
    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("inventory_items.id"))
    transaction_type = Column(String)  # add, remove, usage, waste
    quantity = Column(Integer)
    reference = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    notes = Column(Text, nullable=True)

class WasteTracking(Base):
    __tablename__ = "waste_tracking"
    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("inventory_items.id"))
    quantity = Column(Integer)
    reason = Column(String)  # Expired, Damaged, Spillage, etc.
    cost = Column(Float, nullable=True)
    date = Column(Date, default=datetime.date.today)
    reported_by = Column(String)
    notes = Column(Text, nullable=True)

# ============= SUPPLIER MANAGEMENT =============
class Supplier(Base):
    __tablename__ = "suppliers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    email = Column(String)
    phone = Column(String)
    address = Column(Text)
    city = Column(String)
    rating = Column(Float, default=0)  # 0-5
    reliability_score = Column(Float, default=0)  # 0-100
    quality_score = Column(Float, default=0)  # 0-100
    status = Column(String, default="Active")
    preferred = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)

# ============= PRODUCTION & SCHEDULING =============
class ProductionSchedule(Base):
    __tablename__ = "production_schedules"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, index=True)
    product_name = Column(String)
    quantity = Column(Integer)
    shift = Column(String)  # Morning, Evening, Night
    assigned_workers = Column(String, nullable=True)  # JSON list
    status = Column(String, default="Scheduled")  # Scheduled, In Progress, Completed
    priority = Column(String, default="Medium")
    notes = Column(Text, nullable=True)

class Batch(Base):
    __tablename__ = "batches"
    id = Column(Integer, primary_key=True, index=True)
    batch_number = Column(String, unique=True, index=True)
    product_name = Column(String)
    quantity = Column(Integer)
    production_date = Column(Date)
    expiry_date = Column(Date)
    status = Column(String, default="Active")  # Active, Used, Expired, Recalled
    quality_check = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)

class Recipe(Base):
    __tablename__ = "recipes"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(Text, nullable=True)
    yield_quantity = Column(Integer)
    yield_unit = Column(String)
    ingredients = Column(Text)  # JSON format
    instructions = Column(Text)
    prep_time = Column(Integer)  # minutes
    cooking_time = Column(Integer)  # minutes
    estimated_cost = Column(Float, nullable=True)
    version = Column(Integer, default=1)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)
    modified_date = Column(DateTime, default=datetime.datetime.utcnow)

# ============= TASK MANAGEMENT (Enhanced) =============
class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text, nullable=True)
    status = Column(String, default="Todo")
    priority = Column(String, default="Medium")
    due_date = Column(DateTime, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    owner = relationship("User", back_populates="tasks")
    task_type = Column(String, default="production")  # production, maintenance, cleaning, quality
    estimated_hours = Column(Float, nullable=True)
    actual_hours = Column(Float, nullable=True)
    batch_id = Column(String, nullable=True)
    workflows = relationship("WorkflowTrigger", back_populates="task")
    audit_logs = relationship("AuditLog", back_populates="task", cascade="all, delete-orphan")
    assignments = relationship("WorkerAssignment", back_populates="task")

class WorkerAssignment(Base):
    __tablename__ = "worker_assignments"
    id = Column(Integer, primary_key=True, index=True)
    worker_id = Column(Integer, ForeignKey("workers.id"))
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)
    assigned_date = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String, default="Assigned")
    worker = relationship("Worker", back_populates="assignments")
    task = relationship("Task", back_populates="assignments")

# ============= QUALITY CONTROL =============
class QualityCheck(Base):
    __tablename__ = "quality_checks"
    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(String, index=True)
    product_name = Column(String)
    check_date = Column(DateTime, default=datetime.datetime.utcnow)
    inspector = Column(String)
    temperature = Column(Float, nullable=True)
    appearance = Column(String)  # Pass/Fail
    taste = Column(String)  # Pass/Fail
    texture = Column(String)  # Pass/Fail
    packaging = Column(String)  # Pass/Fail
    overall_status = Column(String, default="Pending")  # Pass, Fail, Pending
    notes = Column(Text, nullable=True)
    recommendations = Column(Text, nullable=True)

class QualityReport(Base):
    __tablename__ = "quality_reports"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, index=True)
    total_checks = Column(Integer)
    passed = Column(Integer)
    failed = Column(Integer)
    pass_rate = Column(Float)  # percentage
    critical_issues = Column(Integer, default=0)
    report = Column(Text)  # Detailed report

# ============= EQUIPMENT & MAINTENANCE =============
class Equipment(Base):
    __tablename__ = "equipment"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    equipment_type = Column(String)  # Oven, Mixer, Fryer, etc.
    model = Column(String)
    serial_number = Column(String, unique=True)
    purchase_date = Column(Date)
    installation_date = Column(Date, nullable=True)
    status = Column(String, default="Active")  # Active, Maintenance, Broken, Retired
    location = Column(String)
    maintenance_records = relationship("MaintenanceSchedule", back_populates="equipment")

class MaintenanceSchedule(Base):
    __tablename__ = "maintenance_schedules"
    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(Integer, ForeignKey("equipment.id"))
    maintenance_type = Column(String)  # Preventive, Corrective, Inspection
    scheduled_date = Column(Date)
    completed_date = Column(Date, nullable=True)
    technician = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    cost = Column(Float, nullable=True)
    status = Column(String, default="Scheduled")  # Scheduled, In Progress, Completed
    equipment = relationship("Equipment", back_populates="maintenance_records")

class EquipmentAlert(Base):
    __tablename__ = "equipment_alerts"
    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(Integer, ForeignKey("equipment.id"))
    alert_type = Column(String)  # Malfunction, Maintenance Due, Health Check
    severity = Column(String)  # Low, Medium, High, Critical
    description = Column(Text)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)
    resolved_date = Column(DateTime, nullable=True)
    status = Column(String, default="Open")

# ============= ORDERS & COMPLAINTS =============
class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String, unique=True, index=True)
    customer_name = Column(String)
    customer_email = Column(String)
    product = Column(String)
    quantity = Column(Integer)
    order_date = Column(Date)
    delivery_date = Column(Date, nullable=True)
    total_cost = Column(Float)
    status = Column(String, default="Pending")  # Pending, Processing, Shipped, Delivered, Cancelled
    notes = Column(Text, nullable=True)

class Complaint(Base):
    __tablename__ = "complaints"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, nullable=True)
    customer_name = Column(String)
    complaint_type = Column(String)  # Quality, Delivery, Packaging, Taste
    description = Column(Text)
    date_reported = Column(Date, default=datetime.date.today)
    severity = Column(String)  # Low, Medium, High, Critical
    status = Column(String, default="Open")  # Open, In Progress, Resolved, Closed
    resolution = Column(Text, nullable=True)
    resolved_date = Column(Date, nullable=True)

class Return(Base):
    __tablename__ = "returns"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, nullable=True)
    reason = Column(String)  # Defective, Expired, Wrong Item
    quantity = Column(Integer)
    refund_amount = Column(Float)
    status = Column(String, default="Pending")  # Pending, Approved, Rejected, Processed
    date_requested = Column(Date, default=datetime.date.today)
    date_processed = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)

# ============= COST & ANALYTICS =============
class CostTracking(Base):
    __tablename__ = "cost_tracking"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, index=True)
    category = Column(String)  # Labor, Materials, Equipment, Utilities
    description = Column(String)
    amount = Column(Float)
    notes = Column(Text, nullable=True)

class DailyReport(Base):
    __tablename__ = "daily_reports"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, unique=True, index=True)
    tasks_completed = Column(Integer, default=0)
    workers_present = Column(Integer, default=0)
    production_units = Column(Integer, default=0)
    waste_amount = Column(Float, default=0)
    quality_issues = Column(Integer, default=0)
    total_cost = Column(Float, default=0)
    summary = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)

# ============= SAFETY & COMPLIANCE =============
class SafetyIncident(Base):
    __tablename__ = "safety_incidents"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=datetime.datetime.utcnow)
    worker_id = Column(Integer, ForeignKey("workers.id"), nullable=True)
    incident_type = Column(String)  # Injury, Near Miss, Property Damage
    description = Column(Text)
    severity = Column(String)  # Minor, Moderate, Severe
    first_aid_given = Column(Boolean, default=False)
    medical_attention_needed = Column(Boolean, default=False)
    investigation_status = Column(String, default="Open")  # Open, In Progress, Closed
    preventive_measures = Column(Text, nullable=True)

class SafetyCheck(Base):
    __tablename__ = "safety_checks"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, index=True)
    area = Column(String)  # Kitchen, Storage, Processing, Packaging
    inspector = Column(String)
    fire_safety = Column(Boolean, default=True)
    electrical_safety = Column(Boolean, default=True)
    hygiene_standards = Column(Boolean, default=True)
    equipment_safety = Column(Boolean, default=True)
    emergency_exits = Column(Boolean, default=True)
    issues_found = Column(Text, nullable=True)
    follow_up_date = Column(Date, nullable=True)

# ============= WORKFLOW & AUDIT =============
class WorkflowTrigger(Base):
    __tablename__ = "workflow_triggers"
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    condition = Column(String)
    action = Column(String)
    is_active = Column(Boolean, default=True)
    task = relationship("Task", back_populates="workflows")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    worker_id = Column(Integer, ForeignKey("workers.id"), nullable=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)
    inventory_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=True)
    action = Column(String)
    entity_type = Column(String)
    entity_id = Column(Integer)
    description = Column(Text)
    user = relationship("User", back_populates="audits")
    worker = relationship("Worker", back_populates="audit_logs")
    task = relationship("Task", back_populates="audit_logs")
    inventory = relationship("InventoryItem", back_populates="audit_logs")
    source = Column(String, default="api")
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)

class SystemAlert(Base):
    __tablename__ = "system_alerts"
    id = Column(Integer, primary_key=True, index=True)
    alert_type = Column(String)  # Low Stock, Maintenance Due, Expired Item, Quality Issue
    severity = Column(String)  # Info, Warning, Critical
    message = Column(String)
    entity_type = Column(String, nullable=True)
    entity_id = Column(Integer, nullable=True)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)
    resolved_date = Column(DateTime, nullable=True)
    status = Column(String, default="Active")  # Active, Resolved, Ignored
    action_required = Column(Text, nullable=True)

class TaskAuditLog(Base):
    __tablename__ = "task_audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), index=True)
    task = relationship("Task")
    action = Column(String)
    field_name = Column(String, nullable=True)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    source = Column(String, default="api")
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    details = Column(Text, nullable=True)
