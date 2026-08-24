import uuid
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.database.repository import FeedbackRepository, RoadmapRepository, RoadmapTaskRepository
from app.services.feedback_service import FeedbackService
from app.taxonomy.taxonomy_engine import TaxonomyEngine
from app.schemas.feedback import (
    FeedbackCreate,
    FeedbackRead,
    FeedbackDetailRead,
    FeedbackStatusUpdate,
    FeedbackListResponse
)
from app.schemas.roadmap import RoadmapRead, RoadmapTaskRead
from app.utils.logger import logger

router = APIRouter(prefix="/feedback", tags=["Feedback"])


@router.post(
    "",
    response_model=FeedbackDetailRead,
    status_code=status.HTTP_201_CREATED,
    summary="Submit and analyze new customer feedback"
)
def create_feedback(
    payload: FeedbackCreate,
    db: Session = Depends(get_db)
) -> FeedbackDetailRead:
    """
    Submits raw user feedback to execute the complete ProductIQ pipeline:
    - AI Classification via FeedbackAgent (local Ollama llama3.1)
    - Duplicate detection via DuplicateService
    - Rule-based action assignment via DecisionEngine
    - Feedback persistence
    - Developer roadmap and task generation if applicable
    """
    try:
        service = FeedbackService(session=db)
        result = service.process_and_store_feedback(
            raw_text=payload.original_text,
            platform=payload.platform
        )

        fb = result["feedback"]
        dup = result["duplicate_result"]
        rm = result["roadmap"]
        tasks = result["tasks"]

        roadmap_read = None
        if rm:
            task_reads = [RoadmapTaskRead.model_validate(t) for t in tasks] if tasks else []
            roadmap_read = RoadmapRead(
                id=rm.id,
                feedback_id=rm.feedback_id,
                title=rm.title,
                description=rm.description,
                status=rm.status,
                effort=rm.effort,
                progress=rm.progress,
                created_at=rm.created_at,
                updated_at=rm.updated_at,
                tasks=task_reads
            )

        return FeedbackDetailRead(
            id=fb.id,
            original_text=fb.original_text,
            summary=fb.summary,
            feedback_type=fb.feedback_type,
            category=fb.category,
            subcategory=fb.subcategory,
            bug_category=fb.bug_category,
            severity=fb.severity,
            priority=fb.priority,
            impact_area=fb.impact_area,
            platform=fb.platform,
            recommended_action=fb.recommended_action,
            confidence=fb.confidence,
            status=fb.status,
            created_at=fb.created_at,
            updated_at=fb.updated_at,
            duplicate=dup,
            roadmap=roadmap_read
        )
    except RuntimeError as e:
        logger.error(f"Feedback processing pipeline failed due to LLM error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"error": {"code": "AI_SERVICE_UNAVAILABLE", "message": "The feedback analysis service is currently unavailable."}}
        )
    except Exception as e:
        logger.error(f"Feedback creation unexpected failure: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": {"code": "INTERNAL_SERVER_ERROR", "message": f"Feedback processing failed: {str(e)}"}}
        )


