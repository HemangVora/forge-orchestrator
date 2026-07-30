from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import require_token
from app.db.session import get_db
from app.models.task import Task
from app.schemas.internal import ProgressEventIn, TaskOutcomeIn
from app.services.event_service import EventService

router = APIRouter(prefix="/internal", tags=["internal"])

TERMINAL_STATUSES = {"done", "failed", "cancelled"}


@router.post("/tasks/{task_id}/events", status_code=status.HTTP_202_ACCEPTED)
def record_event(
    task_id: UUID,
    payload: ProgressEventIn,
    db: Session = Depends(get_db),
    _: None = Depends(require_token),
) -> dict:
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.status in TERMINAL_STATUSES:
        # Late events after a terminal result are accepted-and-dropped, not an
        # error: the runtime retries and must not be made to fail.
        return {"accepted": False, "reason": "task already terminal"}

    EventService(db).transition(
        task,
        status=payload.status,
        stage=payload.stage,
        progress=payload.progress,
        message=payload.message,
    )
    db.commit()
    return {"accepted": True}


@router.post("/tasks/{task_id}/result")
def record_result(
    task_id: UUID,
    payload: TaskOutcomeIn,
    db: Session = Depends(get_db),
    _: None = Depends(require_token),
) -> dict:
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.status in TERMINAL_STATUSES:
        raise HTTPException(status_code=409, detail="Task already terminal")

    task.branch = payload.branch
    task.result = payload.model_dump(mode="json")
    EventService(db).transition(
        task,
        status=payload.status,
        stage="done",
        progress=100,
        message=payload.summary or payload.error,
    )
    db.commit()
    return {"accepted": True, "status": payload.status}
