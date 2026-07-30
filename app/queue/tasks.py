from app.queue.celery_app import celery_app


@celery_app.task(name="app.queue.tasks.enqueue_task")
def enqueue_task(task_id: str) -> dict:
    return {"task_id": task_id, "queued": True}
