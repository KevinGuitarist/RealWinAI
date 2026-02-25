"""add MAX integration

Revision ID: c7e2ef2a2f1a
Revises: 9631ee0e99ad
Create Date: 2025-09-17 19:35:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c7e2ef2a2f1a"
down_revision = "9631ee0e99ad"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable pgcrypto extension for gen_random_uuid() if available
    try:
        op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
    except Exception:
        # Ignore if not permitted (e.g., in managed PG); UUIDs can be client-generated
        pass

    # Alter User table: add MAX columns if not exists
    op.execute(
        sa.text(
            'ALTER TABLE "public"."User"\n'
            "ADD COLUMN IF NOT EXISTS telegram_user_id INTEGER UNIQUE NULL,\n"
            "ADD COLUMN IF NOT EXISTS preferred_channel VARCHAR(50) DEFAULT 'webapp',\n"
            "ADD COLUMN IF NOT EXISTS personality_string TEXT;"
        )
    )

    # user_stats
    op.execute(
        sa.text(
            """
            CREATE TABLE IF NOT EXISTS "public"."user_stats" (
                "id" SERIAL PRIMARY KEY,
                "user_id" INTEGER UNIQUE NOT NULL REFERENCES "User"(id) ON DELETE CASCADE,
                "total_amount_spent" REAL DEFAULT 0.0,
                "average_stake_size" REAL DEFAULT 0.0,
                "net_profit_loss" REAL DEFAULT 0.0,
                "betting_frequency" REAL DEFAULT 0.0,
                "favorite_sports" TEXT,
                "favorite_markets" TEXT,
                "last_message_date" TIMESTAMP WITH TIME ZONE,
                "session_count" INTEGER DEFAULT 0,
                "avg_session_length" REAL DEFAULT 0.0,
                "total_engagement_time" REAL DEFAULT 0.0,
                "risk_tolerance" REAL DEFAULT 50.0,
                "preferred_stake_percentage" REAL DEFAULT 0.02,
                "bankroll_size" REAL,
                "current_strategy" VARCHAR(100) DEFAULT 'conservative',
                "last_updated" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
    )

    # conversation_stats
    op.execute(
        sa.text(
            """
            CREATE TABLE IF NOT EXISTS "public"."conversation_stats" (
                "id" SERIAL PRIMARY KEY,
                "user_id" INTEGER UNIQUE NOT NULL REFERENCES "User"(id) ON DELETE CASCADE,
                "confidence_level" REAL DEFAULT 50.0,
                "empathy_level" REAL DEFAULT 50.0,
                "trust_indicators" REAL DEFAULT 50.0,
                "engagement_level" REAL DEFAULT 50.0,
                "message_count" INTEGER DEFAULT 0,
                "avg_response_time" REAL DEFAULT 0.0,
                "sentiment_trend" REAL DEFAULT 0.0,
                "communication_style" VARCHAR(50),
                "last_conversation_date" TIMESTAMP WITH TIME ZONE,
                "preferred_topics" TEXT,
                "last_updated" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
    )

    # received_messages
    op.execute(
        sa.text(
            """
            CREATE TABLE IF NOT EXISTS "public"."received_messages" (
                "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                "user_id" INTEGER NOT NULL REFERENCES "User"(id) ON DELETE CASCADE,
                "message_text" TEXT NOT NULL,
                "timestamp" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                "sentiment_score_nlp" REAL,
                "confidence_change" REAL DEFAULT 0.0,
                "empathy_change" REAL DEFAULT 0.0,
                "trust_change" REAL DEFAULT 0.0,
                "engagement_change" REAL DEFAULT 0.0,
                "personality_insights" TEXT,
                "message_category" VARCHAR(50),
                "processed" BOOLEAN DEFAULT FALSE
            )
            """
        )
    )

    # sent_messages
    op.execute(
        sa.text(
            """
            CREATE TABLE IF NOT EXISTS "public"."sent_messages" (
                "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                "user_id" INTEGER NOT NULL REFERENCES "User"(id) ON DELETE CASCADE,
                "message_text" TEXT NOT NULL,
                "message_type" VARCHAR(50) NOT NULL,
                "timestamp" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                "reply_to_message_id" UUID REFERENCES "received_messages"(id),
                "delivery_status" VARCHAR(20) DEFAULT 'sent',
                "channel_used" VARCHAR(50),
                "read_status" BOOLEAN DEFAULT FALSE,
                "response_triggered" BOOLEAN DEFAULT FALSE
            )
            """
        )
    )

    # suggestions
    op.execute(
        sa.text(
            """
            CREATE TABLE IF NOT EXISTS "public"."suggestions" (
                "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                "user_id" INTEGER NOT NULL REFERENCES "User"(id) ON DELETE CASCADE,
                "sport" VARCHAR(30) NOT NULL,
                "legacy_prediction_id" INTEGER NOT NULL,
                "legacy_prediction_key" VARCHAR(255),
                "suggested_stake" REAL NOT NULL,
                "timestamp" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                "user_action" VARCHAR(20),
                "actual_stake" REAL,
                "suggestion_rating" INTEGER,
                "outcome_profit_loss" REAL,
                "confidence_at_suggestion" REAL,
                "reasoning_provided" TEXT
            )
            """
        )
    )

    # results
    op.execute(
        sa.text(
            """
            CREATE TABLE IF NOT EXISTS "public"."results" (
                "id" SERIAL PRIMARY KEY,
                "suggestion_id" UUID NOT NULL REFERENCES "suggestions"(id) ON DELETE CASCADE,
                "actual_outcome" VARCHAR(100),
                "profit_loss" REAL,
                "roi_percentage" REAL,
                "timestamp" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                "accuracy_score" REAL,
                "confidence_validation" REAL,
                "learning_points" TEXT
            )
            """
        )
    )

    # indexes
    op.execute(
        sa.text(
            "CREATE INDEX IF NOT EXISTS idx_user_stats_user_id ON user_stats(user_id)"
        )
    )
    op.execute(
        sa.text(
            "CREATE INDEX IF NOT EXISTS idx_conversation_stats_user_id ON conversation_stats(user_id)"
        )
    )
    op.execute(
        sa.text(
            "CREATE INDEX IF NOT EXISTS idx_received_messages_user_id ON received_messages(user_id)"
        )
    )
    op.execute(
        sa.text(
            "CREATE INDEX IF NOT EXISTS idx_received_messages_timestamp ON received_messages(timestamp)"
        )
    )
    op.execute(
        sa.text(
            "CREATE INDEX IF NOT EXISTS idx_sent_messages_user_id ON sent_messages(user_id)"
        )
    )
    op.execute(
        sa.text(
            "CREATE INDEX IF NOT EXISTS idx_sent_messages_timestamp ON sent_messages(timestamp)"
        )
    )
    op.execute(
        sa.text(
            "CREATE INDEX IF NOT EXISTS idx_suggestions_user_id ON suggestions(user_id)"
        )
    )
    op.execute(
        sa.text(
            "CREATE INDEX IF NOT EXISTS idx_suggestions_sport ON suggestions(sport)"
        )
    )
    op.execute(
        sa.text(
            "CREATE INDEX IF NOT EXISTS idx_suggestions_legacy_prediction_id ON suggestions(legacy_prediction_id)"
        )
    )
    op.execute(
        sa.text(
            "CREATE INDEX IF NOT EXISTS idx_suggestions_legacy_prediction_key ON suggestions(legacy_prediction_key)"
        )
    )
    op.execute(
        sa.text(
            "CREATE INDEX IF NOT EXISTS idx_suggestions_timestamp ON suggestions(timestamp)"
        )
    )
    op.execute(
        sa.text(
            "CREATE INDEX IF NOT EXISTS idx_results_suggestion_id ON results(suggestion_id)"
        )
    )

    # comments
    op.execute(
        sa.text(
            "COMMENT ON COLUMN \"User\".telegram_user_id IS 'Telegram user ID for M.A.X. integration, nullable for existing users'"
        )
    )
    op.execute(
        sa.text(
            "COMMENT ON COLUMN \"User\".preferred_channel IS 'Preferred communication channel: webapp, telegram, sms, email, in_app'"
        )
    )
    op.execute(
        sa.text(
            "COMMENT ON COLUMN \"User\".personality_string IS 'JSON string storing personality analysis and preferences'"
        )
    )
    op.execute(
        sa.text(
            "COMMENT ON TABLE user_stats IS 'User behavioral and financial statistics for M.A.X. betting analysis'"
        )
    )
    op.execute(
        sa.text(
            "COMMENT ON TABLE conversation_stats IS 'Conversation metrics and communication patterns for personalization'"
        )
    )
    op.execute(
        sa.text(
            "COMMENT ON TABLE received_messages IS 'Messages received from users with sentiment and impact analysis'"
        )
    )
    op.execute(
        sa.text(
            "COMMENT ON TABLE sent_messages IS 'Messages sent by M.A.X. system with delivery tracking'"
        )
    )
    op.execute(
        sa.text(
            "COMMENT ON TABLE suggestions IS 'Betting suggestions made by M.A.X. with user response tracking'"
        )
    )
    op.execute(
        sa.text(
            "COMMENT ON TABLE results IS 'Outcome tracking for suggestions to measure M.A.X. performance'"
        )
    )


def downgrade() -> None:
    # drop indexes (IF EXISTS guard)
    for stmt in [
        "DROP INDEX IF EXISTS idx_results_suggestion_id",
        "DROP INDEX IF EXISTS idx_suggestions_timestamp",
        "DROP INDEX IF EXISTS idx_suggestions_legacy_prediction_key",
        "DROP INDEX IF EXISTS idx_suggestions_legacy_prediction_id",
        "DROP INDEX IF EXISTS idx_suggestions_sport",
        "DROP INDEX IF EXISTS idx_suggestions_user_id",
        "DROP INDEX IF EXISTS idx_sent_messages_timestamp",
        "DROP INDEX IF EXISTS idx_sent_messages_user_id",
        "DROP INDEX IF EXISTS idx_received_messages_timestamp",
        "DROP INDEX IF EXISTS idx_received_messages_user_id",
        "DROP INDEX IF EXISTS idx_conversation_stats_user_id",
        "DROP INDEX IF EXISTS idx_user_stats_user_id",
    ]:
        op.execute(sa.text(stmt))

    # drop tables
    for tbl in [
        "results",
        "suggestions",
        "sent_messages",
        "received_messages",
        "conversation_stats",
        "user_stats",
    ]:
        op.execute(sa.text(f'DROP TABLE IF EXISTS "public"."{tbl}" CASCADE'))

    # drop columns from User (if exist)
    op.execute(
        sa.text(
            'ALTER TABLE "public"."User"\n'
            "DROP COLUMN IF EXISTS telegram_user_id,\n"
            "DROP COLUMN IF EXISTS preferred_channel,\n"
            "DROP COLUMN IF EXISTS personality_string"
        )
    )
