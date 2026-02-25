"""
M.A.X. Enhanced API Endpoints
Expose all new features through REST API
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

# Import all new systems
from source.app.MAX.tools.max_track_record import (
    TrackRecordManager,
    get_max_track_record,
    verify_max_prediction
)
from source.app.MAX.tools.max_explainable_predictions import (
    ExplainablePredictionSystem,
    explain_prediction
)
from source.app.MAX.tools.max_personalized_strategies import (
    PersonalizedStrategyManager,
    create_user_strategy,
    get_bet_recommendation_for_user
)
from source.app.MAX.tools.max_responsible_gambling import (
    ResponsibleGamblingManager,
    check_betting_safety,
    set_user_limits,
    get_reality_check
)
from source.app.MAX.tools.max_analytics_dashboard import (
    AnalyticsDashboardManager,
    get_user_analytics
)
from source.app.MAX.tools.max_ensemble_predictions import (
    EnsemblePredictionSystem,
    get_ensemble_prediction
)

from source.core.database import get_db

# Create router
router = APIRouter(prefix="/max/enhanced", tags=["MAX Enhanced Features"])


# Pydantic models for request/response
class PredictionRequest(BaseModel):
    match_data: Dict[str, Any]
    analysis_data: Dict[str, Any]


class StrategyRequest(BaseModel):
    bankroll: float = Field(..., gt=0)
    goals: Dict[str, Any] = {}
    risk_profile: str = Field(default="balanced", pattern="^(conservative|balanced|aggressive|value_hunter)$")


class SpendingLimitsRequest(BaseModel):
    daily: Optional[float] = Field(None, ge=0)
    weekly: Optional[float] = Field(None, ge=0)
    monthly: Optional[float] = Field(None, ge=0)


class SelfExclusionRequest(BaseModel):
    duration_days: int = Field(..., ge=-1)
    reason: Optional[str] = None


class BetSafetyRequest(BaseModel):
    stake: float = Field(..., gt=0)
    odds: float = Field(..., gt=1.0)
    confidence: Optional[float] = Field(None, ge=0, le=100)


# ===== TRACK RECORD ENDPOINTS =====

@router.get("/track-record")
async def get_track_record(
    sport: Optional[str] = None,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """
    Get MAX's public track record
    
    Query Parameters:
    - sport: Filter by sport (cricket, football, etc.)
    - days: Number of days to analyze (default: 30)
    """
    try:
        track_record = get_max_track_record(db, sport=sport, days=days)
        return {
            "success": True,
            "data": track_record
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/track-record/verify/{prediction_id}")
async def verify_prediction(
    prediction_id: str,
    actual_result: str,
    match_outcome: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Verify a prediction against actual result
    
    Path Parameters:
    - prediction_id: Prediction to verify
    
    Body:
    - actual_result: Actual match outcome
    - match_outcome: Full match details
    """
    try:
        result = verify_max_prediction(db, prediction_id, actual_result, match_outcome)
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ===== EXPLAINABLE PREDICTIONS =====

