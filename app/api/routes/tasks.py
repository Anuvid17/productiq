import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.database.repository import RoadmapTaskRepository
from app.schemas.roadmap import RoadmapTaskRead, TaskProgressUpdate
from app.services.task_workflow_service import TaskWorkflowService
from app.utils.logger import logger

router = APIRouter(prefix="/tasks", tags=["Tasks"])


def _parse_uuid(id_str: str, resource_name: str = "Task") -> uuid.UUID:
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


@router.get("/{task_id}", response_model=RoadmapTaskRead)
def get_task(task_id: str, db: Session = Depends(get_db)):
    """
    Retrieve single roadmap task by UUID.
    """
    u_id = _parse_uuid(task_id)
    task_repo = RoadmapTaskRepository(db)
    task = task_repo.get_by_id(u_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "TASK_NOT_FOUND", "message": f"Task with ID '{task_id}' not found."}}
        )
    return RoadmapTaskRead.model_validate(task)


@router.patch("/{task_id}", response_model=RoadmapTaskRead)
def update_task(
    task_id: str,
    update: TaskProgressUpdate,
    db: Session = Depends(get_db)
):
    """
    Update developer task progress and status.
    Uses TaskWorkflowService to enforce:
    - progress bounds (0-100)
    - status transitions & progress consistency
    - recalculation of parent roadmap status & progress
    - checking feedback resolution & notification creation
    """
    u_id = _parse_uuid(task_id)
    workflow_service = TaskWorkflowService(db)

    try:
        res = workflow_service.update_task_progress_and_status(u_id, update)
        db.commit()
        db.refresh(res["task"])
        return RoadmapTaskRead.model_validate(res["task"])
    except ValueError as ve:
        db.rollback()
        err_msg = str(ve)
        if "does not exist" in err_msg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": {"code": "TASK_NOT_FOUND", "message": err_msg}}
            )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"error": {"code": "TASK_VALIDATION_ERROR", "message": err_msg}}
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating task '{task_id}': {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": {"code": "WORKFLOW_ERROR", "message": "Failed to execute developer task workflow update."}}
        )
