import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.database.repository import NotificationRepository
from app.schemas.notification import NotificationRead
from app.utils.logger import logger

router = APIRouter(prefix="/notifications", tags=["Notifications"])


def _parse_uuid(id_str: str, resource_name: str = "Notification") -> uuid.UUID:
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


@router.get("", response_model=List[NotificationRead])
def list_notifications(
    feedback_id: Optional[str] = Query(None, description="Filter notifications by feedback UUID"),
    read: Optional[bool] = Query(None, description="Filter by read state (e.g. read=false for unread notifications)"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    List system notifications with optional unread filter and pagination.
    """
    f_uuid = _parse_uuid(feedback_id, "Feedback") if feedback_id else None
    repo = NotificationRepository(db)
    unread_only = (read is False)
    notifs = repo.list(feedback_id=f_uuid, unread_only=unread_only, limit=limit, offset=offset)
    return [NotificationRead.model_validate(n) for n in notifs]


@router.patch("/read-all")
def mark_all_notifications_read(db: Session = Depends(get_db)):
    """
    Mark all unread notifications as read.
    """
    repo = NotificationRepository(db)
    unread_notifs = repo.list(unread_only=True, limit=500)
    count = 0
    for n in unread_notifs:
        n.read = True
        count += 1
    db.commit()
    return {"updated_count": count, "message": f"Marked {count} notifications as read."}


@router.patch("/{notification_id}/read", response_model=NotificationRead)
def mark_notification_read(notification_id: str, db: Session = Depends(get_db)):
    """
    Mark single notification as read.
    """
    u_id = _parse_uuid(notification_id)
    repo = NotificationRepository(db)
    notif = repo.mark_as_read(u_id)
    if not notif:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOTIFICATION_NOT_FOUND", "message": f"Notification with ID '{notification_id}' not found."}}
        )
    db.commit()
    db.refresh(notif)
    return NotificationRead.model_validate(notif)
