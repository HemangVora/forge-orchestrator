from uuid import UUID

from sqlalchemy.orm import Session

from app.domain.capabilities import Capability
from app.models.task import Task
from app.models.task_event import TaskEvent
from app.queue.tasks import enqueue_task
from app.schemas.task import TaskCreateRequest, TaskCreateResponse, TaskStatusResponse
from app.schemas.task_event import TaskEventResponse
from app.services.event_service import EventService


class TaskService:
    def __init__(self, db: Session):
        self.db = db
        self.events = EventService(db)

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

        self.events.transition(task, status="queued", stage="queued", progress=0)

        self.db.commit()
        self.db.refresh(task)

        enqueue_task.delay(str(task.id))

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

    def get_task_events(self, task_id: UUID) -> list[TaskEventResponse] | None:
        task = self.db.get(Task, task_id)
        if task is None:
            return None

        events = (
            self.db.query(TaskEvent)
            .filter(TaskEvent.task_id == task_id)
            .order_by(TaskEvent.created_at)
            .all()
        )
        return [TaskEventResponse.model_validate(e) for e in events]
