import pytest
import uuid
from unittest.mock import MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.db import Base
from app.database.repository import FeedbackRepository
from app.services.roadmap_service import RoadmapService
from app.agents.roadmap_agent import RoadmapAgent


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


def test_roadmap_service_transactional_creation(db_session):
    feedback_repo = FeedbackRepository(db_session)
    feedback_record = feedback_repo.create(
        original_text="The login page freezes after clicking Sign In.",
        feedback_type="Bug Report",
        category="Authentication",
        subcategory="Login"
    )
    db_session.commit()

    mock_agent = MagicMock(spec=RoadmapAgent)
    mock_agent.generate_roadmap.return_value = {
        "title": "Resolve Login Page Freeze",
        "description": "Investigate and resolve authentication UI freeze.",
        "status": "Backlog",
        "effort": "M",
        "progress": 0,
        "tasks": [
            {
                "title": "Investigate login request lifecycle",
                "description": "Identify where UI event thread blocks.",
                "effort": "S",
                "status": "Open",
                "progress": 0,
                "dependencies": [],
                "acceptance_criteria": ["Login button click does not freeze UI"]
            },
            {
                "title": "Add regression test coverage",
                "description": "Ensure login timeout path is tested.",
                "effort": "S",
                "status": "Open",
                "progress": 0,
                "dependencies": [],
                "acceptance_criteria": ["Automated test suite passes"]
            }
        ]
    }

    service = RoadmapService(session=db_session, agent=mock_agent)
    roadmap = service.create_roadmap_for_feedback(
        feedback_id=feedback_record.id,
        analysis={"category": "Authentication", "subcategory": "Login"},
        feedback_text="The login page freezes after clicking Sign In."
    )
    db_session.commit()

    assert roadmap.id is not None
    assert str(roadmap.feedback_id) == str(feedback_record.id)
    assert roadmap.title == "Resolve Login Page Freeze"
    assert roadmap.progress == 0
    assert roadmap.status == "Backlog"

    tasks = service.task_repo.list_by_roadmap(roadmap.id)
    assert len(tasks) == 2
    assert tasks[0].title == "Investigate login request lifecycle"
    assert tasks[0].progress == 0
    assert tasks[1].title == "Add regression test coverage"
    assert tasks[1].progress == 0
