"""
Market Analysis Tools for M.A.X. AI Agent
Comprehensive analysis for various betting markets with data-backed reasoning
"""

from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
from enum import Enum


class BettingMarket(Enum):
    """Supported betting markets"""
    MATCH_WINNER = "Match Winner"
    DRAW_NO_BET = "Draw No Bet"
    OVER_UNDER_GOALS = "Over/Under Goals"
    BOTH_TEAMS_TO_SCORE = "Both Teams To Score"
    CORRECT_SCORE = "Correct Score"
    FIRST_GOALSCORER = "First Goalscorer"
    PLAYER_PROPS = "Player Props"
    HANDICAP = "Handicap"
    TOTAL_RUNS = "Total Runs (Cricket)"
    TOP_BATSMAN = "Top Batsman"
    TOP_BOWLER = "Top Bowler"
    METHOD_OF_DISMISSAL = "Method of Dismissal"


@dataclass
class MarketAnalysis:
    """Data class for market analysis results"""
    market: BettingMarket
    recommended_bet: str
    confidence: float  # 0.0 to 1.0
    reasoning: str
    key_factors: List[str]
    risk_level: str  # LOW, MEDIUM, HIGH
    expected_value: Optional[float]
    alternative_options: List[str]


@dataclass
class TeamStats:
    """Team statistics for analysis"""
    team_name: str
    recent_form: List[str]  # W, L, D for last 5 games
    goals_scored_avg: float
    goals_conceded_avg: float
    clean_sheets: int
    wins: int
    losses: int
    draws: int
    home_record: Dict[str, int]
    away_record: Dict[str, int]
    key_players: List[str]
    injuries: List[str]
    head_to_head: Dict[str, Any]


@dataclass
class CricketTeamStats:
    """Cricket team statistics"""
    team_name: str
    recent_form: List[str]  # W, L for last 5 games
    runs_scored_avg: float
    runs_conceded_avg: float
    win_rate: float
    home_record: Dict[str, int]
    away_record: Dict[str, int]
    key_batsmen: List[str]
    key_bowlers: List[str]
    pitch_preference: str  # batting, bowling, balanced
    weather_form: Dict[str, float]  # sunny, cloudy, rain


