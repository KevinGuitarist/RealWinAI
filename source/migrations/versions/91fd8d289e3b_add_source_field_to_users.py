"""add source field to users

Revision ID: 91fd8d289e3b
Revises: 89a67a531cc7
Create Date: 2025-09-16 10:46:38.447745

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '91fd8d289e3b'
down_revision = '89a67a531cc7'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column("User", sa.Column("source", sa.String(), nullable=True))

def downgrade():
    op.drop_column("User", "source")
