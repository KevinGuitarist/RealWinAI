"""add_missing_max_columns

Revision ID: e0e0596cfe4e
Revises: c7e2ef2a2f1a
Create Date: 2025-09-17 20:05:30.140194

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e0e0596cfe4e"
down_revision = "c7e2ef2a2f1a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add missing columns to user_stats table
    op.execute(
        sa.text(
            """
            ALTER TABLE "public"."user_stats"
            ADD COLUMN IF NOT EXISTS churn_risk_score REAL DEFAULT 0.0,
            ADD COLUMN IF NOT EXISTS loss_chasing_index REAL DEFAULT 0.0,
            ADD COLUMN IF NOT EXISTS user_momentum_score REAL DEFAULT 0.0,
            ADD COLUMN IF NOT EXISTS current_agent_state VARCHAR(50) DEFAULT 'guide',
            ADD COLUMN IF NOT EXISTS player_persona VARCHAR(50),
            ADD COLUMN IF NOT EXISTS total_bets INTEGER DEFAULT 0,
            ADD COLUMN IF NOT EXISTS win_rate REAL DEFAULT 0.0,
            ADD COLUMN IF NOT EXISTS roi_percentage REAL DEFAULT 0.0,
            ADD COLUMN IF NOT EXISTS days_since_last_session INTEGER DEFAULT 0
            """
        )
    )

    # Add missing columns to conversation_stats table
    op.execute(
        sa.text(
            """
            ALTER TABLE "public"."conversation_stats"
            ADD COLUMN IF NOT EXISTS suggestion_acceptance_rate REAL DEFAULT 0.0,
            ADD COLUMN IF NOT EXISTS suggestion_success_rate REAL DEFAULT 0.0,
            ADD COLUMN IF NOT EXISTS missed_opportunity_value REAL DEFAULT 0.0,
            ADD COLUMN IF NOT EXISTS trust_score REAL DEFAULT 0.0,
            ADD COLUMN IF NOT EXISTS current_win_streak INTEGER DEFAULT 0,
            ADD COLUMN IF NOT EXISTS current_loss_streak INTEGER DEFAULT 0,
            ADD COLUMN IF NOT EXISTS engagement_score REAL DEFAULT 50.0,
            ADD COLUMN IF NOT EXISTS last_calculated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            """
        )
    )

    # Add missing columns to suggestions table
    op.execute(
        sa.text(
            """
            ALTER TABLE "public"."suggestions"
            ADD COLUMN IF NOT EXISTS suggested_by_trigger VARCHAR(50),
            ADD COLUMN IF NOT EXISTS agent_state_when_suggested VARCHAR(50),
            ADD COLUMN IF NOT EXISTS response_timestamp TIMESTAMP WITH TIME ZONE
            """
        )
    )

    # Add missing column to results table
    op.execute(
        sa.text(
            """
            ALTER TABLE "public"."results"
            ADD COLUMN IF NOT EXISTS final_outcome VARCHAR(20)
            """
        )
    )


def downgrade() -> None:
    # Remove columns from results table
    op.execute(
        sa.text(
            """
            ALTER TABLE "public"."results"
            DROP COLUMN IF EXISTS final_outcome
            """
        )
    )

    # Remove columns from suggestions table
    op.execute(
        sa.text(
            """
            ALTER TABLE "public"."suggestions"
            DROP COLUMN IF EXISTS suggested_by_trigger,
            DROP COLUMN IF EXISTS agent_state_when_suggested,
            DROP COLUMN IF EXISTS response_timestamp
            """
        )
    )

    # Remove columns from conversation_stats table
    op.execute(
        sa.text(
            """
            ALTER TABLE "public"."conversation_stats"
            DROP COLUMN IF EXISTS suggestion_acceptance_rate,
            DROP COLUMN IF EXISTS suggestion_success_rate,
            DROP COLUMN IF EXISTS missed_opportunity_value,
            DROP COLUMN IF EXISTS trust_score,
            DROP COLUMN IF EXISTS current_win_streak,
            DROP COLUMN IF EXISTS current_loss_streak,
            DROP COLUMN IF EXISTS engagement_score,
            DROP COLUMN IF EXISTS last_calculated
            """
        )
    )

    # Remove columns from user_stats table
    op.execute(
        sa.text(
            """
            ALTER TABLE "public"."user_stats"
            DROP COLUMN IF EXISTS churn_risk_score,
            DROP COLUMN IF EXISTS loss_chasing_index,
            DROP COLUMN IF EXISTS user_momentum_score,
            DROP COLUMN IF EXISTS current_agent_state,
            DROP COLUMN IF EXISTS player_persona,
            DROP COLUMN IF EXISTS total_bets,
            DROP COLUMN IF EXISTS win_rate,
            DROP COLUMN IF EXISTS roi_percentage,
            DROP COLUMN IF EXISTS days_since_last_session
            """
        )
    )
