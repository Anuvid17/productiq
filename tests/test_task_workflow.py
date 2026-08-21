import pytest
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.db import Base
from app.database.repository import FeedbackRepository, RoadmapRepository, RoadmapTaskRepository
from app.services.task_workflow_service import TaskWorkflowService
from app.schemas.roadmap import TaskProgressUpdate


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


@pytest.fixture
def sample_task_fixture(db_session):
    fb_repo = FeedbackRepository(db_session)
    rm_repo = RoadmapRepository(db_session)
    task_repo = RoadmapTaskRepository(db_session)

    fb = fb_repo.create(
        original_text="The login page freezes after clicking Sign In.",
        feedback_type="Bug Report",
        category="Authentication",
        subcategory="Login",
        status="Triaged"
    )
    rm = rm_repo.create(
        feedback_id=fb.id,
        title="Resolve Login Freeze",
        status="Backlog",
        progress=0
    )
    t1 = task_repo.create(
        roadmap_id=rm.id,
        title="Fix UI freeze",
        status="Open",
        progress=0,
        acceptance_criteria=["No UI freeze"]
    )
    db_session.commit()
    return fb, rm, t1


def test_valid_task_progress_update(db_session, sample_task_fixture):
    fb, rm, t1 = sample_task_fixture
    service = TaskWorkflowService(session=db_session)

    res = service.update_task_progress_and_status(t1.id, update={"progress": 50, "status": "In Progress"})
    db_session.commit()

    updated_task = res["task"]
    updated_rm = res["roadmap"]

    assert updated_task.progress == 50
    assert updated_task.status == "In Progress"
    assert updated_rm.progress == 50
    assert updated_rm.status == "In Progress"


def test_invalid_negative_progress(db_session, sample_task_fixture):
    _, _, t1 = sample_task_fixture
    service = TaskWorkflowService(session=db_session)

    with pytest.raises(ValueError, match="must be an integer between 0 and 100"):
        service.update_task_progress_and_status(t1.id, update={"progress": -10})


def test_invalid_progress_over_100(db_session, sample_task_fixture):
    _, _, t1 = sample_task_fixture
    service = TaskWorkflowService(session=db_session)

    with pytest.raises(ValueError, match="must be an integer between 0 and 100"):
        service.update_task_progress_and_status(t1.id, update={"progress": 150})


def test_valid_status_transition(db_session, sample_task_fixture):
    _, _, t1 = sample_task_fixture
    service = TaskWorkflowService(session=db_session)

    # Open -> In Review
    res1 = service.update_task_progress_and_status(t1.id, update={"status": "In Review"})
    assert res1["task"].status == "In Review"

    # In Review -> Approved
    res2 = service.update_task_progress_and_status(t1.id, update={"status": "Approved"})
    assert res2["task"].status == "Approved"


def test_invalid_status_transition(db_session, sample_task_fixture):
    _, _, t1 = sample_task_fixture
    service = TaskWorkflowService(session=db_session)

    # Invalid status name
    with pytest.raises(ValueError, match="is invalid"):
        service.update_task_progress_and_status(t1.id, update={"status": "NonexistentStatus"})


def test_open_plus_hundred_percent_consistency(db_session, sample_task_fixture):
    _, _, t1 = sample_task_fixture
    service = TaskWorkflowService(session=db_session)

    # Open + 100% automatically promotes task status to Approved
    res = service.update_task_progress_and_status(t1.id, update={"progress": 100, "status": "Open"})
    assert res["task"].progress == 100
    assert res["task"].status == "Approved"


def test_resolved_less_than_hundred_rejection(db_session, sample_task_fixture):
    _, _, t1 = sample_task_fixture
    service = TaskWorkflowService(session=db_session)

    with pytest.raises(ValueError, match="requires 100% progress"):
        service.update_task_progress_and_status(t1.id, update={"progress": 50, "status": "Resolved"})


def test_closed_less_than_hundred_rejection(db_session, sample_task_fixture):
    _, _, t1 = sample_task_fixture
    service = TaskWorkflowService(session=db_session)

    with pytest.raises(ValueError, match="requires 100% progress"):
        service.update_task_progress_and_status(t1.id, update={"progress": 25, "status": "Closed"})


def test_zero_progress_resolved_rejection(db_session, sample_task_fixture):
    _, _, t1 = sample_task_fixture
    service = TaskWorkflowService(session=db_session)

    with pytest.raises(ValueError, match="requires 100% progress"):
        service.update_task_progress_and_status(t1.id, update={"progress": 0, "status": "Resolved"})


def test_reopening_behavior(db_session, sample_task_fixture):
    _, _, t1 = sample_task_fixture
    service = TaskWorkflowService(session=db_session)

    # Resolve task first
    service.update_task_progress_and_status(t1.id, update={"progress": 100, "status": "Resolved"})
    assert t1.status == "Resolved"

    # Reopen to Closed -> Open -> In Progress
    service.update_task_progress_and_status(t1.id, update={"status": "Closed"})
    res = service.update_task_progress_and_status(t1.id, update={"progress": 50, "status": "In Progress"})
    assert res["task"].status == "In Progress"
    assert res["task"].progress == 50


def test_nonexistent_task(db_session):
    service = TaskWorkflowService(session=db_session)
    random_id = uuid.uuid4()
    with pytest.raises(ValueError, match="does not exist"):
        service.update_task_progress_and_status(random_id, update={"progress": 50})
