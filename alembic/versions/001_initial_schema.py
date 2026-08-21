"""Initial database schema migration

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-08-14 03:20:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Feedbacks table
    op.create_table(
        'feedbacks',
        sa.Column('id', sa.UUID(), nullable=False, primary_key=True),
        sa.Column('original_text', sa.Text(), nullable=False),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('feedback_type', sa.String(length=100), nullable=True),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('subcategory', sa.String(length=100), nullable=True),
        sa.Column('bug_category', sa.String(length=100), nullable=True),
        sa.Column('severity', sa.String(length=50), nullable=True),
        sa.Column('priority', sa.String(length=50), nullable=True),
        sa.Column('impact_area', sa.String(length=100), nullable=True),
        sa.Column('platform', sa.String(length=50), nullable=True),
        sa.Column('recommended_action', sa.String(length=100), nullable=True),
        sa.Column('confidence', sa.String(length=50), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='Open'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('idx_feedback_status', 'feedbacks', ['status'])
    op.create_index('idx_feedback_type', 'feedbacks', ['feedback_type'])
    op.create_index('idx_feedback_category', 'feedbacks', ['category'])
    op.create_index('idx_feedback_priority', 'feedbacks', ['priority'])
    op.create_index('idx_feedback_severity', 'feedbacks', ['severity'])
    op.create_index('idx_feedback_created_at', 'feedbacks', ['created_at'])

    # 2. Roadmaps table
    op.create_table(
        'roadmaps',
        sa.Column('id', sa.UUID(), nullable=False, primary_key=True),
        sa.Column('feedback_id', sa.UUID(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='Backlog'),
        sa.Column('effort', sa.String(length=50), nullable=True),
        sa.Column('progress', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['feedback_id'], ['feedbacks.id'], ondelete='CASCADE'),
        sa.CheckConstraint('progress >= 0 AND progress <= 100', name='chk_roadmap_progress_range'),
        sa.UniqueConstraint('feedback_id')
    )
    op.create_index('idx_roadmap_status', 'roadmaps', ['status'])

    # 3. Roadmap Tasks table
    op.create_table(
        'roadmap_tasks',
        sa.Column('id', sa.UUID(), nullable=False, primary_key=True),
        sa.Column('roadmap_id', sa.UUID(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('effort', sa.String(length=50), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='Open'),
        sa.Column('progress', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('dependencies', sa.JSON().with_variant(postgresql.JSONB(), 'postgresql'), nullable=True),
        sa.Column('acceptance_criteria', sa.JSON().with_variant(postgresql.JSONB(), 'postgresql'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['roadmap_id'], ['roadmaps.id'], ondelete='CASCADE'),
        sa.CheckConstraint('progress >= 0 AND progress <= 100', name='chk_task_progress_range')
    )
    op.create_index('idx_roadmap_task_status', 'roadmap_tasks', ['status'])

    # 4. Notifications table
    op.create_table(
        'notifications',
        sa.Column('id', sa.UUID(), nullable=False, primary_key=True),
        sa.Column('feedback_id', sa.UUID(), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('notification_type', sa.String(length=50), nullable=False),
        sa.Column('read', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['feedback_id'], ['feedbacks.id'], ondelete='CASCADE')
    )
    op.create_index('idx_notification_feedback_read_created', 'notifications', ['feedback_id', 'read', 'created_at'])


def downgrade() -> None:
    op.drop_table('notifications')
    op.drop_table('roadmap_tasks')
    op.drop_table('roadmaps')
    op.drop_table('feedbacks')
