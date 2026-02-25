"""add telegram_user_id and session tracking fields

Revision ID: 8f3475fb1f8e
Revises: 09efbf1dcbc6
Create Date: 2025-09-23 07:09:02.646753

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8f3475fb1f8e'
down_revision = '09efbf1dcbc6'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # --- Columns (idempotent) ---
    # User table (quoted)
    op.execute('ALTER TABLE "User" ADD COLUMN IF NOT EXISTS telegram_chat_id VARCHAR;')

    # Messages tables
    op.execute("ALTER TABLE received_messages ADD COLUMN IF NOT EXISTS session_id UUID;")
    op.execute("ALTER TABLE sent_messages ADD COLUMN IF NOT EXISTS session_id UUID;")

    # User stats table
    op.execute("ALTER TABLE user_stats ADD COLUMN IF NOT EXISTS session_count INTEGER DEFAULT 0;")
    op.execute("ALTER TABLE user_stats ADD COLUMN IF NOT EXISTS avg_session_length FLOAT DEFAULT 0.0;")
    op.execute("ALTER TABLE user_stats ADD COLUMN IF NOT EXISTS total_engagement_time FLOAT DEFAULT 0.0;")
    op.execute("ALTER TABLE user_stats ADD COLUMN IF NOT EXISTS current_session_id UUID;")
    op.execute("ALTER TABLE user_stats ADD COLUMN IF NOT EXISTS current_session_start_time TIMESTAMP;")
    op.execute("ALTER TABLE user_stats ADD COLUMN IF NOT EXISTS last_activity_time TIMESTAMP;")

    # --- Indexes (idempotent) ---
    op.execute('CREATE UNIQUE INDEX IF NOT EXISTS ix_User_telegram_chat_id ON "User"(telegram_chat_id);')
    op.execute("CREATE INDEX IF NOT EXISTS idx_received_messages_session_id ON received_messages(session_id);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_sent_messages_session_id ON sent_messages(session_id);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_user_stats_current_session ON user_stats(current_session_id);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_user_stats_last_activity ON user_stats(last_activity_time);")

    # --- Comments ---
    op.execute("""
        COMMENT ON COLUMN received_messages.session_id
        IS 'UUID linking messages to a chat session for tracking user engagement';
    """)
    op.execute("""
        COMMENT ON COLUMN sent_messages.session_id
        IS 'UUID linking messages to a chat session for tracking user engagement';
    """)
    op.execute("""
        COMMENT ON COLUMN user_stats.session_count
        IS 'Total number of chat sessions initiated by the user';
    """)
    op.execute("""
        COMMENT ON COLUMN user_stats.avg_session_length
        IS 'Average duration of user chat sessions in minutes';
    """)
    op.execute("""
        COMMENT ON COLUMN user_stats.total_engagement_time
        IS 'Total time user has spent in chat sessions (minutes)';
    """)
    op.execute("""
        COMMENT ON COLUMN user_stats.current_session_id
        IS 'UUID of the currently active chat session, NULL if no active session';
    """)
    op.execute("""
        COMMENT ON COLUMN user_stats.current_session_start_time
        IS 'Timestamp when the current session started';
    """)
    op.execute("""
        COMMENT ON COLUMN user_stats.last_activity_time
        IS 'Timestamp of the last activity in the current session';
    """)


def downgrade() -> None:
    # Remove comments (safe even if column missing to leave as-is)
    # Using DO blocks to avoid errors if columns were never added.
    op.execute("""
    DO $$
    BEGIN
        IF EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name='received_messages' AND column_name='session_id') THEN
            COMMENT ON COLUMN received_messages.session_id IS NULL;
        END IF;
        IF EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name='sent_messages' AND column_name='session_id') THEN
            COMMENT ON COLUMN sent_messages.session_id IS NULL;
        END IF;
        IF EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name='user_stats' AND column_name='session_count') THEN
            COMMENT ON COLUMN user_stats.session_count IS NULL;
        END IF;
        IF EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name='user_stats' AND column_name='avg_session_length') THEN
            COMMENT ON COLUMN user_stats.avg_session_length IS NULL;
        END IF;
        IF EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name='user_stats' AND column_name='total_engagement_time') THEN
            COMMENT ON COLUMN user_stats.total_engagement_time IS NULL;
        END IF;
        IF EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name='user_stats' AND column_name='current_session_id') THEN
            COMMENT ON COLUMN user_stats.current_session_id IS NULL;
        END IF;
        IF EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name='user_stats' AND column_name='current_session_start_time') THEN
            COMMENT ON COLUMN user_stats.current_session_start_time IS NULL;
        END IF;
        IF EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name='user_stats' AND column_name='last_activity_time') THEN
            COMMENT ON COLUMN user_stats.last_activity_time IS NULL;
        END IF;
    END$$;
    """)

    # Drop indexes if they exist
    op.execute('DROP INDEX IF EXISTS ix_User_telegram_chat_id;')
    op.execute('DROP INDEX IF EXISTS idx_received_messages_session_id;')
    op.execute('DROP INDEX IF EXISTS idx_sent_messages_session_id;')
    op.execute('DROP INDEX IF EXISTS idx_user_stats_current_session;')
    op.execute('DROP INDEX IF EXISTS idx_user_stats_last_activity;')

    # Drop columns only if they exist (idempotent downgrade)
    op.execute('ALTER TABLE "User" DROP COLUMN IF EXISTS telegram_chat_id;')
    op.execute("ALTER TABLE received_messages DROP COLUMN IF EXISTS session_id;")
    op.execute("ALTER TABLE sent_messages DROP COLUMN IF EXISTS session_id;")
    op.execute("ALTER TABLE user_stats DROP COLUMN IF EXISTS session_count;")
    op.execute("ALTER TABLE user_stats DROP COLUMN IF EXISTS avg_session_length;")
    op.execute("ALTER TABLE user_stats DROP COLUMN IF EXISTS total_engagement_time;")
    op.execute("ALTER TABLE user_stats DROP COLUMN IF EXISTS current_session_id;")
    op.execute("ALTER TABLE user_stats DROP COLUMN IF EXISTS current_session_start_time;")
    op.execute("ALTER TABLE user_stats DROP COLUMN IF EXISTS last_activity_time;")