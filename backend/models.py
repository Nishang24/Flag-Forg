from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship
from database import Base
import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="user") # "admin", "manager", "user"
    tasks = relationship("Task", back_populates="owner")

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text, nullable=True)
    status = Column(String, default="Todo") # Todo, In Progress, Done
    priority = Column(String, default="Medium") # Low, Medium, High
    due_date = Column(DateTime, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="tasks")
    workflows = relationship("WorkflowTrigger", back_populates="task")
    audit_logs = relationship("TaskAuditLog", back_populates="task", cascade="all, delete-orphan")

class WorkflowTrigger(Base):
    __tablename__ = "workflow_triggers"
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    condition = Column(String) # e.g., "Status Changed to Done"
    action = Column(String) # e.g., "Send Slack Notification"
    task = relationship("Task", back_populates="workflows")

class TaskAuditLog(Base):
    __tablename__ = "task_audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), index=True)
    task = relationship("Task", back_populates="audit_logs")
    
    # Audit details
    action = Column(String)  # "created", "updated", "deleted", "voice_command"
    field_name = Column(String, nullable=True)  # Which field changed (title, status, priority, etc)
    old_value = Column(Text, nullable=True)  # Previous value
    new_value = Column(Text, nullable=True)  # New value
    
    # Metadata
    source = Column(String, default="api")  # "voice", "api", "workflow", "ui"
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    details = Column(Text, nullable=True)  # Additional context
