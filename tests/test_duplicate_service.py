import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.db import Base
from app.database.repository import FeedbackRepository
from app.services.duplicate_service import DuplicateService


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


def test_duplicate_service_with_database(db_session):
    repo = FeedbackRepository(db_session)
    rec1 = repo.create(
        original_text="OTP verification code fails to arrive in email inbox.",
        feedback_type="Bug Report",
        category="Authentication",
        subcategory="OTP Verification"
    )
    db_session.commit()

    service = DuplicateService(session=db_session)

    # Search with similar text
    dup_res = service.check_duplicate(
        new_text="OTP verification code fails to arrive in email inbox.",
        feedback_type="Bug Report",
        category="Authentication"
    )

    assert dup_res.is_duplicate is True
    assert dup_res.matched_feedback_id == str(rec1.id)
    assert dup_res.similarity_score >= 0.90
