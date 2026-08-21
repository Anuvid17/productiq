import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database.repository import FeedbackRepository, RoadmapRepository

client = TestClient(app)


def test_dashboard_summary_api(db_session):
    fb_repo = FeedbackRepository(db_session)
    rm_repo = RoadmapRepository(db_session)

    fb1 = fb_repo.create(
        original_text="Login freezes on submit",
        feedback_type="Bug Report",
        category="Authentication",
        severity="Critical",
        priority="P0",
        status="Triaged"
    )
    fb2 = fb_repo.create(
        original_text="Add CSV export",
        feedback_type="Feature Request",
        category="Reporting",
        severity="Minor",
        priority="P2",
        status="Resolved"
    )

    rm = rm_repo.create(feedback_id=fb1.id, title="Fix Login Freeze", status="Backlog", progress=50)
    db_session.commit()

    response = client.get("/api/v1/dashboard/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["total_feedback"] == 2
    assert data["open_feedback"] == 1
    assert data["resolved_feedback"] == 1
    assert data["critical_blocker_issues"] == 1
    assert data["bug_reports"] == 1
    assert data["feature_requests"] == 1
    assert data["active_roadmaps"] == 1
    assert data["average_roadmap_progress"] == 50.0
    assert data["resolution_rate"] == 50.0
    assert "Bug Report" in data["feedback_by_type"]
    assert "Authentication" in data["feedback_by_category"]


def test_dashboard_summary_empty(db_session):
    response = client.get("/api/v1/dashboard/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["total_feedback"] == 0
    assert data["open_feedback"] == 0
    assert data["resolved_feedback"] == 0
    assert data["critical_blocker_issues"] == 0
    assert data["active_roadmaps"] == 0
    assert data["average_roadmap_progress"] == 0.0
    assert data["resolution_rate"] == 0.0

