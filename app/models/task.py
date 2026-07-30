import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    repository = Column(String, nullable=False)
    prompt = Column(String, nullable=False)
    status = Column(String, nullable=False, default="queued")
    stage = Column(String, nullable=True)
    progress = Column(Integer, nullable=False, default=0)
    required_capability = Column(String, nullable=False, default="coding")
    branch = Column(String, nullable=True)
    result = Column(JSONB, nullable=True)
    worker_id = Column(UUID(as_uuid=True), ForeignKey("workers.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    worker = relationship("Worker", back_populates="tasks")
    events = relationship(
        "TaskEvent", back_populates="task", order_by="TaskEvent.created_at"
    )
