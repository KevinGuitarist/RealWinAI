"""user_geo_fields

Revision ID: 89a67a531cc7
Revises: 9631ee0e99ad
Create Date: 2025-09-13 14:59:05.637653

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '89a67a531cc7'
down_revision = '9631ee0e99ad'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('User') as batch:
        batch.add_column(sa.Column('last_login_ip', sa.String(length=45), nullable=True))
        batch.add_column(sa.Column('geo_country',   sa.String(length=64),  nullable=True))
        batch.add_column(sa.Column('geo_region',    sa.String(length=128), nullable=True))
        batch.add_column(sa.Column('geo_city',      sa.String(length=128), nullable=True))
        batch.add_column(sa.Column('geo_latitude',  sa.Float(),            nullable=True))
        batch.add_column(sa.Column('geo_longitude', sa.Float(),            nullable=True))
        batch.add_column(sa.Column('last_seen_at',  sa.DateTime(),         nullable=True))
    # optional index for ip
    op.create_index('ix_user_last_login_ip', 'User', ['last_login_ip'])

def downgrade():
    op.drop_index('ix_user_last_login_ip', table_name='User')
    with op.batch_alter_table('User') as batch:
        batch.drop_column('last_seen_at')
        batch.drop_column('geo_longitude')
        batch.drop_column('geo_latitude')
        batch.drop_column('geo_city')
        batch.drop_column('geo_region')
        batch.drop_column('geo_country')
        batch.drop_column('last_login_ip')
    
