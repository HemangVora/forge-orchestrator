from datetime import datetime

from sqlalchemy.orm import Session

from app.models.task import Task
from app.models.task_event import TaskEvent


class EventService:
    def __init__(self, db: Session):
        self.db = db

    def transition(
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
