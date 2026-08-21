import pytest
from app.agents.roadmap_validator import RoadmapValidator, RoadmapValidationError


def test_roadmap_validator_valid():
    validator = RoadmapValidator()
    valid_data = {
        "title": "Resolve Login Freeze",
        "description": "Engineering tasks to debug authentication loop",
        "status": "Backlog",
        "effort": "M",
        "progress": 0,
        "tasks": [
            {
                "title": "Trace authentication event handlers",
                "description": "Inspect button click handler in login module",
                "effort": "S",
                "status": "Open",
                "progress": 0,
                "dependencies": [],
                "acceptance_criteria": ["UI remains responsive during click"]
            }
        ]
    }
    validator.validate(valid_data)  # Should pass without raising exception


def test_roadmap_validator_invalid_status():
    validator = RoadmapValidator()
    data = {
        "title": "Resolve Login Freeze",
        "status": "InvalidStatus",
        "effort": "M",
        "progress": 0,
        "tasks": [{"title": "Task 1", "effort": "S", "progress": 0, "acceptance_criteria": ["Criteria 1"]}]
    }
    with pytest.raises(RoadmapValidationError, match="Invalid roadmap status"):
        validator.validate(data)


def test_roadmap_validator_invalid_effort():
    validator = RoadmapValidator()
    data = {
        "title": "Resolve Login Freeze",
        "status": "Backlog",
        "effort": "SuperHigh",
        "progress": 0,
        "tasks": [{"title": "Task 1", "effort": "S", "progress": 0, "acceptance_criteria": ["Criteria 1"]}]
    }
    with pytest.raises(RoadmapValidationError, match="Invalid roadmap effort level"):
        validator.validate(data)


def test_roadmap_validator_invalid_progress():
    validator = RoadmapValidator()
    data = {
        "title": "Resolve Login Freeze",
        "status": "Backlog",
        "effort": "M",
        "progress": 150,  # Invalid progress > 100
        "tasks": [{"title": "Task 1", "effort": "S", "progress": 0, "acceptance_criteria": ["Criteria 1"]}]
    }
    with pytest.raises(RoadmapValidationError, match="Invalid roadmap progress"):
        validator.validate(data)


def test_roadmap_validator_empty_tasks():
    validator = RoadmapValidator()
    data = {
        "title": "Resolve Login Freeze",
        "status": "Backlog",
        "effort": "M",
        "progress": 0,
        "tasks": []
    }
    with pytest.raises(RoadmapValidationError, match="must contain a non-empty list of developer tasks"):
        validator.validate(data)
