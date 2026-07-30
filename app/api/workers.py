from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.worker import (
    WorkerHeartbeatRequest,
    WorkerRegisterRequest,
    WorkerRegisterResponse,
)
from app.services.worker_service import WorkerService

router = APIRouter(prefix="/workers", tags=["workers"])


@router.post("/register", response_model=WorkerRegisterResponse)
def register_worker(payload: WorkerRegisterRequest, db: Session = Depends(get_db)):
    service = WorkerService(db)
    return service.register(payload)


@router.post("/heartbeat", response_model=WorkerRegisterResponse)
def worker_heartbeat(payload: WorkerHeartbeatRequest, db: Session = Depends(get_db)):
    service = WorkerService(db)
    result = service.heartbeat(payload.hostname)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Worker not found. Register first.",
        )
    return result
