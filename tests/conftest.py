import uuid

import pytest

from app.db.session import SessionLocal
from app.models.task import Task
from app.models.task_event import TaskEvent


@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def seeded_task(db):
    """A queued task, removed afterwards so tests do not accumulate rows."""
    task = Task(
        id=uuid.uuid4(),
        repository="HemangVora/forge",
        prompt="Build login",
        status="queued",
        stage="queued",
        progress=0,
        required_capability="coding",
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    yield task

    db.query(TaskEvent).filter(TaskEvent.task_id == task.id).delete()
    db.query(Task).filter(Task.id == task.id).delete()
    db.commit()
