import pytest
from app.taxonomy.taxonomy_engine import TaxonomyEngine
from app.taxonomy.taxonomy_mapper import TaxonomyMapper


@pytest.fixture
def mapper():
    engine = TaxonomyEngine()
    return TaxonomyMapper(engine)


def test_category_mapper_lookups(mapper):
    cat_id = mapper.category_to_id("Authentication")
    assert cat_id == "CAT001"

    cat_name = mapper.category_id_to_name("CAT001")
    assert cat_name == "Authentication"


def test_subcategory_mapper_lookups(mapper):
    sub_id = mapper.subcategory_to_id("OTP Verification")
    assert sub_id == "AUTH003"

    sub_name = mapper.subcategory_id_to_name("AUTH003")
    assert sub_name == "OTP Verification"


def test_feedback_type_mapper_lookups(mapper):
    ft_id = mapper.feedback_type_to_id("Bug Report")
    assert ft_id == "FT002"

    ft_name = mapper.feedback_type_id_to_name("FT002")
    assert ft_name == "Bug Report"


def test_bug_category_mapper_lookup(mapper):
    bug_id = mapper.bug_category_to_id("Functional Bug")
    assert bug_id == "Functional Bug"

    invalid_bug = mapper.bug_category_to_id("Nonexistent Bug")
    assert invalid_bug is None


def test_parent_category_lookup(mapper):
    parent = mapper.get_parent_category("OTP Verification")
    assert parent == "Authentication"