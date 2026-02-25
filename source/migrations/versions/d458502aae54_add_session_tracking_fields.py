"""add_session_tracking_fields

Revision ID: d458502aae54
Revises: 34e21a550f67
Create Date: 2025-09-20 22:18:34.576604

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd458502aae54'
down_revision = '34e21a550f67'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add session_id column to sent_messages table
    op.execute("""
        ALTER TABLE sent_messages 
        ADD COLUMN IF NOT EXISTS session_id UUID;
    """)
    
    # Add session_id column to received_messages table
    op.execute("""
        ALTER TABLE received_messages 
        ADD COLUMN IF NOT EXISTS session_id UUID;
    """)
    
    # Add current session tracking fields to user_stats table
    op.execute("""
        ALTER TABLE user_stats 
        ADD COLUMN IF NOT EXISTS current_session_id UUID;
    """)
    
    op.execute("""
        ALTER TABLE user_stats 
        ADD COLUMN IF NOT EXISTS current_session_start TIMESTAMP;
    """)
    
    # Create indexes for better performance
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_sent_messages_session_user 
        ON sent_messages(session_id, user_id);
    """)
    
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_received_messages_session_user 
        ON received_messages(session_id, user_id);
    """)
    
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_user_stats_current_session 
        ON user_stats(current_session_id) WHERE current_session_id IS NOT NULL;
    """)


def downgrade() -> None:
    # Drop indexes first
    op.execute("""
        DROP INDEX IF EXISTS idx_sent_messages_session_user;
    """)
    
    op.execute("""
        DROP INDEX IF EXISTS idx_received_messages_session_user;
    """)
    
    op.execute("""
        DROP INDEX IF EXISTS idx_user_stats_current_session;
    """)
    
    # Remove session tracking fields from user_stats
    op.execute("""
        ALTER TABLE user_stats 
        DROP COLUMN IF EXISTS current_session_id;
    """)
    
    op.execute("""
        ALTER TABLE user_stats 
        DROP COLUMN IF EXISTS current_session_start;
    """)
    
    # Remove session_id from message tables
    op.execute("""
        ALTER TABLE sent_messages 
        DROP COLUMN IF EXISTS session_id;
    """)
    
    op.execute("""
        ALTER TABLE received_messages 
        DROP COLUMN IF EXISTS session_id;
    """)
