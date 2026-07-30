import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.db.base import Base


class Repository(Base):
    __tablename__ = "repositories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    github = Column(String, unique=True, nullable=False)
    framework = Column(String, nullable=True)
    language = Column(String, nullable=True)
    package_manager = Column(String, nullable=True)
    preview = Column(String, nullable=True)
    test_strategy = Column(String, nullable=True)
    provider_preferences = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
