"""
MAX Memory System
================
Comprehensive memory and context retention system for tracking user bets,
preferences, conversation history, and providing personalized experiences.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict, field
from enum import Enum
import asyncio
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BetStatus(Enum):
    """Status of a bet"""

    PENDING = "pending"
    WON = "won"
    LOST = "lost"
    VOID = "void"
    CASHED_OUT = "cashed_out"


class RiskLevel(Enum):
    """Risk level preferences"""

    SAFE = "safe"
    MEDIUM = "medium"
    RISKY = "risky"


@dataclass
class UserBet:
    """Individual bet record"""

    bet_id: str
    user_id: str
    timestamp: datetime
    sport: str
    market: str
    selection: str
    odds: float
    stake: float
    potential_return: float
    status: BetStatus
    result: Optional[str] = None
    profit_loss: Optional[float] = None
    match_details: Optional[Dict] = None
    notes: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        data["status"] = self.status.value
        return data


@dataclass
class UserSession:
    """User session data"""

    session_id: str
    user_id: str
    start_time: datetime
    last_activity: datetime
    messages_count: int = 0
    bets_placed: int = 0
    topics_discussed: List[str] = field(default_factory=list)
    risk_preference: Optional[RiskLevel] = None
    sport_preference: Optional[str] = None
    active: bool = True


@dataclass
class UserPreferences:
    """User preferences and settings"""

    user_id: str
    preferred_sports: List[str] = field(default_factory=list)
    preferred_markets: List[str] = field(default_factory=list)
    risk_level: RiskLevel = RiskLevel.MEDIUM
    default_stake: float = 10.0
    bankroll: float = 1000.0
    notification_preferences: Dict = field(default_factory=dict)
    language: str = "en"
    timezone: str = "UTC"
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class UserStats:
    """User betting statistics"""

    user_id: str
    total_bets: int = 0
    won_bets: int = 0
    lost_bets: int = 0
    pending_bets: int = 0
    total_staked: float = 0.0
    total_returns: float = 0.0
    total_profit: float = 0.0
    win_rate: float = 0.0
    roi: float = 0.0
    average_odds: float = 0.0
    biggest_win: float = 0.0
    biggest_loss: float = 0.0
    current_streak: int = 0
    streak_type: str = "none"  # win, loss, none
    favorite_sport: Optional[str] = None
    favorite_market: Optional[str] = None
    last_bet_date: Optional[datetime] = None


class MaxMemorySystem:
    """
    MAX Memory System

    Features:
    - User bet tracking and history
    - Session management
    - Preference storage
    - Statistics calculation
    - Context retention
    - Conversation history
    - Personalization engine
    """

    def __init__(self, storage_backend: Optional[Any] = None):
        """
        Initialize memory system

        Args:
            storage_backend: Optional database connection for persistent storage
        """
        self.storage_backend = storage_backend

        # In-memory storage (cache)
        self.user_bets: Dict[str, List[UserBet]] = defaultdict(list)
        self.user_sessions: Dict[str, UserSession] = {}
        self.user_preferences: Dict[str, UserPreferences] = {}
        self.user_stats: Dict[str, UserStats] = {}
        self.conversation_history: Dict[str, List[Dict]] = defaultdict(list)

        # Configuration
        self.max_history_length = 100
        self.session_timeout_minutes = 60

        logger.info("MAX Memory System initialized")

    # ==================== BET TRACKING ====================

    async def record_bet(
        self,
        user_id: str,
        sport: str,
        market: str,
        selection: str,
        odds: float,
        stake: float,
        match_details: Optional[Dict] = None,
        notes: Optional[str] = None,
    ) -> UserBet:
        """
        Record a new bet

        Args:
            user_id: User identifier
            sport: Sport type (cricket, football)
            market: Betting market (match_winner, over_under, etc.)
            selection: Specific selection
            odds: Odds value
            stake: Stake amount
            match_details: Optional match information
            notes: Optional notes

        Returns:
            UserBet object
        """
        try:
            bet = UserBet(
                bet_id=f"bet_{user_id}_{datetime.now().timestamp()}",
                user_id=user_id,
                timestamp=datetime.now(),
                sport=sport,
                market=market,
                selection=selection,
                odds=odds,
                stake=stake,
                potential_return=stake * odds,
                status=BetStatus.PENDING,
                match_details=match_details,
                notes=notes,
            )

            # Store in memory
            self.user_bets[user_id].append(bet)

            # Update statistics
            await self._update_user_stats(user_id)

            # Persist to database if available
            if self.storage_backend:
                await self._persist_bet(bet)

            logger.info(f"Recorded bet {bet.bet_id} for user {user_id}")
            return bet

        except Exception as e:
            logger.error(f"Error recording bet: {e}")
            raise

    async def update_bet_result(
        self,
        bet_id: str,
        status: BetStatus,
        result: Optional[str] = None,
        profit_loss: Optional[float] = None,
    ) -> bool:
        """
        Update bet result

        Args:
            bet_id: Bet identifier
            status: New status
            result: Result description
            profit_loss: Actual profit/loss

        Returns:
            True if updated successfully
        """
        try:
            # Find the bet
            for user_id, bets in self.user_bets.items():
                for bet in bets:
                    if bet.bet_id == bet_id:
                        bet.status = status
                        bet.result = result

                        if profit_loss is not None:
                            bet.profit_loss = profit_loss
                        elif status == BetStatus.WON:
                            bet.profit_loss = bet.potential_return - bet.stake
                        elif status == BetStatus.LOST:
                            bet.profit_loss = -bet.stake

                        # Update stats
                        await self._update_user_stats(user_id)

                        # Persist
                        if self.storage_backend:
                            await self._persist_bet(bet)

                        logger.info(f"Updated bet {bet_id} to status {status.value}")
                        return True

            logger.warning(f"Bet {bet_id} not found")
            return False

        except Exception as e:
            logger.error(f"Error updating bet result: {e}")
            return False

    async def get_user_bets(
        self,
        user_id: str,
        status: Optional[BetStatus] = None,
        sport: Optional[str] = None,
        days: int = 30,
        limit: int = 50,
    ) -> List[UserBet]:
        """
        Get user's betting history

        Args:
            user_id: User identifier
            status: Filter by status
            sport: Filter by sport
            days: Number of days to look back
            limit: Maximum number of bets to return

        Returns:
            List of UserBet objects
        """
        try:
            bets = self.user_bets.get(user_id, [])

            # Apply filters
            cutoff_date = datetime.now() - timedelta(days=days)

            filtered_bets = [
                bet
                for bet in bets
                if bet.timestamp >= cutoff_date
                and (status is None or bet.status == status)
                and (sport is None or bet.sport.lower() == sport.lower())
            ]

            # Sort by timestamp (most recent first)
            filtered_bets.sort(key=lambda x: x.timestamp, reverse=True)

            return filtered_bets[:limit]

        except Exception as e:
            logger.error(f"Error getting user bets: {e}")
            return []

    async def get_yesterday_bets(self, user_id: str) -> List[UserBet]:
        """Get user's bets from yesterday"""
        try:
            yesterday = datetime.now() - timedelta(days=1)
            yesterday_start = yesterday.replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            yesterday_end = yesterday.replace(
                hour=23, minute=59, second=59, microsecond=999999
            )

            bets = self.user_bets.get(user_id, [])

            yesterday_bets = [
                bet for bet in bets if yesterday_start <= bet.timestamp <= yesterday_end
            ]

            return yesterday_bets

        except Exception as e:
            logger.error(f"Error getting yesterday's bets: {e}")
            return []

    async def get_today_bets(self, user_id: str) -> List[UserBet]:
        """Get user's bets from today"""
        try:
            today_start = datetime.now().replace(
                hour=0, minute=0, second=0, microsecond=0
            )

            bets = self.user_bets.get(user_id, [])

            today_bets = [bet for bet in bets if bet.timestamp >= today_start]

            return today_bets

        except Exception as e:
            logger.error(f"Error getting today's bets: {e}")
            return []

    # ==================== USER PREFERENCES ====================

    async def get_user_preferences(self, user_id: str) -> UserPreferences:
        """Get or create user preferences"""
        if user_id not in self.user_preferences:
            self.user_preferences[user_id] = UserPreferences(user_id=user_id)

        return self.user_preferences[user_id]

    async def update_user_preferences(self, user_id: str, **kwargs) -> UserPreferences:
        """Update user preferences"""
        try:
            prefs = await self.get_user_preferences(user_id)

            for key, value in kwargs.items():
                if hasattr(prefs, key):
                    setattr(prefs, key, value)

            prefs.last_updated = datetime.now()

            # Persist
            if self.storage_backend:
                await self._persist_preferences(prefs)

            logger.info(f"Updated preferences for user {user_id}")
            return prefs

        except Exception as e:
            logger.error(f"Error updating preferences: {e}")
            raise

    async def set_risk_preference(self, user_id: str, risk_level: RiskLevel):
        """Set user's risk preference"""
        await self.update_user_preferences(user_id, risk_level=risk_level)

    async def add_preferred_sport(self, user_id: str, sport: str):
        """Add a preferred sport"""
        prefs = await self.get_user_preferences(user_id)
        if sport not in prefs.preferred_sports:
            prefs.preferred_sports.append(sport)
            await self.update_user_preferences(
                user_id, preferred_sports=prefs.preferred_sports
            )

    # ==================== USER STATISTICS ====================

    async def get_user_stats(self, user_id: str) -> UserStats:
        """Get user statistics"""
        if user_id not in self.user_stats:
            self.user_stats[user_id] = UserStats(user_id=user_id)
            await self._update_user_stats(user_id)

        return self.user_stats[user_id]

    async def _update_user_stats(self, user_id: str):
        """Recalculate user statistics"""
        try:
            bets = self.user_bets.get(user_id, [])

            if not bets:
                return

            stats = UserStats(user_id=user_id)

            # Count bets by status
            stats.total_bets = len(bets)
            stats.won_bets = sum(1 for bet in bets if bet.status == BetStatus.WON)
            stats.lost_bets = sum(1 for bet in bets if bet.status == BetStatus.LOST)
            stats.pending_bets = sum(
                1 for bet in bets if bet.status == BetStatus.PENDING
            )

            # Financial stats
            stats.total_staked = sum(bet.stake for bet in bets)
            stats.total_returns = sum(
                bet.potential_return for bet in bets if bet.status == BetStatus.WON
            )
            stats.total_profit = sum(
                bet.profit_loss for bet in bets if bet.profit_loss is not None
            )

            # Calculate rates
            completed_bets = stats.won_bets + stats.lost_bets
            if completed_bets > 0:
                stats.win_rate = (stats.won_bets / completed_bets) * 100

            if stats.total_staked > 0:
                stats.roi = (stats.total_profit / stats.total_staked) * 100

            # Average odds
            if stats.total_bets > 0:
                stats.average_odds = sum(bet.odds for bet in bets) / stats.total_bets

            # Biggest wins/losses
            profit_losses = [
                bet.profit_loss for bet in bets if bet.profit_loss is not None
            ]
            if profit_losses:
                stats.biggest_win = max(profit_losses)
                stats.biggest_loss = min(profit_losses)

            # Calculate current streak
            recent_bets = sorted(
                [bet for bet in bets if bet.status in [BetStatus.WON, BetStatus.LOST]],
                key=lambda x: x.timestamp,
                reverse=True,
            )

            if recent_bets:
                stats.last_bet_date = recent_bets[0].timestamp
                current_status = recent_bets[0].status
                streak = 0

                for bet in recent_bets:
                    if bet.status == current_status:
                        streak += 1
                    else:
                        break

                stats.current_streak = streak
                stats.streak_type = "win" if current_status == BetStatus.WON else "loss"

            # Favorite sport and market
            sport_counts = defaultdict(int)
            market_counts = defaultdict(int)

            for bet in bets:
                sport_counts[bet.sport] += 1
                market_counts[bet.market] += 1

            if sport_counts:
                stats.favorite_sport = max(sport_counts, key=sport_counts.get)
            if market_counts:
                stats.favorite_market = max(market_counts, key=market_counts.get)

            self.user_stats[user_id] = stats

        except Exception as e:
            logger.error(f"Error updating user stats: {e}")

    # ==================== SESSION MANAGEMENT ====================

    async def create_session(
        self, user_id: str, session_id: Optional[str] = None
    ) -> UserSession:
        """Create a new user session"""
        try:
            if session_id is None:
                session_id = f"session_{user_id}_{datetime.now().timestamp()}"

            session = UserSession(
                session_id=session_id,
                user_id=user_id,
                start_time=datetime.now(),
                last_activity=datetime.now(),
            )

            self.user_sessions[session_id] = session

            logger.info(f"Created session {session_id} for user {user_id}")
            return session

        except Exception as e:
            logger.error(f"Error creating session: {e}")
            raise

    async def get_or_create_session(self, user_id: str) -> UserSession:
        """Get active session or create new one"""
        # Find active session for user
        for session in self.user_sessions.values():
            if session.user_id == user_id and session.active:
                # Check if session is still valid
                if datetime.now() - session.last_activity < timedelta(
                    minutes=self.session_timeout_minutes
                ):
                    session.last_activity = datetime.now()
                    return session
                else:
                    session.active = False

        # Create new session
        return await self.create_session(user_id)

    async def update_session(self, session_id: str, **kwargs):
        """Update session data"""
        if session_id in self.user_sessions:
            session = self.user_sessions[session_id]
            session.last_activity = datetime.now()

            for key, value in kwargs.items():
                if hasattr(session, key):
                    setattr(session, key, value)

    # ==================== CONVERSATION HISTORY ====================

    async def add_conversation(
        self,
        user_id: str,
        user_message: str,
        max_response: str,
        metadata: Optional[Dict] = None,
    ):
        """Add conversation exchange to history"""
        try:
            conversation = {
                "timestamp": datetime.now().isoformat(),
                "user_message": user_message,
                "max_response": max_response,
                "metadata": metadata or {},
            }

            self.conversation_history[user_id].append(conversation)

            # Limit history length
            if len(self.conversation_history[user_id]) > self.max_history_length:
                self.conversation_history[user_id] = self.conversation_history[user_id][
                    -self.max_history_length :
                ]

            # Update session
            session = await self.get_or_create_session(user_id)
            session.messages_count += 1

        except Exception as e:
            logger.error(f"Error adding conversation: {e}")

    async def get_conversation_history(
        self, user_id: str, limit: int = 10
    ) -> List[Dict]:
        """Get recent conversation history"""
        history = self.conversation_history.get(user_id, [])
        return history[-limit:]

    async def get_conversation_context(self, user_id: str, messages: int = 5) -> str:
        """Get conversation context as formatted string"""
        history = await self.get_conversation_history(user_id, messages)

        if not history:
            return "No previous conversation"

        context_lines = []
        for conv in history:
            context_lines.append(f"User: {conv['user_message']}")
            context_lines.append(f"MAX: {conv['max_response'][:100]}...")  # Truncate

        return "\n".join(context_lines)

    # ==================== SMART QUERIES ====================

    async def generate_yesterday_summary(self, user_id: str) -> str:
        """Generate summary of yesterday's activity"""
        try:
            yesterday_bets = await self.get_yesterday_bets(user_id)

            if not yesterday_bets:
                return "You didn't place any bets yesterday. Ready to find today's opportunities? 🎯"

            won = [bet for bet in yesterday_bets if bet.status == BetStatus.WON]
            lost = [bet for bet in yesterday_bets if bet.status == BetStatus.LOST]
            pending = [bet for bet in yesterday_bets if bet.status == BetStatus.PENDING]

            total_profit = sum(bet.profit_loss or 0 for bet in yesterday_bets)

            summary = f"📊 **Yesterday's Activity ({len(yesterday_bets)} bets)**\n\n"

            if won:
                summary += f"✅ Won: {len(won)} bet(s)\n"
                for bet in won:
                    summary += f"   • {bet.selection} ({bet.sport}) at {bet.odds} - Won £{bet.profit_loss:.2f}\n"

            if lost:
                summary += f"❌ Lost: {len(lost)} bet(s)\n"
                for bet in lost:
                    summary += f"   • {bet.selection} ({bet.sport}) at {bet.odds} - Lost £{abs(bet.profit_loss):.2f}\n"

            if pending:
                summary += f"⏳ Pending: {len(pending)} bet(s)\n"

            summary += f"\n💰 Net Result: £{total_profit:+.2f}\n"
            summary += f"\n🎯 Ready for today's picks?"

            return summary

        except Exception as e:
            logger.error(f"Error generating yesterday summary: {e}")
            return "I couldn't retrieve your yesterday's data. Let's focus on today's opportunities!"

    async def get_user_context_summary(self, user_id: str) -> Dict:
        """Get comprehensive user context for personalization"""
        try:
            prefs = await self.get_user_preferences(user_id)
            stats = await self.get_user_stats(user_id)
            recent_bets = await self.get_user_bets(user_id, limit=5)
            session = await self.get_or_create_session(user_id)

            return {
                "user_id": user_id,
                "preferences": {
                    "sports": prefs.preferred_sports,
                    "markets": prefs.preferred_markets,
                    "risk_level": prefs.risk_level.value,
                    "default_stake": prefs.default_stake,
                    "bankroll": prefs.bankroll,
                },
                "statistics": {
                    "total_bets": stats.total_bets,
                    "win_rate": f"{stats.win_rate:.1f}%",
                    "roi": f"{stats.roi:+.1f}%",
                    "total_profit": f"£{stats.total_profit:+.2f}",
                    "current_streak": f"{stats.current_streak} {stats.streak_type}",
                    "favorite_sport": stats.favorite_sport,
                    "favorite_market": stats.favorite_market,
                },
                "recent_activity": {
                    "recent_bets": [
                        {
                            "selection": bet.selection,
                            "sport": bet.sport,
                            "odds": bet.odds,
                            "stake": bet.stake,
                            "status": bet.status.value,
                            "when": self._time_ago(bet.timestamp),
                        }
                        for bet in recent_bets
                    ],
                    "session_messages": session.messages_count,
                    "session_duration": self._time_ago(session.start_time),
                },
            }

        except Exception as e:
            logger.error(f"Error getting user context summary: {e}")
            return {}

    def _time_ago(self, timestamp: datetime) -> str:
        """Convert timestamp to human-readable time ago"""
        delta = datetime.now() - timestamp

        if delta.days > 0:
            return f"{delta.days} day{'s' if delta.days > 1 else ''} ago"
        elif delta.seconds >= 3600:
            hours = delta.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif delta.seconds >= 60:
            minutes = delta.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "just now"

    # ==================== PERSISTENCE ====================

    async def _persist_bet(self, bet: UserBet):
        """Persist bet to database"""
        if self.storage_backend:
            try:
                # Implement database storage here
                pass
            except Exception as e:
                logger.error(f"Error persisting bet: {e}")

    async def _persist_preferences(self, prefs: UserPreferences):
        """Persist preferences to database"""
        if self.storage_backend:
            try:
                # Implement database storage here
                pass
            except Exception as e:
                logger.error(f"Error persisting preferences: {e}")

    # ==================== CLEANUP ====================

    async def cleanup_old_data(self, days: int = 90):
        """Clean up old data from memory"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)

            # Clean old bets
            for user_id in self.user_bets:
                self.user_bets[user_id] = [
                    bet
                    for bet in self.user_bets[user_id]
                    if bet.timestamp >= cutoff_date
                ]

            # Clean inactive sessions
            inactive_sessions = [
                sid
                for sid, session in self.user_sessions.items()
                if datetime.now() - session.last_activity > timedelta(days=1)
            ]

            for sid in inactive_sessions:
                del self.user_sessions[sid]

            logger.info(f"Cleaned up data older than {days} days")

        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")


# Factory function
def create_memory_system(storage_backend: Optional[Any] = None) -> MaxMemorySystem:
    """
    Create MAX Memory System instance

    Args:
        storage_backend: Optional database connection

    Returns:
        MaxMemorySystem: Ready-to-use memory system
    """
    return MaxMemorySystem(storage_backend=storage_backend)


# Export
__all__ = [
    "MaxMemorySystem",
    "UserBet",
    "UserSession",
    "UserPreferences",
    "UserStats",
    "BetStatus",
    "RiskLevel",
    "create_memory_system",
]
