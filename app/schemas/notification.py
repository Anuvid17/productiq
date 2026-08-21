import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class NotificationCreate(BaseModel):
    feedback_id: uuid.UUID
    message: str = Field(..., min_length=1)
    notification_type: str = Field(..., description="Internal type, e.g., RESOLVED, ROADMAP_UPDATED, STATUS_CHANGED")


class NotificationRead(BaseModel):
    id: uuid.UUID
    feedback_id: uuid.UUID
    message: str
    notification_type: str
    read: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
