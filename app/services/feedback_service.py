from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from app.database.models import Feedback, Roadmap
from app.database.repository import FeedbackRepository
from app.agents.feedback_agent import FeedbackAgent
from app.agents.decision_engine import DecisionEngine
from app.services.duplicate_service import DuplicateService
from app.services.roadmap_service import RoadmapService
from app.schemas.duplicate import DuplicateCheckResult
from app.utils.logger import logger


class FeedbackService:
    """
    Business service orchestrating the complete ProductIQ intelligence pipeline:
    FeedbackAgent -> DuplicateService -> DecisionEngine -> Database Persistence -> RoadmapService.
    """

    def __init__(
        self,
        session: Session,
        agent: Optional[FeedbackAgent] = None,
        duplicate_service: Optional[DuplicateService] = None,
        decision_engine: Optional[DecisionEngine] = None,
        roadmap_service: Optional[RoadmapService] = None
    ):
        self.session = session
        self.repository = FeedbackRepository(session)
        self.agent = agent or FeedbackAgent()
        self.duplicate_service = duplicate_service or DuplicateService(session)
        self.decision_engine = decision_engine or DecisionEngine()
        self.roadmap_service = roadmap_service or RoadmapService(session)

    def process_and_store_feedback(
        self,
        raw_text: str,
        platform: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Runs complete ProductIQ analysis pipeline on raw customer feedback:
        1. AI Classification via FeedbackAgent.
        2. Candidate retrieval and TF-IDF duplicate detection via DuplicateService.
        3. DecisionEngine rule resolution.
        4. Feedback record persistence.
        5. Developer Roadmap + Task generation if new item.
        """
        logger.info(f"Processing new feedback item ({len(raw_text)} chars)")

        # 1. AI Analysis via FeedbackAgent
        analysis = self.agent.analyze(raw_text, platform=platform)

        # 2. Duplicate Detection via DuplicateService
        dup_result = self.duplicate_service.check_duplicate(
            new_text=raw_text,
            feedback_type=analysis.feedback_type,
            category=analysis.category,
            subcategory=analysis.subcategory
        )

        # 3. Decision Engine Processing
        triaged_data = self.decision_engine.process(analysis, input_platform=platform)

        # If duplicate detected, adjust recommended action if appropriate
        action = triaged_data["recommended_action"]
        if dup_result.is_duplicate and dup_result.matched_feedback_id:
            if triaged_data["feedback_type"] == "Bug Report":
                action = "LINK_BUG"
            elif triaged_data["feedback_type"] == "Feature Request":
                action = "LINK_FEATURE"
            else:
                action = "MERGE_DUPLICATE"

        # 4. Database Persistence for Feedback record
        status_val = "Linked" if dup_result.is_duplicate else "Triaged"
        feedback_record = self.repository.create(
            original_text=raw_text,
            summary=triaged_data["summary"],
            feedback_type=triaged_data["feedback_type"],
            category=triaged_data["category"],
            subcategory=triaged_data["subcategory"],
            bug_category=triaged_data["bug_category"],
            severity=triaged_data["severity"],
            priority=triaged_data["priority"],
            impact_area=triaged_data["impact_area"],
            platform=triaged_data["platform"],
            recommended_action=action,
            confidence=triaged_data["confidence"],
            status=status_val
        )

        # 5. Roadmap Generation
        roadmap_record: Optional[Roadmap] = None
        tasks_list = []
        try:
            roadmap_record = self.roadmap_service.create_roadmap_for_feedback(
                feedback_id=feedback_record.id,
                analysis=analysis,
                feedback_text=raw_text
            )
            tasks_list = self.roadmap_service.task_repo.list_by_roadmap(roadmap_record.id)
        except Exception as rm_err:
            logger.error(f"Roadmap creation error: {rm_err}. Attempting fallback roadmap.")
            if dup_result.matched_feedback_id:
                roadmap_repo = RoadmapRepository(self.session)
                rm_parent = roadmap_repo.get_by_feedback_id(dup_result.matched_feedback_id)
                if rm_parent:
                    roadmap_record = rm_parent
                    tasks_list = self.roadmap_service.task_repo.list_by_roadmap(rm_parent.id)

        self.session.commit()

        logger.info(f"Successfully processed feedback pipeline [Feedback ID: {feedback_record.id}]")
        return {
            "feedback": feedback_record,
            "duplicate_result": dup_result,
            "roadmap": roadmap_record,
            "tasks": tasks_list,
            "action": action
        }
