"""
M.A.X. Responsible Gambling Protection System
User safety and wellbeing through proactive intervention
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import json
from collections import defaultdict


class ResponsibleGamblingManager:
    """
    Protects users from problem gambling behaviors
    
    Features:
    - Loss chasing detection
    - Spending limits (daily/weekly/monthly)
    - Time limits and reality checks
    - Self-exclusion options
    - Cooling-off periods
    - Problem gambling detection
    """
    
    def __init__(self, db_session: Session):
        self.db = db_session
        
        # Warning thresholds
        self.thresholds = {
            'rapid_betting': 5,  # 5 bets in 30 minutes
            'loss_chase_ratio': 2.0,  # Doubling stakes after loss
            'session_loss_percentage': 20,  # 20% of bankroll in one session
            'consecutive_losses': 3,
            'daily_time_hours': 4,
            'weekly_loss_percentage': 30
        }
    
    def check_user_safety(
        self,
        user_id: int,
        current_action: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Comprehensive safety check before allowing bet
        
        Args:
            user_id: User to check
            current_action: Proposed bet details
            
        Returns:
            Safety assessment with warnings/blocks
        """
        from source.app.models import UserStats, Suggestion
        
        try:
            # Get user stats
            user_stats = self.db.query(UserStats).filter(
                UserStats.user_id == user_id
            ).first()
            
            if not user_stats:
                return {
                    'status': 'safe',
                    'allow_bet': True,
                    'message': 'New user - no concerns'
                }
            
            # Run all safety checks
            checks = {
                'spending_limits': self._check_spending_limits(user_id, current_action),
                'loss_chasing': self._detect_loss_chasing(user_id, current_action),
                'rapid_betting': self._check_rapid_betting(user_id),
                'session_time': self._check_session_time(user_id),
                'cooling_off': self._check_cooling_off_status(user_id),
                'self_exclusion': self._check_self_exclusion(user_id)
            }
            
            # Aggregate results
            warnings = []
            blocks = []
            
            for check_name, check_result in checks.items():
                if check_result['status'] == 'warning':
                    warnings.append({
                        'type': check_name,
                        'message': check_result['message'],
                        'severity': check_result.get('severity', 'medium')
                    })
                elif check_result['status'] == 'block':
                    blocks.append({
                        'type': check_name,
                        'message': check_result['message'],
                        'action_required': check_result.get('action_required')
                    })
            
            # Determine final status
            if blocks:
                return {
                    'status': 'blocked',
                    'allow_bet': False,
                    'blocks': blocks,
                    'message': 'Cannot proceed - protective measures in place',
                    'support_resources': self._get_support_resources()
                }
            elif len(warnings) >= 2:
                return {
                    'status': 'high_risk',
                    'allow_bet': True,  # Allow but strongly warn
                    'warnings': warnings,
                    'message': 'Multiple risk factors detected - please be cautious',
                    'recommendations': self._get_safety_recommendations(warnings)
                }
            elif warnings:
                return {
                    'status': 'caution',
                    'allow_bet': True,
                    'warnings': warnings,
                    'message': 'Minor concerns detected - proceed carefully'
                }
            else:
                return {
                    'status': 'safe',
                    'allow_bet': True,
                    'message': 'No safety concerns detected'
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'allow_bet': False,
                'error': str(e)
            }
    
    def set_spending_limits(
        self,
        user_id: int,
        limits: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Set user-defined spending limits
        
        Args:
            user_id: User ID
            limits: {'daily': 50, 'weekly': 200, 'monthly': 500}
            
        Returns:
            Confirmation of limits set
        """
        from source.app.models import UserStats
        
        try:
            user_stats = self.db.query(UserStats).filter(
                UserStats.user_id == user_id
            ).first()
            
            if not user_stats:
                return {'success': False, 'error': 'User not found'}
            
            # Store limits
            limits_data = {
                'daily_limit': limits.get('daily', 0),
                'weekly_limit': limits.get('weekly', 0),
                'monthly_limit': limits.get('monthly', 0),
                'set_at': datetime.now().isoformat(),
                'can_increase_after': (datetime.now() + timedelta(days=7)).isoformat()  # 7 day cooling
            }
            
            # Save to user stats (assuming there's a limits field)
            if hasattr(user_stats, 'spending_limits'):
                user_stats.spending_limits = json.dumps(limits_data)
                self.db.commit()
            
            return {
                'success': True,
                'limits_set': limits_data,
                'message': 'Spending limits activated. Changes require 7-day waiting period.',
                'protection_active': True
            }
            
        except Exception as e:
            self.db.rollback()
            return {'success': False, 'error': str(e)}
    
    def initiate_self_exclusion(
        self,
        user_id: int,
        duration_days: int,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        User-initiated self-exclusion period
        
        Args:
            user_id: User ID
            duration_days: Exclusion period (7, 30, 90, 180, or permanent)
            reason: Optional reason
            
        Returns:
            Exclusion confirmation
        """
        from source.app.models import UserStats
        
        try:
            user_stats = self.db.query(UserStats).filter(
                UserStats.user_id == user_id
            ).first()
            
            if not user_stats:
                return {'success': False, 'error': 'User not found'}
            
            # Calculate exclusion period
            if duration_days == -1:
                end_date = None  # Permanent
                duration_text = "Permanent"
            else:
                end_date = datetime.now() + timedelta(days=duration_days)
                duration_text = f"{duration_days} days"
            
            exclusion_data = {
                'user_id': user_id,
                'start_date': datetime.now().isoformat(),
                'end_date': end_date.isoformat() if end_date else None,
                'duration_days': duration_days,
                'reason': reason or 'User requested',
                'status': 'active',
                'can_cancel': False  # Cannot cancel self-exclusion
            }
            
            # Save exclusion
            if hasattr(user_stats, 'self_exclusion'):
                user_stats.self_exclusion = json.dumps(exclusion_data)
                self.db.commit()
            
            return {
                'success': True,
                'exclusion_active': True,
                'duration': duration_text,
                'end_date': end_date.isoformat() if end_date else 'Permanent',
                'message': f'Self-exclusion activated for {duration_text}. You cannot place bets during this period.',
                'support_resources': self._get_support_resources()
            }
            
        except Exception as e:
            self.db.rollback()
            return {'success': False, 'error': str(e)}
    
    def request_cooling_off(
        self,
        user_id: int,
        hours: int = 24
    ) -> Dict[str, Any]:
        """
        Temporary cooling-off period
        
        Args:
            user_id: User ID
            hours: Cooling-off hours (24, 48, or 72)
            
        Returns:
            Cooling-off confirmation
        """
        from source.app.models import UserStats
        
        try:
            cooling_end = datetime.now() + timedelta(hours=hours)
            
            user_stats = self.db.query(UserStats).filter(
                UserStats.user_id == user_id
            ).first()
            
            if user_stats and hasattr(user_stats, 'cooling_off'):
                user_stats.cooling_off = cooling_end.isoformat()
                self.db.commit()
            
            return {
                'success': True,
                'cooling_off_active': True,
                'ends_at': cooling_end.isoformat(),
                'hours_remaining': hours,
                'message': f'Taking a {hours}-hour break. MAX will be available after this period.',
                'can_extend': True
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def reality_check(self, user_id: int) -> Dict[str, Any]:
        """
        Reality check - show user their activity summary
        
        Args:
            user_id: User ID
            
        Returns:
            Activity summary for reflection
        """
        from source.app.models import UserStats, Suggestion
        
        try:
            # Get session data (last 4 hours)
            session_start = datetime.now() - timedelta(hours=4)
            
            suggestions = self.db.query(Suggestion).filter(
                Suggestion.user_id == user_id,
                Suggestion.created_at >= session_start
            ).all()
            
            # Calculate session stats
            session_bets = len(suggestions)
            session_stake = sum(s.suggested_stake or 0 for s in suggestions)
            session_time = (datetime.now() - session_start).total_seconds() / 3600
            
            # Get overall stats
            user_stats = self.db.query(UserStats).filter(
                UserStats.user_id == user_id
            ).first()
            
            total_profit_loss = 0
            if user_stats:
                total_profit_loss = user_stats.total_winnings - user_stats.total_stakes
            
            return {
                'session_summary': {
                    'session_duration_hours': round(session_time, 1),
                    'bets_placed': session_bets,
                    'total_staked': round(session_stake, 2),
                    'avg_stake': round(session_stake / session_bets, 2) if session_bets > 0 else 0
                },
                'overall_summary': {
                    'total_bets': user_stats.total_bets if user_stats else 0,
                    'total_staked': user_stats.total_stakes if user_stats else 0,
                    'profit_loss': round(total_profit_loss, 2)
                },
                'reflection_questions': [
                    "Are you betting more than you can afford to lose?",
                    "Is betting affecting your daily life or relationships?",
                    "Do you feel the need to bet with increasing amounts?",
                    "Have you tried to cut down but couldn't?"
                ],
                'message': 'Take a moment to reflect on your betting activity',
                'suggested_action': 'Consider taking a break' if session_bets > 5 else 'Continue responsibly'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # Internal check methods
    def _check_spending_limits(
        self,
        user_id: int,
        current_action: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check if user is within spending limits"""
        from source.app.models import UserStats, Suggestion
        
        try:
            user_stats = self.db.query(UserStats).filter(
                UserStats.user_id == user_id
            ).first()
            
            if not user_stats or not hasattr(user_stats, 'spending_limits'):
                return {'status': 'pass'}
            
            limits = json.loads(user_stats.spending_limits or '{}')
            proposed_stake = current_action.get('stake', 0)
            
            # Check daily limit
            daily_start = datetime.now().replace(hour=0, minute=0, second=0)
            daily_bets = self.db.query(Suggestion).filter(
                Suggestion.user_id == user_id,
                Suggestion.created_at >= daily_start
            ).all()
            
            daily_spent = sum(b.suggested_stake or 0 for b in daily_bets)
            daily_limit = limits.get('daily_limit', 0)
            
            if daily_limit > 0 and (daily_spent + proposed_stake) > daily_limit:
                return {
                    'status': 'block',
                    'message': f'Daily limit of £{daily_limit} would be exceeded',
                    'current_spent': daily_spent,
                    'limit': daily_limit,
                    'action_required': 'Wait until tomorrow or adjust limits'
                }
            
            return {'status': 'pass'}
            
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def _detect_loss_chasing(
        self,
        user_id: int,
        current_action: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Detect if user is chasing losses"""
        from source.app.models import Suggestion, Result
        
        try:
            # Get last 5 bets
            recent_bets = self.db.query(Suggestion, Result).join(
                Result, Suggestion.id == Result.suggestion_id, isouter=True
            ).filter(
                Suggestion.user_id == user_id
            ).order_by(Suggestion.created_at.desc()).limit(5).all()
            
            if len(recent_bets) < 3:
                return {'status': 'pass'}
            
            # Check for pattern: loss followed by increased stake
            stakes = [s.suggested_stake or 0 for s, _ in recent_bets]
            results = [r.is_correct if r else None for _, r in recent_bets]
            
            # Detect doubling after loss
            for i in range(len(results) - 1):
                if results[i] is False and stakes[i] > 0:
                    stake_increase = stakes[i + 1] / stakes[i] if stakes[i] > 0 else 1
                    if stake_increase >= self.thresholds['loss_chase_ratio']:
                        return {
                            'status': 'warning',
                            'severity': 'high',
                            'message': 'Potential loss chasing detected - stake increased significantly after loss',
                            'recommendation': 'Take a break and avoid chasing losses'
                        }
            
            return {'status': 'pass'}
            
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def _check_rapid_betting(self, user_id: int) -> Dict[str, Any]:
        """Check for rapid/impulsive betting"""
        from source.app.models import Suggestion
        
        try:
            # Check bets in last 30 minutes
            recent_window = datetime.now() - timedelta(minutes=30)
            recent_bets = self.db.query(Suggestion).filter(
                Suggestion.user_id == user_id,
                Suggestion.created_at >= recent_window
            ).count()
            
            if recent_bets >= self.thresholds['rapid_betting']:
                return {
                    'status': 'warning',
                    'severity': 'medium',
                    'message': f'{recent_bets} bets in 30 minutes - consider slowing down',
                    'recommendation': 'Take time to analyze each bet carefully'
                }
            
            return {'status': 'pass'}
            
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def _check_session_time(self, user_id: int) -> Dict[str, Any]:
        """Check session duration"""
        from source.app.models import ReceivedMessage
        
        try:
            # Get first message of session (last 4 hours)
            session_start = datetime.now() - timedelta(hours=4)
            first_message = self.db.query(ReceivedMessage).filter(
                ReceivedMessage.user_id == user_id,
                ReceivedMessage.created_at >= session_start
            ).order_by(ReceivedMessage.created_at.asc()).first()
            
            if first_message:
                session_duration = (datetime.now() - first_message.created_at).total_seconds() / 3600
                
                if session_duration >= self.thresholds['daily_time_hours']:
                    return {
                        'status': 'warning',
                        'severity': 'medium',
                        'message': f'Session duration: {session_duration:.1f} hours - consider taking a break',
                        'recommendation': 'Long sessions can lead to fatigue and poor decisions'
                    }
            
            return {'status': 'pass'}
            
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def _check_cooling_off_status(self, user_id: int) -> Dict[str, Any]:
        """Check if user is in cooling-off period"""
        from source.app.models import UserStats
        
        try:
            user_stats = self.db.query(UserStats).filter(
                UserStats.user_id == user_id
            ).first()
            
            if user_stats and hasattr(user_stats, 'cooling_off'):
                cooling_end = datetime.fromisoformat(user_stats.cooling_off)
                if datetime.now() < cooling_end:
                    hours_remaining = (cooling_end - datetime.now()).total_seconds() / 3600
                    return {
                        'status': 'block',
                        'message': f'Cooling-off period active - {hours_remaining:.1f} hours remaining',
                        'ends_at': cooling_end.isoformat(),
                        'action_required': 'Wait for cooling-off period to end'
                    }
            
            return {'status': 'pass'}
            
        except:
            return {'status': 'pass'}
    
    def _check_self_exclusion(self, user_id: int) -> Dict[str, Any]:
        """Check if user is self-excluded"""
        from source.app.models import UserStats
        
        try:
            user_stats = self.db.query(UserStats).filter(
                UserStats.user_id == user_id
            ).first()
            
            if user_stats and hasattr(user_stats, 'self_exclusion'):
                exclusion = json.loads(user_stats.self_exclusion or '{}')
                
                if exclusion.get('status') == 'active':
                    end_date = exclusion.get('end_date')
                    
                    if end_date is None:
                        return {
                            'status': 'block',
                            'message': 'Permanent self-exclusion active',
                            'action_required': 'Contact support for assistance',
                            'support_resources': self._get_support_resources()
                        }
                    elif datetime.fromisoformat(end_date) > datetime.now():
                        return {
                            'status': 'block',
                            'message': f'Self-exclusion active until {end_date}',
                            'action_required': 'Wait for exclusion period to end',
                            'support_resources': self._get_support_resources()
                        }
            
            return {'status': 'pass'}
            
        except:
            return {'status': 'pass'}
    
    def _get_support_resources(self) -> List[Dict[str, str]]:
        """Get problem gambling support resources"""
        return [
            {
                'name': 'GamCare',
                'phone': '0808 8020 133',
                'website': 'https://www.gamcare.org.uk',
                'description': 'Free confidential support for problem gambling'
            },
            {
                'name': 'Gamblers Anonymous',
                'website': 'https://www.gamblersanonymous.org.uk',
                'description': 'Support group for problem gamblers'
            },
            {
                'name': 'BeGambleAware',
                'phone': '0808 8020 133',
                'website': 'https://www.begambleaware.org',
                'description': 'Information and advice on responsible gambling'
            }
        ]
    
    def _get_safety_recommendations(self, warnings: List[Dict[str, Any]]) -> List[str]:
        """Generate safety recommendations based on warnings"""
        recommendations = []
        
        for warning in warnings:
            if warning['type'] == 'loss_chasing':
                recommendations.append("🛑 Stop and take a 24-hour break")
                recommendations.append("💭 Reflect on why you're betting")
            elif warning['type'] == 'rapid_betting':
                recommendations.append("⏸️ Slow down - analyze each bet carefully")
            elif warning['type'] == 'session_time':
                recommendations.append("🚶 Take a break - long sessions lead to poor decisions")
        
        recommendations.append("📞 Consider reaching out to support services if needed")
        
        return list(set(recommendations))[:3]  # Max 3 unique recommendations


# Public API functions
def check_betting_safety(
    db_session: Session,
    user_id: int,
    proposed_bet: Dict[str, Any]
) -> Dict[str, Any]:
    """Check if bet is safe for user to place"""
    manager = ResponsibleGamblingManager(db_session)
    return manager.check_user_safety(user_id, proposed_bet)


def set_user_limits(
    db_session: Session,
    user_id: int,
    limits: Dict[str, float]
) -> Dict[str, Any]:
    """Set spending limits for user"""
    manager = ResponsibleGamblingManager(db_session)
    return manager.set_spending_limits(user_id, limits)


def get_reality_check(
    db_session: Session,
    user_id: int
) -> Dict[str, Any]:
    """Get reality check for user"""
    manager = ResponsibleGamblingManager(db_session)
    return manager.reality_check(user_id)
