"""
Alembic Migration: Add Performance Indexes

Adds composite indexes to the predictions table for query optimization.

Revision ID: 002_add_indexes
Revises: 001_initial_schema
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '002_add_indexes'
down_revision = '001_initial_schema'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Index for time-based queries (analytics, trends)
    op.create_index(
        'ix_predictions_created_at',
        'predictions',
        ['created_at'],
        unique=False
    )
    
    # Index for sentiment filtering
    op.create_index(
        'ix_predictions_sentiment',
        'predictions',
        ['sentiment'],
        unique=False
    )
    
    # Composite index for time + sentiment queries
    op.create_index(
        'ix_predictions_sentiment_created_at',
        'predictions',
        ['sentiment', 'created_at'],
        unique=False
    )
    
    # Index for model version queries
    op.create_index(
        'ix_predictions_model_version',
        'predictions',
        ['model_version'],
        unique=False
    )
    
    # Index for user lookup (if user_id column exists)
    # op.create_index(
    #     'ix_predictions_user_id',
    #     'predictions',
    #     ['user_id'],
    #     unique=False
    # )
    
    # Index on users table for email lookup
    op.create_index(
        'ix_users_email',
        'users',
        ['email'],
        unique=True
    )
    
    # Index for active users
    op.create_index(
        'ix_users_is_active',
        'users',
        ['is_active'],
        unique=False
    )


def downgrade() -> None:
    op.drop_index('ix_users_is_active', table_name='users')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_index('ix_predictions_model_version', table_name='predictions')
    op.drop_index('ix_predictions_sentiment_created_at', table_name='predictions')
    op.drop_index('ix_predictions_sentiment', table_name='predictions')
    op.drop_index('ix_predictions_created_at', table_name='predictions')
