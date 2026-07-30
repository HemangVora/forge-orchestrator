from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.domain.capabilities import Capability
from app.models.task import Task
from app.models.task_event import TaskEvent
from app.schemas.task import TaskCreateRequest, TaskCreateResponse, TaskStatusResponse


class TaskService:
    def __init__(self, db: Session):
        self.db = db

    def create_task(self, payload: TaskCreateRequest) -> TaskCreateResponse:
        task = Task(
            repository=payload.repository,
            prompt=payload.prompt,
            status="queued",
            stage="queued",
            progress=0,
            required_capability=Capability.CODING.value,
        )
        self.db.add(task)
        self.db.flush()

        self._record_event(task, status="queued", stage="queued", progress=0)

        self.db.commit()
        self.db.refresh(task)

        return TaskCreateResponse(task_id=task.id, status=task.status)

    def get_task_status(self, task_id: UUID) -> TaskStatusResponse | None:
        task = self.db.get(Task, task_id)
        if task is None:
            return None

        return TaskStatusResponse(
            status=task.status,
            progress=task.progress,
            stage=task.stage,
        )

    def _record_event(
        self,
        task: Task,
        *,
        status: str,
        stage: str | None,
        progress: int,
        message: str | None = None,
    ) -> TaskEvent:
        event = TaskEvent(
            task_id=task.id,
            status=status,
            stage=stage,
            progress=progress,
            message=message,
        )
        self.db.add(event)
        task.status = status
        task.stage = stage
        task.progress = progress
        task.updated_at = datetime.utcnow()
        return event
