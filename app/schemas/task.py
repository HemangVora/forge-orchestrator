from uuid import UUID

from pydantic import BaseModel, Field


class TaskCreateRequest(BaseModel):
    repository: str = Field(..., examples=["HemangVora/forge"])
    prompt: str = Field(..., examples=["Build authentication"])


class TaskCreateResponse(BaseModel):
    task_id: UUID
    status: str


class TaskStatusResponse(BaseModel):
    status: str
    progress: int
    stage: str | None = None
