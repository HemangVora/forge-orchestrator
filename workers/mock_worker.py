import time
from uuid import UUID

from app.db.session import SessionLocal
from app.models.task import Task
from app.queue.celery_app import celery_app
from app.services.event_service import EventService


@celery_app.task(name="workers.mock_worker.execute_mock_task")
def execute_mock_task(task_id: str, worker_hostname: str) -> dict:
    """Mock worker: receives a task, sleeps 5 seconds, marks done."""
    db = SessionLocal()
    try:
        events = EventService(db)
        task = db.get(Task, UUID(task_id))
        if task is None:
            return {"task_id": task_id, "error": "not_found"}

        time.sleep(5)

        for status, stage, progress in [
            ("coding", "coding", 50),
            ("testing", "testing", 80),
            ("done", "done", 100),
        ]:
            events.transition(
                task,
                status=status,
                stage=stage,
                progress=progress,
                message=f"Mock worker {worker_hostname} completed {stage}",
            )
            db.commit()

        return {"task_id": task_id, "status": "done", "worker": worker_hostname}
    finally:
        db.close()
