import pytest
from app.agents.duplicate_detector import DuplicateDetector
from app.schemas.duplicate import DuplicateCheckResult


def test_duplicate_detector_identical_text():
    detector = DuplicateDetector(threshold=0.75)
    new_text = "OTP verification code is not delivered."
    candidates = [
        {"id": "cand-1", "original_text": "OTP verification code is not delivered.", "category": "Authentication"}
    ]
    result = detector.detect(new_text, candidates)
    assert isinstance(result, DuplicateCheckResult)
    assert result.is_duplicate is True
    assert result.similarity_score >= 0.95
    assert result.matched_feedback_id == "cand-1"


def test_duplicate_detector_highly_similar():
    detector = DuplicateDetector(threshold=0.70)
    new_text = "I am not receiving my verification OTP code when attempting to log in."
    candidates = [
        {"id": "cand-1", "original_text": "OTP verification code is not delivered during login.", "category": "Authentication"}
    ]
    result = detector.detect(new_text, candidates)
    assert result.is_duplicate is True
    assert result.similarity_score >= 0.70


def test_duplicate_detector_clearly_different():
    detector = DuplicateDetector(threshold=0.75)
    new_text = "Please allow exporting invoice reports as PDF files."
    candidates = [
        {"id": "cand-1", "original_text": "OTP verification code is not delivered during login.", "category": "Authentication"}
    ]
    result = detector.detect(new_text, candidates)
    assert result.is_duplicate is False
    assert result.similarity_score < 0.50
    assert result.matched_feedback_id is None


def test_duplicate_detector_empty_and_whitespace_input():
    detector = DuplicateDetector(threshold=0.75)
    candidates = [{"id": "cand-1", "original_text": "Some text"}]

    res_empty = detector.detect("", candidates)
    assert res_empty.is_duplicate is False
    assert res_empty.similarity_score == 0.0

    res_ws = detector.detect("   ", candidates)
    assert res_ws.is_duplicate is False
    assert res_ws.similarity_score == 0.0


def test_duplicate_detector_no_candidates():
    detector = DuplicateDetector(threshold=0.75)
    result = detector.detect("OTP verification code is not delivered.", [])
    assert result.is_duplicate is False
    assert result.similarity_score == 0.0
    assert result.matched_feedback_id is None
