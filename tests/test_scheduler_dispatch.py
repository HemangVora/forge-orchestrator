"""The seam: the orchestrator must dispatch by task NAME, never by import."""

import uuid

import pytest

from app.models.task import Task
from app.models.worker import Worker
from app.services.scheduler_service import SchedulerService


@pytest.fixture
def online_worker(db):
    worker = Worker(
        id=uuid.uuid4(),
        hostname=f"worker-test-{uuid.uuid4().hex[:8]}",
        capabilities=["coding"],
        status="online",
    )
    db.add(worker)
    db.commit()
    yield worker

    # Scheduling assigns tasks to this worker; clear those references before
    # deleting it, or tasks_worker_id_fkey rejects the delete.
    db.rollback()
    db.query(Task).filter(Task.worker_id == worker.id).update({"worker_id": None})
    db.query(Worker).filter(Worker.id == worker.id).delete()
    db.commit()


def test_scheduler_dispatches_by_name_not_import(monkeypatch, seeded_task, online_worker, db):
    sent = {}

    from app.queue.celery_app import celery_app

    monkeypatch.setattr(
        celery_app,
        "send_task",
        lambda name, args=None, queue=None, **kw: sent.update(
            {"name": name, "args": args, "queue": queue}
        ),
    )

    SchedulerService(db).schedule(seeded_task.id)

    assert sent["name"] == "runtime.execute_task"
    assert sent["queue"] == "forge.runtime"
    payload = sent["args"][0]
    assert payload["repository"] == seeded_task.repository
    assert payload["schema_version"] == 1


def test_payload_carries_capability_never_a_provider(
    monkeypatch, seeded_task, online_worker, db
):
    sent = {}
    from app.queue.celery_app import celery_app

    monkeypatch.setattr(
        celery_app,
        "send_task",
        lambda name, args=None, queue=None, **kw: sent.update({"args": args}),
    )

    SchedulerService(db).schedule(seeded_task.id)

    payload = sent["args"][0]
    assert payload["required_capability"] == "coding"
    assert "provider" not in payload, "orchestrator must stay provider-blind"


def test_orchestrator_tree_does_not_import_runtime_code():
    """Regression guard for the whole point of the split."""
    import pathlib

    offenders = []
    for path in pathlib.Path("app").rglob("*.py"):
        text = path.read_text()
        if "workers.mock_worker" in text or "from app.runtime" in text:
            offenders.append(str(path))
    assert offenders == [], f"orchestrator imports runtime code: {offenders}"
