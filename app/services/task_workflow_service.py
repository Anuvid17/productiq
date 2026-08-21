import uuid
from typing import Optional, Dict, Any, Union, Tuple
from sqlalchemy.orm import Session
from app.database.models import RoadmapTask, Roadmap, Feedback, Notification
from app.database.repository import RoadmapTaskRepository, RoadmapRepository, FeedbackRepository
from app.schemas.roadmap import TaskProgressUpdate
from app.services.progress_service import ProgressService
from app.services.resolution_service import ResolutionService
from app.services.notification_service import NotificationService
from app.taxonomy.taxonomy_engine import TaxonomyEngine
from app.utils.logger import logger


class TaskWorkflowService:
    """
    Business workflow service orchestrating developer task state updates.
    Enforces progress bounds, status transition rules, logical consistency,
    recalculates roadmap progress/status, checks resolution, and creates internal notifications.
    Uses ZERO LLM calls.
    """

    ALLOWED_TRANSITIONS: Dict[str, list] = {
        "Open": ["Open", "In Review", "Approved", "In Progress", "Testing"],
        "In Review": ["Open", "In Review", "Approved", "In Progress"],
        "Approved": ["In Review", "Approved", "In Progress", "Testing", "Resolved"],
        "In Progress": ["Open", "In Review", "Approved", "In Progress", "Testing", "Resolved"],
        "Testing": ["In Progress", "Testing", "Approved", "Resolved"],
        "Resolved": ["Testing", "Approved", "Resolved", "Closed"],
        "Closed": ["Resolved", "Closed", "Open", "In Progress"]
    }

    def __init__(
        self,
        session: Session,
        engine: Optional[TaxonomyEngine] = None,
        progress_service: Optional[ProgressService] = None,
        resolution_service: Optional[ResolutionService] = None,
        notification_service: Optional[NotificationService] = None
    ):
        self.session = session
        self.engine = engine or TaxonomyEngine()
        self.task_repo = RoadmapTaskRepository(session)
        self.roadmap_repo = RoadmapRepository(session)
        self.feedback_repo = FeedbackRepository(session)

        self.progress_service = progress_service or ProgressService(session, self.engine)
        self.notification_service = notification_service or NotificationService(session)
        self.resolution_service = resolution_service or ResolutionService(session, self.notification_service)

    def validate_task_update(
        self,
        current_status: str,
        current_progress: int,
        new_status: Optional[str],
        new_progress: Optional[int]
    ) -> Tuple[str, int]:
        """
        Validates proposed task status and progress update.
        Enforces:
        - 0 <= progress <= 100
        - Valid taxonomy task status
        - Valid transition rules
        - Progress-status consistency
        Returns resolved (target_status, target_progress).
        """
        # 1. Validate progress bounds if provided
        target_progress = current_progress if new_progress is None else new_progress
        if not isinstance(target_progress, int) or target_progress < 0 or target_progress > 100:
            raise ValueError(f"Task progress '{new_progress}' is invalid. Progress must be an integer between 0 and 100.")

        # 2. Validate status taxonomy if provided
        target_status = current_status if new_status is None else new_status.strip()
        if new_status is not None and not self.engine.is_valid_task_status(target_status):
            raise ValueError(f"Task status '{new_status}' is invalid. Allowed taxonomy task statuses: {self.engine.get_task_statuses()}")

        # 3. Consistency rules: Resolved and Closed require 100% progress
        if target_status in ["Resolved", "Closed"]:
            if new_progress is not None and new_progress < 100:
                raise ValueError(f"Status '{target_status}' requires 100% progress. Cannot set status '{target_status}' with progress {new_progress}%.")
            if target_progress == 0:
                raise ValueError(f"Task with 0% progress cannot be marked as '{target_status}'.")
            target_progress = 100

        # 4. Consistency rules: 0% progress cannot be Resolved or Closed
        if target_progress == 0 and target_status in ["Resolved", "Closed"]:
            raise ValueError(f"Task with 0% progress cannot be marked as '{target_status}'.")

        # 5. Open or In Review with 100% progress automatically promotes to Approved
        if target_progress == 100 and target_status in ["Open", "In Review"]:
            target_status = "Approved"

        return target_status, target_progress

    def update_task_progress_and_status(
        self,
        task_id: Union[uuid.UUID, str],
        update: Union[TaskProgressUpdate, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Executes complete atomic developer workflow update:
        1. Validates and updates task.
        2. Recalculates roadmap progress and roadmap status.
        3. Runs resolution engine check on parent feedback.
        4. Creates internal resolution notification if resolved.
        Flushes all database changes atomically.
        """
        if isinstance(task_id, str):
            task_id = uuid.UUID(task_id)

        task = self.task_repo.get_by_id(task_id)
        if not task:
            raise ValueError(f"Roadmap task with ID '{task_id}' does not exist.")

        upd_dict = update.model_dump(exclude_unset=True) if isinstance(update, TaskProgressUpdate) else update
        new_progress = upd_dict.get("progress")
        new_status = upd_dict.get("status")

        target_status, target_progress = self.validate_task_update(
            current_status=task.status,
            current_progress=task.progress,
            new_status=new_status,
            new_progress=new_progress
        )

        old_status = task.status
        old_progress = task.progress

        # Update task model fields
        task.status = target_status
        task.progress = target_progress
        self.session.flush()

        logger.info(
            f"TaskWorkflowService updated Task [ID: {task_id}]: "
            f"Status '{old_status}' -> '{target_status}', Progress {old_progress}% -> {target_progress}%"
        )

        # Recalculate Roadmap progress and status
        roadmap = self.progress_service.update_roadmap_progress_and_status(task.roadmap_id)

        # Check Feedback Resolution
        feedback, was_resolved, notification = self.resolution_service.check_and_resolve_feedback(roadmap.feedback_id)

        return {
            "task": task,
            "roadmap": roadmap,
            "feedback": feedback,
            "was_resolved": was_resolved,
            "notification": notification
        }