@router.post("/explain-prediction")
async def get_prediction_explanation(request: PredictionRequest):
    """
    Get detailed explanation for a prediction
    
    Body:
    - match_data: Match information
    - analysis_data: Analyzed factors
    """
    try:
        prediction = request.match_data.get('prediction', {})
        explanation = explain_prediction(
            prediction=prediction,
            match_data=request.match_data,
            analysis_data=request.analysis_data
        )
        return {
            "success": True,
            "data": explanation
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ===== PERSONALIZED STRATEGIES =====

@router.post("/strategy/create/{user_id}")
async def create_strategy(
    user_id: int,
    request: StrategyRequest,
    db: Session = Depends(get_db)
):
    """
    Create personalized betting strategy for user
    
    Path Parameters:
    - user_id: User ID
    
    Body:
    - bankroll: Available bankroll
    - goals: User's betting goals
    - risk_profile: Risk appetite (conservative/balanced/aggressive/value_hunter)
    """
    try:
        strategy = create_user_strategy(
            db_session=db,
            user_id=user_id,
            bankroll=request.bankroll,
            goals=request.goals,
            risk_profile=request.risk_profile
        )
        return {
            "success": True,
            "data": strategy
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/strategy/{user_id}/recommendation")
async def get_bet_recommendation(
    user_id: int,
    prediction: Dict[str, Any],
    current_bankroll: float,
    db: Session = Depends(get_db)
):
    """
    Get bet recommendation based on user's strategy
    
    Path Parameters:
    - user_id: User ID
    
    Query Parameters:
    - prediction: Prediction details
    - current_bankroll: Current bankroll
    """
    try:
        recommendation = get_bet_recommendation_for_user(
            db_session=db,
            user_id=user_id,
            prediction=prediction,
            current_bankroll=current_bankroll
        )
        return {
            "success": True,
            "data": recommendation
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ===== RESPONSIBLE GAMBLING =====

@router.post("/safety/check/{user_id}")
async def check_safety(
    user_id: int,
    request: BetSafetyRequest,
    db: Session = Depends(get_db)
):
    """
    Check if bet is safe for user
    
    Path Parameters:
    - user_id: User ID
    
    Body:
    - stake: Proposed stake
    - odds: Bet odds
    - confidence: Prediction confidence
    """
    try:
        proposed_bet = {
            'stake': request.stake,
            'odds': request.odds,
            'confidence': request.confidence
        }
        
        safety_check = check_betting_safety(
            db_session=db,
            user_id=user_id,
            proposed_bet=proposed_bet
        )
        return {
            "success": True,
            "data": safety_check
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/safety/limits/{user_id}")
async def set_spending_limits(
    user_id: int,
    request: SpendingLimitsRequest,
    db: Session = Depends(get_db)
):
    """
    Set spending limits for user
    
    Path Parameters:
    - user_id: User ID
    
    Body:
    - daily: Daily limit
    - weekly: Weekly limit
    - monthly: Monthly limit
    """
    try:
        limits = {}
        if request.daily is not None:
            limits['daily'] = request.daily
        if request.weekly is not None:
            limits['weekly'] = request.weekly
        if request.monthly is not None:
            limits['monthly'] = request.monthly
        
        result = set_user_limits(
            db_session=db,
            user_id=user_id,
            limits=limits
        )
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/safety/self-exclusion/{user_id}")
async def initiate_exclusion(
    user_id: int,
    request: SelfExclusionRequest,
    db: Session = Depends(get_db)
):
    """
    Initiate self-exclusion period
    
    Path Parameters:
    - user_id: User ID
    
    Body:
    - duration_days: Exclusion period (7/30/90/180 or -1 for permanent)
    - reason: Optional reason
    """
    try:
        manager = ResponsibleGamblingManager(db)
        result = manager.initiate_self_exclusion(
            user_id=user_id,
            duration_days=request.duration_days,
            reason=request.reason
        )
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/safety/reality-check/{user_id}")
async def reality_check(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Get reality check for user
    
    Path Parameters:
    - user_id: User ID
    """
    try:
        check = get_reality_check(db_session=db, user_id=user_id)
        return {
            "success": True,
            "data": check
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ===== ANALYTICS DASHBOARD =====

@router.get("/analytics/{user_id}")
async def get_analytics(
    user_id: int,
    timeframe: str = "30d",
    db: Session = Depends(get_db)
):
    """
    Get comprehensive analytics for user
    
    Path Parameters:
    - user_id: User ID
    
    Query Parameters:
    - timeframe: Analysis period (7d/30d/90d/1y/all)
    """
    try:
        analytics = get_user_analytics(
            db_session=db,
            user_id=user_id,
            timeframe=timeframe
        )
        return {
            "success": True,
            "data": analytics
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ===== ENSEMBLE PREDICTIONS =====

@router.post("/ensemble/predict")
async def get_ensemble_pred(request: PredictionRequest):
    """
    Get ensemble prediction from multiple AI models
    
    Body:
    - match_data: Match information
    - analysis_data: Pre-analyzed factors
    """
    try:
        prediction = get_ensemble_prediction(
            match_data=request.match_data,
            analysis_data=request.analysis_data
        )
        return {
            "success": True,
            "data": prediction
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ===== HEALTH CHECK =====

@router.get("/health")
async def health_check():
    """Health check for enhanced features"""
    return {
        "status": "healthy",
        "features": {
            "track_record": "active",
            "explainable_predictions": "active",
            "personalized_strategies": "active",
            "responsible_gambling": "active",
            "analytics_dashboard": "active",
            "ensemble_predictions": "active"
        },
        "timestamp": datetime.now().isoformat()
    }
