import uuid
from typing import Optional, List, Dict, Any, Union
from sqlalchemy.orm import Session
from app.database.models import Roadmap, RoadmapTask
from app.database.repository import RoadmapRepository, RoadmapTaskRepository
from app.taxonomy.taxonomy_engine import TaxonomyEngine
from app.utils.logger import logger


class ProgressService:
    """
    Service handling deterministic roadmap progress math and roadmap status updates.
    Does NOT use LLMs or external calls.
    """

    def __init__(self, session: Optional[Session] = None, engine: Optional[TaxonomyEngine] = None):
        self.session = session
        self.engine = engine or TaxonomyEngine()
        self.roadmap_repo = RoadmapRepository(session) if session else None
        self.task_repo = RoadmapTaskRepository(session) if session else None

    @staticmethod
    def calculate_progress(tasks: List[Union[RoadmapTask, Dict[str, Any]]]) -> int:
        """
        Calculates overall roadmap progress deterministically from task progress values.
        Formula: round(sum(task_progress) / count).
        Returns integer between 0 and 100.
        """
        if not tasks:
            return 0

        total_progress = 0
        for t in tasks:
            p = getattr(t, "progress", None) if hasattr(t, "progress") else (t.get("progress") if isinstance(t, dict) else 0)
            p = max(0, min(100, int(p or 0)))
            total_progress += p

        avg_progress = round(total_progress / len(tasks))
        return max(0, min(100, int(avg_progress)))

    def calculate_roadmap_status(self, tasks: List[Union[RoadmapTask, Dict[str, Any]]]) -> str:
        """
        Calculates roadmap status deterministically based on task progress and task statuses.
        Uses taxonomy-approved roadmap statuses: Backlog, Planned, In Progress, Testing, Released.
        """
        if not tasks:
            return "Backlog"

        progresses = []
        statuses = []

        for t in tasks:
            p = getattr(t, "progress", None) if hasattr(t, "progress") else (t.get("progress") if isinstance(t, dict) else 0)
            s = getattr(t, "status", None) if hasattr(t, "status") else (t.get("status") if isinstance(t, dict) else "Open")
            progresses.append(max(0, min(100, int(p or 0))))
            statuses.append(str(s or "Open").strip())

        # 1. All tasks 100% progress and in Resolved or Closed status -> Released
        if all(p == 100 for p in progresses) and all(s in ["Resolved", "Closed"] for s in statuses):
            return "Released"

        # 2. All tasks 100% progress, but some tasks are in Testing / Approved / In Review state -> Testing
        if all(p == 100 for p in progresses):
            return "Testing"

        # 3. All tasks 0% progress
        if all(p == 0 for p in progresses):
            if any(s in ["Planned", "Approved", "In Review"] for s in statuses):
                return "Planned"
            return "Backlog"

        # 4. Mixed work in progress
        return "In Progress"

    def update_roadmap_progress_and_status(self, roadmap_id: Union[uuid.UUID, str]) -> Roadmap:
        """
        Retrieves all tasks for roadmap_id, recalculates progress and status,
        updates the Roadmap record in the active database session.
        """
        if not self.session or not self.roadmap_repo or not self.task_repo:
            raise ValueError("Session is required for database operations in ProgressService.")

        if isinstance(roadmap_id, str):
            roadmap_id = uuid.UUID(roadmap_id)

        roadmap = self.roadmap_repo.get_by_id(roadmap_id)
        if not roadmap:
            raise ValueError(f"Roadmap with ID '{roadmap_id}' does not exist.")

        tasks = self.task_repo.list_by_roadmap(roadmap_id)

        new_progress = self.calculate_progress(tasks)
        new_status = self.calculate_roadmap_status(tasks)

        roadmap.progress = new_progress
        roadmap.status = new_status
        self.session.flush()

        logger.info(
            f"ProgressService recalculated Roadmap [ID: {roadmap_id}]: "
            f"Progress={new_progress}%, Status='{new_status}' across {len(tasks)} tasks."
        )
        return roadmap
