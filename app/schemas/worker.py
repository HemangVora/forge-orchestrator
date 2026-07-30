from pydantic import BaseModel, Field


class WorkerRegisterRequest(BaseModel):
    hostname: str = Field(..., examples=["worker-01"])
    capabilities: list[str] = Field(
        ..., examples=[["coding", "review", "testing"]]
    )


class WorkerRegisterResponse(BaseModel):
    worker_id: str
    hostname: str
    status: str


class WorkerHeartbeatRequest(BaseModel):
    hostname: str
