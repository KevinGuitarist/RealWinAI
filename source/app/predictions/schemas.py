from typing import Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class PredictionOut(BaseModel):
    id: int
    key: Optional[str] = None
    date: Optional[str] = Field(None, description="YYYY-MM-DD or custom token")
    prediction: Any

    class Config:
        from_attributes = True

class FootballPredictionOut(BaseModel):
    id: int
    key: str
    match_name: Optional[str] = None
    match_kick_off: Optional[str] = None
    predicted_winner: Optional[str] = None
    win_probability_percent: Optional[float] = None
    prediction_object: Any
    logos: Any

class CricketPredictionOut(BaseModel):
    match_name: Optional[str] = None
    summary: Optional[str] = None
    venue: Optional[str] = None
    match_date: Optional[str] = None
    match_time: Optional[str] = None
    match_kick_off: Optional[datetime] = None
    explanation: Optional[str] = None
    predicted_winner: Optional[str] = None
    win_probability: Optional[float] = None
    prediction_object: Any