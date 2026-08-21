import pytest
from app.utils.json_parser import JSONParser


def test_json_parser_valid():
    raw = '{"key": "value", "count": 42}'
    parsed = JSONParser.parse(raw)
    assert parsed == {"key": "value", "count": 42}


def test_json_parser_fenced():
    raw = """```json
    {
        "feedback_type": "Bug Report",
        "category": "Authentication"
    }
    ```"""
    parsed = JSONParser.parse(raw)
    assert parsed == {
        "feedback_type": "Bug Report",
        "category": "Authentication"
    }


def test_json_parser_invalid():
    raw = "This is not json at all."
    with pytest.raises(ValueError) as excinfo:
        JSONParser.parse(raw)
    assert "Invalid JSON Returned" in str(excinfo.value)
