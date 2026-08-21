import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database.repository import FeedbackRepository, RoadmapRepository, RoadmapTaskRepository, NotificationRepository

client = TestClient(app)


def test_get_task_by_id(db_session):
    fb_repo = FeedbackRepository(db_session)
    rm_repo = RoadmapRepository(db_session)
    task_repo = RoadmapTaskRepository(db_session)

    fb = fb_repo.create(original_text="Button unclickable", platform="Web")
    rm = rm_repo.create(feedback_id=fb.id, title="Fix Button", status="Backlog", progress=0)
    t = task_repo.create(roadmap_id=rm.id, title="Fix CSS overflow", status="Open", progress=0)
    db_session.commit()

    response = client.get(f"/api/v1/tasks/{t.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(t.id)
    assert data["title"] == "Fix CSS overflow"


def test_update_task_progress_and_workflow(db_session):
    fb_repo = FeedbackRepository(db_session)
    rm_repo = RoadmapRepository(db_session)
    task_repo = RoadmapTaskRepository(db_session)
    notif_repo = NotificationRepository(db_session)

    fb = fb_repo.create(original_text="Login freezes on submit", platform="Web")
    rm = rm_repo.create(feedback_id=fb.id, title="Fix Login Freeze", status="Backlog", progress=0)
    t = task_repo.create(roadmap_id=rm.id, title="Fix JS error", status="Open", progress=0)
    db_session.commit()

    # Update task progress to 100% and status to Resolved
    response = client.patch(f"/api/v1/tasks/{t.id}", json={
        "progress": 100,
        "status": "Resolved"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["progress"] == 100
    assert data["status"] == "Resolved"

    # Verify roadmap and feedback resolution state recalculation
    db_session.refresh(rm)
    db_session.refresh(fb)
    assert rm.progress == 100
    assert rm.status == "Released"
    assert fb.status == "Resolved"

    # Verify notification created
    notifs = notif_repo.list(feedback_id=fb.id)
    assert len(notifs) == 1
    assert notifs[0].notification_type == "RESOLUTION"


def test_update_task_invalid_progress(db_session):
    fb_repo = FeedbackRepository(db_session)
    rm_repo = RoadmapRepository(db_session)
    task_repo = RoadmapTaskRepository(db_session)

    fb = fb_repo.create(original_text="Invalid update test", platform="Web")
    rm = rm_repo.create(feedback_id=fb.id, title="Test Roadmap", status="Backlog", progress=0)
    t = task_repo.create(roadmap_id=rm.id, title="Task 1", status="Open", progress=0)
    db_session.commit()

    # Try setting progress < 100 on Resolved
    response = client.patch(f"/api/v1/tasks/{t.id}", json={
        "progress": 50,
        "status": "Resolved"
    })
    assert response.status_code == 422
    assert response.json()["detail"]["error"]["code"] == "TASK_VALIDATION_ERROR"
