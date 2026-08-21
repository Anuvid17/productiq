import pytest
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pydantic import ValidationError

from app.database.db import Base, check_db_health
from app.database.models import Feedback, Roadmap, RoadmapTask, Notification
from app.database.repository import (
    FeedbackRepository,
    RoadmapRepository,
    RoadmapTaskRepository,
    NotificationRepository
)
from app.schemas.roadmap import RoadmapCreate, RoadmapTaskCreate, RoadmapUpdate, RoadmapTaskUpdate


@pytest.fixture
def db_session():
    """
    Isolated test database session fixture using in-memory SQLite engine.
    """
    test_engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(test_engine)
    Session = sessionmaker(bind=test_engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(test_engine)


def test_db_engine_configuration_and_health(db_session):
    health = check_db_health(db_session.bind)
    assert health["status"] == "healthy"
    assert health["connected"] is True


def test_feedback_crud(db_session):
    repo = FeedbackRepository(db_session)

    # Create
    fb = repo.create(
        original_text="OTP code email never arrives during login.",
        platform="Web",
        category="Authentication",
        subcategory="OTP Verification",
        priority="P0",
        severity="Critical"
    )
    assert fb.id is not None
    assert fb.status == "Open"

    # Get by ID
    retrieved = repo.get_by_id(fb.id)
    assert retrieved is not None
    assert retrieved.original_text == "OTP code email never arrives during login."
    assert retrieved.priority == "P0"

    # Update
    updated = repo.update(fb.id, status="Triaged", summary="Login OTP delivery issue")
    assert updated.status == "Triaged"
    assert updated.summary == "Login OTP delivery issue"

    # List
    items = repo.list(status="Triaged")
    assert len(items) == 1
    assert items[0].id == fb.id

    # Delete
    deleted = repo.delete(fb.id)
    assert deleted is True
    assert repo.get_by_id(fb.id) is None


def test_roadmap_creation_and_feedback_relationship(db_session):
    fb_repo = FeedbackRepository(db_session)
    rm_repo = RoadmapRepository(db_session)

    fb = fb_repo.create(original_text="Add dark mode support to dashboard")
    rm = rm_repo.create(
        feedback_id=fb.id,
        title="Dashboard Dark Mode Support",
        description="Implement theme toggle and CSS glassmorphism",
        status="Planned",
        effort="M",
        progress=10
    )

    assert rm.id is not None
    assert rm.feedback_id == fb.id
    assert rm.status == "Planned"

    # Relationship verify
    assert fb.roadmap is not None
    assert fb.roadmap.id == rm.id
    assert rm.feedback.id == fb.id

    # Lookup by feedback ID
    rm_by_fb = rm_repo.get_by_feedback_id(fb.id)
    assert rm_by_fb is not None
    assert rm_by_fb.id == rm.id


def test_roadmap_task_creation_and_relationship(db_session):
    fb_repo = FeedbackRepository(db_session)
    rm_repo = RoadmapRepository(db_session)
    task_repo = RoadmapTaskRepository(db_session)

    fb = fb_repo.create(original_text="Fix CSV export memory leak")
    rm = rm_repo.create(feedback_id=fb.id, title="Optimize CSV Export Stream")

    task1 = task_repo.create(
        roadmap_id=rm.id,
        title="Refactor generator chunk size",
        status="In Progress",
        progress=50,
        dependencies=["PR-101"],
        acceptance_criteria=["Memory under 50MB"]
    )
    task2 = task_repo.create(
        roadmap_id=rm.id,
        title="Add automated benchmark test",
        status="Open",
        progress=0
    )

    tasks = task_repo.list_by_roadmap(rm.id)
    assert len(tasks) == 2
    assert tasks[0].id == task1.id
    assert tasks[1].id == task2.id

    # Verify task -> roadmap relationship
    assert task1.roadmap.id == rm.id
    assert len(rm.tasks) == 2


def test_notification_creation_and_relationship(db_session):
    fb_repo = FeedbackRepository(db_session)
    notif_repo = NotificationRepository(db_session)

    fb = fb_repo.create(original_text="Password reset link expires instantly")
    notif = notif_repo.create(
        feedback_id=fb.id,
        message="Feedback triage status updated to P0 Critical.",
        notification_type="STATUS_CHANGED"
    )

    assert notif.id is not None
    assert notif.read is False
    assert len(fb.notifications) == 1
    assert fb.notifications[0].id == notif.id

    # Mark read
    updated_notif = notif_repo.mark_as_read(notif.id)
    assert updated_notif.read is True


def test_progress_validation():
    # Valid Pydantic progress values
    rm = RoadmapCreate(feedback_id=uuid.uuid4(), title="Test Progress", progress=75)
    assert rm.progress == 75

    # Invalid progress < 0
    with pytest.raises(ValidationError):
        RoadmapCreate(feedback_id=uuid.uuid4(), title="Test Progress", progress=-5)

    # Invalid progress > 100
    with pytest.raises(ValidationError):
        RoadmapTaskUpdate(progress=150)


def test_cascade_delete_behavior(db_session):
    fb_repo = FeedbackRepository(db_session)
    rm_repo = RoadmapRepository(db_session)
    task_repo = RoadmapTaskRepository(db_session)
    notif_repo = NotificationRepository(db_session)

    fb = fb_repo.create(original_text="System crash during PDF export")
    rm = rm_repo.create(feedback_id=fb.id, title="Fix PDF Exporter Crash")
    task = task_repo.create(roadmap_id=rm.id, title="Inspect buffer overflow")
    notif = notif_repo.create(
        feedback_id=fb.id,
        message="Created task for PDF crash",
        notification_type="ROADMAP_UPDATED"
    )

    # Delete Feedback
    fb_repo.delete(fb.id)

    # Verify cascade deletion of roadmap, task, and notification
    assert rm_repo.get_by_id(rm.id) is None
    assert task_repo.get_by_id(task.id) is None
    assert notif_repo.get_by_id(notif.id) is None
