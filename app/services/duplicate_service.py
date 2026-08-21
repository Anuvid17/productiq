from typing import Optional
from sqlalchemy.orm import Session
from app.database.repository import FeedbackRepository
from app.agents.duplicate_detector import DuplicateDetector
from app.schemas.duplicate import DuplicateCheckResult
from app.utils.logger import logger


class DuplicateService:
    """
    Business service bridging repository persistence queries and DuplicateDetector logic.
    Retrieves candidates from database layer and delegates similarity calculation to DuplicateDetector.
    """

    def __init__(self, session: Session, detector: Optional[DuplicateDetector] = None):
        self.session = session
        self.repository = FeedbackRepository(session)
        self.detector = detector or DuplicateDetector()

    def check_duplicate(
        self,
        new_text: str,
        feedback_type: Optional[str] = None,
        category: Optional[str] = None,
        subcategory: Optional[str] = None
    ) -> DuplicateCheckResult:
        logger.info(f"DuplicateService retrieving candidates for check (Text length: {len(new_text)})")
        candidates = self.repository.find_feedback_candidates(feedback_type=feedback_type, category=category)
        logger.info(f"Retrieved {len(candidates)} candidate feedback records for similarity comparison.")

        metadata = {
            "feedback_type": feedback_type,
            "category": category,
            "subcategory": subcategory
        }

        result = self.detector.detect(new_text, candidates, new_metadata=metadata)
        logger.info(f"Duplicate check result: is_duplicate={result.is_duplicate}, score={result.similarity_score}")
        return result
