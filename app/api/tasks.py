from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.task import TaskCreateRequest, TaskCreateResponse
from app.services.task_service import TaskService

router = APIRouter(tags=["tasks"])


@router.post("/task", response_model=TaskCreateResponse, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreateRequest, db: Session = Depends(get_db)):
    service = TaskService(db)
    return service.create_task(payload)
