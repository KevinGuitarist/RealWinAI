"""
M.A.X. Personalized Betting Strategies
Custom strategies tailored to each user's profile and goals
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import json
from collections import defaultdict


class PersonalizedStrategyManager:
    """
    Creates and manages personalized betting strategies for users
    
    Features:
    - Risk profile assessment
    - Custom stake sizing
    - Portfolio diversification
    - Bankroll management
    - Goal-based strategies
    """
    
    def __init__(self, db_session: Session):
        self.db = db_session
        
        # Strategy templates
        self.strategy_templates = {
            'conservative': {
                'name': 'Safe & Steady',
                'risk_level': 'low',
                'stake_percentage': 2,  # 2% of bankroll per bet
                'min_confidence': 75,
                'max_odds': 2.0,
                'max_daily_bets': 2,
                'focus': 'High confidence, lower odds'
            },
            'balanced': {
                'name': 'Balanced Growth',
                'risk_level': 'medium',
                'stake_percentage': 3,
                'min_confidence': 65,
                'max_odds': 3.0,
                'max_daily_bets': 3,
                'focus': 'Balance between safety and value'
            },
            'aggressive': {
                'name': 'High Risk High Reward',
                'risk_level': 'high',
                'stake_percentage': 5,
                'min_confidence': 55,
                'max_odds': 5.0,
                'max_daily_bets': 5,
                'focus': 'Value hunting, accepts higher variance'
            },
            'value_hunter': {
                'name': 'Value Betting',
                'risk_level': 'medium',
                'stake_percentage': 3,
                'min_confidence': 60,
                'min_ev_percentage': 5,  # Only positive EV bets
                'max_odds': 4.0,
                'max_daily_bets': 4,
                'focus': 'Positive expected value opportunities'
            }
        }
    
    def assess_risk_profile(
        self,
        user_id: int,
        questionnaire: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Assess user's risk profile through behavior and questionnaire
        
        Args:
            user_id: User to assess
            questionnaire: Optional risk questionnaire answers
            
        Returns:
            Risk profile with recommended strategy
        """
        from source.app.models import UserStats, ReceivedMessage, Suggestion
        
        try:
            # Get user stats
            user_stats = self.db.query(UserStats).filter(
                UserStats.user_id == user_id
            ).first()
            
            if not user_stats:
                # New user - use questionnaire or default
                return self._create_default_profile(questionnaire)
            
            # Analyze betting behavior
            suggestions = self.db.query(Suggestion).filter(
                Suggestion.user_id == user_id
            ).all()
            
            if len(suggestions) < 5:
                # Not enough data - use questionnaire
                return self._create_default_profile(questionnaire)
            
            # Calculate behavior metrics
            avg_stake = sum(s.suggested_stake or 0 for s in suggestions) / len(suggestions)
            avg_odds = sum(s.odds or 2.0 for s in suggestions) / len(suggestions)
            high_risk_count = sum(1 for s in suggestions if (s.odds or 0) > 3.0)
            
            # Determine risk appetite from behavior
            risk_ratio = high_risk_count / len(suggestions)
            
            if avg_odds < 2.0 and risk_ratio < 0.2:
                risk_profile = 'conservative'
            elif avg_odds > 3.0 or risk_ratio > 0.5:
                risk_profile = 'aggressive'
            else:
                risk_profile = 'balanced'
            
            # Get user's win rate
            win_rate = user_stats.total_wins / user_stats.total_bets if user_stats.total_bets > 0 else 0
            roi = ((user_stats.total_winnings - user_stats.total_stakes) / user_stats.total_stakes * 100) if user_stats.total_stakes > 0 else 0
            
            return {
                'user_id': user_id,
                'risk_profile': risk_profile,
                'recommended_strategy': risk_profile,
                'behavior_analysis': {
                    'total_bets': len(suggestions),
                    'avg_stake': round(avg_stake, 2),
                    'avg_odds': round(avg_odds, 2),
                    'high_risk_ratio': round(risk_ratio * 100, 2),
                    'win_rate': round(win_rate * 100, 2),
                    'roi': round(roi, 2)
                },
                'strategy_details': self.strategy_templates[risk_profile],
                'assessment_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def create_personalized_strategy(
        self,
        user_id: int,
        bankroll: float,
        goals: Dict[str, Any],
        risk_profile: str = 'balanced'
    ) -> Dict[str, Any]:
        """
        Create custom strategy for user
        
        Args:
            user_id: User ID
            bankroll: Available bankroll
            goals: User's betting goals
            risk_profile: Risk appetite
            
        Returns:
            Personalized strategy
        """
        
        # Get base template
        base_strategy = self.strategy_templates.get(risk_profile, self.strategy_templates['balanced'])
        
        # Calculate stake sizing
        stake_per_bet = bankroll * (base_strategy['stake_percentage'] / 100)
        max_daily_risk = stake_per_bet * base_strategy['max_daily_bets']
        
        # Adjust for goals
        if goals.get('target_monthly_return'):
            target = goals['target_monthly_return']
            # Calculate required win rate and adjustments
            strategy_adjustment = self._adjust_for_target(target, base_strategy, bankroll)
        else:
            strategy_adjustment = {}
        
        # Build personalized strategy
        strategy = {
            'user_id': user_id,
            'strategy_name': f"Personalized {base_strategy['name']}",
            'risk_profile': risk_profile,
            'bankroll_management': {
                'total_bankroll': bankroll,
                'stake_per_bet': round(stake_per_bet, 2),
                'stake_percentage': base_strategy['stake_percentage'],
                'max_daily_risk': round(max_daily_risk, 2),
                'max_daily_bets': base_strategy['max_daily_bets'],
                'reserve_fund': round(bankroll * 0.2, 2)  # 20% emergency fund
            },
            'bet_selection_criteria': {
                'min_confidence': base_strategy['min_confidence'],
                'max_odds': base_strategy['max_odds'],
                'min_ev_percentage': base_strategy.get('min_ev_percentage', 0),
                'preferred_markets': self._get_preferred_markets(risk_profile),
                'avoid_markets': ['exotic', 'novelty'] if risk_profile == 'conservative' else []
            },
            'portfolio_rules': {
                'max_same_sport_per_day': 2,
                'diversification': 'Spread across different matches',
                'correlation_limit': 'Avoid heavily correlated bets'
            },
            'goals': goals,
            'strategy_adjustment': strategy_adjustment,
            'rules': self._generate_strategy_rules(risk_profile, bankroll),
            'created_at': datetime.now().isoformat()
        }
        
        # Save strategy to database
        try:
            from source.app.models import UserStats
            user_stats = self.db.query(UserStats).filter(
                UserStats.user_id == user_id
            ).first()
            
            if user_stats:
                # Store strategy in user stats
                if hasattr(user_stats, 'strategy_data'):
                    user_stats.strategy_data = json.dumps(strategy)
                    self.db.commit()
        except:
            pass  # Strategy creation successful even if saving fails
        
        return strategy
    
    def get_bet_recommendation(
        self,
        user_id: int,
        prediction: Dict[str, Any],
        current_bankroll: float
    ) -> Dict[str, Any]:
        """
        Recommend if user should take bet based on their strategy
        
        Args:
            user_id: User ID
            prediction: Prediction details
            current_bankroll: Current bankroll
            
        Returns:
            Recommendation with reasoning
        """
        
        try:
            # Get user's strategy
            from source.app.models import UserStats
            user_stats = self.db.query(UserStats).filter(
                UserStats.user_id == user_id
            ).first()
            
            if not user_stats or not hasattr(user_stats, 'strategy_data'):
                # No strategy - use balanced default
                strategy = self.create_personalized_strategy(
                    user_id=user_id,
                    bankroll=current_bankroll,
                    goals={},
                    risk_profile='balanced'
                )
            else:
                strategy = json.loads(user_stats.strategy_data or '{}')
            
            # Extract criteria
            criteria = strategy['bet_selection_criteria']
            bankroll_rules = strategy['bankroll_management']
            
            # Check against criteria
            confidence = prediction.get('confidence', 0)
            odds = prediction.get('odds', 2.0)
            ev_percentage = prediction.get('ev_percentage', 0)
            
            # Evaluate
            passes = []
            fails = []
            
            if confidence >= criteria['min_confidence']:
                passes.append(f"✅ Confidence {confidence}% meets minimum {criteria['min_confidence']}%")
            else:
                fails.append(f"❌ Confidence {confidence}% below minimum {criteria['min_confidence']}%")
            
            if odds <= criteria['max_odds']:
                passes.append(f"✅ Odds {odds} within acceptable range")
            else:
                fails.append(f"❌ Odds {odds} too high (max {criteria['max_odds']})")
            
            if criteria.get('min_ev_percentage', 0) > 0:
                if ev_percentage >= criteria['min_ev_percentage']:
                    passes.append(f"✅ EV {ev_percentage}% is positive")
                else:
                    fails.append(f"❌ EV {ev_percentage}% below minimum {criteria['min_ev_percentage']}%")
            
            # Calculate recommended stake
            if len(fails) == 0:
                recommended_stake = bankroll_rules['stake_per_bet']
                
                # Adjust stake based on confidence
                if confidence >= 80:
                    recommended_stake *= 1.2  # 20% increase for high confidence
                elif confidence < 65:
                    recommended_stake *= 0.8  # 20% decrease for lower confidence
                
                recommended_stake = min(recommended_stake, current_bankroll * 0.05)  # Never more than 5%
                
                recommendation = 'TAKE BET'
                confidence_level = 'High'
            elif len(fails) == 1:
                recommended_stake = bankroll_rules['stake_per_bet'] * 0.5
                recommendation = 'CONSIDER (with smaller stake)'
                confidence_level = 'Medium'
            else:
                recommended_stake = 0
                recommendation = 'SKIP'
                confidence_level = 'Low'
            
            return {
                'recommendation': recommendation,
                'confidence_level': confidence_level,
                'recommended_stake': round(recommended_stake, 2),
                'reasoning': {
                    'passes': passes,
                    'concerns': fails,
                    'strategy_alignment': len(passes) / (len(passes) + len(fails)) * 100 if (passes or fails) else 0
                },
                'strategy_name': strategy.get('strategy_name', 'Default'),
                'risk_management': f"Stake represents {(recommended_stake/current_bankroll*100):.1f}% of bankroll"
            }
            
        except Exception as e:
            return {
                'recommendation': 'ERROR',
                'error': str(e)
            }
    
    def track_strategy_performance(
        self,
        user_id: int,
        days: int = 30
    ) -> Dict[str, Any]:
        """Track how well user's strategy is performing"""
        
        from source.app.models import Suggestion, Result
        
        try:
            # Get bets in time period
            suggestions = self.db.query(Suggestion, Result).join(
                Result, Suggestion.id == Result.suggestion_id, isouter=True
            ).filter(
                Suggestion.user_id == user_id,
                Suggestion.created_at >= datetime.now() - timedelta(days=days)
            ).all()
            
            if not suggestions:
                return {
                    'message': 'No betting activity in this period',
                    'days': days
                }
            
            # Calculate metrics
            total_bets = len(suggestions)
            total_stake = sum(s.suggested_stake or 0 for s, _ in suggestions)
            
            wins = sum(1 for _, r in suggestions if r and r.is_correct)
            total_return = sum(
                (s.suggested_stake or 0) * (s.odds or 2.0)
                for s, r in suggestions if r and r.is_correct
            )
            
            profit = total_return - total_stake
            roi = (profit / total_stake * 100) if total_stake > 0 else 0
            win_rate = (wins / total_bets * 100) if total_bets > 0 else 0
            
            # Check adherence to strategy
            from source.app.models import UserStats
            user_stats = self.db.query(UserStats).filter(
                UserStats.user_id == user_id
            ).first()
            
            strategy = {}
            if user_stats and hasattr(user_stats, 'strategy_data'):
                strategy = json.loads(user_stats.strategy_data or '{}')
            
            # Analyze strategy adherence
            adherence = self._analyze_strategy_adherence(suggestions, strategy)
            
            return {
                'period': f'Last {days} days',
                'performance': {
                    'total_bets': total_bets,
                    'wins': wins,
                    'win_rate': round(win_rate, 2),
                    'total_stake': round(total_stake, 2),
                    'total_return': round(total_return, 2),
                    'profit_loss': round(profit, 2),
                    'roi': round(roi, 2)
                },
                'strategy_adherence': adherence,
                'recommendations': self._generate_performance_recommendations(
                    roi, win_rate, adherence
                ),
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # Helper methods
    def _create_default_profile(self, questionnaire: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Create default profile for new users"""
        
        if questionnaire:
            # Use questionnaire to determine profile
            risk_score = sum(questionnaire.values()) / len(questionnaire) if questionnaire else 5
            
            if risk_score < 3:
                profile = 'conservative'
            elif risk_score > 7:
                profile = 'aggressive'
            else:
                profile = 'balanced'
        else:
            profile = 'balanced'  # Default to balanced
        
        return {
            'risk_profile': profile,
            'recommended_strategy': profile,
            'strategy_details': self.strategy_templates[profile],
            'note': 'Profile will be refined based on betting behavior',
            'assessment_date': datetime.now().isoformat()
        }
    
    def _adjust_for_target(
        self,
        target: float,
        base_strategy: Dict[str, Any],
        bankroll: float
    ) -> Dict[str, Any]:
        """Adjust strategy to meet target return"""
        
        required_roi = (target / bankroll) * 100
        
        if required_roi > 20:
            return {
                'warning': f'Target requires {required_roi:.0f}% ROI - very challenging',
                'recommendation': 'Consider lowering target or increasing bankroll'
            }
        elif required_roi > 10:
            return {
                'note': f'Target requires {required_roi:.0f}% ROI - requires disciplined value betting',
                'recommendation': 'Focus on positive EV bets only'
            }
        else:
            return {
                'note': f'Target requires {required_roi:.0f}% ROI - achievable with good strategy',
                'recommendation': 'Stick to your strategy consistently'
            }
    
    def _get_preferred_markets(self, risk_profile: str) -> List[str]:
        """Get preferred markets for risk profile"""
        
        if risk_profile == 'conservative':
            return ['match_winner', 'over_under_2.5']
        elif risk_profile == 'aggressive':
            return ['match_winner', 'over_under', 'btts', 'correct_score']
        else:
            return ['match_winner', 'over_under', 'btts']
    
    def _generate_strategy_rules(self, risk_profile: str, bankroll: float) -> List[str]:
        """Generate strategy rules"""
        
        rules = [
            f"Never bet more than 5% of bankroll on single bet",
            f"Take mandatory 48-hour break after losing 3 bets in a row",
            f"When bankroll drops 25%, reduce stake size proportionally",
            f"Never chase losses by increasing stakes",
            f"Review and adjust strategy monthly"
        ]
        
        if risk_profile == 'conservative':
            rules.append("Only bet on matches with 75%+ confidence")
            rules.append("Avoid odds above 2.0")
        elif risk_profile == 'aggressive':
            rules.append("Ensure every bet has positive expected value")
            rules.append("Diversify across multiple matches")
        
        return rules
    
    def _analyze_strategy_adherence(
        self,
        suggestions: List[Any],
        strategy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze how well user followed their strategy"""
        
        if not strategy:
            return {'note': 'No strategy defined'}
        
        criteria = strategy.get('bet_selection_criteria', {})
        bankroll_rules = strategy.get('bankroll_management', {})
        
        violations = []
        good_practices = []
        
        for suggestion, _ in suggestions:
            # Check confidence
            if hasattr(suggestion, 'confidence') and suggestion.confidence:
                if suggestion.confidence < criteria.get('min_confidence', 0):
                    violations.append("Bet below minimum confidence threshold")
                else:
                    good_practices.append("Maintained confidence standards")
            
            # Check odds
            if hasattr(suggestion, 'odds') and suggestion.odds:
                if suggestion.odds > criteria.get('max_odds', 10):
                    violations.append("Odds exceeded maximum")
        
        adherence_score = (len(good_practices) / (len(good_practices) + len(violations)) * 100) if (good_practices or violations) else 100
        
        return {
            'adherence_score': round(adherence_score, 2),
            'violations': len(violations),
            'good_practices': len(good_practices),
            'assessment': 'Excellent' if adherence_score >= 90 else 'Good' if adherence_score >= 70 else 'Needs Improvement'
        }
    
    def _generate_performance_recommendations(
        self,
        roi: float,
        win_rate: float,
        adherence: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations based on performance"""
        
        recommendations = []
        
        if roi < -10:
            recommendations.append("⚠️ Significant losses - consider taking a break to reassess")
        elif roi < 0:
            recommendations.append("📊 Slight losses - focus on higher confidence bets")
        elif roi > 10:
            recommendations.append("🎉 Strong performance - maintain your strategy!")
        
        if win_rate < 40:
            recommendations.append("🎯 Low win rate - be more selective with bets")
        elif win_rate > 60:
            recommendations.append("✅ Excellent win rate - keep up the good work!")
        
        if adherence.get('adherence_score', 100) < 70:
            recommendations.append("📋 Improve strategy adherence for better results")
        
        return recommendations


# Public API functions
def create_user_strategy(
    db_session: Session,
    user_id: int,
    bankroll: float,
    goals: Dict[str, Any],
    risk_profile: str = 'balanced'
) -> Dict[str, Any]:
    """Create personalized strategy for user"""
    manager = PersonalizedStrategyManager(db_session)
    return manager.create_personalized_strategy(user_id, bankroll, goals, risk_profile)


def get_bet_recommendation_for_user(
    db_session: Session,
    user_id: int,
    prediction: Dict[str, Any],
    current_bankroll: float
) -> Dict[str, Any]:
    """Get bet recommendation based on user's strategy"""
    manager = PersonalizedStrategyManager(db_session)
    return manager.get_bet_recommendation(user_id, prediction, current_bankroll)
