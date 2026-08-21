import uuid
from typing import Optional, List, Union
from sqlalchemy.orm import Session
from app.database.models import Feedback, Roadmap, RoadmapTask, Notification
from app.database.repository import FeedbackRepository, RoadmapRepository, RoadmapTaskRepository
from app.services.notification_service import NotificationService
from app.utils.logger import logger


class ResolutionService:
    """
    Service responsible for resolution detection and feedback status updates.
    Enforces that feedback is marked 'Resolved' ONLY when roadmap status is 'Released'
    and all tasks have 100% progress and are in 'Resolved' or 'Closed' state.
    Triggers creation of internal resolution notifications.
    """

    def __init__(
        self,
        session: Session,
        notification_service: Optional[NotificationService] = None
    ):
        self.session = session
        self.feedback_repo = FeedbackRepository(session)
        self.roadmap_repo = RoadmapRepository(session)
        self.task_repo = RoadmapTaskRepository(session)
        self.notification_service = notification_service or NotificationService(session)

    def is_roadmap_fully_resolved(self, roadmap: Roadmap, tasks: List[RoadmapTask]) -> bool:
        """
        Determines whether a roadmap meets resolution criteria.
        Criteria:
        1. Roadmap status is 'Released'
        2. All tasks have progress == 100
        3. All tasks have status in ['Resolved', 'Closed']
        """
        if not roadmap or roadmap.status != "Released":
            return False

        if not tasks:
            return False

        for t in tasks:
            if t.progress < 100 or t.status not in ["Resolved", "Closed"]:
                return False

        return True

    def check_and_resolve_feedback(
        self,
        feedback_id: Union[uuid.UUID, str]
    ) -> tuple[Feedback, bool, Optional[Notification]]:
        """
        Inspects feedback's roadmap and tasks.
        If resolution criteria are satisfied:
        1. Sets Feedback.status = 'Resolved'
        2. Creates internal resolution notification (with duplicate prevention)
        Returns tuple of (Feedback, was_resolved, Notification)
        """
        if isinstance(feedback_id, str):
            feedback_id = uuid.UUID(feedback_id)

        feedback = self.feedback_repo.get_by_id(feedback_id)
        if not feedback:
            raise ValueError(f"Feedback with ID '{feedback_id}' does not exist.")

        roadmap = self.roadmap_repo.get_by_feedback_id(feedback_id)
        if not roadmap:
            logger.info(f"Feedback {feedback_id} has no associated roadmap. Resolution check skipped.")
            return feedback, False, None

        tasks = self.task_repo.list_by_roadmap(roadmap.id)

        if self.is_roadmap_fully_resolved(roadmap, tasks):
            if feedback.status != "Resolved":
                feedback.status = "Resolved"
                self.session.flush()
                logger.info(f"ResolutionEngine marked Feedback [ID: {feedback_id}] as Resolved.")

            notification = self.notification_service.create_resolution_notification(feedback_id)
            return feedback, True, notification

        logger.info(f"ResolutionEngine check for Feedback {feedback_id}: Criteria not met yet.")
        return feedback, False, None
