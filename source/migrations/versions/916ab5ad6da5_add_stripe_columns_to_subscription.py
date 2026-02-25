"""add stripe columns to subscription

Revision ID: 916ab5ad6da5
Revises: 34e21a550f67
Create Date: 2025-09-19 14:47:00.303756

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '916ab5ad6da5'
down_revision = '34e21a550f67'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("subscription") as batch:
        batch.add_column(sa.Column("stripe_customer_id", sa.String(), nullable=True))
        batch.add_column(sa.Column("stripe_subscription_id", sa.String(), nullable=True))
        batch.add_column(sa.Column("stripe_checkout_session_id", sa.String(), nullable=True))
        batch.add_column(sa.Column("stripe_status", sa.String(), nullable=True))
        batch.add_column(sa.Column("stripe_latest_invoice_id", sa.String(), nullable=True))
        batch.create_index("ix_subscription_stripe_customer_id", ["stripe_customer_id"])
        batch.create_index("ix_subscription_stripe_subscription_id", ["stripe_subscription_id"])
        batch.create_index("ix_subscription_stripe_checkout_session_id", ["stripe_checkout_session_id"])
        batch.create_index("ix_subscription_stripe_status", ["stripe_status"])
        batch.create_index("ix_subscription_stripe_latest_invoice_id", ["stripe_latest_invoice_id"])

def downgrade():
    with op.batch_alter_table("subscription") as batch:
        batch.drop_index("ix_subscription_stripe_latest_invoice_id")
        batch.drop_index("ix_subscription_stripe_status")
        batch.drop_index("ix_subscription_stripe_checkout_session_id")
        batch.drop_index("ix_subscription_stripe_subscription_id")
        batch.drop_index("ix_subscription_stripe_customer_id")
        batch.drop_column("stripe_latest_invoice_id")
        batch.drop_column("stripe_status")
        batch.drop_column("stripe_checkout_session_id")
        batch.drop_column("stripe_subscription_id")
        batch.drop_column("stripe_customer_id")