import uuid
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete
from app.database.models import Feedback, Roadmap, RoadmapTask, Notification


class FeedbackRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, original_text: str, **kwargs) -> Feedback:
        feedback = Feedback(original_text=original_text, **kwargs)
        self.session.add(feedback)
        self.session.flush()
        return feedback

    def get_by_id(self, feedback_id: uuid.UUID | str) -> Optional[Feedback]:
        if isinstance(feedback_id, str):
            feedback_id = uuid.UUID(feedback_id)
        stmt = select(Feedback).where(Feedback.id == feedback_id)
        return self.session.scalar(stmt)

    def list(
        self,
        status: Optional[str] = None,
        category: Optional[str] = None,
        feedback_type: Optional[str] = None,
        priority: Optional[str] = None,
        severity: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Feedback]:
        stmt = select(Feedback)
        if status:
            stmt = stmt.where(Feedback.status == status)
        if category:
            stmt = stmt.where(Feedback.category == category)
        if feedback_type:
            stmt = stmt.where(Feedback.feedback_type == feedback_type)
        if priority:
            stmt = stmt.where(Feedback.priority == priority)
        if severity:
            stmt = stmt.where(Feedback.severity == severity)
        if search:
            stmt = stmt.where(Feedback.original_text.ilike(f"%{search}%"))
        stmt = stmt.order_by(Feedback.created_at.desc()).offset(offset).limit(limit)
        return list(self.session.scalars(stmt).all())

    def count(
        self,
        status: Optional[str] = None,
        category: Optional[str] = None,
        feedback_type: Optional[str] = None,
        priority: Optional[str] = None,
        severity: Optional[str] = None,
        search: Optional[str] = None
    ) -> int:
        from sqlalchemy import func
        stmt = select(func.count(Feedback.id))
        if status:
            stmt = stmt.where(Feedback.status == status)
        if category:
            stmt = stmt.where(Feedback.category == category)
        if feedback_type:
            stmt = stmt.where(Feedback.feedback_type == feedback_type)
        if priority:
            stmt = stmt.where(Feedback.priority == priority)
        if severity:
            stmt = stmt.where(Feedback.severity == severity)
        if search:
            stmt = stmt.where(Feedback.original_text.ilike(f"%{search}%"))
        return self.session.scalar(stmt) or 0

    def find_feedback_candidates(
        self,
        feedback_type: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 100
    ) -> List[Feedback]:
        stmt = select(Feedback)
        if feedback_type:
            stmt = stmt.where(Feedback.feedback_type == feedback_type)
        if category:
            stmt = stmt.where(Feedback.category == category)
        stmt = stmt.order_by(Feedback.created_at.desc()).limit(limit)
        results = list(self.session.scalars(stmt).all())
        # If filtered query returns empty set, fallback to general candidates
        if not results:
            stmt = select(Feedback).order_by(Feedback.created_at.desc()).limit(limit)
            results = list(self.session.scalars(stmt).all())
        return results


    def update(self, feedback_id: uuid.UUID | str, **kwargs) -> Optional[Feedback]:
        feedback = self.get_by_id(feedback_id)
        if not feedback:
            return None
        for key, value in kwargs.items():
            if hasattr(feedback, key) and value is not None:
                setattr(feedback, key, value)
        self.session.flush()
        return feedback

    def delete(self, feedback_id: uuid.UUID | str) -> bool:
        feedback = self.get_by_id(feedback_id)
        if not feedback:
            return False
        self.session.delete(feedback)
        self.session.flush()
        return True


class RoadmapRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, feedback_id: uuid.UUID | str, title: str, **kwargs) -> Roadmap:
        if isinstance(feedback_id, str):
            feedback_id = uuid.UUID(feedback_id)
        roadmap = Roadmap(feedback_id=feedback_id, title=title, **kwargs)
        self.session.add(roadmap)
        self.session.flush()
        return roadmap

    def get_by_id(self, roadmap_id: uuid.UUID | str) -> Optional[Roadmap]:
        if isinstance(roadmap_id, str):
            roadmap_id = uuid.UUID(roadmap_id)
        stmt = select(Roadmap).where(Roadmap.id == roadmap_id)
        return self.session.scalar(stmt)

    def get_by_feedback_id(self, feedback_id: uuid.UUID | str) -> Optional[Roadmap]:
        if isinstance(feedback_id, str):
            feedback_id = uuid.UUID(feedback_id)
        stmt = select(Roadmap).where(Roadmap.feedback_id == feedback_id)
        return self.session.scalar(stmt)

    def list(self, status: Optional[str] = None, limit: int = 50, offset: int = 0) -> List[Roadmap]:
        stmt = select(Roadmap)
        if status:
            stmt = stmt.where(Roadmap.status == status)
        stmt = stmt.order_by(Roadmap.created_at.desc()).offset(offset).limit(limit)
        return list(self.session.scalars(stmt).all())

    def update(self, roadmap_id: uuid.UUID | str, **kwargs) -> Optional[Roadmap]:
        roadmap = self.get_by_id(roadmap_id)
        if not roadmap:
            return None
        for key, value in kwargs.items():
            if hasattr(roadmap, key) and value is not None:
                setattr(roadmap, key, value)
        self.session.flush()
        return roadmap


class RoadmapTaskRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, roadmap_id: uuid.UUID | str, title: str, **kwargs) -> RoadmapTask:
        if isinstance(roadmap_id, str):
            roadmap_id = uuid.UUID(roadmap_id)
        task = RoadmapTask(roadmap_id=roadmap_id, title=title, **kwargs)
        self.session.add(task)
        self.session.flush()
        return task

    def get_by_id(self, task_id: uuid.UUID | str) -> Optional[RoadmapTask]:
        if isinstance(task_id, str):
            task_id = uuid.UUID(task_id)
        stmt = select(RoadmapTask).where(RoadmapTask.id == task_id)
        return self.session.scalar(stmt)

    def list_by_roadmap(self, roadmap_id: uuid.UUID | str) -> List[RoadmapTask]:
        if isinstance(roadmap_id, str):
            roadmap_id = uuid.UUID(roadmap_id)
        stmt = select(RoadmapTask).where(RoadmapTask.roadmap_id == roadmap_id).order_by(RoadmapTask.created_at.asc())
        return list(self.session.scalars(stmt).all())

    def update(self, task_id: uuid.UUID | str, **kwargs) -> Optional[RoadmapTask]:
        task = self.get_by_id(task_id)
        if not task:
            return None
        for key, value in kwargs.items():
            if hasattr(task, key) and value is not None:
                setattr(task, key, value)
        self.session.flush()
        return task


class NotificationRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, feedback_id: uuid.UUID | str, message: str, notification_type: str, **kwargs) -> Notification:
        if isinstance(feedback_id, str):
            feedback_id = uuid.UUID(feedback_id)
        notif = Notification(
            feedback_id=feedback_id,
            message=message,
            notification_type=notification_type,
            **kwargs
        )
        self.session.add(notif)
        self.session.flush()
        return notif

    def get_by_id(self, notification_id: uuid.UUID | str) -> Optional[Notification]:
        if isinstance(notification_id, str):
            notification_id = uuid.UUID(notification_id)
        stmt = select(Notification).where(Notification.id == notification_id)
        return self.session.scalar(stmt)

    def list(
        self,
        feedback_id: Optional[uuid.UUID | str] = None,
        unread_only: bool = False,
        limit: int = 50,
        offset: int = 0
    ) -> List[Notification]:
        stmt = select(Notification)
        if feedback_id:
            if isinstance(feedback_id, str):
                feedback_id = uuid.UUID(feedback_id)
            stmt = stmt.where(Notification.feedback_id == feedback_id)
        if unread_only:
            stmt = stmt.where(Notification.read == False)
        stmt = stmt.order_by(Notification.created_at.desc()).offset(offset).limit(limit)
        return list(self.session.scalars(stmt).all())

    def mark_as_read(self, notification_id: uuid.UUID | str) -> Optional[Notification]:
        notif = self.get_by_id(notification_id)
        if notif:
            notif.read = True
            self.session.flush()
        return notif
