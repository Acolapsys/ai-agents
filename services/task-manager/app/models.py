from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, Index
from sqlalchemy.sql import func
import enum
from .database import Base

class TaskStatus(str, enum.Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    ARCHIVED = "archived"

class TaskPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(TaskStatus), default=TaskStatus.NEW)
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM)
    assignee = Column(String(50), nullable=True)
    project = Column(String(100), nullable=True, index=True)  # новое поле
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # составной индекс для частых запросов (например, project + status)
    __table_args__ = (
        Index('ix_tasks_project_status', 'project', 'status'),
    )