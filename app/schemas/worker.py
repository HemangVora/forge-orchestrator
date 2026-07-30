from pydantic import BaseModel, Field


class WorkerRegisterRequest(BaseModel):
    """Worker registration.

    Everything past `capabilities` is additive and defaulted, so a worker
    predating the runtime handoff keeps registering unchanged.
    """

    hostname: str = Field(..., examples=["worker-01"])
    capabilities: list[str] = Field(
        ..., examples=[["coding", "review", "testing"]]
    )
    providers: list[str] = Field(default_factory=list, examples=[["mock"]])
    runtime_version: str | None = None
    environment: dict = Field(default_factory=dict)
    manifest: dict = Field(default_factory=dict)


class WorkerRegisterResponse(BaseModel):
    worker_id: str
    hostname: str
    status: str


class WorkerHeartbeatRequest(BaseModel):
    hostname: str
