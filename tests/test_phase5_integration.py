import pytest
import uuid
from unittest.mock import MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.db import Base
from app.database.repository import FeedbackRepository, RoadmapRepository, RoadmapTaskRepository, NotificationRepository
from app.services.task_workflow_service import TaskWorkflowService


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


def test_phase5_step_by_step_developer_workflow(db_session):
    fb_repo = FeedbackRepository(db_session)
    rm_repo = RoadmapRepository(db_session)
    task_repo = RoadmapTaskRepository(db_session)
    notif_repo = NotificationRepository(db_session)

    # Initial setup: 1 Feedback, 1 Roadmap, 3 Tasks
    fb = fb_repo.create(
        original_text="The login page freezes after clicking Sign In.",
        feedback_type="Bug Report",
        category="Authentication",
        subcategory="Login",
        status="Triaged"
    )

    rm = rm_repo.create(
        feedback_id=fb.id,
        title="Resolve Frozen Login Page Issue",
        status="Backlog",
        progress=0
    )

    t1 = task_repo.create(roadmap_id=rm.id, title="Analyze Login Freeze", progress=0, status="Open")
    t2 = task_repo.create(roadmap_id=rm.id, title="Fix Login Freeze", progress=0, status="Open")
    t3 = task_repo.create(roadmap_id=rm.id, title="Test & Validate Fix", progress=0, status="Open")
    db_session.commit()

    workflow = TaskWorkflowService(session=db_session)

    # STEP 1: Developer updates Task 1 -> 100%, Resolved
    r1 = workflow.update_task_progress_and_status(t1.id, update={"progress": 100, "status": "Resolved"})
    db_session.commit()

    assert r1["roadmap"].progress == 33
    assert r1["roadmap"].status == "In Progress"
    assert r1["feedback"].status == "Triaged"
    assert r1["was_resolved"] is False

    # STEP 2: Developer updates Task 2 -> 100%, Resolved
    r2 = workflow.update_task_progress_and_status(t2.id, update={"progress": 100, "status": "Resolved"})
    db_session.commit()

    assert r2["roadmap"].progress == 67
    assert r2["roadmap"].status == "In Progress"
    assert r2["feedback"].status == "Triaged"
    assert r2["was_resolved"] is False

    # STEP 3: Developer updates Task 3 -> 100%, Approved
    r3 = workflow.update_task_progress_and_status(t3.id, update={"progress": 100, "status": "Approved"})
    db_session.commit()

    assert r3["roadmap"].progress == 100
    assert r3["roadmap"].status == "Testing"
    assert r3["feedback"].status == "Triaged"
    assert r3["was_resolved"] is False

    # STEP 4: Developer updates Task 3 -> 100%, Resolved (Final completion)
    r4 = workflow.update_task_progress_and_status(t3.id, update={"status": "Resolved"})
    db_session.commit()

    assert r4["roadmap"].progress == 100
    assert r4["roadmap"].status == "Released"
    assert r4["feedback"].status == "Resolved"
    assert r4["was_resolved"] is True
    assert r4["notification"] is not None
    assert "resolved" in r4["notification"].message.lower()

    # Verify notification in database
    notifs = notif_repo.list(feedback_id=fb.id)
    assert len(notifs) == 1
    assert notifs[0].notification_type == "RESOLUTION"


def test_transactional_rollback_on_failure(db_session):
    fb_repo = FeedbackRepository(db_session)
    rm_repo = RoadmapRepository(db_session)
    task_repo = RoadmapTaskRepository(db_session)

    fb = fb_repo.create(original_text="Login issue", status="Triaged")
    rm = rm_repo.create(feedback_id=fb.id, title="Fix Login", status="Backlog", progress=0)
    t1 = task_repo.create(roadmap_id=rm.id, title="Task 1", progress=0, status="Open")
    db_session.commit()

    workflow = TaskWorkflowService(session=db_session)
    # Mock notification service to raise Exception
    workflow.notification_service.create_resolution_notification = MagicMock(side_effect=RuntimeError("DB Error"))

    with pytest.raises(RuntimeError, match="DB Error"):
        try:
            workflow.update_task_progress_and_status(t1.id, update={"progress": 100, "status": "Resolved"})
        except Exception:
            db_session.rollback()
            raise

    # Verify atomic rollback
    db_session.rollback()
    t1_refreshed = task_repo.get_by_id(t1.id)
    rm_refreshed = rm_repo.get_by_id(rm.id)
    fb_refreshed = fb_repo.get_by_id(fb.id)

    assert t1_refreshed.progress == 0
    assert t1_refreshed.status == "Open"
    assert rm_refreshed.progress == 0
    assert rm_refreshed.status == "Backlog"
    assert fb_refreshed.status == "Triaged"