class MarketAnalyzer:
    """
    Comprehensive market analysis engine for M.A.X.
    
    Features:
    - Multiple market type support
    - Data-driven reasoning
    - Risk assessment
    - Alternative option suggestions
    - Confidence scoring
    """
    
    def __init__(self):
        self.market_handlers = {
            BettingMarket.MATCH_WINNER: self._analyze_match_winner,
            BettingMarket.DRAW_NO_BET: self._analyze_draw_no_bet,
            BettingMarket.OVER_UNDER_GOALS: self._analyze_over_under,
            BettingMarket.BOTH_TEAMS_TO_SCORE: self._analyze_btts,
            BettingMarket.PLAYER_PROPS: self._analyze_player_props,
            BettingMarket.TOTAL_RUNS: self._analyze_total_runs,
            BettingMarket.TOP_BATSMAN: self._analyze_top_batsman,
            BettingMarket.TOP_BOWLER: self._analyze_top_bowler,
        }
    
    def analyze_market(
        self,
        market: BettingMarket,
        team_a: Dict[str, Any],
        team_b: Dict[str, Any],
        match_context: Dict[str, Any],
        odds_data: Optional[Dict[str, float]] = None
    ) -> MarketAnalysis:
        """
        Analyze a specific betting market
        
        Args:
            market: Betting market to analyze
            team_a: Team A statistics and info
            team_b: Team B statistics and info
            match_context: Match context (venue, weather, etc.)
            odds_data: Available odds for the market
            
        Returns:
            MarketAnalysis with recommendations
        """
        if market not in self.market_handlers:
            return self._default_analysis(market)
        
        return self.market_handlers[market](team_a, team_b, match_context, odds_data)
    
    def get_market_recommendations(
        self,
        sport: str,
        team_a_data: Dict[str, Any],
        team_b_data: Dict[str, Any],
        match_info: Dict[str, Any],
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> List[MarketAnalysis]:
        """
        Get recommendations across multiple markets
        
        Args:
            sport: Sport type ('cricket' or 'football')
            team_a_data: Team A comprehensive data
            team_b_data: Team B comprehensive data
            match_info: Match information
            user_preferences: User's betting preferences
            
        Returns:
            List of market analyses sorted by confidence
        """
        if sport.lower() == 'cricket':
            markets_to_analyze = [
                BettingMarket.MATCH_WINNER,
                BettingMarket.TOTAL_RUNS,
                BettingMarket.TOP_BATSMAN,
                BettingMarket.TOP_BOWLER
            ]
        else:  # football
            markets_to_analyze = [
                BettingMarket.MATCH_WINNER,
                BettingMarket.DRAW_NO_BET,
                BettingMarket.OVER_UNDER_GOALS,
                BettingMarket.BOTH_TEAMS_TO_SCORE
            ]
        
        # Filter based on user preferences
        if user_preferences and "favorite_markets" in user_preferences:
            preferred_markets = [
                market for market in markets_to_analyze 
                if market.value in user_preferences["favorite_markets"]
            ]
            if preferred_markets:
                markets_to_analyze = preferred_markets
        
        analyses = []
        for market in markets_to_analyze:
            try:
                analysis = self.analyze_market(
                    market, team_a_data, team_b_data, match_info
                )
                analyses.append(analysis)
            except Exception as e:
                print(f"Error analyzing {market.value}: {e}")
                continue
        
        # Sort by confidence (highest first)
        analyses.sort(key=lambda x: x.confidence, reverse=True)
        return analyses
    
    def _analyze_match_winner(
        self,
        team_a: Dict[str, Any],
        team_b: Dict[str, Any],
        context: Dict[str, Any],
        odds: Optional[Dict[str, float]] = None
    ) -> MarketAnalysis:
        """Analyze Match Winner market"""
        
        # Calculate team strengths
        team_a_strength = self._calculate_team_strength(team_a, context, True)
        team_b_strength = self._calculate_team_strength(team_b, context, False)
        
        # Determine recommendation
        if team_a_strength > team_b_strength * 1.2:
            recommended = f"{team_a.get('name', 'Team A')} to Win"
            confidence = min(0.9, 0.6 + (team_a_strength - team_b_strength) / 10)
        elif team_b_strength > team_a_strength * 1.2:
            recommended = f"{team_b.get('name', 'Team B')} to Win"
            confidence = min(0.9, 0.6 + (team_b_strength - team_a_strength) / 10)
        else:
            recommended = "Consider Draw or avoid this market"
            confidence = 0.4
        
        # Generate reasoning
        key_factors = []
        if team_a.get('recent_form', []):
            form_a = team_a['recent_form']
            wins_a = form_a.count('W')
            key_factors.append(f"{team_a.get('name', 'Team A')}: {wins_a}/5 recent wins")
        
        if team_b.get('recent_form', []):
            form_b = team_b['recent_form']
            wins_b = form_b.count('W')
            key_factors.append(f"{team_b.get('name', 'Team B')}: {wins_b}/5 recent wins")
        
        if context.get('venue'):
            if context.get('home_team') == team_a.get('name'):
                key_factors.append(f"Home advantage for {team_a.get('name')}")
            else:
                key_factors.append(f"Home advantage for {team_b.get('name')}")
        
        reasoning = f"Analysis based on recent form, head-to-head record, and match context. {recommended}"
        
        return MarketAnalysis(
            market=BettingMarket.MATCH_WINNER,
            recommended_bet=recommended,
            confidence=confidence,
            reasoning=reasoning,
            key_factors=key_factors,
            risk_level="MEDIUM" if confidence > 0.7 else "HIGH",
            expected_value=None,
            alternative_options=["Draw No Bet", "Handicap betting"]
        )
    
    def _analyze_draw_no_bet(
        self,
        team_a: Dict[str, Any],
        team_b: Dict[str, Any],
        context: Dict[str, Any],
        odds: Optional[Dict[str, float]] = None
    ) -> MarketAnalysis:
        """Analyze Draw No Bet market"""
        
        # Get match winner analysis first
        winner_analysis = self._analyze_match_winner(team_a, team_b, context, odds)
        
        # DNB reduces risk by removing draw possibility
        if "Draw" in winner_analysis.recommended_bet:
            recommended = "Avoid - teams too evenly matched"
            confidence = 0.3
            risk_level = "HIGH"
        else:
            recommended = winner_analysis.recommended_bet.replace("to Win", "DNB")
            confidence = min(winner_analysis.confidence + 0.1, 0.9)  # Slight confidence boost
            risk_level = "LOW" if confidence > 0.8 else "MEDIUM"
        
        key_factors = winner_analysis.key_factors + [
            "Draw refunded in DNB market",
            "Lower risk than straight win"
        ]
        
        # Check historical draw frequency
        draw_frequency = self._estimate_draw_frequency(team_a, team_b, context)
        if draw_frequency > 0.3:
            key_factors.append(f"High draw probability (~{draw_frequency*100:.0f}%)")
            confidence += 0.1  # DNB more valuable when draws are likely
        
        reasoning = f"Draw No Bet analysis: {recommended}. Safer than match winner with draw protection."
        
        return MarketAnalysis(
            market=BettingMarket.DRAW_NO_BET,
            recommended_bet=recommended,
            confidence=confidence,
            reasoning=reasoning,
            key_factors=key_factors,
            risk_level=risk_level,
            expected_value=None,
            alternative_options=["Match Winner", "Handicap"]
        )
    
    def _analyze_over_under(
        self,
        team_a: Dict[str, Any],
        team_b: Dict[str, Any],
        context: Dict[str, Any],
        odds: Optional[Dict[str, float]] = None
    ) -> MarketAnalysis:
        """Analyze Over/Under Goals market"""
        
        # Calculate expected goals
        goals_a = team_a.get('goals_scored_avg', 1.5)
        goals_b = team_b.get('goals_scored_avg', 1.5)
        conceded_a = team_a.get('goals_conceded_avg', 1.2)
        conceded_b = team_b.get('goals_conceded_avg', 1.2)
        
        # Adjust for match context
        expected_total = (goals_a + goals_b + conceded_a + conceded_b) / 2
        
        # Context adjustments
        if context.get('weather') == 'rain':
            expected_total *= 0.85  # Rain typically reduces goals
        if context.get('importance') == 'high':
            expected_total *= 0.9   # Important matches often cagier
        
        # Determine Over/Under 2.5 recommendation
        line = 2.5  # Most common line
        if expected_total > line + 0.3:
            recommended = f"Over {line} Goals"
            confidence = min(0.85, 0.6 + (expected_total - line) / 3)
        elif expected_total < line - 0.3:
            recommended = f"Under {line} Goals"
            confidence = min(0.85, 0.6 + (line - expected_total) / 3)
        else:
            recommended = "Avoid - too close to call"
            confidence = 0.4
        
        key_factors = [
            f"Team A avg goals: {goals_a:.1f}",
            f"Team B avg goals: {goals_b:.1f}",
            f"Expected total: {expected_total:.1f}",
            f"Line: {line}"
        ]
        
        # Add defensive stats
        clean_sheets_a = team_a.get('clean_sheets', 0)
        clean_sheets_b = team_b.get('clean_sheets', 0)
        if clean_sheets_a + clean_sheets_b > 8:
            key_factors.append("Both teams have strong defensive records")
        
        reasoning = f"Expected goals analysis suggests {recommended}. Based on offensive/defensive averages."
        
        return MarketAnalysis(
            market=BettingMarket.OVER_UNDER_GOALS,
            recommended_bet=recommended,
            confidence=confidence,
            reasoning=reasoning,
            key_factors=key_factors,
            risk_level="MEDIUM",
            expected_value=None,
            alternative_options=[f"Over {line-0.5} Goals", f"Under {line+0.5} Goals"]
        )
    
    def _analyze_btts(
        self,
        team_a: Dict[str, Any],
        team_b: Dict[str, Any],
        context: Dict[str, Any],
        odds: Optional[Dict[str, float]] = None
    ) -> MarketAnalysis:
        """Analyze Both Teams To Score market"""
        
        # Calculate BTTS probability factors
        goals_a = team_a.get('goals_scored_avg', 1.5)
        goals_b = team_b.get('goals_scored_avg', 1.5)
        conceded_a = team_a.get('goals_conceded_avg', 1.2)
        conceded_b = team_b.get('goals_conceded_avg', 1.2)
        
        # BTTS more likely if both teams score regularly and concede
        scoring_factor = min(goals_a, goals_b)  # Limited by weaker attack
        defending_factor = max(conceded_a, conceded_b)  # Limited by stronger defense
        
        btts_score = (scoring_factor + defending_factor) / 2
        
        # Clean sheet factor
        clean_sheets_a = team_a.get('clean_sheets', 0)
        clean_sheets_b = team_b.get('clean_sheets', 0)
        clean_sheet_factor = (clean_sheets_a + clean_sheets_b) / 20  # Out of last 10 games each
        
        # Adjust BTTS probability
        btts_probability = btts_score * (1 - clean_sheet_factor)
        
        if btts_probability > 1.3:
            recommended = "Both Teams To Score - YES"
            confidence = min(0.85, 0.5 + btts_probability / 4)
        elif btts_probability < 0.8:
            recommended = "Both Teams To Score - NO"
            confidence = min(0.8, 0.6 + (1 - btts_probability) / 3)
        else:
            recommended = "Avoid BTTS market - uncertain"
            confidence = 0.4
        
        key_factors = [
            f"Team A goals avg: {goals_a:.1f}, conceded: {conceded_a:.1f}",
            f"Team B goals avg: {goals_b:.1f}, conceded: {conceded_b:.1f}",
            f"Combined clean sheets: {clean_sheets_a + clean_sheets_b}",
            f"BTTS probability score: {btts_probability:.2f}"
        ]
        
        reasoning = f"BTTS analysis based on scoring/conceding averages: {recommended}"
        
        return MarketAnalysis(
            market=BettingMarket.BOTH_TEAMS_TO_SCORE,
            recommended_bet=recommended,
            confidence=confidence,
            reasoning=reasoning,
            key_factors=key_factors,
            risk_level="MEDIUM",
            expected_value=None,
            alternative_options=["Over/Under Goals", "First Goal markets"]
        )
    
    def _analyze_player_props(
        self,
        team_a: Dict[str, Any],
        team_b: Dict[str, Any],
        context: Dict[str, Any],
        odds: Optional[Dict[str, float]] = None
    ) -> MarketAnalysis:
        """Analyze Player Props markets"""
        
        # Get key players from both teams
        key_players_a = team_a.get('key_players', [])
        key_players_b = team_b.get('key_players', [])
        
        if not key_players_a and not key_players_b:
            return MarketAnalysis(
                market=BettingMarket.PLAYER_PROPS,
                recommended_bet="No player data available",
                confidence=0.0,
                reasoning="Insufficient player information for analysis",
                key_factors=[],
                risk_level="HIGH",
                expected_value=None,
                alternative_options=["Match markets"]
            )
        
        # Analyze top goalscorer candidates
        recommendations = []
        
        for team, players in [(team_a, key_players_a), (team_b, key_players_b)]:
            team_name = team.get('name', 'Team')
            for player in players[:2]:  # Top 2 players per team
                if isinstance(player, dict):
                    player_name = player.get('name', str(player))
                    goals_avg = player.get('goals_per_game', 0.5)
                else:
                    player_name = str(player)
                    goals_avg = 0.5  # Default assumption
                
                if goals_avg > 0.3:
                    recommendations.append(f"{player_name} anytime goalscorer")
        
        if recommendations:
            recommended = recommendations[0]  # Top recommendation
            confidence = 0.65
            risk_level = "MEDIUM"
        else:
            recommended = "No standout player props identified"
            confidence = 0.3
            risk_level = "HIGH"
        
        key_factors = [
            f"Analyzing players from {team_a.get('name', 'Team A')} and {team_b.get('name', 'Team B')}",
            "Based on recent scoring form and match importance"
        ]
        
        reasoning = f"Player analysis suggests {recommended}. Consider anytime goalscorer markets."
        
        return MarketAnalysis(
            market=BettingMarket.PLAYER_PROPS,
            recommended_bet=recommended,
            confidence=confidence,
            reasoning=reasoning,
            key_factors=key_factors,
            risk_level=risk_level,
            expected_value=None,
            alternative_options=recommendations[1:3] if len(recommendations) > 1 else []
        )
    
    def _analyze_total_runs(
        self,
        team_a: Dict[str, Any],
        team_b: Dict[str, Any],
        context: Dict[str, Any],
        odds: Optional[Dict[str, float]] = None
    ) -> MarketAnalysis:
        """Analyze Total Runs market for cricket"""
        
        # Get batting averages
        runs_a = team_a.get('runs_scored_avg', 250)
        runs_b = team_b.get('runs_scored_avg', 250)
        
        # Get bowling averages (runs conceded)
        conceded_a = team_a.get('runs_conceded_avg', 240)
        conceded_b = team_b.get('runs_conceded_avg', 240)
        
        # Calculate expected total runs
        expected_runs = (runs_a + runs_b + conceded_a + conceded_b) / 2
        
        # Context adjustments
        pitch_type = context.get('pitch_type', 'balanced')
        if pitch_type == 'batting':
            expected_runs *= 1.15
        elif pitch_type == 'bowling':
            expected_runs *= 0.85
        
        weather = context.get('weather', 'clear')
        if weather in ['overcast', 'humid']:
            expected_runs *= 1.05  # Good for batting
        elif weather == 'windy':
            expected_runs *= 0.95
        
        # Determine over/under recommendation (common line: 300-350 runs)
        line = 320  # Typical total runs line
        
        if expected_runs > line + 30:
            recommended = f"Over {line} Total Runs"
            confidence = min(0.85, 0.6 + (expected_runs - line) / 100)
        elif expected_runs < line - 30:
            recommended = f"Under {line} Total Runs"
            confidence = min(0.85, 0.6 + (line - expected_runs) / 100)
        else:
            recommended = "Avoid total runs - too close to line"
            confidence = 0.4
        
        key_factors = [
            f"Team A avg runs: {runs_a}",
            f"Team B avg runs: {runs_b}",
            f"Expected total: {expected_runs:.0f}",
            f"Pitch type: {pitch_type}",
            f"Weather: {weather}"
        ]
        
        reasoning = f"Total runs analysis: {recommended}. Based on batting averages and conditions."
        
        return MarketAnalysis(
            market=BettingMarket.TOTAL_RUNS,
            recommended_bet=recommended,
            confidence=confidence,
            reasoning=reasoning,
            key_factors=key_factors,
            risk_level="MEDIUM",
            expected_value=None,
            alternative_options=[f"Over {line-20}", f"Under {line+20}"]
        )
    
    def _analyze_top_batsman(
        self,
        team_a: Dict[str, Any],
        team_b: Dict[str, Any],
        context: Dict[str, Any],
        odds: Optional[Dict[str, float]] = None
    ) -> MarketAnalysis:
        """Analyze Top Batsman market for cricket"""
        
        # Get key batsmen
        batsmen_a = team_a.get('key_batsmen', [])
        batsmen_b = team_b.get('key_batsmen', [])
        
        all_batsmen = []
        
        # Process Team A batsmen
        for batsman in batsmen_a[:3]:  # Top 3
            if isinstance(batsman, dict):
                name = batsman.get('name', str(batsman))
                avg = batsman.get('batting_average', 35)
            else:
                name = str(batsman)
                avg = 35  # Default
            all_batsmen.append((name, avg, team_a.get('name', 'Team A')))
        
        # Process Team B batsmen
        for batsman in batsmen_b[:3]:  # Top 3
            if isinstance(batsman, dict):
                name = batsman.get('name', str(batsman))
                avg = batsman.get('batting_average', 35)
            else:
                name = str(batsman)
                avg = 35  # Default
            all_batsmen.append((name, avg, team_b.get('name', 'Team B')))
        
        if not all_batsmen:
            return MarketAnalysis(
                market=BettingMarket.TOP_BATSMAN,
                recommended_bet="No batsman data available",
                confidence=0.0,
                reasoning="Insufficient batting statistics",
                key_factors=[],
                risk_level="HIGH",
                expected_value=None,
                alternative_options=["Match winner", "Total runs"]
            )
        
        # Sort by batting average
        all_batsmen.sort(key=lambda x: x[1], reverse=True)
        top_batsman = all_batsmen[0]
        
        recommended = f"{top_batsman[0]} (Top Batsman)"
        confidence = min(0.75, 0.5 + (top_batsman[1] - 30) / 50)
        
        key_factors = [
            f"Top pick: {top_batsman[0]} (avg: {top_batsman[1]})",
            f"From {top_batsman[2]}",
            "Based on recent batting form and averages"
        ]
        
        # Add alternatives
        alternatives = [f"{bat[0]} (avg: {bat[1]})" for bat in all_batsmen[1:3]]
        
        reasoning = f"Top batsman analysis recommends {recommended}. Best recent form and average."
        
        return MarketAnalysis(
            market=BettingMarket.TOP_BATSMAN,
            recommended_bet=recommended,
            confidence=confidence,
            reasoning=reasoning,
            key_factors=key_factors,
            risk_level="MEDIUM",
            expected_value=None,
            alternative_options=alternatives
        )
    
    def _analyze_top_bowler(
        self,
        team_a: Dict[str, Any],
        team_b: Dict[str, Any],
        context: Dict[str, Any],
        odds: Optional[Dict[str, float]] = None
    ) -> MarketAnalysis:
        """Analyze Top Bowler market for cricket"""
        
        # Get key bowlers
        bowlers_a = team_a.get('key_bowlers', [])
        bowlers_b = team_b.get('key_bowlers', [])
        
        all_bowlers = []
        
        # Process bowlers from both teams
        for team, bowlers in [(team_a, bowlers_a), (team_b, bowlers_b)]:
            team_name = team.get('name', 'Team')
            for bowler in bowlers[:2]:  # Top 2 per team
                if isinstance(bowler, dict):
                    name = bowler.get('name', str(bowler))
                    wickets_avg = bowler.get('wickets_per_game', 2.0)
                    bowling_avg = bowler.get('bowling_average', 25.0)
                else:
                    name = str(bowler)
                    wickets_avg = 2.0
                    bowling_avg = 25.0
                
                # Calculate bowler score (lower bowling average is better)
                bowler_score = wickets_avg * (30 / bowling_avg)
                all_bowlers.append((name, bowler_score, team_name, wickets_avg))
        
        if not all_bowlers:
            return MarketAnalysis(
                market=BettingMarket.TOP_BOWLER,
                recommended_bet="No bowler data available",
                confidence=0.0,
                reasoning="Insufficient bowling statistics",
                key_factors=[],
                risk_level="HIGH",
                expected_value=None,
                alternative_options=["Match winner", "Total runs"]
            )
        
        # Sort by bowler score
        all_bowlers.sort(key=lambda x: x[1], reverse=True)
        top_bowler = all_bowlers[0]
        
        recommended = f"{top_bowler[0]} (Top Bowler)"
        confidence = min(0.75, 0.5 + (top_bowler[1] - 2) / 4)
        
        key_factors = [
            f"Top pick: {top_bowler[0]}",
            f"From {top_bowler[2]}",
            f"Avg wickets/game: {top_bowler[3]:.1f}",
            "Based on recent bowling form"
        ]
        
        alternatives = [f"{bow[0]} ({bow[2]})" for bow in all_bowlers[1:3]]
        
        reasoning = f"Top bowler analysis recommends {recommended}. Best wicket-taking record."
        
        return MarketAnalysis(
            market=BettingMarket.TOP_BOWLER,
            recommended_bet=recommended,
            confidence=confidence,
            reasoning=reasoning,
            key_factors=key_factors,
            risk_level="MEDIUM",
            expected_value=None,
            alternative_options=alternatives
        )
    
    def _calculate_team_strength(
        self, 
        team: Dict[str, Any], 
        context: Dict[str, Any], 
        is_home: bool
    ) -> float:
        """Calculate overall team strength score"""
        
        strength = 5.0  # Base strength
        
        # Recent form factor
        recent_form = team.get('recent_form', [])
        if recent_form:
            wins = recent_form.count('W')
            draws = recent_form.count('D')
            strength += (wins * 1.0) + (draws * 0.5)
        
        # Home advantage
        if is_home:
            strength += 0.8
        
        # Goal/run scoring ability
        if 'goals_scored_avg' in team:
            strength += team['goals_scored_avg'] * 0.5
        if 'runs_scored_avg' in team:
            strength += team['runs_scored_avg'] / 100
        
        # Defensive strength
        if 'goals_conceded_avg' in team:
            strength += (2.0 - team['goals_conceded_avg']) * 0.3
        if 'clean_sheets' in team:
            strength += team['clean_sheets'] * 0.1
        
        return max(0, strength)
    
    def _estimate_draw_frequency(
        self,
        team_a: Dict[str, Any],
        team_b: Dict[str, Any],
        context: Dict[str, Any]
    ) -> float:
        """Estimate probability of draw based on team data"""
        
        # Default draw probability
        base_draw_prob = 0.25
        
        # If teams are evenly matched, higher draw probability
        strength_a = self._calculate_team_strength(team_a, context, True)
        strength_b = self._calculate_team_strength(team_b, context, False)
        
        strength_diff = abs(strength_a - strength_b)
        if strength_diff < 1.0:
            return min(0.4, base_draw_prob + 0.1)
        elif strength_diff > 3.0:
            return max(0.15, base_draw_prob - 0.1)
        
        return base_draw_prob
    
    def _default_analysis(self, market: BettingMarket) -> MarketAnalysis:
        """Default analysis for unsupported markets"""
        return MarketAnalysis(
            market=market,
            recommended_bet=f"{market.value} analysis not implemented",
            confidence=0.0,
            reasoning="Market analysis not available",
            key_factors=[],
            risk_level="HIGH",
            expected_value=None,
            alternative_options=[]
        )
    
    def format_analysis_for_chat(self, analysis: MarketAnalysis) -> str:
        """Format market analysis for M.A.X. chat responses"""
        
        confidence_emoji = "🟢" if analysis.confidence > 0.7 else "🟡" if analysis.confidence > 0.5 else "🔴"
        risk_emoji = "🛡️" if analysis.risk_level == "LOW" else "⚠️" if analysis.risk_level == "MEDIUM" else "🚨"
        
        result = f"📊 **{analysis.market.value}** {confidence_emoji}\n"
        result += f"💡 **Recommendation:** {analysis.recommended_bet}\n"
        result += f"🎯 **Confidence:** {analysis.confidence*100:.0f}%\n"
        result += f"{risk_emoji} **Risk:** {analysis.risk_level}\n\n"
        
        result += f"**Key Factors:**\n"
        for factor in analysis.key_factors[:3]:  # Top 3 factors
            result += f"• {factor}\n"
        
        if analysis.alternative_options:
            result += f"\n**Alternatives:** {', '.join(analysis.alternative_options[:2])}"
        
        return result


# Export main components
__all__ = [
    "MarketAnalyzer",
    "BettingMarket",
    "MarketAnalysis",
    "TeamStats",
    "CricketTeamStats"
]