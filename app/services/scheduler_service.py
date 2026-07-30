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

        self._dispatch(task)
        return {
            "task_id": str(task.id),
            "scheduled": True,
            "worker": worker.hostname,
        }

    def _dispatch(self, task: Task) -> None:
        """Hand off to forge-worker-runtime by task NAME, never by import.

        The orchestrator must not import runtime code — that is the seam that
        lets the runtime live in a separate repo and deploy independently.
        Note the payload carries a capability, never a provider name: which
        provider actually runs is entirely the runtime's business.
        """
        from app.queue.celery_app import celery_app

        celery_app.send_task(
            "runtime.execute_task",
            args=[
                {
                    "schema_version": 1,
                    "task_id": str(task.id),
                    "repository": task.repository,
                    "prompt": task.prompt,
                    "required_capability": task.required_capability,
                    # Omitted deliberately: the runtime reads the repository's
                    # real default branch from its mirror. Hardcoding "main"
                    # here broke every master-based repo.
                    "base_branch": None,
                    "policies": {},
                }
            ],
            queue="forge.runtime",
        )

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
