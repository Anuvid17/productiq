import uuid
from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database.db import get_db
from app.database.models import Feedback, Roadmap, RoadmapTask
from app.schemas.duplicate import DuplicateCheckResult

client = TestClient(app)


@pytest.fixture
def mock_db_session():
    session = MagicMock()
    return session


@pytest.fixture
def sample_feedback_model():
    from datetime import datetime
    now = datetime.utcnow()
    return Feedback(
        id=uuid.UUID("11111111-1111-1111-1111-111111111111"),
        original_text="The login page freezes after clicking Sign In.",
        summary="Login page freezes after clicking Sign In",
        feedback_type="Bug Report",
        category="Authentication",
        subcategory="Login",
        bug_category="Functional Bug",
        severity="Major",
        priority="P1",
        impact_area="All Users",
        platform="Web",
        recommended_action="CREATE_BUG",
        confidence="High",
        status="Triaged",
        created_at=now,
        updated_at=now
    )


# 1. POST valid feedback -> 201 Created
def test_post_valid_feedback(mock_db_session, sample_feedback_model):
    dup_res = DuplicateCheckResult(
        is_duplicate=False,
        similarity_score=0.0,
        matched_feedback_id=None,
        matched_text=None,
        reason="No matching candidate feedback items found."
    )
    roadmap_mock = Roadmap(
        id=uuid.UUID("22222222-2222-2222-2222-222222222222"),
        feedback_id=sample_feedback_model.id,
        title="Resolve Login Freeze",
        status="Backlog",
        effort="M",
        progress=0
    )
    tasks_mock = [
        RoadmapTask(
            id=uuid.UUID("33333333-3333-3333-3333-333333333333"),
            roadmap_id=roadmap_mock.id,
            title="Investigate Login Freeze",
            status="Open",
            progress=0
        )
    ]

    mock_process = MagicMock(return_value={
        "feedback": sample_feedback_model,
        "duplicate_result": dup_res,
        "roadmap": roadmap_mock,
        "tasks": tasks_mock,
        "action": "CREATE_BUG"
    })

    with patch("app.api.routes.feedback.FeedbackService") as mock_service_cls:
        instance = mock_service_cls.return_value
        instance.process_and_store_feedback = mock_process

        app.dependency_overrides[get_db] = lambda: mock_db_session
        try:
            res = client.post(
                "/api/v1/feedback",
                json={"original_text": "The login page freezes after clicking Sign In.", "platform": "Web"}
            )
            assert res.status_code == 201
            data = res.json()
            assert data["id"] == str(sample_feedback_model.id)
            assert data["feedback_type"] == "Bug Report"
            assert data["duplicate"]["is_duplicate"] is False
            assert data["roadmap"]["title"] == "Resolve Login Freeze"
        finally:
            app.dependency_overrides.clear()


# 2. POST empty feedback -> 422
def test_post_empty_feedback():
    res = client.post("/api/v1/feedback", json={"original_text": ""})
    assert res.status_code == 422


# 3. POST whitespace-only feedback -> 422
def test_post_whitespace_feedback():
    res = client.post("/api/v1/feedback", json={"original_text": "    \n   "})
    assert res.status_code == 422


# 4. POST invalid platform -> 422
def test_post_invalid_platform():
    res = client.post(
        "/api/v1/feedback",
        json={"original_text": "The login page freezes", "platform": "InvalidPlatformName"}
    )
    assert res.status_code == 422


# 5. GET feedback list -> 200
def test_get_feedback_list(mock_db_session, sample_feedback_model):
    with patch("app.api.routes.feedback.FeedbackRepository") as mock_repo_cls:
        repo_instance = mock_repo_cls.return_value
        repo_instance.list.return_value = [sample_feedback_model]
        repo_instance.count.return_value = 1

        app.dependency_overrides[get_db] = lambda: mock_db_session
        try:
            res = client.get("/api/v1/feedback")
            assert res.status_code == 200
            data = res.json()
            assert data["total"] == 1
            assert len(data["items"]) == 1
            assert data["items"][0]["id"] == str(sample_feedback_model.id)
        finally:
            app.dependency_overrides.clear()


# 6. GET feedback list pagination -> correct metadata
def test_get_feedback_list_pagination(mock_db_session):
    with patch("app.api.routes.feedback.FeedbackRepository") as mock_repo_cls:
        repo_instance = mock_repo_cls.return_value
        repo_instance.list.return_value = []
        repo_instance.count.return_value = 45

        app.dependency_overrides[get_db] = lambda: mock_db_session
        try:
            res = client.get("/api/v1/feedback?page=2&page_size=10")
            assert res.status_code == 200
            data = res.json()
            assert data["page"] == 2
            assert data["page_size"] == 10
            assert data["total"] == 45
            assert data["items"] == []
        finally:
            app.dependency_overrides.clear()


