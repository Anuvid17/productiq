import pytest
from app.taxonomy.taxonomy_engine import TaxonomyEngine


@pytest.fixture
def engine():
    return TaxonomyEngine()


def test_taxonomy_loading(engine):
    taxonomy = engine.get_taxonomy()
    assert isinstance(taxonomy, dict)
    assert "version" in taxonomy
    assert "categories" in taxonomy
    assert "feedback_types" in taxonomy


def test_taxonomy_indexes(engine):
    assert len(engine.category_by_name) > 0
    assert "authentication" in engine.category_by_name
    assert "CAT001" in engine.category_by_id
    assert "otp verification" in engine.subcategory_by_name
    assert engine.subcategory_to_parent.get("otp verification") == "Authentication"


def test_category_subcategory_relationships(engine):
    categories = engine.get_categories()
    assert "Authentication" in categories

    subs = engine.get_subcategories("Authentication")
    assert "Login" in subs
    assert "OTP Verification" in subs

    parent = engine.get_parent_category("OTP Verification")
    assert parent == "Authentication"

    assert engine.is_valid_subcategory("Authentication", "OTP Verification") is True
    assert engine.is_valid_subcategory("Authentication", "Refunds") is False


def test_taxonomy_getters(engine):
    assert "Bug Report" in engine.get_feedback_types()
    assert "Critical" in engine.get_severity_levels()
    assert "P0" in engine.get_priority_levels()
    assert "All Users" in engine.get_impact_areas()
    assert "CREATE_BUG" in engine.get_agent_actions()
    assert "High" in engine.get_confidence_bands()
    assert "Backlog" in engine.get_roadmap_statuses()
    assert "Web" in engine.get_platforms()