from datetime import datetime

from pydantic import BaseModel, Field


class ArtifactRefIn(BaseModel):
    artifact_id: str
    name: str
    download_url: str
    size: int
    content_type: str = "application/octet-stream"


class ProgressEventIn(BaseModel):
    """Mirrors forge-worker-runtime's ProgressEvent.

    Deliberately permissive: the runtime may add fields ahead of the
    orchestrator, and an unknown field must not reject a valid event.
    """

    schema_version: int = 1
    task_id: str
    status: str
    stage: str | None = None
    progress: int = 0
    message: str | None = None
    provider: str | None = None
    timestamp: datetime


class TaskOutcomeIn(BaseModel):
    """Mirrors forge-worker-runtime's TaskOutcome."""

    schema_version: int = 1
    task_id: str
    ok: bool
    status: str
    provider: str | None = None
    branch: str | None = None
    commit_sha: str | None = None
    files_changed: list[str] = Field(default_factory=list)
    summary: str = ""
    error: str | None = None
    artifacts: list[ArtifactRefIn] = Field(default_factory=list)
    started_at: datetime
    finished_at: datetime