@router.get(
    "",
    response_model=FeedbackListResponse,
    summary="List feedback items with pagination and filters"
)
def list_feedback(
    page: int = Query(default=1, ge=1, description="Page number starting at 1"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    status_filter: Optional[str] = Query(default=None, alias="status", description="Filter by status"),
    priority: Optional[str] = Query(default=None, description="Filter by priority (P0, P1, P2, P3)"),
    severity: Optional[str] = Query(default=None, description="Filter by severity"),
    category: Optional[str] = Query(default=None, description="Filter by category"),
    feedback_type: Optional[str] = Query(default=None, description="Filter by feedback type"),
    search: Optional[str] = Query(default=None, description="Text search in feedback content"),
    db: Session = Depends(get_db)
) -> FeedbackListResponse:
    """
    Retrieves paginated feedback items with optional filters.
    """
    offset = (page - 1) * page_size
    repo = FeedbackRepository(db)

    items = repo.list(
        status=status_filter,
        category=category,
        feedback_type=feedback_type,
        priority=priority,
        severity=severity,
        search=search,
        limit=page_size,
        offset=offset
    )

    total = repo.count(
        status=status_filter,
        category=category,
        feedback_type=feedback_type,
        priority=priority,
        severity=severity,
        search=search
    )

    item_reads = [FeedbackRead.model_validate(x) for x in items]
    return FeedbackListResponse(
        items=item_reads,
        page=page,
        page_size=page_size,
        total=total
    )


@router.get(
    "/{feedback_id}",
    response_model=FeedbackDetailRead,
    summary="Get feedback item details by ID"
)
def get_feedback(
    feedback_id: uuid.UUID,
    db: Session = Depends(get_db)
) -> FeedbackDetailRead:
    """
    Retrieves detailed information for a specific feedback item by UUID.
    """
    repo = FeedbackRepository(db)
    fb = repo.get_by_id(feedback_id)
    if not fb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "FEEDBACK_NOT_FOUND", "message": f"Feedback with ID '{feedback_id}' was not found."}}
        )

    roadmap_repo = RoadmapRepository(db)
    rm = roadmap_repo.get_by_feedback_id(feedback_id)

    if not rm:
        from app.services.roadmap_service import RoadmapService
        from app.schemas.agent import FeedbackAnalysis
        roadmap_service = RoadmapService(db)
        try:
            analysis = FeedbackAnalysis(
                summary=fb.summary or fb.original_text[:80],
                feedback_type=fb.feedback_type or "General Feedback",
                category=fb.category or "Authentication",
                subcategory=fb.subcategory or "Login",
                bug_category=fb.bug_category or "N/A",
                severity=fb.severity or "Major",
                priority=fb.priority or "P2",
                impact_area=fb.impact_area or "All Users",
                platform=fb.platform or "Web",
                recommended_action=fb.recommended_action or "CREATE_FEATURE",
                confidence=fb.confidence or "Medium"
            )
            rm = roadmap_service.create_roadmap_for_feedback(
                feedback_id=feedback_id,
                analysis=analysis,
                feedback_text=fb.original_text
            )
            db.commit()
        except Exception as err:
            logger.warning(f"Could not auto-generate missing roadmap for feedback '{feedback_id}': {err}")

    roadmap_read = None
    if rm:
        task_repo = RoadmapTaskRepository(db)
        tasks = task_repo.list_by_roadmap(rm.id)
        task_reads = [RoadmapTaskRead.model_validate(t) for t in tasks] if tasks else []
        roadmap_read = RoadmapRead(
            id=rm.id,
            feedback_id=rm.feedback_id,
            title=rm.title,
            description=rm.description,
            status=rm.status,
            effort=rm.effort,
            progress=rm.progress,
            created_at=rm.created_at,
            updated_at=rm.updated_at,
            tasks=task_reads
        )

    return FeedbackDetailRead(
        id=fb.id,
        original_text=fb.original_text,
        summary=fb.summary,
        feedback_type=fb.feedback_type,
        category=fb.category,
        subcategory=fb.subcategory,
        bug_category=fb.bug_category,
        severity=fb.severity,
        priority=fb.priority,
        impact_area=fb.impact_area,
        platform=fb.platform,
        recommended_action=fb.recommended_action,
        confidence=fb.confidence,
        status=fb.status,
        created_at=fb.created_at,
        updated_at=fb.updated_at,
        roadmap=roadmap_read
    )


@router.patch(
    "/{feedback_id}/status",
    response_model=FeedbackRead,
    summary="Update feedback status"
)
def update_feedback_status(
    feedback_id: uuid.UUID,
    payload: FeedbackStatusUpdate,
    db: Session = Depends(get_db)
) -> FeedbackRead:
    """
    Updates the status of a feedback item after validating against taxonomy.
    """
    repo = FeedbackRepository(db)
    fb = repo.get_by_id(feedback_id)
    if not fb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "FEEDBACK_NOT_FOUND", "message": f"Feedback with ID '{feedback_id}' was not found."}}
        )

    engine = TaxonomyEngine()
    valid_statuses = set(engine.get_status_values() + engine.get_task_statuses())
    if payload.status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"error": {"code": "INVALID_STATUS", "message": f"Status '{payload.status}' is not valid. Allowed: {sorted(list(valid_statuses))}"}}
        )

    updated_fb = repo.update(feedback_id, status=payload.status)
    db.commit()
    return FeedbackRead.model_validate(updated_fb)
