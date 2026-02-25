from typing import Optional

from pydantic import BaseModel, Field


class SuggestionDetails(BaseModel):
    """Details of a betting suggestion"""

    class Config:
        extra = "forbid"

    prediction_id: str = Field(..., description="ID of the prediction")
    stake_amount: float = Field(..., description="Suggested stake amount")
    sport: str = Field(..., description="Sport category")
    market: str = Field(..., description="Betting market type")


class FinancialImpact(BaseModel):
    """Financial impact analysis"""

    class Config:
        extra = "forbid"

    stake_mentioned: bool = Field(
        default=False, description="Whether stake was mentioned"
    )
    stake_amount: float = Field(default=0.0, description="Stake amount mentioned")
    win_loss_reported: bool = Field(
        default=False, description="Whether win/loss was reported"
    )
    profit_loss_amount: float = Field(default=0.0, description="Profit or loss amount")
    betting_frequency_change: float = Field(
        default=0.0, description="Change in betting frequency"
    )


class BehavioralInsights(BaseModel):
    """Behavioral patterns detected"""

    class Config:
        extra = "forbid"

    sport_preference_mentioned: Optional[str] = Field(
        default=None, description="Sport preference mentioned"
    )
    market_preference_mentioned: Optional[str] = Field(
        default=None, description="Market preference mentioned"
    )
    risk_appetite_change: float = Field(
        default=0.0, description="Change in risk appetite"
    )
    activity_level_change: float = Field(
        default=0.0, description="Change in activity level"
    )
    loss_chasing_indicators: bool = Field(
        default=False, description="Signs of loss chasing behavior"
    )


class SafetyConcerns(BaseModel):
    """Safety and responsible gaming indicators"""

    class Config:
        extra = "forbid"

    excessive_betting_indicated: bool = Field(
        default=False, description="Excessive betting detected"
    )
    emotional_distress_detected: bool = Field(
        default=False, description="Emotional distress signs"
    )
    loss_chasing_behavior: bool = Field(
        default=False, description="Loss chasing behavior"
    )
    intervention_needed: bool = Field(
        default=False, description="Whether intervention is needed"
    )


class QuickReplyResponse(BaseModel):
    class Config:
        extra = "forbid"

    required: bool = Field(..., description="Whether an immediate response is required")
    response: Optional[str] = Field(
        None, description="The quick acknowledgment response if required is true"
    )
    requires_more_response: Optional[bool] = Field(
        None, description="Whether the user message requires further processing"
    )


class ConversationAnalysis(BaseModel):
    """Schema for LLM conversation analysis extraction with comprehensive metrics"""

    class Config:
        extra = "forbid"

    # Raw conversation effects (-1.0 to 1.0)
    confidence_change: float = Field(
        default=0.0, description="Change in user confidence (-1.0 to 1.0)"
    )
    empathy_change: float = Field(
        default=0.0, description="Change in perceived empathy (-1.0 to 1.0)"
    )
    trust_change: float = Field(
        default=0.0, description="Change in user trust (-1.0 to 1.0)"
    )
    engagement_change: float = Field(
        default=0.0, description="Change in user engagement (-1.0 to 1.0)"
    )

    # Betting and suggestion analysis
    suggestion_provided: bool = Field(
        default=False, description="Whether a betting suggestion was provided"
    )
    suggestion_details: Optional[dict] = Field(
        default=None,
        description="Details if suggestion provided (dict with prediction_id, stake_amount, sport, market)",
    )
    user_action_on_suggestion: Optional[str] = Field(
        default=None,
        description="User response to previous suggestion: ACCEPTED, IGNORED, or null",
    )

    # Financial impact analysis
    financial_impact: dict = Field(
        default_factory=lambda: {
            "stake_mentioned": False,
            "stake_amount": 0.0,
            "win_loss_reported": False,
            "profit_loss_amount": 0.0,
            "betting_frequency_change": 0.0,
        },
        description="Financial impact extracted from conversation",
    )

    # Behavioral pattern detection
    behavioral_insights: dict = Field(
        default_factory=lambda: {
            "sport_preference_mentioned": None,
            "market_preference_mentioned": None,
            "risk_appetite_change": 0.0,
            "activity_level_change": 0.0,
            "loss_chasing_indicators": False,
        },
        description="Behavioral patterns detected in conversation",
    )

    # Conversation classification
    user_sentiment: str = Field(
        default="neutral", description="User sentiment: positive, negative, neutral"
    )
    conversation_type: str = Field(
        default="general",
        description="Type: betting_inquiry, result_report, strategy_discussion, casual, complaint, etc.",
    )

    # Risk and safety indicators
    safety_concerns: dict = Field(
        default_factory=lambda: {
            "excessive_betting_indicated": False,
            "emotional_distress_detected": False,
            "loss_chasing_behavior": False,
            "intervention_needed": False,
        },
        description="Safety and responsible gaming indicators",
    )

    # Analysis reasoning
    reasoning: str = Field(
        default="",
        description="Brief explanation of the analysis and extracted insights",
    )


