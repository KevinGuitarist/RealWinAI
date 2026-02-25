"""Add personalization tables

Revision ID: 67fac2986c19
Revises: 89a67a531cc7
Create Date: 2025-10-28 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '67fac2986c19'
down_revision: Union[str, None] = '89a67a531cc7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Create user_preferences table
    op.create_table(
        'user_preferences',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('create_date', sa.DateTime(), nullable=True),
        sa.Column('update_date', sa.DateTime(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('preferred_name', sa.String(length=50), nullable=True),
        sa.Column('preferred_greeting', sa.String(length=50), nullable=True),
        sa.Column('betting_preferences', sa.JSON(), nullable=True),
        sa.Column('favorite_teams', sa.JSON(), nullable=True),
        sa.Column('favorite_sports', sa.JSON(), nullable=True),
        sa.Column('notification_preferences', sa.JSON(), nullable=True),
        sa.Column('communication_style', sa.String(length=20), nullable=True),
        sa.Column('expertise_level', sa.String(length=20), nullable=True),
        sa.Column('risk_tolerance', sa.String(length=20), nullable=True),
        sa.Column('last_interaction', sa.DateTime(), nullable=True),
        sa.Column('last_betting_activity', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['User.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create user_interactions table
    op.create_table(
        'user_interactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('create_date', sa.DateTime(), nullable=True),
        sa.Column('update_date', sa.DateTime(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('preferences_id', sa.Integer(), nullable=True),
        sa.Column('interaction_type', sa.String(length=50), nullable=False),
        sa.Column('message', sa.String(), nullable=True),
        sa.Column('response', sa.String(), nullable=True),
        sa.Column('emotional_state', sa.String(length=20), nullable=True),
        sa.Column('satisfaction_score', sa.Float(), nullable=True),
        sa.Column('context_data', sa.JSON(), nullable=True),
        sa.Column('session_id', sa.String(length=50), nullable=True),
        sa.Column('betting_amount', sa.Float(), nullable=True),
        sa.Column('betting_type', sa.String(length=50), nullable=True),
        sa.Column('betting_outcome', sa.String(length=20), nullable=True),
        sa.ForeignKeyConstraint(['preferences_id'], ['user_preferences.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['User.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create user_sessions table
    op.create_table(
        'user_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('create_date', sa.DateTime(), nullable=True),
        sa.Column('update_date', sa.DateTime(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.String(length=50), nullable=False),
        sa.Column('start_time', sa.DateTime(), nullable=True),
        sa.Column('end_time', sa.DateTime(), nullable=True),
        sa.Column('message_count', sa.Integer(), nullable=True),
        sa.Column('betting_count', sa.Integer(), nullable=True),
        sa.Column('total_wagered', sa.Float(), nullable=True),
        sa.Column('net_profit_loss', sa.Float(), nullable=True),
        sa.Column('emotional_states', sa.JSON(), nullable=True),
        sa.Column('topics_discussed', sa.JSON(), nullable=True),
        sa.Column('betting_types', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['User.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('session_id')
    )

def downgrade() -> None:
    op.drop_table('user_sessions')
    op.drop_table('user_interactions')
    op.drop_table('user_preferences')