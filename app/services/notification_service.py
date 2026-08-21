import uuid
from typing import Optional, List, Union
from sqlalchemy.orm import Session
from app.database.models import Notification
from app.database.repository import NotificationRepository, FeedbackRepository
from app.schemas.notification import NotificationCreate
from app.utils.logger import logger


class NotificationService:
    """
    Internal notification service managing persistent notification records.
    Does NOT connect to external email, Slack, or push services.
    Enforces duplicate prevention for resolution notifications.
    """

    def __init__(self, session: Session):
        self.session = session
        self.repository = NotificationRepository(session)
        self.feedback_repo = FeedbackRepository(session)

    def create_notification(
        self,
        feedback_id: Union[uuid.UUID, str],
        message: str,
        notification_type: str = "RESOLUTION"
    ) -> Notification:
        if isinstance(feedback_id, str):
            feedback_id = uuid.UUID(feedback_id)

        feedback = self.feedback_repo.get_by_id(feedback_id)
        if not feedback:
            raise ValueError(f"Feedback with ID '{feedback_id}' does not exist.")

        notif = self.repository.create(
            feedback_id=feedback_id,
            message=message,
            notification_type=notification_type
        )
        logger.info(f"Notification created [ID: {notif.id}, Type: {notification_type}] for Feedback {feedback_id}")
        return notif

    def create_resolution_notification(
        self,
        feedback_id: Union[uuid.UUID, str],
        custom_message: Optional[str] = None
    ) -> Optional[Notification]:
        """
        Creates an internal resolution notification.
        Prevents creating duplicate resolution notifications for the same feedback record.
        """
        if isinstance(feedback_id, str):
            feedback_id = uuid.UUID(feedback_id)

        # Check for duplicate resolution notification
        existing_notifications = self.repository.list(feedback_id=feedback_id)
        for n in existing_notifications:
            if n.notification_type == "RESOLUTION":
                logger.info(f"Resolution notification already exists for Feedback {feedback_id}. Skipping creation.")
                return n

        msg = custom_message or "Your reported issue has been resolved. You can now check the fix."
        return self.create_notification(
            feedback_id=feedback_id,
            message=msg,
            notification_type="RESOLUTION"
        )

    def get_notifications(
        self,
        feedback_id: Optional[Union[uuid.UUID, str]] = None,
        unread_only: bool = False,
        limit: int = 50,
        offset: int = 0
    ) -> List[Notification]:
        return self.repository.list(
            feedback_id=feedback_id,
            unread_only=unread_only,
            limit=limit,
            offset=offset
        )

    def mark_as_read(self, notification_id: Union[uuid.UUID, str]) -> Optional[Notification]:
        return self.repository.mark_as_read(notification_id)
