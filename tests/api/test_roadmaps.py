import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database.repository import FeedbackRepository, RoadmapRepository, RoadmapTaskRepository

client = TestClient(app)


def test_list_roadmaps_empty(db_session):
    response = client.get("/api/v1/roadmaps")
    assert response.status_code == 200
    assert response.json() == []


def test_get_roadmap_by_id(db_session):
    fb_repo = FeedbackRepository(db_session)
    rm_repo = RoadmapRepository(db_session)
    task_repo = RoadmapTaskRepository(db_session)

    fb = fb_repo.create(original_text="Login freezes on submit", platform="Web")
    rm = rm_repo.create(feedback_id=fb.id, title="Fix Login Freeze", status="Backlog", progress=0)
    t1 = task_repo.create(roadmap_id=rm.id, title="Investigate JS error", status="Open", progress=0)
    db_session.commit()

    response = client.get(f"/api/v1/roadmaps/{rm.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(rm.id)
    assert data["title"] == "Fix Login Freeze"
    assert len(data["tasks"]) == 1
    assert data["tasks"][0]["title"] == "Investigate JS error"


def test_get_nonexistent_roadmap(db_session):
    fake_id = str(uuid.uuid4())
    response = client.get(f"/api/v1/roadmaps/{fake_id}")
    assert response.status_code == 404
    assert response.json()["detail"]["error"]["code"] == "ROADMAP_NOT_FOUND"


def test_update_roadmap(db_session):
    fb_repo = FeedbackRepository(db_session)
    rm_repo = RoadmapRepository(db_session)

    fb = fb_repo.create(original_text="Search filter issue", platform="Web")
    rm = rm_repo.create(feedback_id=fb.id, title="Fix Search Filter", status="Backlog", progress=0)
    db_session.commit()

    response = client.patch(f"/api/v1/roadmaps/{rm.id}", json={
        "status": "In Progress",
        "progress": 30
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "In Progress"
    assert data["progress"] == 30
