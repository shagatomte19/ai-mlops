"""Add users table and initial schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2025-12-25

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create initial database schema."""
    
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('is_admin', sa.Boolean(), nullable=False, default=False),
        sa.Column('is_verified', sa.Boolean(), nullable=False, default=False),
        sa.Column('api_key', sa.String(length=64), nullable=True),
        sa.Column('api_requests_count', sa.Integer(), nullable=True, default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_index('ix_users_id', 'users', ['id'], unique=False)
    op.create_index('ix_users_api_key', 'users', ['api_key'], unique=True)
    
    # Create predictions table
    op.create_table(
        'predictions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('sentiment', sa.String(length=20), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('positive_score', sa.Float(), nullable=False),
        sa.Column('negative_score', sa.Float(), nullable=False),
        sa.Column('neutral_score', sa.Float(), nullable=True, default=0.0),
        sa.Column('model_version', sa.String(length=20), nullable=True, default='v1.0'),
        sa.Column('processing_time_ms', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_predictions_id', 'predictions', ['id'], unique=False)
    op.create_index('ix_predictions_sentiment', 'predictions', ['sentiment'], unique=False)
    op.create_index('ix_predictions_created_at', 'predictions', ['created_at'], unique=False)
    
    # Create model_versions table
    op.create_table(
        'model_versions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('version', sa.String(length=20), nullable=False),
        sa.Column('accuracy', sa.Float(), nullable=True),
        sa.Column('precision', sa.Float(), nullable=True),
        sa.Column('recall', sa.Float(), nullable=True),
        sa.Column('f1_score', sa.Float(), nullable=True),
        sa.Column('training_samples', sa.Integer(), nullable=True),
        sa.Column('model_path', sa.String(length=255), nullable=True),
        sa.Column('vectorizer_path', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=False),
        sa.Column('model_metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('version')
    )
    op.create_index('ix_model_versions_id', 'model_versions', ['id'], unique=False)
    
    # Create analytics_snapshots table
    op.create_table(
        'analytics_snapshots',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('total_predictions', sa.Integer(), nullable=True, default=0),
        sa.Column('positive_count', sa.Integer(), nullable=True, default=0),
        sa.Column('negative_count', sa.Integer(), nullable=True, default=0),
        sa.Column('neutral_count', sa.Integer(), nullable=True, default=0),
        sa.Column('avg_confidence', sa.Float(), nullable=True),
        sa.Column('avg_processing_time_ms', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_analytics_snapshots_id', 'analytics_snapshots', ['id'], unique=False)
    op.create_index('ix_analytics_snapshots_date', 'analytics_snapshots', ['date'], unique=False)


def downgrade() -> None:
    """Drop all tables."""
    op.drop_index('ix_analytics_snapshots_date', table_name='analytics_snapshots')
    op.drop_index('ix_analytics_snapshots_id', table_name='analytics_snapshots')
    op.drop_table('analytics_snapshots')
    
    op.drop_index('ix_model_versions_id', table_name='model_versions')
    op.drop_table('model_versions')
    
    op.drop_index('ix_predictions_created_at', table_name='predictions')
    op.drop_index('ix_predictions_sentiment', table_name='predictions')
    op.drop_index('ix_predictions_id', table_name='predictions')
    op.drop_table('predictions')
    
    op.drop_index('ix_users_api_key', table_name='users')
    op.drop_index('ix_users_id', table_name='users')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_table('users')
