from fastapi.testclient import TestClient

from main import app

client = TestClient(app)
AUTH = {"X-Forge-Token": "dev-secret-change-me"}


def _event(task_id) -> dict:
    return {
        "task_id": str(task_id),
        "status": "running",
        "stage": "executing",
        "progress": 30,
        "message": "go",
        "timestamp": "2026-07-31T10:00:00Z",
    }


def _outcome(task_id, **overrides) -> dict:
    body = {
        "task_id": str(task_id),
        "ok": True,
        "status": "done",
        "summary": "done",
        "artifacts": [],
        "started_at": "2026-07-31T10:00:00Z",
        "finished_at": "2026-07-31T10:05:00Z",
    }
    body.update(overrides)
    return body


def test_events_endpoint_rejects_missing_token(seeded_task):
    response = client.post(
        f"/internal/tasks/{seeded_task.id}/events", json=_event(seeded_task.id)
    )
    assert response.status_code == 401


def test_events_endpoint_records_a_task_event(seeded_task, db):
    response = client.post(
        f"/internal/tasks/{seeded_task.id}/events",
        headers=AUTH,
        json=_event(seeded_task.id),
    )
    assert response.status_code == 202
    db.refresh(seeded_task)
    assert seeded_task.stage == "executing"
    assert seeded_task.progress == 30


def test_result_endpoint_marks_task_done_with_branch(seeded_task, db):
    response = client.post(
        f"/internal/tasks/{seeded_task.id}/result",
        headers=AUTH,
        json=_outcome(seeded_task.id, branch="forge/task-1", commit_sha="f" * 40),
    )
    assert response.status_code == 200
    db.refresh(seeded_task)
    assert seeded_task.status == "done"
    assert seeded_task.branch == "forge/task-1"
    assert seeded_task.result["commit_sha"] == "f" * 40


def test_result_endpoint_is_idempotent(seeded_task):
    body = _outcome(seeded_task.id)
    first = client.post(f"/internal/tasks/{seeded_task.id}/result", headers=AUTH, json=body)
    second = client.post(f"/internal/tasks/{seeded_task.id}/result", headers=AUTH, json=body)
    assert first.status_code == 200
    assert second.status_code == 409, "a terminal task must reject further writes"


def test_late_event_after_terminal_is_dropped_not_errored(seeded_task):
    client.post(
        f"/internal/tasks/{seeded_task.id}/result", headers=AUTH, json=_outcome(seeded_task.id)
    )
    late = client.post(
        f"/internal/tasks/{seeded_task.id}/events", headers=AUTH, json=_event(seeded_task.id)
    )
    assert late.status_code == 202
    assert late.json()["accepted"] is False


def test_unknown_task_is_404():
    missing = "00000000-0000-0000-0000-000000000000"
    response = client.post(f"/internal/tasks/{missing}/events", headers=AUTH, json=_event(missing))
    assert response.status_code == 404


def test_task_submission_requires_a_token():
    """POST /task clones private repos with the runtime's GitHub token and
    spends Anthropic credits. Unauthenticated, anyone who knows the URL can
    do both."""
    response = client.post(
        "/task", json={"repository": "HemangVora/forge-worker-runtime", "prompt": "probe"}
    )
    assert response.status_code == 401


def test_task_submission_succeeds_with_a_token(db):
    from app.models.task import Task
    from app.models.task_event import TaskEvent

    response = client.post(
        "/task",
        headers=AUTH,
        json={"repository": "HemangVora/forge-worker-runtime", "prompt": "authorized"},
    )
    assert response.status_code == 201
    task_id = response.json()["task_id"]

    db.query(TaskEvent).filter(TaskEvent.task_id == task_id).delete()
    db.query(Task).filter(Task.id == task_id).delete()
    db.commit()


def test_status_and_events_reads_require_a_token(seeded_task):
    """Task events carry prompts and provider output from private repos."""
    assert client.get(f"/tasks/{seeded_task.id}").status_code == 401
    assert client.get(f"/tasks/{seeded_task.id}/events").status_code == 401


def test_health_stays_open_for_platform_probes():
    assert client.get("/health").status_code == 200
