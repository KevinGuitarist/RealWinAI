"""add predictions tables

Revision ID: 425ac62dbc73
Revises: 94f68d8257b2
Create Date: 2025-08-28 06:09:48.104961

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '425ac62dbc73'
down_revision = '94f68d8257b2'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "cricket_predictions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, unique=True, index=True),
        sa.Column("create_date", sa.DateTime(), server_default=sa.text("now()"), index=True),
        sa.Column("update_date", sa.DateTime(), server_default=sa.text("now()"), index=True),
        sa.Column("key", sa.String(length=255), nullable=False, index=True),
        sa.Column("prediction", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("date", sa.String(length=10), nullable=True, index=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
    )

    op.create_table(
        "football_predictions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, unique=True, index=True),
        sa.Column("create_date", sa.DateTime(), server_default=sa.text("now()"), index=True),
        sa.Column("update_date", sa.DateTime(), server_default=sa.text("now()"), index=True),
        sa.Column("key", sa.String(length=255), nullable=True, index=True),
        sa.Column("prediction", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("date", sa.String(length=10), nullable=True, index=True),
    )

def downgrade():
    op.drop_table("football_predictions")
    op.drop_table("cricket_predictions")