import pytest
from app.taxonomy.taxonomy_engine import TaxonomyEngine
from app.taxonomy.taxonomy_validator import TaxonomyValidator, TaxonomyValidationError


@pytest.fixture
def validator():
    engine = TaxonomyEngine()
    return TaxonomyValidator(engine)


def test_validator_valid_input(validator):
    valid_sample = {
        "summary": "OTP code email never arrives during login.",
        "feedback_type": "Bug Report",
        "category": "Authentication",
        "subcategory": "OTP Verification",
        "bug_category": "Functional Bug",
        "severity": "Critical",
        "priority": "P0",
        "impact_area": "All Users",
        "platform": "Web",
        "recommended_action": "CREATE_BUG",
        "confidence": "High"
    }

    assert validator.validate(valid_sample) is True
    res = validator.validate_structured(valid_sample)
    assert res.is_valid is True
    assert len(res.errors) == 0


def test_validator_invalid_input(validator):
    invalid_sample = {
        "summary": "Sample issue.",
        "feedback_type": "Invalid Type",
        "category": "Nonexistent Category",
        "subcategory": "OTP Verification",
        "bug_category": "Fake Bug Cat",
        "severity": "Ultra High",
        "priority": "P99",
        "impact_area": "Nobody",
        "platform": "SmartFridge",
        "recommended_action": "DO_NOTHING",
        "confidence": "Extreme"
    }

    with pytest.raises(TaxonomyValidationError) as excinfo:
        validator.validate(invalid_sample)

    errors = excinfo.value.errors
    assert len(errors) > 1

    res = validator.validate_structured(invalid_sample)
    assert res.is_valid is False
    assert len(res.errors) >= 7


def test_validator_relationship_mismatch(validator):
    mismatch_sample = {
        "feedback_type": "Bug Report",
        "category": "Authentication",
        "subcategory": "Refunds",  # Refunds belongs to "Billing & Subscription", not "Authentication"
        "severity": "Critical",
        "priority": "P0",
        "impact_area": "All Users",
        "platform": "Web",
        "recommended_action": "CREATE_BUG",
        "confidence": "High"
    }

    with pytest.raises(TaxonomyValidationError) as excinfo:
        validator.validate(mismatch_sample)

    assert any("does not belong to" in err for err in excinfo.value.errors)