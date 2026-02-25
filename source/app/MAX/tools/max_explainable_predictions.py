"""
M.A.X. Explainable AI Prediction System
Transparency through detailed reasoning and factor breakdown
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json
from openai import OpenAI
import os

OPENAI_API_KEY = os.getenv(
    'OPENAI_API_KEY',
    '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'
)

client = OpenAI(api_key=OPENAI_API_KEY)


class ExplainablePredictionSystem:
    """
    Makes MAX's predictions transparent and understandable
    
    Features:
    - Factor breakdown (form, H2H, odds, pitch, etc.)
    - Confidence reasoning
    - Risk assessment
    - Counter-arguments
    - Visual factor weights
    """
    
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        
        # Prediction factors with weights
        self.factors = {
            'recent_form': {
                'weight': 0.30,
                'description': 'Team performance in last 10 matches'
            },
            'head_to_head': {
                'weight': 0.20,
                'description': 'Historical record between teams'
            },
            'betting_odds': {
                'weight': 0.25,
                'description': 'Market consensus from bookmakers'
            },
            'pitch_conditions': {
                'weight': 0.10,
                'description': 'Venue and pitch characteristics'
            },
            'team_news': {
                'weight': 0.10,
                'description': 'Injuries, suspensions, lineup changes'
            },
            'home_advantage': {
                'weight': 0.05,
                'description': 'Home ground benefit'
            }
        }
    
    def explain_prediction(
        self,
        prediction: Dict[str, Any],
        match_data: Dict[str, Any],
        analysis_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate comprehensive explanation for a prediction
        
        Args:
            prediction: The prediction details
            match_data: Match information
            analysis_data: Analyzed factors
            
        Returns:
            Detailed explanation with reasoning
        """
        
        # Extract key information
        predicted_winner = prediction.get('predicted_winner', 'Unknown')
        confidence = prediction.get('confidence', 50)
        odds = prediction.get('odds', 2.0)
        
        # Analyze each factor
        factor_analysis = self._analyze_factors(match_data, analysis_data)
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            predicted_winner=predicted_winner,
            confidence=confidence,
            factor_analysis=factor_analysis
        )
        
        # Risk assessment
        risk_assessment = self._assess_risk(
            confidence=confidence,
            odds=odds,
            factor_analysis=factor_analysis
        )
        
        # Counter-arguments
        counter_args = self._generate_counter_arguments(
            predicted_winner=predicted_winner,
            match_data=match_data,
            factor_analysis=factor_analysis
        )
        
        # Build explanation
        explanation = {
            'prediction_summary': {
                'predicted_winner': predicted_winner,
                'confidence': confidence,
                'odds': odds,
                'recommendation': self._get_recommendation(confidence, odds)
            },
            'factor_breakdown': factor_analysis,
            'detailed_reasoning': reasoning,
            'risk_assessment': risk_assessment,
            'counter_arguments': counter_args,
            'confidence_explanation': self._explain_confidence(confidence, factor_analysis),
            'key_insights': self._extract_key_insights(factor_analysis),
            'transparency_note': 'This prediction is based on data-driven analysis. No guarantees.',
            'generated_at': datetime.now().isoformat()
        }
        
        return explanation
    
    def _analyze_factors(
        self,
        match_data: Dict[str, Any],
        analysis_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze each prediction factor"""
        
        factors = {}
        
        # Recent Form
        factors['recent_form'] = {
            'weight': self.factors['recent_form']['weight'],
            'score': self._calculate_form_score(analysis_data.get('recent_form', {})),
            'details': analysis_data.get('recent_form', {}),
            'impact': 'Strongly favors' if analysis_data.get('recent_form', {}).get('advantage', 0) > 0.6 else 'Slightly favors',
            'explanation': self._explain_form(analysis_data.get('recent_form', {}))
        }
        
        # Head to Head
        factors['head_to_head'] = {
            'weight': self.factors['head_to_head']['weight'],
            'score': self._calculate_h2h_score(analysis_data.get('head_to_head', {})),
            'details': analysis_data.get('head_to_head', {}),
            'impact': self._get_h2h_impact(analysis_data.get('head_to_head', {})),
            'explanation': self._explain_h2h(analysis_data.get('head_to_head', {}))
        }
        
        # Betting Odds
        factors['betting_odds'] = {
            'weight': self.factors['betting_odds']['weight'],
            'score': self._calculate_odds_score(analysis_data.get('odds', {})),
            'details': analysis_data.get('odds', {}),
            'impact': 'Market consensus',
            'explanation': self._explain_odds(analysis_data.get('odds', {}))
        }
        
        # Pitch Conditions
        factors['pitch_conditions'] = {
            'weight': self.factors['pitch_conditions']['weight'],
            'score': 0.5,  # Neutral unless specific data
            'details': analysis_data.get('pitch', {}),
            'impact': 'Moderate',
            'explanation': self._explain_pitch(analysis_data.get('pitch', {}))
        }
        
        # Team News
        factors['team_news'] = {
            'weight': self.factors['team_news']['weight'],
            'score': self._calculate_team_news_score(analysis_data.get('team_news', {})),
            'details': analysis_data.get('team_news', {}),
            'impact': self._get_team_news_impact(analysis_data.get('team_news', {})),
            'explanation': self._explain_team_news(analysis_data.get('team_news', {}))
        }
        
        # Home Advantage
        factors['home_advantage'] = {
            'weight': self.factors['home_advantage']['weight'],
            'score': 0.6 if match_data.get('is_home') else 0.4,
            'details': {'is_home': match_data.get('is_home', False)},
            'impact': 'Slight advantage' if match_data.get('is_home') else 'Away team',
            'explanation': 'Home teams historically win ~55% of matches' if match_data.get('is_home') else 'Playing away'
        }
        
        return factors
    
    def _generate_reasoning(
        self,
        predicted_winner: str,
        confidence: float,
        factor_analysis: Dict[str, Any]
    ) -> str:
        """Generate human-readable reasoning"""
        
        # Sort factors by impact
        sorted_factors = sorted(
            factor_analysis.items(),
            key=lambda x: x[1]['score'] * x[1]['weight'],
            reverse=True
        )
        
        reasoning = f"I'm predicting {predicted_winner} to win with {confidence}% confidence. Here's why:\n\n"
        
        # Top 3 supporting factors
        reasoning += "**Strongest Supporting Factors:**\n"
        for i, (factor_name, factor_data) in enumerate(sorted_factors[:3], 1):
            reasoning += f"{i}. **{factor_name.replace('_', ' ').title()}** ({factor_data['weight']*100:.0f}% weight): {factor_data['explanation']}\n"
        
        reasoning += "\n**Overall Assessment:**\n"
        reasoning += self._synthesize_factors(factor_analysis, predicted_winner)
        
        return reasoning
    
    def _assess_risk(
        self,
        confidence: float,
        odds: float,
        factor_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess betting risk"""
        
        # Calculate risk score (0-100, higher = riskier)
        risk_score = 100 - confidence
        
        # Adjust for odds
        if odds > 3.0:
            risk_score += 20  # Higher odds = higher risk
        elif odds < 1.5:
            risk_score += 10  # Low odds = lower value
        
        # Check factor agreement
        factor_agreement = self._calculate_factor_agreement(factor_analysis)
        if factor_agreement < 0.7:
            risk_score += 15  # Low agreement = higher uncertainty
        
        # Cap at 100
        risk_score = min(risk_score, 100)
        
        # Determine risk level
        if risk_score < 30:
            risk_level = 'Low'
            recommendation = 'Safe bet with good confidence'
        elif risk_score < 60:
            risk_level = 'Medium'
            recommendation = 'Moderate risk, stake accordingly'
        else:
            risk_level = 'High'
            recommendation = 'High risk - consider smaller stake or skip'
        
        return {
            'risk_score': round(risk_score, 2),
            'risk_level': risk_level,
            'recommendation': recommendation,
            'factors_agreement': round(factor_agreement * 100, 2),
            'volatility': 'High' if odds > 2.5 else 'Low'
        }
    
    def _generate_counter_arguments(
        self,
        predicted_winner: str,
        match_data: Dict[str, Any],
        factor_analysis: Dict[str, Any]
    ) -> List[str]:
        """Generate counter-arguments for balanced view"""
        
        counter_args = []
        
        # Check for weak factors
        for factor_name, factor_data in factor_analysis.items():
            if factor_data['score'] < 0.4:
                counter_args.append(
                    f"{factor_name.replace('_', ' ').title()} doesn't favor this prediction: {factor_data['explanation']}"
                )
        
        # Add general cautions
        counter_args.append("Cricket/football is unpredictable - unexpected outcomes happen")
        counter_args.append("Past performance doesn't guarantee future results")
        
        # Odds-based counter
        odds = match_data.get('odds', 2.0)
        if odds < 1.5:
            counter_args.append("Low odds mean lower value even if confidence is high")
        elif odds > 3.0:
            counter_args.append("High odds reflect genuine uncertainty in the market")
        
        return counter_args[:3]  # Top 3 counter-arguments
    
    def _explain_confidence(
        self,
        confidence: float,
        factor_analysis: Dict[str, Any]
    ) -> str:
        """Explain why specific confidence level"""
        
        if confidence >= 80:
            return f"High confidence ({confidence}%) because multiple strong factors align: form, odds, and historical data all point the same direction."
        elif confidence >= 60:
            return f"Moderate confidence ({confidence}%) as main factors support this outcome, but some uncertainty remains in specific areas."
        else:
            return f"Lower confidence ({confidence}%) due to mixed signals from different factors. This is a closer matchup than odds might suggest."
    
    def _extract_key_insights(self, factor_analysis: Dict[str, Any]) -> List[str]:
        """Extract 2-3 key insights"""
        
        insights = []
        
        # Find strongest factor
        strongest = max(factor_analysis.items(), key=lambda x: x[1]['score'] * x[1]['weight'])
        insights.append(f"🎯 {strongest[0].replace('_', ' ').title()} is the strongest indicator")
        
        # Check for unanimous factors
        strong_factors = [name for name, data in factor_analysis.items() if data['score'] > 0.6]
        if len(strong_factors) >= 4:
            insights.append(f"✅ {len(strong_factors)} out of {len(factor_analysis)} factors support this prediction")
        
        # Add value insight
        insights.append("💡 Always bet within your budget - no prediction is guaranteed")
        
        return insights
    
    # Helper calculation methods
    def _calculate_form_score(self, form_data: Dict[str, Any]) -> float:
        """Calculate form score 0-1"""
        wins = form_data.get('wins', 0)
        total = form_data.get('total', 10)
        return wins / total if total > 0 else 0.5
    
    def _calculate_h2h_score(self, h2h_data: Dict[str, Any]) -> float:
        """Calculate H2H score 0-1"""
        wins = h2h_data.get('wins', 0)
        total = h2h_data.get('total', 1)
        return wins / total if total > 0 else 0.5
    
    def _calculate_odds_score(self, odds_data: Dict[str, Any]) -> float:
        """Calculate odds-based score 0-1"""
        odds = odds_data.get('odds', 2.0)
        # Convert odds to implied probability
        return 1 / odds if odds > 0 else 0.5
    
    def _calculate_team_news_score(self, news_data: Dict[str, Any]) -> float:
        """Calculate team news impact 0-1"""
        injuries = news_data.get('key_injuries', 0)
        if injuries > 2:
            return 0.3  # Significant injuries hurt
        elif injuries == 0:
            return 0.7  # Full strength helps
        return 0.5
    
    def _calculate_factor_agreement(self, factor_analysis: Dict[str, Any]) -> float:
        """Calculate how much factors agree (0-1)"""
        scores = [data['score'] for data in factor_analysis.values()]
        avg = sum(scores) / len(scores)
        variance = sum((s - avg) ** 2 for s in scores) / len(scores)
        # Low variance = high agreement
        return 1 - min(variance, 1)
    
    def _get_recommendation(self, confidence: float, odds: float) -> str:
        """Get betting recommendation"""
        if confidence >= 75 and odds >= 1.5:
            return "Strong bet - good confidence and value"
        elif confidence >= 60:
            return "Consider betting - decent confidence"
        else:
            return "Proceed with caution - lower confidence"
    
    # Explanation helpers
    def _explain_form(self, form_data: Dict[str, Any]) -> str:
        wins = form_data.get('wins', 0)
        total = form_data.get('total', 10)
        return f"Won {wins} of last {total} matches ({wins/total*100:.0f}% win rate)"
    
    def _explain_h2h(self, h2h_data: Dict[str, Any]) -> str:
        wins = h2h_data.get('wins', 0)
        total = h2h_data.get('total', 1)
        return f"Won {wins} of {total} previous encounters"
    
    def _explain_odds(self, odds_data: Dict[str, Any]) -> str:
        odds = odds_data.get('odds', 2.0)
        implied_prob = (1 / odds) * 100
        return f"Market odds of {odds:.2f} imply {implied_prob:.1f}% probability"
    
    def _explain_pitch(self, pitch_data: Dict[str, Any]) -> str:
        condition = pitch_data.get('condition', 'Unknown')
        return f"Pitch conditions: {condition}"
    
    def _explain_team_news(self, news_data: Dict[str, Any]) -> str:
        injuries = news_data.get('key_injuries', 0)
        if injuries > 2:
            return f"{injuries} key injuries impact team strength"
        return "Full strength squad available"
    
    def _get_h2h_impact(self, h2h_data: Dict[str, Any]) -> str:
        wins = h2h_data.get('wins', 0)
        total = h2h_data.get('total', 1)
        win_rate = wins / total if total > 0 else 0.5
        if win_rate > 0.7:
            return "Strongly favors"
        elif win_rate > 0.5:
            return "Slightly favors"
        return "Neutral/Against"
    
    def _get_team_news_impact(self, news_data: Dict[str, Any]) -> str:
        injuries = news_data.get('key_injuries', 0)
        if injuries > 2:
            return "Negative impact"
        elif injuries == 0:
            return "Positive impact"
        return "Minor impact"
    
    def _synthesize_factors(self, factor_analysis: Dict[str, Any], winner: str) -> str:
        """Synthesize all factors into conclusion"""
        strong_factors = sum(1 for data in factor_analysis.values() if data['score'] > 0.6)
        total_factors = len(factor_analysis)
        
        return f"With {strong_factors} out of {total_factors} factors showing strong support, {winner} has a clear edge in this matchup. The combination of recent form, historical performance, and market consensus all point toward this outcome."


# Public API function
def explain_prediction(
    prediction: Dict[str, Any],
    match_data: Dict[str, Any],
    analysis_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Generate explainable prediction"""
    explainer = ExplainablePredictionSystem()
    return explainer.explain_prediction(prediction, match_data, analysis_data)
