from typing import Dict, Any, Optional, List
from app.taxonomy.taxonomy_engine import TaxonomyEngine


class RoadmapValidationError(ValueError):
    """Raised when generated roadmap fails taxonomy or structural rules."""
    pass


class RoadmapValidator:
    """
    Validates LLM-generated developer roadmap structure, task completeness,
    effort levels, progress ranges, and acceptance criteria.
    """

    def __init__(self, engine: Optional[TaxonomyEngine] = None):
        self.engine = engine or TaxonomyEngine()

    def validate(self, roadmap_data: Dict[str, Any]) -> None:
        if not isinstance(roadmap_data, dict):
            raise RoadmapValidationError("Roadmap data must be a valid JSON dictionary object.")

        title = roadmap_data.get("title")
        if not title or not isinstance(title, str) or not title.strip():
            raise RoadmapValidationError("Roadmap 'title' is required and must be a non-empty string.")

        status = roadmap_data.get("status")
        valid_statuses = set(x.lower() for x in self.engine.get_roadmap_statuses())
        if not status or status.lower() not in valid_statuses:
            raise RoadmapValidationError(
                f"Invalid roadmap status '{status}'. Allowed values: {self.engine.get_roadmap_statuses()}"
            )

        effort = roadmap_data.get("effort")
        valid_efforts = set(x.lower() for x in self.engine.get_effort_levels())
        if not effort or effort.lower() not in valid_efforts:
            raise RoadmapValidationError(
                f"Invalid roadmap effort level '{effort}'. Allowed values: {self.engine.get_effort_levels()}"
            )

        progress = roadmap_data.get("progress")
        if progress is None or not isinstance(progress, (int, float)) or not (0 <= progress <= 100):
            raise RoadmapValidationError(f"Invalid roadmap progress '{progress}'. Must be an integer between 0 and 100.")

        tasks = roadmap_data.get("tasks")
        if not tasks or not isinstance(tasks, list) or len(tasks) == 0:
            raise RoadmapValidationError("Roadmap must contain a non-empty list of developer tasks.")

        for idx, task in enumerate(tasks, start=1):
            if not isinstance(task, dict):
                raise RoadmapValidationError(f"Task #{idx} must be a dictionary object.")

            task_title = task.get("title")
            if not task_title or not isinstance(task_title, str) or not task_title.strip():
                raise RoadmapValidationError(f"Task #{idx} 'title' is required.")

            task_effort = task.get("effort")
            if not task_effort or task_effort.lower() not in valid_efforts:
                raise RoadmapValidationError(
                    f"Task #{idx} invalid effort '{task_effort}'. Allowed values: {self.engine.get_effort_levels()}"
                )

            task_progress = task.get("progress")
            if task_progress is None or not isinstance(task_progress, (int, float)) or not (0 <= task_progress <= 100):
                raise RoadmapValidationError(f"Task #{idx} invalid progress '{task_progress}'. Must be between 0 and 100.")

            criteria = task.get("acceptance_criteria")
            if not criteria or not isinstance(criteria, list) or len(criteria) == 0:
                raise RoadmapValidationError(f"Task #{idx} ('{task_title}') must contain non-empty acceptance criteria.")
