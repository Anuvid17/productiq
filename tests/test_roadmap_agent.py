import pytest
from unittest.mock import MagicMock
from app.agents.roadmap_agent import RoadmapAgent
from app.schemas.agent import FeedbackAnalysis


def test_roadmap_agent_mocked_success():
    mock_client = MagicMock()
    valid_response = """{
        "title": "Fix OTP Delivery Timeout",
        "description": "Engineers need to audit OTP email queue dispatch.",
        "status": "Backlog",
        "effort": "M",
        "progress": 0,
        "tasks": [
            {
                "title": "Trace OTP queue handler",
                "description": "Inspect SMTP connection timeout logic.",
                "effort": "S",
                "status": "Open",
                "progress": 0,
                "dependencies": [],
                "acceptance_criteria": ["Emails are dispatched within 5 seconds"]
            }
        ]
    }"""
    mock_client.generate.return_value = valid_response

    agent = RoadmapAgent(client=mock_client)
    analysis = FeedbackAnalysis(
        summary="OTP code email never arrives during login",
        feedback_type="Bug Report",
        category="Authentication",
        subcategory="OTP Verification",
        bug_category="Functional Bug",
        severity="Critical",
        priority="P0",
        impact_area="All Users",
        platform="Web",
        recommended_action="CREATE_BUG",
        confidence="High"
    )

    roadmap = agent.generate_roadmap(analysis, "OTP code email never arrives during login")
    assert roadmap["title"] == "Fix OTP Delivery Timeout"
    assert roadmap["status"] == "Backlog"
    assert len(roadmap["tasks"]) == 1


def test_roadmap_agent_retry_on_invalid_status():
    mock_client = MagicMock()
    invalid_response = """{
        "title": "Fix OTP Delivery Timeout",
        "status": "Completed",
        "effort": "M",
        "progress": 0,
        "tasks": [{"title": "Task 1", "effort": "S", "status": "Open", "progress": 0, "acceptance_criteria": ["Crit 1"]}]
    }"""
    corrected_response = """{
        "title": "Fix OTP Delivery Timeout",
        "status": "Backlog",
        "effort": "M",
        "progress": 0,
        "tasks": [{"title": "Task 1", "effort": "S", "status": "Open", "progress": 0, "acceptance_criteria": ["Crit 1"]}]
    }"""
    mock_client.generate.side_effect = [invalid_response, corrected_response]

    agent = RoadmapAgent(client=mock_client, max_retries=2)
    analysis = {"summary": "Sample bug", "feedback_type": "Bug Report", "category": "Authentication", "subcategory": "Login"}

    roadmap = agent.generate_roadmap(analysis, "Sample feedback text")
    assert roadmap["status"] == "Backlog"
    assert mock_client.generate.call_count == 2
