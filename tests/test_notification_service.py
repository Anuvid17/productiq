import pytest
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.db import Base
from app.database.repository import FeedbackRepository
from app.services.notification_service import NotificationService


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)


def test_notification_service_lifecycle(db_session):
    fb_repo = FeedbackRepository(db_session)
    fb = fb_repo.create(original_text="OTP code timeout", status="Triaged")
    db_session.commit()

    service = NotificationService(db_session)

    # 1. Create notification
    notif1 = service.create_notification(fb.id, "First notification", notification_type="INFO")
    db_session.commit()

    assert notif1.id is not None
    assert notif1.read is False

    # 2. Retrieve unread notifications
    unread_list = service.get_notifications(feedback_id=fb.id, unread_only=True)
    assert len(unread_list) == 1
    assert unread_list[0].id == notif1.id

    # 3. Mark as read
    service.mark_as_read(notif1.id)
    db_session.commit()

    unread_list_after = service.get_notifications(feedback_id=fb.id, unread_only=True)
    assert len(unread_list_after) == 0


def test_duplicate_resolution_notification_prevention(db_session):
    fb_repo = FeedbackRepository(db_session)
    fb = fb_repo.create(original_text="OTP code timeout", status="Triaged")
    db_session.commit()

    service = NotificationService(db_session)

    # First resolution notification
    n1 = service.create_resolution_notification(fb.id)
    db_session.commit()

    # Second resolution notification attempt
    n2 = service.create_resolution_notification(fb.id)
    db_session.commit()

    assert n1.id == n2.id
    all_notifs = service.get_notifications(feedback_id=fb.id)
    assert len(all_notifs) == 1


def test_invalid_feedback_id(db_session):
    service = NotificationService(db_session)
    random_id = uuid.uuid4()
    with pytest.raises(ValueError, match="does not exist"):
        service.create_notification(random_id, "Test message")
