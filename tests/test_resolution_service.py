import pytest
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.db import Base
from app.database.repository import FeedbackRepository, RoadmapRepository, RoadmapTaskRepository, NotificationRepository
from app.services.resolution_service import ResolutionService
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


def test_resolution_service_incomplete_roadmap(db_session):
    fb_repo = FeedbackRepository(db_session)
    rm_repo = RoadmapRepository(db_session)
    task_repo = RoadmapTaskRepository(db_session)

    fb = fb_repo.create(original_text="Login issue", status="Triaged")
    rm = rm_repo.create(feedback_id=fb.id, title="Fix Login", status="In Progress", progress=50)
    t1 = task_repo.create(roadmap_id=rm.id, title="Task 1", progress=50, status="In Progress")
    db_session.commit()

    service = ResolutionService(session=db_session)
    fb_res, was_resolved, notif = service.check_and_resolve_feedback(fb.id)

    assert was_resolved is False
    assert fb_res.status == "Triaged"
    assert notif is None


def test_resolution_service_hundred_percent_numerical_but_not_resolved_status(db_session):
    fb_repo = FeedbackRepository(db_session)
    rm_repo = RoadmapRepository(db_session)
    task_repo = RoadmapTaskRepository(db_session)

    fb = fb_repo.create(original_text="Login issue", status="Triaged")
    rm = rm_repo.create(feedback_id=fb.id, title="Fix Login", status="Testing", progress=100)
    t1 = task_repo.create(roadmap_id=rm.id, title="Task 1", progress=100, status="Approved")
    db_session.commit()

    service = ResolutionService(session=db_session)
    fb_res, was_resolved, notif = service.check_and_resolve_feedback(fb.id)

    assert was_resolved is False
    assert fb_res.status == "Triaged"
    assert notif is None


def test_resolution_service_complete_release_and_notification(db_session):
    fb_repo = FeedbackRepository(db_session)
    rm_repo = RoadmapRepository(db_session)
    task_repo = RoadmapTaskRepository(db_session)
    notif_repo = NotificationRepository(db_session)

    fb = fb_repo.create(original_text="Login issue", status="Triaged")
    rm = rm_repo.create(feedback_id=fb.id, title="Fix Login", status="Released", progress=100)
    t1 = task_repo.create(roadmap_id=rm.id, title="Task 1", progress=100, status="Resolved")
    db_session.commit()

    service = ResolutionService(session=db_session)
    fb_res, was_resolved, notif = service.check_and_resolve_feedback(fb.id)
    db_session.commit()

    assert was_resolved is True
    assert fb_res.status == "Resolved"
    assert notif is not None
    assert "resolved" in notif.message.lower()

    # Second check -> duplicate notification prevention
    fb_res2, was_resolved2, notif2 = service.check_and_resolve_feedback(fb.id)
    all_notifs = notif_repo.list(feedback_id=fb.id)
    assert len(all_notifs) == 1
