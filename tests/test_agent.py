import pytest
import uuid
from unittest.mock import MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.db import Base
from app.schemas.agent import FeedbackAnalysis
from app.prompts.feedback_prompt import FeedbackPromptBuilder
from app.agents.decision_engine import DecisionEngine
from app.agents.feedback_agent import FeedbackAgent
from app.agents.roadmap_agent import RoadmapAgent
from app.services.feedback_service import FeedbackService
from app.services.roadmap_service import RoadmapService
from app.taxonomy.taxonomy_engine import TaxonomyEngine
from app.taxonomy.taxonomy_validator import TaxonomyValidationError
from app.config import OLLAMA_HOST
import urllib.request


@pytest.fixture
def test_db_session():
    test_engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(test_engine)
    Session = sessionmaker(bind=test_engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(test_engine)


def test_prompt_builder_structure():
    builder = FeedbackPromptBuilder()
    sys_prompt = builder.build_system_prompt()
    user_prompt = builder.build_user_prompt("Login OTP fails on Android", platform="Android")

    assert "ProductIQ's Feedback Analysis Agent" in sys_prompt
    assert "========== CATEGORIES ==========" in sys_prompt
    assert "AUTHORITATIVE SYSTEM TAXONOMY:" in sys_prompt
    assert "USER FEEDBACK TO ANALYZE:" in user_prompt
    assert "Reported Platform: Android" in user_prompt


def test_decision_engine_rules_and_mapping():
    engine = TaxonomyEngine()
    decision_engine = DecisionEngine(engine=engine)

    analysis = FeedbackAnalysis(
        summary="OTP code email never arrives during login",
        feedback_type="Bug Report",
        category="Authentication",
        subcategory="OTP Verification",
        bug_category="Functional Bug",
        severity="Critical",
        priority="P2",  # Should be elevated to P0 for Critical bug
        impact_area="All Users",
        platform="Web",
        recommended_action="CREATE_BUG",
        confidence="High"
    )

    processed = decision_engine.process(analysis)

    assert processed["feedback_type_id"] == "FT002"
    assert processed["category_id"] == "CAT001"
    assert processed["subcategory_id"] == "AUTH003"
    assert processed["priority"] == "P0"  # Elevated from P2 -> P0 for Critical severity
    assert processed["platform"] == "Web"


def test_feedback_agent_with_mocked_ollama():
    mock_client = MagicMock()
    valid_json_response = """
    {
        "summary": "Password reset link is expired upon opening",
        "feedback_type": "Bug Report",
        "category": "Authentication",
        "subcategory": "Password Recovery",
        "bug_category": "Functional Bug",
        "severity": "Major",
        "priority": "P1",
        "impact_area": "All Users",
        "platform": "Web",
        "recommended_action": "CREATE_BUG",
        "confidence": "High",
        "reasoning": "Standard password recovery bug."
    }
    """
    mock_client.generate.return_value = valid_json_response

    agent = FeedbackAgent(client=mock_client)
    analysis = agent.analyze("Password reset link is expired upon opening", platform="Web")

    assert isinstance(analysis, FeedbackAnalysis)
    assert analysis.category == "Authentication"
    assert analysis.subcategory == "Password Recovery"
    assert analysis.priority == "P1"


def test_feedback_agent_retry_on_invalid_taxonomy():
    mock_client = MagicMock()
    # First response returns invalid category "InvalidCat"
    invalid_response = """
    {
        "summary": "Sample issue",
        "feedback_type": "Bug Report",
        "category": "InvalidCat",
        "subcategory": "Password Recovery",
        "bug_category": "Functional Bug",
        "severity": "Major",
        "priority": "P1",
        "impact_area": "All Users",
        "platform": "Web",
        "recommended_action": "CREATE_BUG",
        "confidence": "High"
    }
    """
    # Second response returns corrected category "Authentication"
    valid_response = """
    {
        "summary": "Sample issue",
        "feedback_type": "Bug Report",
        "category": "Authentication",
        "subcategory": "Password Recovery",
        "bug_category": "Functional Bug",
        "severity": "Major",
        "priority": "P1",
        "impact_area": "All Users",
        "platform": "Web",
        "recommended_action": "CREATE_BUG",
        "confidence": "High"
    }
    """
    mock_client.generate.side_effect = [invalid_response, valid_response]

    agent = FeedbackAgent(client=mock_client, max_retries=2)
    analysis = agent.analyze("Sample issue", platform="Web")

    assert analysis.category == "Authentication"
    assert mock_client.generate.call_count == 2


def test_feedback_service_end_to_end(test_db_session):
    mock_client = MagicMock()
    valid_feedback_response = """
    {
        "summary": "Billing invoice PDF download crashes app",
        "feedback_type": "Bug Report",
        "category": "Billing & Subscription",
        "subcategory": "Invoices",
        "bug_category": "Crash/Fatal Error",
        "severity": "Blocker",
        "priority": "P0",
        "impact_area": "Enterprise Customers",
        "platform": "iOS",
        "recommended_action": "CREATE_BUG",
        "confidence": "High"
    }
    """
    valid_roadmap_response = """{
        "title": "Fix Billing Invoice PDF Download",
        "description": "Resolve PDF rendering crash on iOS",
        "status": "Backlog",
        "effort": "M",
        "progress": 0,
        "tasks": [
            {
                "title": "Debug PDF generation crash on iOS",
                "description": "Inspect crash log when downloading invoice PDF.",
                "effort": "S",
                "status": "Open",
                "progress": 0,
                "dependencies": [],
                "acceptance_criteria": ["PDF downloads without crashing app"]
            }
        ]
    }"""
    mock_client.generate.side_effect = [valid_feedback_response, valid_roadmap_response]

    agent = FeedbackAgent(client=mock_client)
    roadmap_agent = RoadmapAgent(client=mock_client)
    roadmap_service = RoadmapService(session=test_db_session, agent=roadmap_agent)
    service = FeedbackService(session=test_db_session, agent=agent, roadmap_service=roadmap_service)

    result = service.process_and_store_feedback(
        raw_text="Billing invoice PDF download crashes app whenever opened on iPhone 15.",
        platform="iOS"
    )
    record = result["feedback"]

    assert record.id is not None
    assert record.category == "Billing & Subscription"
    assert record.subcategory == "Invoices"
    assert record.priority == "P0"
    assert record.status == "Triaged"



def is_ollama_available() -> bool:
    try:
        url = f"{OLLAMA_HOST.rstrip('/')}/api/tags"
        with urllib.request.urlopen(url, timeout=2.0) as resp:
            return resp.status == 200
    except Exception:
        return False


@pytest.mark.skipif(not is_ollama_available(), reason="Ollama server is unavailable")
def test_live_feedback_agent_with_ollama():
    agent = FeedbackAgent()
    analysis = agent.analyze(
        "When I try to log in using OTP on the mobile web app, the code never arrives in my inbox.",
        platform="Web"
    )
    assert isinstance(analysis, FeedbackAnalysis)
    assert analysis.category == "Authentication"
    assert analysis.subcategory in ["Login", "OTP Verification"]
