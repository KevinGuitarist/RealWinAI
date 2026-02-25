"""add_agent_state_to_sent_messages

Revision ID: 66bed4986c18
Revises: 089aa281e49b
Create Date: 2025-09-17 20:09:19.526547

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "66bed4986c18"
down_revision = "e0e0596cfe4e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add agent_state_when_sent column to sent_messages table
    op.execute(
        sa.text(
            """
            ALTER TABLE "public"."sent_messages"
            ADD COLUMN IF NOT EXISTS agent_state_when_sent VARCHAR(50)
            """
        )
    )


def downgrade() -> None:
    # Remove agent_state_when_sent column from sent_messages table
    op.execute(
        sa.text(
            """
            ALTER TABLE "public"."sent_messages"
            DROP COLUMN IF EXISTS agent_state_when_sent
            """
        )
    )