# 7. GET feedback by valid ID -> 200
def test_get_feedback_by_valid_id(mock_db_session, sample_feedback_model):
    target_id = sample_feedback_model.id
    roadmap_mock = Roadmap(
        id=uuid.UUID("22222222-2222-2222-2222-222222222222"),
        feedback_id=target_id,
        title="Resolve Login Freeze",
        status="Backlog",
        effort="M",
        progress=0
    )
    with patch("app.api.routes.feedback.FeedbackRepository") as mock_fb_repo, \
         patch("app.api.routes.feedback.RoadmapRepository") as mock_rm_repo, \
         patch("app.api.routes.feedback.RoadmapTaskRepository") as mock_task_repo:

        mock_fb_repo.return_value.get_by_id.return_value = sample_feedback_model
        mock_rm_repo.return_value.get_by_feedback_id.return_value = roadmap_mock
        mock_task_repo.return_value.list_by_roadmap.return_value = []

        app.dependency_overrides[get_db] = lambda: mock_db_session
        try:
            res = client.get(f"/api/v1/feedback/{target_id}")
            assert res.status_code == 200
            data = res.json()
            assert data["id"] == str(target_id)
        finally:
            app.dependency_overrides.clear()


# 8. GET nonexistent feedback -> 404
def test_get_nonexistent_feedback(mock_db_session):
    random_id = uuid.uuid4()
    with patch("app.api.routes.feedback.FeedbackRepository") as mock_fb_repo:
        mock_fb_repo.return_value.get_by_id.return_value = None

        app.dependency_overrides[get_db] = lambda: mock_db_session
        try:
            res = client.get(f"/api/v1/feedback/{random_id}")
            assert res.status_code == 404
            data = res.json()
            assert data["detail"]["error"]["code"] == "FEEDBACK_NOT_FOUND"
        finally:
            app.dependency_overrides.clear()


# 9. PATCH valid status -> 200
def test_patch_valid_status(mock_db_session, sample_feedback_model):
    target_id = sample_feedback_model.id
    updated_model = sample_feedback_model
    updated_model.status = "Resolved"

    with patch("app.api.routes.feedback.FeedbackRepository") as mock_fb_repo:
        instance = mock_fb_repo.return_value
        instance.get_by_id.return_value = sample_feedback_model
        instance.update.return_value = updated_model

        app.dependency_overrides[get_db] = lambda: mock_db_session
        try:
            res = client.patch(f"/api/v1/feedback/{target_id}/status", json={"status": "Resolved"})
            assert res.status_code == 200
            data = res.json()
            assert data["status"] == "Resolved"
        finally:
            app.dependency_overrides.clear()


# 10. PATCH invalid status -> 422
def test_patch_invalid_status():
    target_id = uuid.uuid4()
    res = client.patch(f"/api/v1/feedback/{target_id}/status", json={"status": "NonexistentStatusValue"})
    assert res.status_code == 422


# 11. Malformed UUID -> 422
def test_malformed_uuid():
    res = client.get("/api/v1/feedback/not-a-valid-uuid")
    assert res.status_code == 422


# 12. Ollama / Service failure -> 503
def test_ollama_service_failure(mock_db_session):
    with patch("app.api.routes.feedback.FeedbackService") as mock_service_cls:
        instance = mock_service_cls.return_value
        instance.process_and_store_feedback.side_effect = RuntimeError("Failed to generate response from Ollama")

        app.dependency_overrides[get_db] = lambda: mock_db_session
        try:
            res = client.post(
                "/api/v1/feedback",
                json={"original_text": "Valid feedback text that triggers LLM failure."}
            )
            assert res.status_code == 503
            data = res.json()
            assert data["detail"]["error"]["code"] == "AI_SERVICE_UNAVAILABLE"
        finally:
            app.dependency_overrides.clear()


# 13. Database failure -> 500 safe error
def test_database_failure(mock_db_session):
    with patch("app.api.routes.feedback.FeedbackService") as mock_service_cls:
        instance = mock_service_cls.return_value
        instance.process_and_store_feedback.side_effect = Exception("Database connection lost")

        app.dependency_overrides[get_db] = lambda: mock_db_session
        try:
            res = client.post(
                "/api/v1/feedback",
                json={"original_text": "Valid feedback text that triggers DB failure."}
            )
            assert res.status_code == 500
            data = res.json()
            assert data["detail"]["error"]["code"] == "INTERNAL_SERVER_ERROR"
        finally:
            app.dependency_overrides.clear()
