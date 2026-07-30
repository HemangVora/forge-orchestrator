from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.task import TaskCreateRequest, TaskCreateResponse, TaskStatusResponse
from app.schemas.task_event import TaskEventResponse
from app.services.task_service import TaskService

router = APIRouter(tags=["tasks"])


@router.post("/task", response_model=TaskCreateResponse, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreateRequest, db: Session = Depends(get_db)):
    service = TaskService(db)
    return service.create_task(payload)


@router.get("/tasks/{task_id}/events", response_model=list[TaskEventResponse])
def get_task_events(task_id: UUID, db: Session = Depends(get_db)):
    service = TaskService(db)
    result = service.get_task_events(task_id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return result


@router.get("/tasks/{task_id}", response_model=TaskStatusResponse)
def get_task(task_id: UUID, db: Session = Depends(get_db)):
    service = TaskService(db)
    result = service.get_task_status(task_id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return result
