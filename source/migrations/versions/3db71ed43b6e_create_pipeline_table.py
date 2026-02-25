"""create pipeline table

Revision ID: 3db71ed43b6e
Revises: 8f3475fb1f8e
Create Date: 2025-10-01 07:55:42.308851

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg


# revision identifiers, used by Alembic.
revision = '3db71ed43b6e'
down_revision = '8f3475fb1f8e'
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_type t
                JOIN pg_namespace n ON n.oid = t.typnamespace
                WHERE t.typname = 'pipeline_status'
                  AND n.nspname = current_schema()
            ) THEN
                CREATE TYPE pipeline_status AS ENUM ('pending','running','success','failed');
            END IF;
        END
        $$;
        """
    )

    # 2) Bind to the existing enum without trying to create it again
    pipeline_status = pg.ENUM(
        "pending", "running", "success", "failed",
        name="pipeline_status",
        create_type=False
    )

    op.create_table(
        "pipeline",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, unique=True, index=True),
        sa.Column("create_date", sa.DateTime(), server_default=sa.func.now(), index=True),
        sa.Column("update_date", sa.DateTime(), server_default=sa.func.now(), index=True),
        sa.Column("start_time", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("end_time", sa.DateTime(), nullable=True),
        sa.Column("pipeline_type", sa.String(length=64), nullable=False),
        sa.Column("status", pipeline_status, nullable=False, server_default="pending"),
    )

    # Useful indices
    op.create_index("ix_pipeline_start_time", "pipeline", ["start_time"])
    op.create_index("ix_pipeline_end_time", "pipeline", ["end_time"])
    op.create_index("ix_pipeline_pipeline_type", "pipeline", ["pipeline_type"])
    op.create_index("ix_pipeline_status", "pipeline", ["status"])


def downgrade():
    op.drop_index("ix_pipeline_status", table_name="pipeline")
    op.drop_index("ix_pipeline_pipeline_type", table_name="pipeline")
    op.drop_index("ix_pipeline_end_time", table_name="pipeline")
    op.drop_index("ix_pipeline_start_time", table_name="pipeline")
    op.drop_table("pipeline")

    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM pg_type t
                JOIN pg_namespace n ON n.oid = t.typnamespace
                WHERE t.typname = 'pipeline_status'
                  AND n.nspname = current_schema()
            ) THEN
                DROP TYPE pipeline_status;
            END IF;
        END
        $$;
        """
    )