"""
M.A.X. Advanced Analytics Dashboard Backend
Deep performance insights and data visualization support
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
import json
from collections import defaultdict
import statistics


class AnalyticsDashboardManager:
    """
    Provides comprehensive analytics for betting performance
    
    Features:
    - Win rate trends
    - ROI analysis by sport/market/time
    - Bankroll tracking
    - Profit/loss graphs
    - Comparative benchmarking
    - Risk-adjusted returns
    """
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def get_comprehensive_analytics(
        self,
        user_id: int,
        timeframe: str = '30d'
    ) -> Dict[str, Any]:
        """
        Get complete analytics dashboard data
        
        Args:
            user_id: User ID
            timeframe: '7d', '30d', '90d', '1y', 'all'
            
        Returns:
            Complete analytics data
        """
        
        days = self._parse_timeframe(timeframe)
        
        return {
            'user_id': user_id,
            'timeframe': timeframe,
            'overview': self.get_performance_overview(user_id, days),
            'trends': self.get_performance_trends(user_id, days),
            'breakdown': self.get_performance_breakdown(user_id, days),
            'risk_metrics': self.get_risk_metrics(user_id, days),
            'benchmarking': self.get_comparative_benchmarking(user_id, days),
            'insights': self.generate_insights(user_id, days),
            'generated_at': datetime.now().isoformat()
        }
    
    def get_performance_overview(
        self,
        user_id: int,
        days: int
    ) -> Dict[str, Any]:
        """Get high-level performance overview"""
        from source.app.models import UserStats, Suggestion, Result
        
        try:
            # Get user stats
            user_stats = self.db.query(UserStats).filter(
                UserStats.user_id == user_id
            ).first()
            
            if not user_stats:
                return {'message': 'No data available'}
            
            # Get suggestions in timeframe
            cutoff = datetime.now() - timedelta(days=days)
            suggestions = self.db.query(Suggestion, Result).join(
                Result, Suggestion.id == Result.suggestion_id, isouter=True
            ).filter(
                Suggestion.user_id == user_id,
                Suggestion.created_at >= cutoff
            ).all()
            
            # Calculate metrics
            total_bets = len(suggestions)
            verified_bets = sum(1 for _, r in suggestions if r and r.verified_at)
            wins = sum(1 for _, r in suggestions if r and r.is_correct)
            
            total_stake = sum(s.suggested_stake or 0 for s, _ in suggestions)
            total_return = sum(
                (s.suggested_stake or 0) * (s.odds or 2.0)
                for s, r in suggestions if r and r.is_correct
            )
            
            profit = total_return - total_stake
            roi = (profit / total_stake * 100) if total_stake > 0 else 0
            win_rate = (wins / verified_bets * 100) if verified_bets > 0 else 0
            
            # Average odds
            avg_odds = sum(s.odds or 2.0 for s, _ in suggestions) / total_bets if total_bets > 0 else 0
            
            # Longest streaks
            win_streak, loss_streak = self._calculate_streaks(suggestions)
            
            return {
                'total_bets': total_bets,
                'verified_bets': verified_bets,
                'pending_bets': total_bets - verified_bets,
                'wins': wins,
                'losses': verified_bets - wins,
                'win_rate': round(win_rate, 2),
                'total_stake': round(total_stake, 2),
                'total_return': round(total_return, 2),
                'profit_loss': round(profit, 2),
                'roi': round(roi, 2),
                'avg_odds': round(avg_odds, 2),
                'avg_stake': round(total_stake / total_bets, 2) if total_bets > 0 else 0,
                'longest_win_streak': win_streak,
                'longest_loss_streak': loss_streak,
                'status': 'Profitable' if profit > 0 else 'Loss' if profit < 0 else 'Break-even'
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def get_performance_trends(
        self,
        user_id: int,
        days: int
    ) -> Dict[str, Any]:
        """Get performance trends over time"""
        from source.app.models import Suggestion, Result
        
        try:
            cutoff = datetime.now() - timedelta(days=days)
            suggestions = self.db.query(Suggestion, Result).join(
                Result, Suggestion.id == Result.suggestion_id, isouter=True
            ).filter(
                Suggestion.user_id == user_id,
                Suggestion.created_at >= cutoff
            ).order_by(Suggestion.created_at.asc()).all()
            
            # Group by day
            daily_data = defaultdict(lambda: {
                'bets': 0, 'wins': 0, 'stake': 0, 'return': 0, 'profit': 0
            })
            
            cumulative_profit = 0
            cumulative_data = []
            
            for suggestion, result in suggestions:
                date_key = suggestion.created_at.date().isoformat()
                stake = suggestion.suggested_stake or 0
                
                daily_data[date_key]['bets'] += 1
                daily_data[date_key]['stake'] += stake
                
                if result and result.is_correct:
                    daily_data[date_key]['wins'] += 1
                    ret = stake * (suggestion.odds or 2.0)
                    daily_data[date_key]['return'] += ret
                    daily_data[date_key]['profit'] += (ret - stake)
                    cumulative_profit += (ret - stake)
                elif result:
                    daily_data[date_key]['profit'] -= stake
                    cumulative_profit -= stake
                
                cumulative_data.append({
                    'date': suggestion.created_at.isoformat(),
                    'cumulative_profit': round(cumulative_profit, 2)
                })
            
            # Format for graphing
            daily_trends = []
            for date, data in sorted(daily_data.items()):
                win_rate = (data['wins'] / data['bets'] * 100) if data['bets'] > 0 else 0
                roi = (data['profit'] / data['stake'] * 100) if data['stake'] > 0 else 0
                
                daily_trends.append({
                    'date': date,
                    'bets': data['bets'],
                    'wins': data['wins'],
                    'win_rate': round(win_rate, 2),
                    'stake': round(data['stake'], 2),
                    'profit': round(data['profit'], 2),
                    'roi': round(roi, 2)
                })
            
            return {
                'daily_performance': daily_trends,
                'cumulative_profit': cumulative_data,
                'trend_direction': 'Upward' if cumulative_profit > 0 else 'Downward' if cumulative_profit < 0 else 'Flat'
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def get_performance_breakdown(
        self,
        user_id: int,
        days: int
    ) -> Dict[str, Any]:
        """Break down performance by sport, market, odds range"""
        from source.app.models import Suggestion, Result
        
        try:
            cutoff = datetime.now() - timedelta(days=days)
            suggestions = self.db.query(Suggestion, Result).join(
                Result, Suggestion.id == Result.suggestion_id, isouter=True
            ).filter(
                Suggestion.user_id == user_id,
                Suggestion.created_at >= cutoff,
                Result.verified_at.isnot(None)
            ).all()
            
            # By sport
            by_sport = defaultdict(lambda: {'bets': 0, 'wins': 0, 'stake': 0, 'return': 0})
            
            # By odds range
            by_odds = defaultdict(lambda: {'bets': 0, 'wins': 0, 'stake': 0, 'return': 0})
            
            # By confidence level
            by_confidence = defaultdict(lambda: {'bets': 0, 'wins': 0, 'stake': 0, 'return': 0})
            
            # By day of week
            by_day = defaultdict(lambda: {'bets': 0, 'wins': 0, 'stake': 0, 'return': 0})
            
            for suggestion, result in suggestions:
                sport = suggestion.sport or 'Unknown'
                stake = suggestion.suggested_stake or 0
                odds = suggestion.odds or 2.0
                confidence = suggestion.confidence or 50
                day = suggestion.created_at.strftime('%A')
                
                # Sport breakdown
                by_sport[sport]['bets'] += 1
                by_sport[sport]['stake'] += stake
                if result.is_correct:
                    by_sport[sport]['wins'] += 1
                    by_sport[sport]['return'] += stake * odds
                
                # Odds range breakdown
                if odds < 1.5:
                    odds_range = 'Low (<1.5)'
                elif odds < 2.0:
                    odds_range = 'Medium (1.5-2.0)'
                elif odds < 3.0:
                    odds_range = 'High (2.0-3.0)'
                else:
                    odds_range = 'Very High (3.0+)'
                
                by_odds[odds_range]['bets'] += 1
                by_odds[odds_range]['stake'] += stake
                if result.is_correct:
                    by_odds[odds_range]['wins'] += 1
                    by_odds[odds_range]['return'] += stake * odds
                
                # Confidence breakdown
                if confidence >= 80:
                    conf_level = 'High (80-100%)'
                elif confidence >= 60:
                    conf_level = 'Medium (60-79%)'
                else:
                    conf_level = 'Low (<60%)'
                
                by_confidence[conf_level]['bets'] += 1
                by_confidence[conf_level]['stake'] += stake
                if result.is_correct:
                    by_confidence[conf_level]['wins'] += 1
                    by_confidence[conf_level]['return'] += stake * odds
                
                # Day of week breakdown
                by_day[day]['bets'] += 1
                by_day[day]['stake'] += stake
                if result.is_correct:
                    by_day[day]['wins'] += 1
                    by_day[day]['return'] += stake * odds
            
            # Format results
            return {
                'by_sport': self._format_breakdown(by_sport),
                'by_odds_range': self._format_breakdown(by_odds),
                'by_confidence_level': self._format_breakdown(by_confidence),
                'by_day_of_week': self._format_breakdown(by_day)
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def get_risk_metrics(
        self,
        user_id: int,
        days: int
    ) -> Dict[str, Any]:
        """Calculate risk-adjusted performance metrics"""
        from source.app.models import Suggestion, Result
        
        try:
            cutoff = datetime.now() - timedelta(days=days)
            suggestions = self.db.query(Suggestion, Result).join(
                Result, Suggestion.id == Result.suggestion_id, isouter=True
            ).filter(
                Suggestion.user_id == user_id,
                Suggestion.created_at >= cutoff,
                Result.verified_at.isnot(None)
            ).all()
            
            if not suggestions:
                return {'message': 'No verified bets in period'}
            
            # Calculate daily returns
            daily_returns = defaultdict(float)
            for suggestion, result in suggestions:
                date = suggestion.created_at.date()
                stake = suggestion.suggested_stake or 0
                
                if result.is_correct:
                    profit = stake * ((suggestion.odds or 2.0) - 1)
                else:
                    profit = -stake
                
                daily_returns[date] += profit
            
            returns_list = list(daily_returns.values())
            
            # Calculate metrics
            avg_return = statistics.mean(returns_list) if returns_list else 0
            std_return = statistics.stdev(returns_list) if len(returns_list) > 1 else 0
            
            # Sharpe Ratio (assuming 0% risk-free rate)
            sharpe_ratio = (avg_return / std_return) if std_return > 0 else 0
            
            # Max drawdown
            cumulative = 0
            peak = 0
            max_drawdown = 0
            
            for ret in returns_list:
                cumulative += ret
                peak = max(peak, cumulative)
                drawdown = peak - cumulative
                max_drawdown = max(max_drawdown, drawdown)
            
            # Win/Loss ratio
            wins = [r for r in returns_list if r > 0]
            losses = [abs(r) for r in returns_list if r < 0]
            
            avg_win = statistics.mean(wins) if wins else 0
            avg_loss = statistics.mean(losses) if losses else 0
            win_loss_ratio = (avg_win / avg_loss) if avg_loss > 0 else 0
            
            # Profit factor
            total_wins = sum(wins)
            total_losses = sum(losses)
            profit_factor = (total_wins / total_losses) if total_losses > 0 else 0
            
            return {
                'volatility': round(std_return, 2),
                'sharpe_ratio': round(sharpe_ratio, 3),
                'max_drawdown': round(max_drawdown, 2),
                'avg_win': round(avg_win, 2),
                'avg_loss': round(avg_loss, 2),
                'win_loss_ratio': round(win_loss_ratio, 2),
                'profit_factor': round(profit_factor, 2),
                'risk_assessment': self._assess_risk_level(sharpe_ratio, max_drawdown)
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def get_comparative_benchmarking(
        self,
        user_id: int,
        days: int
    ) -> Dict[str, Any]:
        """Compare user performance to platform averages"""
        from source.app.models import UserStats, Suggestion, Result
        
        try:
            # User stats
            user_overview = self.get_performance_overview(user_id, days)
            
            # Platform averages (all users)
            cutoff = datetime.now() - timedelta(days=days)
            
            all_suggestions = self.db.query(Suggestion, Result).join(
                Result, Suggestion.id == Result.suggestion_id, isouter=True
            ).filter(
                Suggestion.created_at >= cutoff,
                Result.verified_at.isnot(None)
            ).all()
            
            if not all_suggestions:
                return {'message': 'No platform data available'}
            
            platform_wins = sum(1 for _, r in all_suggestions if r and r.is_correct)
            platform_total = len(all_suggestions)
            platform_win_rate = (platform_wins / platform_total * 100) if platform_total > 0 else 0
            
            platform_stake = sum(s.suggested_stake or 0 for s, _ in all_suggestions)
            platform_return = sum(
                (s.suggested_stake or 0) * (s.odds or 2.0)
                for s, r in all_suggestions if r and r.is_correct
            )
            platform_roi = ((platform_return - platform_stake) / platform_stake * 100) if platform_stake > 0 else 0
            
            # Comparison
            user_win_rate = user_overview.get('win_rate', 0)
            user_roi = user_overview.get('roi', 0)
            
            return {
                'user_metrics': {
                    'win_rate': user_win_rate,
                    'roi': user_roi
                },
                'platform_averages': {
                    'win_rate': round(platform_win_rate, 2),
                    'roi': round(platform_roi, 2)
                },
                'comparison': {
                    'win_rate_vs_avg': round(user_win_rate - platform_win_rate, 2),
                    'roi_vs_avg': round(user_roi - platform_roi, 2),
                    'performance': 'Above Average' if user_roi > platform_roi else 'Below Average' if user_roi < platform_roi else 'Average'
                },
                'percentile': self._calculate_percentile(user_roi, all_suggestions)
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def generate_insights(
        self,
        user_id: int,
        days: int
    ) -> List[str]:
        """Generate actionable insights"""
        
        overview = self.get_performance_overview(user_id, days)
        breakdown = self.get_performance_breakdown(user_id, days)
        risk = self.get_risk_metrics(user_id, days)
        
        insights = []
        
        # Win rate insights
        win_rate = overview.get('win_rate', 0)
        if win_rate > 60:
            insights.append(f"🎯 Excellent {win_rate:.1f}% win rate - you're making great predictions!")
        elif win_rate < 45:
            insights.append(f"📊 Win rate at {win_rate:.1f}% - focus on higher confidence bets")
        
        # ROI insights
        roi = overview.get('roi', 0)
        if roi > 10:
            insights.append(f"💰 Strong {roi:.1f}% ROI - your strategy is working!")
        elif roi < -10:
            insights.append(f"⚠️ Negative {roi:.1f}% ROI - consider revising your approach")
        
        # Sport performance
        if 'by_sport' in breakdown:
            best_sport = max(breakdown['by_sport'], key=lambda x: x['roi']) if breakdown['by_sport'] else None
            if best_sport:
                insights.append(f"🏆 Best performance in {best_sport['category']}: {best_sport['roi']:.1f}% ROI")
        
        # Risk insights
        if 'max_drawdown' in risk:
            if risk['max_drawdown'] > 50:
                insights.append(f"📉 High drawdown of £{risk['max_drawdown']:.2f} - manage your bankroll carefully")
        
        # Odds insights
        if 'by_odds_range' in breakdown:
            best_odds = max(breakdown['by_odds_range'], key=lambda x: x['win_rate']) if breakdown['by_odds_range'] else None
            if best_odds:
                insights.append(f"🎲 Best win rate in {best_odds['category']} odds range: {best_odds['win_rate']:.1f}%")
        
        return insights[:5]  # Top 5 insights
    
    # Helper methods
    def _parse_timeframe(self, timeframe: str) -> int:
        """Convert timeframe to days"""
        mapping = {
            '7d': 7,
            '30d': 30,
            '90d': 90,
            '1y': 365,
            'all': 10000
        }
        return mapping.get(timeframe, 30)
    
    def _calculate_streaks(self, suggestions: List[Any]) -> tuple:
        """Calculate longest win/loss streaks"""
        current_win_streak = 0
        current_loss_streak = 0
        max_win_streak = 0
        max_loss_streak = 0
        
        for _, result in suggestions:
            if result and result.verified_at:
                if result.is_correct:
                    current_win_streak += 1
                    current_loss_streak = 0
                    max_win_streak = max(max_win_streak, current_win_streak)
                else:
                    current_loss_streak += 1
                    current_win_streak = 0
                    max_loss_streak = max(max_loss_streak, current_loss_streak)
        
        return max_win_streak, max_loss_streak
    
    def _format_breakdown(self, data: Dict) -> List[Dict[str, Any]]:
        """Format breakdown data for display"""
        results = []
        for category, metrics in data.items():
            win_rate = (metrics['wins'] / metrics['bets'] * 100) if metrics['bets'] > 0 else 0
            profit = metrics['return'] - metrics['stake']
            roi = (profit / metrics['stake'] * 100) if metrics['stake'] > 0 else 0
            
            results.append({
                'category': category,
                'bets': metrics['bets'],
                'wins': metrics['wins'],
                'win_rate': round(win_rate, 2),
                'stake': round(metrics['stake'], 2),
                'profit': round(profit, 2),
                'roi': round(roi, 2)
            })
        
        # Sort by ROI descending
        return sorted(results, key=lambda x: x['roi'], reverse=True)
    
    def _assess_risk_level(self, sharpe_ratio: float, max_drawdown: float) -> str:
        """Assess overall risk level"""
        if sharpe_ratio > 1.5 and max_drawdown < 30:
            return 'Low Risk, Good Returns'
        elif sharpe_ratio > 0.5:
            return 'Moderate Risk'
        else:
            return 'High Risk'
    
    def _calculate_percentile(self, user_roi: float, all_suggestions: List[Any]) -> int:
        """Calculate user's performance percentile"""
        # Simplified percentile calculation
        if user_roi > 10:
            return 90
        elif user_roi > 5:
            return 75
        elif user_roi > 0:
            return 60
        elif user_roi > -5:
            return 40
        else:
            return 25


# Public API function
def get_user_analytics(
    db_session: Session,
    user_id: int,
    timeframe: str = '30d'
) -> Dict[str, Any]:
    """Get comprehensive analytics for user"""
    manager = AnalyticsDashboardManager(db_session)
    return manager.get_comprehensive_analytics(user_id, timeframe)
