from typing import Dict
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.database.db import get_db
from app.database.models import Feedback, Roadmap
from app.schemas.dashboard import DashboardSummaryRead
from app.utils.logger import logger

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=DashboardSummaryRead)
def get_dashboard_summary(db: Session = Depends(get_db)):
    """
    Returns server-aggregated summary metrics for the ProductIQ dashboard.
    """
    try:
        # Total feedback count
        total_feedback = db.scalar(select(func.count(Feedback.id))) or 0

        # Status breakdowns
        open_feedback = db.scalar(
            select(func.count(Feedback.id)).where(Feedback.status.in_(["Open", "Triaged"]))
        ) or 0

        resolved_feedback = db.scalar(
            select(func.count(Feedback.id)).where(Feedback.status == "Resolved")
        ) or 0

        # Critical / Blocker count
        critical_blocker_issues = db.scalar(
            select(func.count(Feedback.id)).where(
                (Feedback.priority == "P0") | (Feedback.severity.in_(["Critical", "Blocker"]))
            )
        ) or 0

        # Type counts
        feature_requests = db.scalar(
            select(func.count(Feedback.id)).where(Feedback.feedback_type == "Feature Request")
        ) or 0

        bug_reports = db.scalar(
            select(func.count(Feedback.id)).where(Feedback.feedback_type == "Bug Report")
        ) or 0

        # Active roadmaps (status != 'Released')
        active_roadmaps = db.scalar(
            select(func.count(Roadmap.id)).where(Roadmap.status != "Released")
        ) or 0

        # Average roadmap progress
        avg_progress = db.scalar(select(func.avg(Roadmap.progress)))
        average_roadmap_progress = round(float(avg_progress), 1) if avg_progress is not None else 0.0

        # Resolution rate percentage
        resolution_rate = round((resolved_feedback / total_feedback) * 100, 1) if total_feedback > 0 else 0.0

        # Breakdown dicts helper
        def get_breakdown(column):
            stmt = select(column, func.count(Feedback.id)).group_by(column)
            rows = db.execute(stmt).all()
            return {str(k): int(v) for k, v in rows if k is not None}

        feedback_by_type = get_breakdown(Feedback.feedback_type)
        feedback_by_category = get_breakdown(Feedback.category)
        feedback_by_priority = get_breakdown(Feedback.priority)
        feedback_by_status = get_breakdown(Feedback.status)

        return DashboardSummaryRead(
            total_feedback=total_feedback,
            open_feedback=open_feedback,
            resolved_feedback=resolved_feedback,
            critical_blocker_issues=critical_blocker_issues,
            feature_requests=feature_requests,
            bug_reports=bug_reports,
            active_roadmaps=active_roadmaps,
            average_roadmap_progress=average_roadmap_progress,
            resolution_rate=resolution_rate,
            feedback_by_type=feedback_by_type,
            feedback_by_category=feedback_by_category,
            feedback_by_priority=feedback_by_priority,
            feedback_by_status=feedback_by_status
        )
    except Exception as e:
        logger.error(f"Error calculating dashboard summary: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": {"code": "DASHBOARD_ERROR", "message": "Failed to calculate dashboard analytics summary."}}
        )
