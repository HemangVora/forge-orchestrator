from uuid import UUID

from app.db.session import SessionLocal
from app.queue.celery_app import celery_app
from app.services.scheduler_service import SchedulerService


@celery_app.task(name="app.queue.tasks.enqueue_task")
def enqueue_task(task_id: str) -> dict:
    db = SessionLocal()
    try:
        service = SchedulerService(db)
        result = service.schedule(UUID(task_id))
        return result or {"task_id": task_id, "scheduled": False}
    finally:
        db.close()
