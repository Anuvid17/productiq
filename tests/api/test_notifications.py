import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database.repository import FeedbackRepository, NotificationRepository

client = TestClient(app)


def test_list_notifications_empty(db_session):
    response = client.get("/api/v1/notifications")
    assert response.status_code == 200
    assert response.json() == []


def test_list_and_mark_notification_read(db_session):
    fb_repo = FeedbackRepository(db_session)
    notif_repo = NotificationRepository(db_session)

    fb = fb_repo.create(original_text="Test notification feedback", platform="Web")
    notif = notif_repo.create(
        feedback_id=fb.id,
        message="Your reported issue has been resolved.",
        notification_type="RESOLUTION"
    )
    db_session.commit()

    # List notifications
    response = client.get("/api/v1/notifications?read=false")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == str(notif.id)
    assert data[0]["read"] is False

    # Mark as read
    response_read = client.patch(f"/api/v1/notifications/{notif.id}/read")
    assert response_read.status_code == 200
    assert response_read.json()["read"] is True


def test_mark_all_notifications_read(db_session):
    fb_repo = FeedbackRepository(db_session)
    notif_repo = NotificationRepository(db_session)

    fb = fb_repo.create(original_text="Batch read test", platform="Web")
    n1 = notif_repo.create(feedback_id=fb.id, message="Notif 1", notification_type="INFO")
    n2 = notif_repo.create(feedback_id=fb.id, message="Notif 2", notification_type="INFO")
    db_session.commit()

    response = client.patch("/api/v1/notifications/read-all")
    assert response.status_code == 200
    assert response.json()["updated_count"] == 2
