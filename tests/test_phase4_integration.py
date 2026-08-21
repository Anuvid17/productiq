import pytest
import urllib.request
from unittest.mock import MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.db import Base
from app.services.feedback_service import FeedbackService
from app.agents.feedback_agent import FeedbackAgent
from app.agents.roadmap_agent import RoadmapAgent
from app.config import OLLAMA_HOST


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


def test_mocked_end_to_end_pipeline(db_session):
    mock_feedback_client = MagicMock()
    mock_feedback_client.generate.return_value = """{
        "summary": "Login page freezes after clicking Sign In",
        "feedback_type": "Bug Report",
        "category": "Authentication",
        "subcategory": "Login",
        "bug_category": "Functional Bug",
        "severity": "Major",
        "priority": "P1",
        "impact_area": "All Users",
        "platform": "Web",
        "recommended_action": "CREATE_BUG",
        "confidence": "High"
    }"""

    mock_roadmap_client = MagicMock()
    mock_roadmap_client.generate.return_value = """{
        "title": "Resolve Login Page Freeze",
        "description": "Engineering tasks to debug authentication thread freeze.",
        "status": "Backlog",
        "effort": "M",
        "progress": 0,
        "tasks": [
            {
                "title": "Investigate login event handling",
                "description": "Trace click listener performance.",
                "effort": "S",
                "status": "Open",
                "progress": 0,
                "dependencies": [],
                "acceptance_criteria": ["Sign in button does not freeze UI"]
            }
        ]
    }"""

    feedback_agent = FeedbackAgent(client=mock_feedback_client)
    roadmap_agent = RoadmapAgent(client=mock_roadmap_client)

    service = FeedbackService(session=db_session, agent=feedback_agent)
    service.roadmap_service.agent = roadmap_agent

    result = service.process_and_store_feedback(
        raw_text="The login page freezes after clicking Sign In.",
        platform="Web"
    )

    feedback_rec = result["feedback"]
    roadmap_rec = result["roadmap"]
    tasks_list = result["tasks"]

    assert feedback_rec.id is not None
    assert feedback_rec.category == "Authentication"

    assert roadmap_rec.id is not None
    assert str(roadmap_rec.feedback_id) == str(feedback_rec.id)
    assert roadmap_rec.progress == 0
    assert roadmap_rec.status == "Backlog"

    assert len(tasks_list) == 1
    assert tasks_list[0].progress == 0
    assert tasks_list[0].status == "Open"
    assert len(tasks_list[0].acceptance_criteria) > 0


def is_ollama_available() -> bool:
    try:
        url = f"{OLLAMA_HOST.rstrip('/')}/api/tags"
        with urllib.request.urlopen(url, timeout=2.0) as resp:
            return resp.status == 200
    except Exception:
        return False


@pytest.mark.skipif(not is_ollama_available(), reason="Ollama server is unavailable")
def test_live_roadmap_generation_integration(db_session):
    service = FeedbackService(session=db_session)
    result = service.process_and_store_feedback(
        raw_text="The login page freezes after clicking Sign In.",
        platform="Web"
    )

    roadmap_rec = result["roadmap"]
    tasks_list = result["tasks"]

    assert roadmap_rec is not None
    assert roadmap_rec.progress == 0
    assert roadmap_rec.status == "Backlog"
    assert len(tasks_list) > 0

    for t in tasks_list:
        assert t.progress == 0
        assert t.effort in ["XS", "S", "M", "L", "XL"]
        assert isinstance(t.acceptance_criteria, list)
        assert len(t.acceptance_criteria) > 0
