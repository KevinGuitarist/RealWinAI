from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy import DateTime
from source.core.models import Model

# NOTE:
# Your base Model already adds id, create_date, update_date.
# The cricket table in your screenshot also has created_at(now()).
# We'll add a separate created_at to match that exactly.

class CricketPrediction(Model):
    __tablename__ = "cricket_predictions"

    key = Column(String(255), nullable=False, index=True)
    prediction = Column(JSONB, nullable=False)
    date = Column(String(10), nullable=True, index=True)  # e.g. "2025-08-28"
    created_at = Column(DateTime, nullable=False, server_default=func.now())


class FootballPrediction(Model):
    __tablename__ = "football_predictions"

    key = Column(String(255), nullable=True, index=True)
    prediction = Column(JSONB, nullable=True)
    date = Column(String(10), nullable=True, index=True)
