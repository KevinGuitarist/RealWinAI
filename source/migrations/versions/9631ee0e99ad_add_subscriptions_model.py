"""Add subscriptions model

Revision ID: 9631ee0e99ad
Revises: 9da172240263
Create Date: 2025-09-02 02:53:30.224134

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9631ee0e99ad'
down_revision = '9da172240263'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'subscription',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True, unique=True, index=True),
        sa.Column('create_date', sa.DateTime(), server_default=sa.text('now()'), index=True),
        sa.Column('update_date', sa.DateTime(), server_default=sa.text('now()'), index=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('User.id'), nullable=False, index=True),
        sa.Column('email', sa.String(), nullable=False, index=True),
        sa.Column('full_name', sa.String(), nullable=True),
        sa.Column('revolut_customer_id', sa.String(), nullable=True, index=True),
        sa.Column('payment_method_id', sa.String(), nullable=True, index=True),
        sa.Column('payment_method_type', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=False, server_default=sa.text("'pending_initial_payment'"), index=True),
        sa.Column('next_billing_at', sa.DateTime(), nullable=True),
        sa.Column('last_order_id', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.false()),
    )

def downgrade():
    op.drop_table('subscription')
