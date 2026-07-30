from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "forge_orchestrator",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.queue.tasks", "workers.mock_worker"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
)
