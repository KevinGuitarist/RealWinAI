"""
M.A.X. Track Record & Prediction Verification System
Public accountability and transparency for building trust
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
import json
from collections import defaultdict

class TrackRecordManager:
    """
    Manages MAX's prediction track record with full transparency
    
    Features:
    - Real-time accuracy tracking
    - Sport/market breakdown
    - Public verification
    - Performance metrics
    - Historical trends
    """
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def record_prediction(
        self,
        prediction_id: str,
        sport: str,
        match_details: Dict[str, Any],
        prediction_details: Dict[str, Any],
        confidence: float,
        odds: float,
        market_type: str = "match_winner"
    ) -> Dict[str, Any]:
        """
        Record a new prediction for tracking
        
        Args:
            prediction_id: Unique identifier
            sport: cricket, football, etc.
            match_details: Team names, date, venue
            prediction_details: Predicted winner, reasoning
            confidence: 0-100 confidence level
            odds: Betting odds
            market_type: Type of bet
            
        Returns:
            Recorded prediction with tracking ID
        """
        from source.app.models import Suggestion
        
        prediction_record = {
            'prediction_id': prediction_id,
            'sport': sport,
            'match_details': match_details,
            'prediction': prediction_details,
            'confidence': confidence,
            'odds': odds,
            'market_type': market_type,
            'predicted_at': datetime.now().isoformat(),
            'status': 'pending',
            'result': None,
            'verified': False
        }
        
        try:
            # Store in database
            suggestion = Suggestion(
                user_id=None,  # Public prediction
                sport=sport,
                team_name=prediction_details.get('predicted_winner', 'Unknown'),
                odds=odds,
                confidence=confidence,
                match_date=match_details.get('date', datetime.now()),
                is_public=True,
                prediction_data=json.dumps(prediction_record)
            )
            
            self.db.add(suggestion)
            self.db.commit()
            
            return {
                'success': True,
                'tracking_id': suggestion.id,
                'prediction_record': prediction_record,
                'message': 'Prediction recorded for public verification'
            }
            
        except Exception as e:
            self.db.rollback()
            return {
                'success': False,
                'error': str(e)
            }
    
    def verify_prediction(
        self,
        prediction_id: str,
        actual_result: str,
        match_outcome: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Verify prediction against actual result
        
        Args:
            prediction_id: Prediction to verify
            actual_result: Actual match outcome
            match_outcome: Full match details
            
        Returns:
            Verification result
        """
        from source.app.models import Suggestion, Result
        
        try:
            # Find prediction
            suggestion = self.db.query(Suggestion).filter(
                Suggestion.id == prediction_id
            ).first()
            
            if not suggestion:
                return {'success': False, 'error': 'Prediction not found'}
            
            prediction_data = json.loads(suggestion.prediction_data or '{}')
            predicted_winner = prediction_data.get('prediction', {}).get('predicted_winner')
            
            # Determine if prediction was correct
            is_correct = (predicted_winner == actual_result)
            
            # Update prediction record
            prediction_data['status'] = 'verified'
            prediction_data['result'] = actual_result
            prediction_data['is_correct'] = is_correct
            prediction_data['verified_at'] = datetime.now().isoformat()
            prediction_data['match_outcome'] = match_outcome
            
            suggestion.prediction_data = json.dumps(prediction_data)
            
            # Create result record
            result = Result(
                suggestion_id=suggestion.id,
                match_result=actual_result,
                is_correct=is_correct,
                verified_at=datetime.now()
            )
            
            self.db.add(result)
            self.db.commit()
            
            return {
                'success': True,
                'prediction_id': prediction_id,
                'predicted': predicted_winner,
                'actual': actual_result,
                'is_correct': is_correct,
                'confidence': prediction_data.get('confidence'),
                'odds': prediction_data.get('odds')
            }
            
        except Exception as e:
            self.db.rollback()
            return {'success': False, 'error': str(e)}
    
    def get_track_record(
        self,
        sport: Optional[str] = None,
        market_type: Optional[str] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get MAX's track record with full transparency
        
        Args:
            sport: Filter by sport
            market_type: Filter by market type
            days: Number of days to analyze
            
        Returns:
            Complete track record with metrics
        """
        from source.app.models import Suggestion, Result
        
        try:
            # Query verified predictions
            query = self.db.query(Suggestion, Result).join(
                Result, Suggestion.id == Result.suggestion_id
            ).filter(
                Suggestion.is_public == True,
                Result.verified_at >= datetime.now() - timedelta(days=days)
            )
            
            if sport:
                query = query.filter(Suggestion.sport == sport)
            
            predictions = query.all()
            
            # Calculate metrics
            total_predictions = len(predictions)
            correct_predictions = sum(1 for _, result in predictions if result.is_correct)
            
            if total_predictions == 0:
                return {
                    'total_predictions': 0,
                    'accuracy': 0,
                    'message': 'No verified predictions in this period'
                }
            
            accuracy = (correct_predictions / total_predictions) * 100
            
            # Break down by confidence level
            confidence_breakdown = {
                'high_confidence': {'correct': 0, 'total': 0},  # 80-100%
                'medium_confidence': {'correct': 0, 'total': 0},  # 60-79%
                'low_confidence': {'correct': 0, 'total': 0}  # 0-59%
            }
            
            # Break down by sport
            sport_breakdown = defaultdict(lambda: {'correct': 0, 'total': 0})
            
            # Break down by market type
            market_breakdown = defaultdict(lambda: {'correct': 0, 'total': 0})
            
            # Calculate ROI (if betting £10 on each)
            total_stake = 0
            total_return = 0
            
            for suggestion, result in predictions:
                # Confidence breakdown
                confidence = suggestion.confidence or 0
                if confidence >= 80:
                    level = 'high_confidence'
                elif confidence >= 60:
                    level = 'medium_confidence'
                else:
                    level = 'low_confidence'
                
                confidence_breakdown[level]['total'] += 1
                if result.is_correct:
                    confidence_breakdown[level]['correct'] += 1
                
                # Sport breakdown
                sport_key = suggestion.sport or 'unknown'
                sport_breakdown[sport_key]['total'] += 1
                if result.is_correct:
                    sport_breakdown[sport_key]['correct'] += 1
                
                # Market breakdown
                prediction_data = json.loads(suggestion.prediction_data or '{}')
                market_key = prediction_data.get('market_type', 'match_winner')
                market_breakdown[market_key]['total'] += 1
                if result.is_correct:
                    market_breakdown[market_key]['correct'] += 1
                
                # ROI calculation
                stake = 10  # £10 per bet
                total_stake += stake
                if result.is_correct:
                    total_return += stake * (suggestion.odds or 2.0)
            
            roi = ((total_return - total_stake) / total_stake * 100) if total_stake > 0 else 0
            
            # Recent predictions (last 10)
            recent_predictions = []
            for suggestion, result in predictions[-10:]:
                prediction_data = json.loads(suggestion.prediction_data or '{}')
                recent_predictions.append({
                    'date': result.verified_at.isoformat() if result.verified_at else None,
                    'sport': suggestion.sport,
                    'match': prediction_data.get('match_details', {}).get('teams', []),
                    'predicted': prediction_data.get('prediction', {}).get('predicted_winner'),
                    'actual': result.match_result,
                    'correct': result.is_correct,
                    'confidence': suggestion.confidence,
                    'odds': suggestion.odds
                })
            
            return {
                'period': f'Last {days} days',
                'total_predictions': total_predictions,
                'correct_predictions': correct_predictions,
                'accuracy_percentage': round(accuracy, 2),
                'roi_percentage': round(roi, 2),
                'total_profit_loss': round(total_return - total_stake, 2),
                'confidence_breakdown': {
                    level: {
                        'accuracy': round((data['correct'] / data['total'] * 100) if data['total'] > 0 else 0, 2),
                        'total': data['total']
                    }
                    for level, data in confidence_breakdown.items()
                },
                'sport_breakdown': {
                    sport: {
                        'accuracy': round((data['correct'] / data['total'] * 100) if data['total'] > 0 else 0, 2),
                        'total': data['total']
                    }
                    for sport, data in sport_breakdown.items()
                },
                'market_breakdown': {
                    market: {
                        'accuracy': round((data['correct'] / data['total'] * 100) if data['total'] > 0 else 0, 2),
                        'total': data['total']
                    }
                    for market, data in market_breakdown.items()
                },
                'recent_predictions': recent_predictions,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_public_verification_link(self, prediction_id: str) -> str:
        """Generate public verification link for transparency"""
        base_url = "https://realwin.ai/max/verify"
        return f"{base_url}/{prediction_id}"
    
    def get_confidence_calibration(self) -> Dict[str, Any]:
        """
        Analyze how well confidence levels match actual accuracy
        Perfect calibration: 80% confidence = 80% accuracy
        """
        from source.app.models import Suggestion, Result
        
        try:
            predictions = self.db.query(Suggestion, Result).join(
                Result, Suggestion.id == Result.suggestion_id
            ).filter(
                Suggestion.is_public == True,
                Result.verified_at.isnot(None)
            ).all()
            
            # Group by confidence ranges
            calibration_data = {}
            for i in range(5, 101, 5):  # 5%, 10%, 15%, ..., 100%
                calibration_data[i] = {'correct': 0, 'total': 0}
            
            for suggestion, result in predictions:
                confidence = int(suggestion.confidence or 50)
                # Round to nearest 5%
                confidence_bucket = round(confidence / 5) * 5
                
                calibration_data[confidence_bucket]['total'] += 1
                if result.is_correct:
                    calibration_data[confidence_bucket]['correct'] += 1
            
            # Calculate calibration scores
            calibration_results = []
            for confidence, data in calibration_data.items():
                if data['total'] > 0:
                    actual_accuracy = (data['correct'] / data['total']) * 100
                    calibration_error = abs(confidence - actual_accuracy)
                    calibration_results.append({
                        'predicted_confidence': confidence,
                        'actual_accuracy': round(actual_accuracy, 2),
                        'calibration_error': round(calibration_error, 2),
                        'sample_size': data['total']
                    })
            
            return {
                'calibration_analysis': calibration_results,
                'overall_calibration': 'Well-calibrated' if all(
                    r['calibration_error'] < 10 for r in calibration_results
                ) else 'Needs improvement',
                'message': 'Lower calibration error = better confidence accuracy'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}


# Public API functions
def get_max_track_record(db_session: Session, sport: str = None, days: int = 30) -> Dict[str, Any]:
    """Get MAX's public track record"""
    tracker = TrackRecordManager(db_session)
    return tracker.get_track_record(sport=sport, days=days)


def verify_max_prediction(
    db_session: Session,
    prediction_id: str,
    actual_result: str,
    match_outcome: Dict[str, Any]
) -> Dict[str, Any]:
    """Verify a MAX prediction against actual result"""
    tracker = TrackRecordManager(db_session)
    return tracker.verify_prediction(prediction_id, actual_result, match_outcome)
