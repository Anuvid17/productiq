import uuid
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import (
    String,
    Text,
    Integer,
    Boolean,
    DateTime,
    ForeignKey,
    CheckConstraint,
    Index,
    JSON
)
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.db import Base

# Universal JSON column type supporting PostgreSQL JSONB and SQLite JSON fallback
JSONType = JSON().with_variant(postgresql.JSONB(), "postgresql")


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Feedback(Base):
    __tablename__ = "feedbacks"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    original_text: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    feedback_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    subcategory: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    bug_category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    severity: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    priority: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    impact_area: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    platform: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    recommended_action: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    confidence: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="Open", server_default="Open")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now
    )

    # Relationships
    roadmap: Mapped[Optional["Roadmap"]] = relationship(
        "Roadmap", back_populates="feedback", uselist=False, cascade="all, delete-orphan"
    )
    notifications: Mapped[List["Notification"]] = relationship(
        "Notification", back_populates="feedback", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_feedback_status", "status"),
        Index("idx_feedback_type", "feedback_type"),
        Index("idx_feedback_category", "category"),
        Index("idx_feedback_priority", "priority"),
        Index("idx_feedback_severity", "severity"),
        Index("idx_feedback_created_at", "created_at"),
    )


class Roadmap(Base):
    __tablename__ = "roadmaps"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    feedback_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("feedbacks.id", ondelete="CASCADE"), unique=True, index=True, nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="Backlog", server_default="Backlog")
    effort: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    progress: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now
    )

    # Relationships
    feedback: Mapped["Feedback"] = relationship("Feedback", back_populates="roadmap")
    tasks: Mapped[List["RoadmapTask"]] = relationship(
        "RoadmapTask", back_populates="roadmap", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint("progress >= 0 AND progress <= 100", name="chk_roadmap_progress_range"),
        Index("idx_roadmap_status", "status"),
    )


class RoadmapTask(Base):
    __tablename__ = "roadmap_tasks"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    roadmap_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("roadmaps.id", ondelete="CASCADE"), index=True, nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    effort: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="Open", server_default="Open")
    progress: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    dependencies: Mapped[Optional[dict | list]] = mapped_column(JSONType, nullable=True)
    acceptance_criteria: Mapped[Optional[list]] = mapped_column(JSONType, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now
    )

    # Relationships
    roadmap: Mapped["Roadmap"] = relationship("Roadmap", back_populates="tasks")

    __table_args__ = (
        CheckConstraint("progress >= 0 AND progress <= 100", name="chk_task_progress_range"),
        Index("idx_roadmap_task_status", "status"),
    )


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    feedback_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("feedbacks.id", ondelete="CASCADE"), index=True, nullable=False
    )
    message: Mapped[str] = mapped_column(Text, nullable=False)
    notification_type: Mapped[str] = mapped_column(String(50), nullable=False)
    read: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false", index=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utc_now, index=True
    )

    # Relationships
    feedback: Mapped["Feedback"] = relationship("Feedback", back_populates="notifications")

    __table_args__ = (
        Index("idx_notification_feedback_read_created", "feedback_id", "read", "created_at"),
    )
