import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.database.repository import RoadmapRepository, RoadmapTaskRepository
from app.schemas.roadmap import RoadmapRead, RoadmapUpdate, RoadmapTaskRead
from app.utils.logger import logger

router = APIRouter(prefix="/roadmaps", tags=["Roadmaps"])


def _parse_uuid(id_str: str, resource_name: str = "Roadmap") -> uuid.UUID:
    try:
        return uuid.UUID(id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": {
                    "code": "INVALID_UUID_FORMAT",
                    "message": f"Invalid {resource_name} UUID format: '{id_str}'"
                }
            }
        )


@router.get("", response_model=List[RoadmapRead])
def list_roadmaps(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status (Backlog, In Progress, Released, etc.)"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    List developer roadmaps with optional status filtering and pagination.
    """
    try:
        roadmap_repo = RoadmapRepository(db)
        task_repo = RoadmapTaskRepository(db)

        roadmaps = roadmap_repo.list(status=status_filter, limit=limit, offset=offset)
        result = []
        for rm in roadmaps:
            tasks = task_repo.list_by_roadmap(rm.id)
            rm_data = RoadmapRead.model_validate(rm)
            rm_data.tasks = [RoadmapTaskRead.model_validate(t) for t in tasks]
            result.append(rm_data)
        return result
    except Exception as e:
        logger.error(f"Error listing roadmaps: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": {"code": "DATABASE_ERROR", "message": "Failed to retrieve roadmaps."}}
        )


@router.get("/{roadmap_id}", response_model=RoadmapRead)
def get_roadmap(roadmap_id: str, db: Session = Depends(get_db)):
    """
    Retrieve single roadmap by UUID with associated developer tasks.
    """
    u_id = _parse_uuid(roadmap_id)
    roadmap_repo = RoadmapRepository(db)
    task_repo = RoadmapTaskRepository(db)

    roadmap = roadmap_repo.get_by_id(u_id)
    if not roadmap:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "ROADMAP_NOT_FOUND", "message": f"Roadmap with ID '{roadmap_id}' not found."}}
        )

    tasks = task_repo.list_by_roadmap(roadmap.id)
    rm_data = RoadmapRead.model_validate(roadmap)
    rm_data.tasks = [RoadmapTaskRead.model_validate(t) for t in tasks]
    return rm_data


@router.patch("/{roadmap_id}", response_model=RoadmapRead)
def update_roadmap(
    roadmap_id: str,
    update_data: RoadmapUpdate,
    db: Session = Depends(get_db)
):
    """
    Update roadmap fields (title, description, status, effort, progress).
    """
    u_id = _parse_uuid(roadmap_id)
    roadmap_repo = RoadmapRepository(db)
    task_repo = RoadmapTaskRepository(db)

    upd_kwargs = update_data.model_dump(exclude_unset=True)
    if not upd_kwargs:
        roadmap = roadmap_repo.get_by_id(u_id)
        if not roadmap:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": {"code": "ROADMAP_NOT_FOUND", "message": f"Roadmap with ID '{roadmap_id}' not found."}}
            )
        tasks = task_repo.list_by_roadmap(roadmap.id)
        rm_data = RoadmapRead.model_validate(roadmap)
        rm_data.tasks = [RoadmapTaskRead.model_validate(t) for t in tasks]
        return rm_data

    updated_roadmap = roadmap_repo.update(u_id, **upd_kwargs)
    if not updated_roadmap:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "ROADMAP_NOT_FOUND", "message": f"Roadmap with ID '{roadmap_id}' not found."}}
        )
    db.commit()
    db.refresh(updated_roadmap)

    tasks = task_repo.list_by_roadmap(updated_roadmap.id)
    rm_data = RoadmapRead.model_validate(updated_roadmap)
    rm_data.tasks = [RoadmapTaskRead.model_validate(t) for t in tasks]
    return rm_data
