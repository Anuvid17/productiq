from typing import Dict
from pydantic import BaseModel, ConfigDict


class DashboardSummaryRead(BaseModel):
    total_feedback: int
    open_feedback: int
    resolved_feedback: int
    critical_blocker_issues: int
    feature_requests: int
    bug_reports: int
    active_roadmaps: int
    average_roadmap_progress: float
    resolution_rate: float
    feedback_by_type: Dict[str, int]
    feedback_by_category: Dict[str, int]
    feedback_by_priority: Dict[str, int]
    feedback_by_status: Dict[str, int]

    model_config = ConfigDict(from_attributes=True)
