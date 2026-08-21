import pytest
from app.taxonomy.taxonomy_engine import TaxonomyEngine
from app.taxonomy.taxonomy_formatter import TaxonomyFormatter


def test_formatter_output():
    engine = TaxonomyEngine()
    formatter = TaxonomyFormatter(engine)
    formatted = formatter.format()

    assert isinstance(formatted, str)
    assert "========== FEEDBACK TYPES ==========" in formatted
    assert "========== CATEGORIES ==========" in formatted
    assert "========== BUG CATEGORIES ==========" in formatted
    assert "========== SEVERITY ==========" in formatted
    assert "========== PRIORITY ==========" in formatted
    assert "========== IMPACT ==========" in formatted
    assert "========== ACTIONS ==========" in formatted
    assert "========== CONFIDENCE ==========" in formatted
    assert "========== ROADMAP STATUS ==========" in formatted
    assert "========== EFFORT ==========" in formatted
    assert "========== PLATFORMS ==========" in formatted
    assert "========== STATUS ==========" in formatted
    assert "Authentication" in formatted
    assert "• OTP Verification" in formatted