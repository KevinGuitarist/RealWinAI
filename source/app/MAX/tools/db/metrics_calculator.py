"""
Comprehensive Metrics Calculator for M.A.X. AI Agent
Implements all M.A.X. blueprint formulas for user metrics calculation
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func, text
import json

from source.app.MAX.models import (
    UserStats,
    ConversationStats,
    Suggestion,
    Result,
    ReceivedMessage,
    UserAction,
    BetOutcome,
    AgentState,
    PlayerPersona,
)
from source.app.users.models import User
from source.core.database import SessionLocal


class MetricsCalculator:
    """Comprehensive metrics calculator implementing M.A.X. blueprint formulas"""

    def __init__(self, db: Session = None):
        self.db = db or SessionLocal()
        self._should_close_db = db is None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._should_close_db:
            self.db.close()

    def calculate_all_metrics(self, user_id: int) -> Dict[str, Any]:
        """
        Calculate all user metrics comprehensively according to M.A.X. blueprint

        Returns complete metrics dictionary with all financial, behavioral,
        engagement, trust, and risk metrics calculated.
        """
        try:
            # Get all required data for calculations
            user_data = self._fetch_user_calculation_data(user_id)

            if not user_data:
                return self._get_default_metrics()

            # Calculate each category of metrics
            financial_metrics = self._calculate_financial_metrics(user_data)
            behavioral_metrics = self._calculate_behavioral_metrics(user_data)
            engagement_metrics = self._calculate_engagement_metrics(user_data)
            trust_metrics = self._calculate_trust_metrics(user_data)
            risk_metrics = self._calculate_risk_metrics(
                user_data, trust_metrics, financial_metrics
            )
            strategy_metrics = self._calculate_strategy_metrics(
                user_data, trust_metrics, risk_metrics
            )

            return {
                "financial_metrics": financial_metrics,
                "behavioral_metrics": behavioral_metrics,
                "engagement_metrics": engagement_metrics,
                "trust_metrics": trust_metrics,
                "risk_metrics": risk_metrics,
                "strategy_metrics": strategy_metrics,
                "calculation_timestamp": datetime.now(),
                "user_id": str(user_id),
            }

        except Exception as e:
            print(f"Error calculating metrics for user {user_id}: {e}")
            return self._get_default_metrics()

    def _fetch_user_calculation_data(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Fetch all data needed for metrics calculations"""
        try:
            # Get user basic info
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return None

            # Get all suggestions with results (last 6 months for comprehensive analysis)
            cutoff_date = datetime.now() - timedelta(days=180)

            suggestions = (
                self.db.query(Suggestion)
                .filter(
                    and_(
                        Suggestion.user_id == user_id,
                        Suggestion.timestamp >= cutoff_date,
                    )
                )
                .order_by(desc(Suggestion.timestamp))
                .all()
            )

            # Get results for suggestions
            suggestion_ids = [s.id for s in suggestions]
            results = []
            if suggestion_ids:
                results = (
                    self.db.query(Result)
                    .filter(Result.suggestion_id.in_(suggestion_ids))
                    .all()
                )

            # Get conversation data (last 3 months)
            conversation_cutoff = datetime.now() - timedelta(days=90)

            messages = (
                self.db.query(ReceivedMessage)
                .filter(
                    and_(
                        ReceivedMessage.user_id == user_id,
                        ReceivedMessage.timestamp >= conversation_cutoff,
                    )
                )
                .order_by(desc(ReceivedMessage.timestamp))
                .all()
            )

            # Get current stats
            user_stats = (
                self.db.query(UserStats).filter(UserStats.user_id == user_id).first()
            )
            conv_stats = (
                self.db.query(ConversationStats)
                .filter(ConversationStats.user_id == user_id)
                .first()
            )

            return {
                "user": user,
                "suggestions": suggestions,
                "results": results,
                "messages": messages,
                "user_stats": user_stats,
                "conv_stats": conv_stats,
                "account_age_days": (datetime.now() - user.account_creation_date).days,
            }

        except Exception as e:
            print(f"Error fetching calculation data: {e}")
            return None

    def _calculate_financial_metrics(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate comprehensive financial metrics following M.A.X. blueprint"""
        suggestions = data.get("suggestions", [])
        results = data.get("results", [])

        # Create results lookup
        results_by_suggestion = {r.suggestion_id: r for r in results}

        # Initialize metrics
        total_amount_spent = 0.0
        total_bets = 0
        total_profit_loss = 0.0
        stake_amounts = []
        wins = 0

        # Calculate from actual suggestions and results
        for suggestion in suggestions:
            if suggestion.user_action == UserAction.ACCEPTED:
                # Use actual stake if available, otherwise suggested stake
                stake = (
                    suggestion.actual_stake_used or suggestion.suggested_stake or 0.0
                )
                total_amount_spent += stake
                total_bets += 1
                stake_amounts.append(stake)

                # Check for results
                result = results_by_suggestion.get(suggestion.id)
                if result:
                    if result.final_outcome == BetOutcome.WIN:
                        wins += 1
                        total_profit_loss += result.profit_loss or 0.0
                    elif result.final_outcome == BetOutcome.LOSS:
                        total_profit_loss += (
                            result.profit_loss or 0.0
                        )  # Should be negative

        # Calculate derived metrics
        average_stake_size = (
            sum(stake_amounts) / len(stake_amounts) if stake_amounts else 0.0
        )
        win_rate = (wins / total_bets) if total_bets > 0 else 0.0
        roi_percentage = (
            ((total_profit_loss / total_amount_spent) * 100)
            if total_amount_spent > 0
            else 0.0
        )

        return {
            "total_amount_spent": round(total_amount_spent, 2),
            "average_stake_size": round(average_stake_size, 2),
            "net_profit_loss": round(total_profit_loss, 2),
            "total_bets": total_bets,
            "win_rate": round(win_rate, 3),
            "roi_percentage": round(roi_percentage, 2),
        }

    def _calculate_behavioral_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate behavioral patterns and preferences"""
        suggestions = data.get("suggestions", [])
        messages = data.get("messages", [])
        account_age_days = data.get("account_age_days", 1)

        # Calculate betting frequency (bets per day)
        accepted_suggestions = [
            s for s in suggestions if s.user_action == UserAction.ACCEPTED
        ]
        betting_frequency = len(accepted_suggestions) / max(account_age_days, 1)

        # Analyze sport and market preferences
        sport_counts = {}
        market_counts = {}
        stake_amounts = []

        for suggestion in accepted_suggestions:
            # Extract sport from suggestion (would need game_prediction joined data)
            # For now, use placeholder logic
            if hasattr(suggestion, "game_prediction") and suggestion.game_prediction:
                sport = getattr(suggestion.game_prediction, "sport", "Unknown")
                market = getattr(suggestion.game_prediction, "market", "Unknown")

                sport_counts[sport] = sport_counts.get(sport, 0) + 1
                market_counts[market] = market_counts.get(market, 0) + 1

            stake = suggestion.actual_stake_used or suggestion.suggested_stake or 0.0
            if stake > 0:
                stake_amounts.append(stake)

        # Get favorite sports and markets
        favorite_sports = sorted(
            sport_counts.items(), key=lambda x: x[1], reverse=True
        )[:3]
        favorite_markets = sorted(
            market_counts.items(), key=lambda x: x[1], reverse=True
        )[:3]

        # Determine betting pattern
        avg_stake = sum(stake_amounts) / len(stake_amounts) if stake_amounts else 0.0
        if avg_stake > 100:
            betting_pattern = "high_roller"
        elif betting_frequency > 0.5:  # More than 1 bet every 2 days
            betting_pattern = "frequent"
        else:
            betting_pattern = "casual"

        # Calculate stake range
        stake_range = {
            "min": min(stake_amounts) if stake_amounts else 0.0,
            "max": max(stake_amounts) if stake_amounts else 0.0,
        }

        return {
            "betting_frequency": round(betting_frequency, 3),
            "favorite_sports": [sport for sport, count in favorite_sports],
            "favorite_markets": [market for market, count in favorite_markets],
            "preferred_stake_range": stake_range,
            "betting_pattern": betting_pattern,
        }

    def _calculate_engagement_metrics(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate user engagement and activity metrics using actual session data"""
        messages = data.get("messages", [])
        user_stats = data.get("user_stats")
        user_id = data.get("user_id")

        # Calculate session-based metrics using actual session data
        session_metrics = self._calculate_session_metrics(user_id)
        
        # Days since last session
        last_message_date = (
            max([m.timestamp for m in messages])
            if messages
            else datetime.now() - timedelta(days=365)
        )
        days_since_last_session = (datetime.now() - last_message_date).days

        # Calculate conversation frequency (messages per week)
        if messages:
            date_range = (datetime.now() - min(m.timestamp for m in messages)).days
            weeks = max(date_range / 7, 1)
            conversation_frequency = len(messages) / weeks
        else:
            conversation_frequency = 0.0

        # Response rate (approximate)
        response_rate = min(conversation_frequency / 7, 1.0)  # Normalize to 0-1

        return {
            "days_since_last_session": days_since_last_session,
            "session_count": session_metrics["session_count"],
            "avg_session_duration": session_metrics["avg_session_length"],
            "total_engagement_time": session_metrics["total_engagement_time"],
            "conversation_frequency": round(conversation_frequency, 2),
            "response_rate": round(response_rate, 3),
        }

    def _calculate_session_metrics(self, user_id: str) -> Dict[str, float]:
        """Calculate precise session-based engagement metrics"""
        try:
            from source.app.MAX.models import ReceivedMessage, SentMessage
            
            # Get all unique sessions for this user from both message tables
            received_sessions = (
                self.db.query(ReceivedMessage.session_id, func.min(ReceivedMessage.timestamp).label("start_time"), 
                             func.max(ReceivedMessage.timestamp).label("end_time"))
                .filter(ReceivedMessage.user_id == user_id, ReceivedMessage.session_id.isnot(None))
                .group_by(ReceivedMessage.session_id)
                .all()
            )
            
            sent_sessions = (
                self.db.query(SentMessage.session_id, func.min(SentMessage.timestamp).label("start_time"),
                             func.max(SentMessage.timestamp).label("end_time"))
                .filter(SentMessage.user_id == user_id, SentMessage.session_id.isnot(None))
                .group_by(SentMessage.session_id)
                .all()
            )
            
            # Combine and deduplicate sessions
            all_sessions = {}
            for session in received_sessions:
                session_id = str(session.session_id)
                if session_id not in all_sessions:
                    all_sessions[session_id] = {"start": session.start_time, "end": session.end_time}
                else:
                    # Update start/end times to get the full session range
                    all_sessions[session_id]["start"] = min(all_sessions[session_id]["start"], session.start_time)
                    all_sessions[session_id]["end"] = max(all_sessions[session_id]["end"], session.end_time)
            
            for session in sent_sessions:
                session_id = str(session.session_id)
                if session_id not in all_sessions:
                    all_sessions[session_id] = {"start": session.start_time, "end": session.end_time}
                else:
                    # Update start/end times to get the full session range
                    all_sessions[session_id]["start"] = min(all_sessions[session_id]["start"], session.start_time)
                    all_sessions[session_id]["end"] = max(all_sessions[session_id]["end"], session.end_time)
            
            # Calculate metrics
            session_count = len(all_sessions)
            
            if session_count > 0:
                # Calculate session durations in minutes
                session_durations = []
                for session_data in all_sessions.values():
                    duration = (session_data["end"] - session_data["start"]).total_seconds() / 60
                    session_durations.append(max(duration, 0.1))  # Minimum 0.1 minute duration
                
                avg_session_length = sum(session_durations) / len(session_durations)
                total_engagement_time = sum(session_durations)
            else:
                avg_session_length = 0.0
                total_engagement_time = 0.0
            
            return {
                "session_count": session_count,
                "avg_session_length": round(avg_session_length, 2),
                "total_engagement_time": round(total_engagement_time, 2),
            }
            
        except Exception as e:
            print(f"Error calculating session metrics: {e}")
            # Fallback to existing logic if there's an error
            return {
                "session_count": 0,
                "avg_session_length": 0.0,
                "total_engagement_time": 0.0,
            }

    def start_session(self, user_id: int, session_id: str) -> bool:
        """Start a new chat session for user"""
        try:
            from source.app.MAX.models import UserStats
            
            user_stats = self.db.query(UserStats).filter(UserStats.user_id == user_id).first()
            if not user_stats:
                user_stats = UserStats(user_id=user_id)
                self.db.add(user_stats)
            
            # Set current session info
            user_stats.current_session_id = session_id
            user_stats.current_session_start_time = datetime.now()
            user_stats.last_activity_time = datetime.now()
            
            self.db.commit()
            return True
            
        except Exception as e:
            print(f"Error starting session: {e}")
            return False

    def end_session(self, user_id: int, session_id: str) -> bool:
        """End current chat session and update metrics"""
        try:
            from source.app.MAX.models import UserStats, ReceivedMessage, SentMessage
            
            user_stats = self.db.query(UserStats).filter(UserStats.user_id == user_id).first()
            if not user_stats or str(user_stats.current_session_id) != session_id:
                return False
            
            # Calculate actual session duration from message timestamps
            session_duration = 0
            if user_stats.current_session_start_time:
                # Get first and last message timestamps for this session
                first_received = self.db.query(ReceivedMessage)\
                    .filter(ReceivedMessage.user_id == user_id, ReceivedMessage.session_id == session_id)\
                    .order_by(ReceivedMessage.timestamp.asc())\
                    .first()
                
                last_received = self.db.query(ReceivedMessage)\
                    .filter(ReceivedMessage.user_id == user_id, ReceivedMessage.session_id == session_id)\
                    .order_by(ReceivedMessage.timestamp.desc())\
                    .first()
                
                # If we have messages, calculate duration from first to last message
                if first_received and last_received:
                    session_duration = (last_received.timestamp - first_received.timestamp).total_seconds() / 60
                else:
                    # Fallback to session start/end time
                    session_duration = (datetime.now() - user_stats.current_session_start_time).total_seconds() / 60
                
                # Update session metrics
                user_stats.session_count += 1
                
                # Update average session length (running average)
                if user_stats.avg_session_length == 0:
                    user_stats.avg_session_length = session_duration
                else:
                    # Calculate weighted average
                    total_time = user_stats.avg_session_length * (user_stats.session_count - 1)
                    user_stats.avg_session_length = (total_time + session_duration) / user_stats.session_count
                
                # Update total engagement time
                user_stats.total_engagement_time += session_duration
            
            # Clear current session info
            user_stats.current_session_id = None
            user_stats.current_session_start_time = None
            
            self.db.commit()
            return True
            
        except Exception as e:
            print(f"Error ending session: {e}")
            return False

    def update_session_activity(self, user_id: int, session_id: str) -> bool:
        """Update last activity time for current session"""
        try:
            from source.app.MAX.models import UserStats
            
            user_stats = self.db.query(UserStats).filter(UserStats.user_id == user_id).first()
            if user_stats and str(user_stats.current_session_id) == session_id:
                user_stats.last_activity_time = datetime.now()
                self.db.commit()
                return True
            return False
            
        except Exception as e:
            print(f"Error updating session activity: {e}")
            return False

    def _calculate_trust_metrics(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate trust and relationship metrics using M.A.X. blueprint formulas"""
        suggestions = data.get("suggestions", [])
        results = data.get("results", [])
        conv_stats = data.get("conv_stats")

        # Create results lookup
        results_by_suggestion = {r.suggestion_id: r for r in results}

        # Calculate Suggestion Acceptance Rate (SAR)
        total_suggestions = len(suggestions)
        accepted_suggestions = [
            s for s in suggestions if s.user_action == UserAction.ACCEPTED
        ]
        sar = (
            len(accepted_suggestions) / total_suggestions
            if total_suggestions > 0
            else 0.0
        )

        # Calculate Suggestion Success Rate (SSR) - success rate of ACCEPTED suggestions
        successful_accepted = 0
        for suggestion in accepted_suggestions:
            result = results_by_suggestion.get(suggestion.id)
            if result and result.final_outcome == BetOutcome.WIN:
                successful_accepted += 1

        ssr = (
            successful_accepted / len(accepted_suggestions)
            if accepted_suggestions
            else 0.0
        )

        # Calculate Missed Opportunity Value (MOV)
        mov = 0.0
        avg_stake = (
            sum([s.suggested_stake for s in accepted_suggestions])
            / len(accepted_suggestions)
            if accepted_suggestions
            else 10.0
        )

        for suggestion in suggestions:
            if suggestion.user_action == UserAction.IGNORED:
                result = results_by_suggestion.get(suggestion.id)
                if result and result.final_outcome == BetOutcome.WIN:
                    # Get actual odds from prediction data through legacy prediction lookup
                    odds = 2.0  # Default odds
                    
                    if suggestion.sport and suggestion.legacy_prediction_id:
                        # Get prediction data from legacy tables
                        prediction = self._get_legacy_prediction(suggestion)
                        if prediction:
                            pred_data = self._extract_prediction_data(prediction)
                            odds = pred_data.get("odds", 2.0)
                    
                    # MOV = (odds - 1) * average_stake for ignored winning suggestions
                    mov += (odds - 1) * avg_stake

        # Calculate Trust Score using M.A.X. blueprint formula
        # Trust = (0.6 × SAR) + (0.4 × SSR)
        trust_score = (0.6 * sar) + (0.4 * ssr)

        # Get conversation stats or use defaults
        confidence_level = conv_stats.confidence_level if conv_stats else 50.0
        empathy_level = conv_stats.empathy_level if conv_stats else 50.0

        return {
            "suggestion_acceptance_rate": round(sar, 3),
            "suggestion_success_rate": round(ssr, 3),
            "missed_opportunity_value": round(mov, 2),
            "trust_score": round(trust_score, 3),
            "confidence_level": confidence_level,
            "empathy_level": empathy_level,
        }

    def _calculate_risk_metrics(
        self, data: Dict[str, Any], trust_metrics: Dict, financial_metrics: Dict
    ) -> Dict[str, Any]:
        """Calculate risk assessment metrics using M.A.X. blueprint formulas"""
        suggestions = data.get("suggestions", [])
        results = data.get("results", [])

        # Calculate User Momentum Score
        # Momentum = NetProfitLoss/AvgStake + (WinRatio - 0.5) × 2
        net_profit_loss = financial_metrics.get("net_profit_loss", 0.0)
        avg_stake = financial_metrics.get("average_stake_size", 1.0)
        win_ratio = financial_metrics.get("win_rate", 0.5)

        momentum_component1 = net_profit_loss / avg_stake if avg_stake > 0 else 0.0
        momentum_component2 = (win_ratio - 0.5) * 2
        user_momentum_score = momentum_component1 + momentum_component2

        # Calculate Loss Chasing Index (LCI)
        # LCI = Average percentage stake increase after losses
        lci = 0.0
        stake_increases = []

        accepted_suggestions = [
            s for s in suggestions if s.user_action == UserAction.ACCEPTED
        ]
        results_by_suggestion = {r.suggestion_id: r for r in results}

        for i in range(1, len(accepted_suggestions)):
            prev_suggestion = accepted_suggestions[i - 1]
            curr_suggestion = accepted_suggestions[i]

            # Check if previous suggestion was a loss
            prev_result = results_by_suggestion.get(prev_suggestion.id)
            if prev_result and prev_result.final_outcome == BetOutcome.LOSS:
                prev_stake = (
                    prev_suggestion.actual_stake_used or prev_suggestion.suggested_stake
                )
                curr_stake = (
                    curr_suggestion.actual_stake_used or curr_suggestion.suggested_stake
                )

                if prev_stake and curr_stake and prev_stake > 0:
                    increase_ratio = (curr_stake / prev_stake) - 1
                    stake_increases.append(increase_ratio)

        lci = sum(stake_increases) / len(stake_increases) if stake_increases else 0.0

        # Calculate Churn Risk Score
        # Churn = w1(1-Trust) + w2(DaysSinceLastSession/T) - w3(Momentum)
        trust_score = trust_metrics.get("trust_score", 0.5)
        
        # Calculate days since last session from message data
        messages = data.get("messages", [])
        if messages:
            last_message_date = max([m.timestamp for m in messages])
            days_since_session = (datetime.now() - last_message_date).days
        else:
            days_since_session = 30  # Default to 30 days if no messages

        w1, w2, w3 = 0.4, 0.3, 0.3  # Weights
        T = 30  # Time normalization factor (30 days)

        churn_risk = (
            (w1 * (1 - trust_score))
            + (w2 * (days_since_session / T))
            - (w3 * max(0, user_momentum_score))
        )
        churn_risk = max(0.0, min(1.0, churn_risk))  # Bound between 0 and 1

        # Calculate sentiment trend (simplified)
        sentiment_trend = 0.0  # Would need sentiment analysis from messages

        # Determine risk level
        if churn_risk > 0.7 or lci > 0.5:
            risk_level = "HIGH"
        elif churn_risk > 0.4 or lci > 0.3:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        return {
            "churn_risk_score": round(churn_risk, 3),
            "loss_chasing_index": round(lci, 3),
            "user_momentum_score": round(user_momentum_score, 3),
            "sentiment_trend": sentiment_trend,
            "risk_level": risk_level,
        }

    def _calculate_strategy_metrics(
        self, data: Dict[str, Any], trust_metrics: Dict, risk_metrics: Dict
    ) -> Dict[str, str]:
        """Calculate agent strategy and personalization metrics"""
        financial_metrics = self._calculate_financial_metrics(data)

        # Determine agent state using M.A.X. blueprint logic
        trust_score = trust_metrics.get("trust_score", 0.5)
        momentum_score = risk_metrics.get("user_momentum_score", 0.0)
        churn_risk = risk_metrics.get("churn_risk_score", 0.3)
        loss_chasing = risk_metrics.get("loss_chasing_index", 0.0)

        # Agent state determination (blueprint logic)
        if loss_chasing > 0.5:
            current_agent_state = "GUARDIAN"
            intervention_needed = True
        elif momentum_score > 1.5 and trust_score > 0.6:
            current_agent_state = "AMPLIFIER"
            intervention_needed = False
        elif momentum_score < -1.5 or churn_risk > 0.7:
            current_agent_state = "COMFORTER"
            intervention_needed = False
        elif trust_score < 0.4:
            current_agent_state = "TRUST_BUILDER"
            intervention_needed = False
        else:
            current_agent_state = "GUIDE"
            intervention_needed = False

        # Determine player persona
        avg_stake = financial_metrics.get("average_stake_size", 0.0)
        betting_frequency = data.get("behavioral_metrics", {}).get(
            "betting_frequency", 0.0
        )

        if avg_stake > 100:
            player_persona = "high_roller"
        elif betting_frequency > 0.5:
            player_persona = "data_analyst"
        else:
            player_persona = "casual_fan"

        return {
            "current_agent_state": current_agent_state,
            "recommended_agent_state": current_agent_state,
            "player_persona": player_persona,
            "intervention_needed": intervention_needed,
        }

    def _get_legacy_prediction(self, suggestion):
        """Get prediction data from legacy tables based on suggestion sport and prediction ID."""
        if suggestion.sport == "cricket":
            from source.app.MAX.models import CricketPrediction
            return (
                self.db.query(CricketPrediction)
                .filter(CricketPrediction.id == suggestion.legacy_prediction_id)
                .first()
            )
        elif suggestion.sport == "football":
            from source.app.MAX.models import FootballPrediction
            return (
                self.db.query(FootballPrediction)
                .filter(FootballPrediction.id == suggestion.legacy_prediction_id)
                .first()
            )
        return None

    def _extract_prediction_data(self, prediction):
        """Extract prediction data from legacy prediction object."""
        if not prediction:
            return {
                "sport": "unknown",
                "market": "unknown", 
                "prediction_text": "",
                "odds": 2.0,
            }

        # Extract data from prediction JSONB field
        if hasattr(prediction, "prediction") and prediction.prediction:
            pred_data = (
                prediction.prediction if isinstance(prediction.prediction, dict) else {}
            )
            return {
                "sport": self._infer_sport_from_table(prediction),
                "market": pred_data.get("market", "unknown"),
                "prediction_text": pred_data.get("prediction_text")
                or pred_data.get("summary", ""),
                "odds": pred_data.get("odds", 2.0),
                "confidence": pred_data.get("confidence", 0.0),
                "reasoning": pred_data.get("reasoning", ""),
            }
        return {"sport": "unknown", "market": "unknown", "prediction_text": "", "odds": 2.0}

    def _infer_sport_from_table(self, prediction):
        """Infer sport from table name."""
        if hasattr(prediction, "__table__"):
            table_name = prediction.__table__.name
            if "cricket" in table_name:
                return "cricket"
            elif "football" in table_name:
                return "football"
        return "unknown"

    def _get_default_metrics(self) -> Dict[str, Any]:
        """Return default metrics when calculation fails"""
        return {
            "financial_metrics": {
                "total_amount_spent": 0.0,
                "average_stake_size": 0.0,
                "net_profit_loss": 0.0,
                "total_bets": 0,
                "win_rate": 0.0,
                "roi_percentage": 0.0,
            },
            "behavioral_metrics": {
                "betting_frequency": 0.0,
                "favorite_sports": [],
                "favorite_markets": [],
                "preferred_stake_range": {"min": 0.0, "max": 0.0},
                "betting_pattern": "casual",
            },
            "engagement_metrics": {
                "days_since_last_session": 365,
                "session_count": 0,
                "avg_session_duration": 0.0,
                "conversation_frequency": 0.0,
                "response_rate": 0.0,
            },
            "trust_metrics": {
                "suggestion_acceptance_rate": 0.0,
                "suggestion_success_rate": 0.0,
                "missed_opportunity_value": 0.0,
                "trust_score": 0.0,
                "confidence_level": 50.0,
                "empathy_level": 50.0,
            },
            "risk_metrics": {
                "churn_risk_score": 0.3,
                "loss_chasing_index": 0.0,
                "user_momentum_score": 0.0,
                "sentiment_trend": 0.0,
                "risk_level": "LOW",
            },
            "strategy_metrics": {
                "current_agent_state": "GUIDE",
                "recommended_agent_state": "GUIDE",
                "player_persona": "casual_fan",
                "intervention_needed": False,
            },
        }


def calculate_user_metrics(user_id: int, db: Session = None) -> Dict[str, Any]:
    """
    Convenience function to calculate all metrics for a user

    Args:
        user_id: User's unique identifier
        db: Optional database session

    Returns:
        Complete metrics dictionary
    """
    with MetricsCalculator(db) as calculator:
        return calculator.calculate_all_metrics(user_id)


def update_user_metrics_in_db(
    user_id: int, metrics: Dict[str, Any], db: Session = None
) -> bool:
    """
    Update user metrics in database tables

    Args:
        user_id: User's unique identifier
        metrics: Calculated metrics dictionary
        db: Optional database session

    Returns:
        Success status
    """
    if db is None:
        db = SessionLocal()
        close_db = True
    else:
        close_db = False

    try:
        # Update UserStats table
        user_stats = db.query(UserStats).filter(UserStats.user_id == user_id).first()
        if not user_stats:
            user_stats = UserStats(user_id=user_id)
            db.add(user_stats)

        # Update financial metrics
        fin_metrics = metrics.get("financial_metrics", {})
        user_stats.total_amount_spent = fin_metrics.get("total_amount_spent", 0.0)
        user_stats.average_stake_size = fin_metrics.get("average_stake_size", 0.0)
        user_stats.net_profit_loss = fin_metrics.get("net_profit_loss", 0.0)

        # Update behavioral metrics
        beh_metrics = metrics.get("behavioral_metrics", {})
        user_stats.betting_frequency = beh_metrics.get("betting_frequency", 0.0)
        user_stats.favorite_sports = json.dumps(beh_metrics.get("favorite_sports", []))
        user_stats.favorite_markets = json.dumps(
            beh_metrics.get("favorite_markets", [])
        )

        # Update engagement metrics (session-based)
        eng_metrics = metrics.get("engagement_metrics", {})
        user_stats.session_count = eng_metrics.get("session_count", 0)
        user_stats.avg_session_length = eng_metrics.get("avg_session_duration", 0.0)
        user_stats.total_engagement_time = eng_metrics.get("total_engagement_time", 0.0)
        user_stats.days_since_last_session = eng_metrics.get("days_since_last_session", 0)

        # Update risk metrics
        risk_metrics = metrics.get("risk_metrics", {})
        user_stats.churn_risk_score = risk_metrics.get("churn_risk_score", 0.0)
        user_stats.loss_chasing_index = risk_metrics.get("loss_chasing_index", 0.0)
        user_stats.user_momentum_score = risk_metrics.get("user_momentum_score", 0.0)

        # Update strategy metrics
        strategy_metrics = metrics.get("strategy_metrics", {})
        agent_state_str = strategy_metrics.get("current_agent_state", "GUIDE")
        try:
            user_stats.current_agent_state = AgentState[agent_state_str.upper()].value
        except KeyError:
            user_stats.current_agent_state = AgentState.GUIDE.value

        persona_str = strategy_metrics.get("player_persona", "casual_fan")
        try:
            user_stats.player_persona = PlayerPersona[persona_str.upper()].value
        except KeyError:
            user_stats.player_persona = PlayerPersona.CASUAL_FAN.value

        user_stats.updated_at = datetime.now()

        # Update ConversationStats table
        conv_stats = (
            db.query(ConversationStats)
            .filter(ConversationStats.user_id == user_id)
            .first()
        )
        if not conv_stats:
            conv_stats = ConversationStats(user_id=user_id)
            db.add(conv_stats)

        # Update trust metrics
        trust_metrics = metrics.get("trust_metrics", {})
        conv_stats.suggestion_acceptance_rate = trust_metrics.get(
            "suggestion_acceptance_rate", 0.0
        )
        conv_stats.suggestion_success_rate = trust_metrics.get(
            "suggestion_success_rate", 0.0
        )
        conv_stats.missed_opportunity_value = trust_metrics.get(
            "missed_opportunity_value", 0.0
        )
        conv_stats.trust_score = trust_metrics.get("trust_score", 0.0)
        conv_stats.confidence_level = trust_metrics.get("confidence_level", 50.0)
        conv_stats.empathy_level = trust_metrics.get("empathy_level", 50.0)

        conv_stats.sentiment_trend = risk_metrics.get("sentiment_trend", 0.0)
        conv_stats.last_calculated = datetime.now()

        db.commit()
        return True

    except Exception as e:
        print(f"Error updating metrics in database: {e}")
        db.rollback()
        return False

    finally:
        if close_db:
            db.close()