class UserMetricsUpdate(BaseModel):
    """Schema for comprehensive user metrics calculation and update"""

    class Config:
        extra = "forbid"

    # Financial metrics
    financial_metrics: dict = Field(
        default_factory=lambda: {
            "total_amount_spent": 0.0,
            "average_stake_size": 0.0,
            "net_profit_loss": 0.0,
            "total_bets": 0,
            "win_rate": 0.0,
            "roi_percentage": 0.0,
        },
        description="Complete financial performance metrics",
    )

    # Behavioral metrics
    behavioral_metrics: dict = Field(
        default_factory=lambda: {
            "betting_frequency": 0.0,
            "favorite_sports": [],
            "favorite_markets": [],
            "preferred_stake_range": {"min": 0.0, "max": 0.0},
            "betting_pattern": "casual",  # casual, frequent, high_roller
        },
        description="User behavioral patterns and preferences",
    )

    # Engagement metrics
    engagement_metrics: dict = Field(
        default_factory=lambda: {
            "days_since_last_session": 0,
            "session_count": 0,
            "avg_session_duration": 0.0,
            "conversation_frequency": 0.0,
            "response_rate": 0.0,
        },
        description="User engagement and activity metrics",
    )

    # Trust and relationship metrics
    trust_metrics: dict = Field(
        default_factory=lambda: {
            "suggestion_acceptance_rate": 0.0,
            "suggestion_success_rate": 0.0,
            "missed_opportunity_value": 0.0,
            "trust_score": 0.0,
            "confidence_level": 50.0,
            "empathy_level": 50.0,
        },
        description="Trust, confidence, and relationship metrics",
    )

    # Risk assessment metrics
    risk_metrics: dict = Field(
        default_factory=lambda: {
            "churn_risk_score": 0.0,
            "loss_chasing_index": 0.0,
            "user_momentum_score": 0.0,
            "sentiment_trend": 0.0,
            "risk_level": "LOW",  # LOW, MEDIUM, HIGH
        },
        description="Risk assessment and safety metrics",
    )

    # Strategy and personalization
    strategy_metrics: dict = Field(
        default_factory=lambda: {
            "current_agent_state": "GUIDE",
            "recommended_agent_state": "GUIDE",
            "player_persona": "casual_fan",
            "intervention_needed": False,
        },
        description="Agent strategy and personalization metrics",
    )


class PredictionParams(BaseModel):
    """Parameters for unified get_predictions() function"""
    
    class Config:
        extra = "forbid"
    
    sport: Optional[str] = Field(
        default=None, description="Sport filter: 'cricket', 'football', or None for both"
    )
    confidence: Optional[str] = Field(
        default=None, description="Confidence filter: 'high', 'medium', 'low', or None for all"
    )
    date: Optional[str] = Field(
        default=None, description="Specific date filter (YYYY-MM-DD) or None for recent"
    )
    essential_only: bool = Field(
        default=False, description="True for minimal data, False for full enhanced data"
    )
    prediction_id: Optional[int] = Field(
        default=None, description="Specific prediction ID or None"
    )
    team_name: Optional[str] = Field(
        default=None, description="Search by exact team name or None"
    )
    match_title: Optional[str] = Field(
        default=None, description="Search by match title or None"
    )
    limit: int = Field(
        default=10, description="Maximum number of predictions to return"
    )


class ConditionalDataDecision(BaseModel):
    """Schema for conditional data fetching decision using unified prediction function"""

    class Config:
        extra = "forbid"

    needs_predictions: bool = Field(
        default=False, description="Whether prediction data is needed"
    )
    prediction_params: Optional[PredictionParams] = Field(
        default=None, description="Parameters for unified get_predictions() function"
    )
    needs_suggestion_history: bool = Field(
        default=False, description="Whether user's recent suggestion history is needed"
    )
    suggestion_limit: int = Field(
        default=5, description="Number of recent suggestions to fetch"
    )
    needs_betting_history: bool = Field(
        default=False,
        description="Whether user's recent betting/result history is needed",
    )
    history_days: int = Field(
        default=30, description="Number of days back to look for betting history"
    )
    reasoning: str = Field(
        default="", description="Why this data is needed to respond effectively"
    )
