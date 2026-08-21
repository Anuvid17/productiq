import uuid
from typing import Optional, List, Dict, Any, Union
from sqlalchemy.orm import Session

from app.database.models import Roadmap, RoadmapTask
from app.database.repository import RoadmapRepository, RoadmapTaskRepository
from app.agents.roadmap_agent import RoadmapAgent
from app.schemas.agent import FeedbackAnalysis
from app.taxonomy.taxonomy_engine import TaxonomyEngine
from app.utils.logger import logger


class RoadmapService:
    """
    Service layer handling developer roadmap generation, deterministic progress math,
    status calculation, and transactional database persistence.
    """

    def __init__(
        self,
        session: Session,
        agent: Optional[RoadmapAgent] = None,
        engine: Optional[TaxonomyEngine] = None
    ):
        self.session = session
        self.roadmap_repo = RoadmapRepository(session)
        self.task_repo = RoadmapTaskRepository(session)
        self.agent = agent or RoadmapAgent()
        self.engine = engine or TaxonomyEngine()

    @staticmethod
    def calculate_progress(tasks: List[Union[RoadmapTask, Dict[str, Any]]]) -> int:
        """
        Calculates overall roadmap progress deterministically from task progress.
        Formula: round(sum(task_progress) / count).
        Returns integer between 0 and 100.
        """
        if not tasks:
            return 0

        total_progress = 0
        for t in tasks:
            p = getattr(t, "progress", None) if hasattr(t, "progress") else t.get("progress", 0)
            p = max(0, min(100, int(p or 0)))
            total_progress += p

        avg_progress = round(total_progress / len(tasks))
        return max(0, min(100, int(avg_progress)))

    def calculate_roadmap_status(self, tasks: List[Union[RoadmapTask, Dict[str, Any]]]) -> str:
        """
        Calculates roadmap status deterministically from task progress states.
        """
        if not tasks:
            return "Backlog"

        progresses = []
        for t in tasks:
            p = getattr(t, "progress", None) if hasattr(t, "progress") else t.get("progress", 0)
            progresses.append(int(p or 0))

        if all(p == 0 for p in progresses):
            return "Backlog"
        elif all(p == 100 for p in progresses):
            return "Released"
        else:
            return "In Progress"

    def create_roadmap_for_feedback(
        self,
        feedback_id: Union[uuid.UUID, str],
        analysis: Union[FeedbackAnalysis, Dict[str, Any]],
        feedback_text: str
    ) -> Roadmap:
        """
        Generates via RoadmapAgent and persists Roadmap + Tasks atomically in a single transaction.
        """
        if isinstance(feedback_id, str):
            feedback_id = uuid.UUID(feedback_id)

        logger.info(f"Creating developer roadmap for Feedback [ID: {feedback_id}]")

        # 1. Generate via LLM agent (no DB writes)
        raw_roadmap = self.agent.generate_roadmap(analysis, feedback_text)

        # 2. Extract tasks and enforce initial 0 progress
        task_data_list = raw_roadmap.get("tasks", [])
        initial_progress = 0
        initial_status = "Backlog"

        # 3. Save Roadmap parent record
        roadmap_record = self.roadmap_repo.create(
            feedback_id=feedback_id,
            title=raw_roadmap.get("title", "Feedback Action Roadmap"),
            description=raw_roadmap.get("description", ""),
            status=initial_status,
            effort=raw_roadmap.get("effort", "M"),
            progress=initial_progress
        )

        # 4. Save RoadmapTask child records
        created_tasks = []
        for t_data in task_data_list:
            task_rec = self.task_repo.create(
                roadmap_id=roadmap_record.id,
                title=t_data.get("title"),
                description=t_data.get("description", ""),
                effort=t_data.get("effort", "M"),
                status=t_data.get("status", "Open"),
                progress=0,
                dependencies=t_data.get("dependencies", []),
                acceptance_criteria=t_data.get("acceptance_criteria", [])
            )
            created_tasks.append(task_rec)

        self.session.flush()
        logger.info(
            f"Successfully persisted Roadmap [ID: {roadmap_record.id}] with {len(created_tasks)} tasks."
        )
        return roadmap_record
