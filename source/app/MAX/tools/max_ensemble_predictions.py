"""
M.A.X. Multi-Model Ensemble Prediction System
Combines multiple AI models for superior accuracy
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import os
from openai import OpenAI

# API Keys
OPENAI_API_KEY = os.getenv(
    'OPENAI_API_KEY',
    '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'
)

openai_client = OpenAI(api_key=OPENAI_API_KEY)


class EnsemblePredictionSystem:
    """
    Combines multiple AI models for better predictions
    
    Models:
    - GPT-4o (primary analyst)
    - GPT-4o-mini (secondary analyst)
    - Claude (if available - counter-arguments)
    - Gemini (if available - statistical analysis)
    
    Methodology:
    - Each model generates independent prediction
    - Predictions are weighted by historical accuracy
    - Final prediction is ensemble consensus
    - Provides confidence intervals
    """
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=OPENAI_API_KEY)
        
        # Model weights (can be adjusted based on performance)
        self.model_weights = {
            'gpt-4o': 0.50,  # Primary model
            'gpt-4o-mini': 0.50  # Secondary model
            # Add Claude/Gemini weights when available
        }
        
        # Track model performance for dynamic weighting
        self.model_performance = {
            'gpt-4o': {'predictions': 0, 'correct': 0, 'accuracy': 0.75},
            'gpt-4o-mini': {'predictions': 0, 'correct': 0, 'accuracy': 0.73}
        }
    
    def generate_ensemble_prediction(
        self,
        match_data: Dict[str, Any],
        analysis_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate ensemble prediction from multiple models
        
        Args:
            match_data: Match information
            analysis_data: Pre-analyzed data (form, h2h, odds, etc.)
            
        Returns:
            Ensemble prediction with consensus and individual model outputs
        """
        
        # Generate predictions from each model
        model_predictions = {}
        
        # GPT-4o prediction
        try:
            model_predictions['gpt-4o'] = self._get_gpt4o_prediction(
                match_data, analysis_data
            )
        except Exception as e:
            model_predictions['gpt-4o'] = {'error': str(e), 'weight': 0}
        
        # GPT-4o-mini prediction
        try:
            model_predictions['gpt-4o-mini'] = self._get_gpt4o_mini_prediction(
                match_data, analysis_data
            )
        except Exception as e:
            model_predictions['gpt-4o-mini'] = {'error': str(e), 'weight': 0}
        
        # Calculate ensemble consensus
        consensus = self._calculate_consensus(model_predictions)
        
        # Generate confidence interval
        confidence_interval = self._calculate_confidence_interval(model_predictions)
        
        # Detect disagreements
        disagreements = self._detect_disagreements(model_predictions)
        
        return {
            'ensemble_prediction': {
                'predicted_winner': consensus['winner'],
                'confidence': consensus['confidence'],
                'consensus_strength': consensus['agreement_level'],
                'recommendation': self._get_ensemble_recommendation(consensus)
            },
            'individual_predictions': model_predictions,
            'confidence_interval': confidence_interval,
            'model_disagreements': disagreements,
            'methodology': 'Multi-model ensemble with weighted voting',
            'generated_at': datetime.now().isoformat()
        }
    
    def _get_gpt4o_prediction(
        self,
        match_data: Dict[str, Any],
        analysis_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get prediction from GPT-4o"""
        
        prompt = self._build_prediction_prompt(match_data, analysis_data)
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert sports analyst. Analyze the data and provide a prediction in JSON format with: winner, confidence (0-100), reasoning."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,  # Lower temperature for consistency
                response_format={"type": "json_object"}
            )
            
            prediction = json.loads(response.choices[0].message.content)
            prediction['model'] = 'gpt-4o'
            prediction['weight'] = self.model_weights['gpt-4o']
            
            return prediction
            
        except Exception as e:
            return {
                'error': str(e),
                'model': 'gpt-4o',
                'weight': 0
            }
    
    def _get_gpt4o_mini_prediction(
        self,
        match_data: Dict[str, Any],
        analysis_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get prediction from GPT-4o-mini"""
        
        prompt = self._build_prediction_prompt(match_data, analysis_data)
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a sports betting analyst. Provide prediction in JSON: winner, confidence (0-100), reasoning."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            prediction = json.loads(response.choices[0].message.content)
            prediction['model'] = 'gpt-4o-mini'
            prediction['weight'] = self.model_weights['gpt-4o-mini']
            
            return prediction
            
        except Exception as e:
            return {
                'error': str(e),
                'model': 'gpt-4o-mini',
                'weight': 0
            }
    
    def _build_prediction_prompt(
        self,
        match_data: Dict[str, Any],
        analysis_data: Dict[str, Any]
    ) -> str:
        """Build comprehensive prediction prompt"""
        
        team1 = match_data.get('team1', 'Team A')
        team2 = match_data.get('team2', 'Team B')
        
        return f"""
Analyze this match and provide a prediction:

**Match:** {team1} vs {team2}
**Date:** {match_data.get('date', 'TBD')}
**Venue:** {match_data.get('venue', 'TBD')}

**Analysis Data:**
- Recent Form: {json.dumps(analysis_data.get('recent_form', {}))}
- Head to Head: {json.dumps(analysis_data.get('head_to_head', {}))}
- Betting Odds: {json.dumps(analysis_data.get('odds', {}))}
- Pitch/Weather: {json.dumps(analysis_data.get('conditions', {}))}
- Team News: {json.dumps(analysis_data.get('team_news', {}))}

Provide your prediction in JSON format:
{{
    "winner": "<team_name>",
    "confidence": <0-100>,
    "reasoning": "<brief explanation>",
    "key_factors": ["<factor1>", "<factor2>", "<factor3>"]
}}

Be objective and data-driven. Consider all factors.
"""
    
    def _calculate_consensus(
        self,
        model_predictions: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate weighted consensus from model predictions"""
        
        # Filter out errored predictions
        valid_predictions = {
            model: pred for model, pred in model_predictions.items()
            if 'error' not in pred and 'winner' in pred
        }
        
        if not valid_predictions:
            return {
                'winner': 'Unknown',
                'confidence': 0,
                'agreement_level': 0,
                'error': 'All models failed'
            }
        
        # Count votes (weighted)
        votes = {}
        total_weight = 0
        
        for model, prediction in valid_predictions.items():
            winner = prediction.get('winner', '')
            weight = prediction.get('weight', 1.0)
            confidence = prediction.get('confidence', 50)
            
            # Weighted vote (weight × confidence)
            vote_power = weight * (confidence / 100)
            
            votes[winner] = votes.get(winner, 0) + vote_power
            total_weight += weight
        
        # Determine consensus winner
        consensus_winner = max(votes.items(), key=lambda x: x[1])[0] if votes else 'Unknown'
        consensus_vote_power = votes.get(consensus_winner, 0)
        
        # Calculate agreement level
        agreement_level = (consensus_vote_power / total_weight * 100) if total_weight > 0 else 0
        
        # Calculate ensemble confidence
        # Average confidence of models that agree with consensus
        agreeing_models = [
            pred for pred in valid_predictions.values()
            if pred.get('winner') == consensus_winner
        ]
        
        ensemble_confidence = sum(
            pred.get('confidence', 50) for pred in agreeing_models
        ) / len(agreeing_models) if agreeing_models else 0
        
        return {
            'winner': consensus_winner,
            'confidence': round(ensemble_confidence, 2),
            'agreement_level': round(agreement_level, 2),
            'agreeing_models': len(agreeing_models),
            'total_models': len(valid_predictions)
        }
    
    def _calculate_confidence_interval(
        self,
        model_predictions: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate confidence interval from model predictions"""
        
        confidences = [
            pred.get('confidence', 0)
            for pred in model_predictions.values()
            if 'error' not in pred and 'confidence' in pred
        ]
        
        if not confidences:
            return {'min': 0, 'max': 0, 'range': 0}
        
        min_conf = min(confidences)
        max_conf = max(confidences)
        avg_conf = sum(confidences) / len(confidences)
        
        return {
            'min_confidence': round(min_conf, 2),
            'max_confidence': round(max_conf, 2),
            'avg_confidence': round(avg_conf, 2),
            'confidence_range': round(max_conf - min_conf, 2),
            'uncertainty': 'High' if (max_conf - min_conf) > 20 else 'Low'
        }
    
    def _detect_disagreements(
        self,
        model_predictions: Dict[str, Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Detect disagreements between models"""
        
        disagreements = []
        
        # Get all predicted winners
        winners = {}
        for model, pred in model_predictions.items():
            if 'error' not in pred and 'winner' in pred:
                winner = pred['winner']
                if winner not in winners:
                    winners[winner] = []
                winners[winner].append({
                    'model': model,
                    'confidence': pred.get('confidence', 0),
                    'reasoning': pred.get('reasoning', '')
                })
        
        # If multiple winners predicted, it's a disagreement
        if len(winners) > 1:
            for winner, supporters in winners.items():
                disagreements.append({
                    'predicted_winner': winner,
                    'supporting_models': [s['model'] for s in supporters],
                    'avg_confidence': round(
                        sum(s['confidence'] for s in supporters) / len(supporters), 2
                    ),
                    'reasoning': supporters[0]['reasoning'] if supporters else ''
                })
        
        return disagreements
    
    def _get_ensemble_recommendation(
        self,
        consensus: Dict[str, Any]
    ) -> str:
        """Get betting recommendation based on ensemble"""
        
        confidence = consensus.get('confidence', 0)
        agreement = consensus.get('agreement_level', 0)
        
        if confidence >= 75 and agreement >= 80:
            return "STRONG BET - High confidence with model consensus"
        elif confidence >= 65 and agreement >= 70:
            return "GOOD BET - Solid confidence and agreement"
        elif confidence >= 55:
            return "CONSIDER - Moderate confidence, stake accordingly"
        else:
            return "SKIP - Low confidence or weak consensus"
    
    def update_model_performance(
        self,
        model_name: str,
        was_correct: bool
    ):
        """Update model performance for dynamic weighting"""
        
        if model_name in self.model_performance:
            self.model_performance[model_name]['predictions'] += 1
            if was_correct:
                self.model_performance[model_name]['correct'] += 1
            
            # Recalculate accuracy
            total = self.model_performance[model_name]['predictions']
            correct = self.model_performance[model_name]['correct']
            self.model_performance[model_name]['accuracy'] = correct / total if total > 0 else 0.5
            
            # Adjust weights based on performance (optional)
            self._adjust_weights()
    
    def _adjust_weights(self):
        """Dynamically adjust model weights based on performance"""
        
        # Get accuracies
        accuracies = {
            model: data['accuracy']
            for model, data in self.model_performance.items()
            if data['predictions'] >= 10  # Minimum 10 predictions
        }
        
        if not accuracies:
            return  # Not enough data
        
        # Normalize to sum to 1.0
        total_accuracy = sum(accuracies.values())
        
        if total_accuracy > 0:
            for model in accuracies:
                self.model_weights[model] = accuracies[model] / total_accuracy


# Public API function
def get_ensemble_prediction(
    match_data: Dict[str, Any],
    analysis_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Generate ensemble prediction from multiple models"""
    ensemble = EnsemblePredictionSystem()
    return ensemble.generate_ensemble_prediction(match_data, analysis_data)


def update_ensemble_performance(
    model_name: str,
    was_correct: bool
):
    """Update ensemble model performance tracking"""
    ensemble = EnsemblePredictionSystem()
    ensemble.update_model_performance(model_name, was_correct)
