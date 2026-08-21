import uuid
from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.taxonomy.taxonomy_engine import TaxonomyEngine
from app.schemas.duplicate import DuplicateCheckResult
from app.schemas.roadmap import RoadmapRead


class FeedbackCreate(BaseModel):
    """Schema for feedback submission from frontend/API."""
    original_text: str = Field(..., min_length=1, max_length=5000, description="Raw feedback text submitted by user")
    platform: Optional[str] = Field(default=None, description="Source platform (Web, iOS, Android, etc.)")

    @field_validator("original_text")
    @classmethod
    def validate_original_text(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Feedback text cannot be empty or whitespace-only.")
        return v.strip()

    @field_validator("platform")
    @classmethod
    def validate_platform(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v_clean = v.strip()
        if not v_clean:
            return None
        engine = TaxonomyEngine()
        if not engine.is_valid_platform(v_clean):
            raise ValueError(f"Platform '{v}' is invalid. Allowed platforms: {engine.get_platforms()}")
        return v_clean


class FeedbackStatusUpdate(BaseModel):
    """Schema for updating feedback status."""
    status: str = Field(..., description="Target feedback status")

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Status cannot be empty.")
        v_clean = v.strip()
        engine = TaxonomyEngine()
        valid_statuses = set(engine.get_status_values() + engine.get_task_statuses())
        if v_clean not in valid_statuses:
            raise ValueError(f"Status '{v}' is invalid. Allowed taxonomy statuses: {sorted(list(valid_statuses))}")
        return v_clean


class FeedbackUpdate(BaseModel):
    """Schema for updating feedback analysis or status."""
    summary: Optional[str] = None
    feedback_type: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    bug_category: Optional[str] = None
    severity: Optional[str] = None
    priority: Optional[str] = None
    impact_area: Optional[str] = None
    platform: Optional[str] = None
    recommended_action: Optional[str] = None
    confidence: Optional[str] = None
    status: Optional[str] = None


class FeedbackRead(BaseModel):
    """Schema for returning complete triaged feedback object."""
    id: uuid.UUID
    original_text: str
    summary: Optional[str] = None
    feedback_type: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    bug_category: Optional[str] = None
    severity: Optional[str] = None
    priority: Optional[str] = None
    impact_area: Optional[str] = None
    platform: Optional[str] = None
    recommended_action: Optional[str] = None
    confidence: Optional[str] = None
    status: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class FeedbackDetailRead(FeedbackRead):
    """Extended schema for single feedback detail view including duplicate, roadmap, and tasks."""
    duplicate: Optional[DuplicateCheckResult] = None
    roadmap: Optional[RoadmapRead] = None


class FeedbackListResponse(BaseModel):
    """Paginated feedback list response schema."""
    items: List[FeedbackRead]
    page: int
    page_size: int
    total: int
