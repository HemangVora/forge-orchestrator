import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class Worker(Base):
    __tablename__ = "workers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    hostname = Column(String, unique=True, nullable=False)
    capabilities = Column(JSONB, nullable=False, default=list)
    status = Column(String, nullable=False, default="online")
    last_heartbeat = Column(DateTime, default=datetime.utcnow, nullable=False)
    worker_metadata = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    tasks = relationship("Task", back_populates="worker")
