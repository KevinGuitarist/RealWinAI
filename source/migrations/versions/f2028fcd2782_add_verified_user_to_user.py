"""add verified_user to User

Revision ID: f2028fcd2782
Revises: 0e1cbca91020
Create Date: 2025-05-26 13:58:24.529959

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f2028fcd2782'
down_revision = 'ea82a03addfc'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'User',
        sa.Column('verified_user', sa.Boolean(), nullable=False, server_default=sa.false())
    )
    # if you want existing rows to show False, server_default handles it

def downgrade():
    op.drop_column('User', 'verified_user')
