from uuid import UUID

from sqlalchemy.orm import Session

from app.models.task import Task
from app.models.worker import Worker
from app.services.event_service import EventService


class SchedulerService:
    """Queue -> find worker -> assign -> update DB."""

    def __init__(self, db: Session):
        self.db = db
        self.events = EventService(db)

    def schedule(self, task_id: UUID) -> dict | None:
        task = self.db.get(Task, task_id)
        if task is None or task.status != "queued":
            return None

        worker = self._find_worker(task.required_capability)
        if worker is None:
            return {"task_id": str(task_id), "scheduled": False, "reason": "no_worker"}

        task.worker_id = worker.id
        self.events.transition(task, status="assigned", stage="planning", progress=10)
        self.db.commit()

        from workers.mock_worker import execute_mock_task

        execute_mock_task.delay(str(task.id), worker.hostname)
        return {
            "task_id": str(task.id),
            "scheduled": True,
            "worker": worker.hostname,
        }

    def _find_worker(self, capability: str) -> Worker | None:
        workers = (
            self.db.query(Worker)
            .filter(Worker.status == "online")
            .order_by(Worker.last_heartbeat.desc())
            .all()
        )
        for worker in workers:
            if capability in (worker.capabilities or []):
                return worker
        return None
