"""add roles, permissions, user settings

Revision ID: 94f68d8257b2
Revises: ea82a03addfc
Create Date: 2025-04-27 01:44:30.028608

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '94f68d8257b2'
down_revision = 'f2028fcd2782'
branch_labels = None
depends_on = None


def upgrade() -> None:
    
    # --- role table ---
    op.create_table(
        "role",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        # If your Model base adds timestamps, include them here:
        # sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        # sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.UniqueConstraint("name", name="uq_role_name"),
    )
    op.create_index("ix_role_name", "role", ["name"], unique=False)

    # --- permission table ---
    op.create_table(
        "permission",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.UniqueConstraint("name", name="uq_permission_name"),
    )
    op.create_index("ix_permission_name", "permission", ["name"], unique=False)

    # --- association: role_permissions ---
    op.create_table(
        "role_permissions",
        sa.Column("role_id", sa.Integer(), sa.ForeignKey("role.id", ondelete="CASCADE"), primary_key=True, nullable=False),
        sa.Column("permission_id", sa.Integer(), sa.ForeignKey("permission.id", ondelete="CASCADE"), primary_key=True, nullable=False),
    )

    # --- association: user_roles ---
    # NOTE: Your models reference ForeignKey("User.id") with a capital U.
    # This assumes a table literally named "User" already exists.
    op.create_table(
        "user_roles",
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("User.id", ondelete="CASCADE"), primary_key=True, nullable=False),
        sa.Column("role_id", sa.Integer(), sa.ForeignKey("role.id", ondelete="CASCADE"), primary_key=True, nullable=False),
    )

    # --- user_settings table ---
    op.create_table(
        "user_settings",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("User.id", ondelete="CASCADE"), nullable=False),
        sa.Column("email_notifications", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("timezone", sa.String(), nullable=False, server_default=sa.text("'UTC'")),
        sa.Column("language", sa.String(), nullable=False, server_default=sa.text("'en'")),
        sa.UniqueConstraint("user_id", name="uq_user_settings_user_id"),
    )
    op.create_index("ix_user_settings_user_id", "user_settings", ["user_id"], unique=True)


def downgrade() -> None:
    # Drop in reverse dependency order
    op.drop_index("ix_user_settings_user_id", table_name="user_settings")
    op.drop_table("user_settings")

    op.drop_table("user_roles")
    op.drop_table("role_permissions")

    op.drop_index("ix_permission_name", table_name="permission")
    op.drop_table("permission")

    op.drop_index("ix_role_name", table_name="role")
    op.drop_table("role")
