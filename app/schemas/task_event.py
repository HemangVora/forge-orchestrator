from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class TaskEventResponse(BaseModel):
    id: UUID
    status: str
    stage: str | None
    progress: int
    message: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
