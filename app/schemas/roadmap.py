import uuid
from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, ConfigDict, Field


# ROADMAP TASK SCHEMAS
class RoadmapTaskCreate(BaseModel):
    roadmap_id: uuid.UUID
    title: str = Field(..., min_length=1)
    description: Optional[str] = None
    effort: Optional[str] = None
    status: str = Field(default="Open", description="Task status: Open, In Progress, Testing, Completed")
    progress: int = Field(default=0, ge=0, le=100)
    dependencies: Optional[Any] = None
    acceptance_criteria: Optional[List[str]] = None


class RoadmapTaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    effort: Optional[str] = None
    status: Optional[str] = None
    progress: Optional[int] = Field(default=None, ge=0, le=100)
    dependencies: Optional[Any] = None
    acceptance_criteria: Optional[List[str]] = None


class TaskProgressUpdate(BaseModel):
    progress: Optional[int] = Field(default=None, ge=0, le=100)
    status: Optional[str] = None


class RoadmapTaskRead(BaseModel):
    id: uuid.UUID
    roadmap_id: uuid.UUID
    title: str
    description: Optional[str] = None
    effort: Optional[str] = None
    status: str
    progress: int
    dependencies: Optional[Any] = None
    acceptance_criteria: Optional[List[str]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ROADMAP SCHEMAS
class RoadmapCreate(BaseModel):
    feedback_id: uuid.UUID
    title: str = Field(..., min_length=1)
    description: Optional[str] = None
    status: str = Field(default="Backlog", description="Roadmap status: Backlog, Planned, In Progress, Testing, Released")
    effort: Optional[str] = None
    progress: int = Field(default=0, ge=0, le=100)


class RoadmapUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    effort: Optional[str] = None
    progress: Optional[int] = Field(default=None, ge=0, le=100)


class RoadmapRead(BaseModel):
    id: uuid.UUID
    feedback_id: uuid.UUID
    title: str
    description: Optional[str] = None
    status: str
    effort: Optional[str] = None
    progress: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    tasks: List[RoadmapTaskRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
