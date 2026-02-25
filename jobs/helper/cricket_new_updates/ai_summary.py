"""
AI Summary Generation for Cricket Match Analysis
"""

import json
import openai
from typing import Dict, Any
from config import OPENAI_API_KEY


# Set OpenAI API key
openai.api_key = OPENAI_API_KEY


def extract_analysis_data_for_summary(prediction_json: str) -> Dict[str, Any]:
    """Extract key analysis data from prediction result for summary generation."""
    try:
        prediction = json.loads(prediction_json)
        supporting = prediction.get('supporting', {})
        
        # Extract all relevant analysis information
        analysis_data = {
            'match_analysis': {
                'recent_form': supporting.get('recent_form_summary', ''),
                'head_to_head': supporting.get('h2h_summary', ''),
                'venue_analysis': supporting.get('venue_analysis', ''),
                'team_analysis': supporting.get('team_analysis', ''),
                'tactical_insights': supporting.get('tactical_insights', ''),
                'momentum_factors': supporting.get('momentum_factors', ''),
                'weather_conditions': supporting.get('weather_conditions', ''),
                'pitch_conditions': supporting.get('pitch_conditions', ''),
                'injury_impacts': supporting.get('injury_impacts', '')
            },
            'key_players': {
                'team_a_players': supporting.get('key_players_a', []),
                'team_b_players': supporting.get('key_players_b', []),
                'key_matchups': supporting.get('key_player_matchups', '')
            },
            'prediction_summary': {
                'winner': prediction.get('prediction', {}).get('winner', ''),
                'winner_probability': prediction.get('prediction', {}).get('a_win_pct' if prediction.get('prediction', {}).get('winner') == 'A' else 'b_win_pct', 0),
                'confidence': prediction.get('confidence', ''),
                'explanation': prediction.get('explanation', '')
            },
            'team_names': {
                'team_a': prediction.get('teams', {}).get('a_name', ''),
                'team_b': prediction.get('teams', {}).get('b_name', '')
            }
        }
        
        return analysis_data
        
    except json.JSONDecodeError as e:
        print(f"⚠️ Error parsing prediction JSON for summary: {e}")
        return {}
    except Exception as e:
        print(f"⚠️ Error extracting analysis data: {e}")
        return {}


def generate_analysis_summary(analysis_data: Dict[str, Any]) -> str:
    """Generate a  summary of the match analysis using OpenAI."""
    
    if not analysis_data:
        return "Analysis data unavailable for summary generation."
    
    try:
        # Prepare the prompt with extracted analysis data
        team_a = analysis_data.get('team_names', {}).get('team_a', 'Team A')
        team_b = analysis_data.get('team_names', {}).get('team_b', 'Team B')
        
        # Build analysis context
        match_analysis = analysis_data.get('match_analysis', {})
        key_players = analysis_data.get('key_players', {})
        prediction_summary = analysis_data.get('prediction_summary', {})
        
        # Create context string with available data
        context_parts = []
        
        if match_analysis.get('recent_form') and match_analysis['recent_form'] != "Data unavailable":
            context_parts.append(f"Recent Form: {match_analysis['recent_form']}")
            
        if match_analysis.get('head_to_head') and match_analysis['head_to_head'] != "Data unavailable":
            context_parts.append(f"Head-to-Head: {match_analysis['head_to_head']}")
            
        if match_analysis.get('venue_analysis') and match_analysis['venue_analysis'] != "Data unavailable":
            context_parts.append(f"Venue: {match_analysis['venue_analysis']}")
            
        if match_analysis.get('team_analysis') and match_analysis['team_analysis'] != "Data unavailable":
            context_parts.append(f"Team Analysis: {match_analysis['team_analysis']}")
            
        if key_players.get('team_a_players') and len(key_players['team_a_players']) > 0:
            context_parts.append(f"Key Players {team_a}: {', '.join(key_players['team_a_players'])}")
            
        if key_players.get('team_b_players') and len(key_players['team_b_players']) > 0:
            context_parts.append(f"Key Players {team_b}: {', '.join(key_players['team_b_players'])}")
            
        if key_players.get('key_matchups') and key_players['key_matchups'] != "Data unavailable":
            context_parts.append(f"Key Matchups: {key_players['key_matchups']}")
            
        if match_analysis.get('tactical_insights') and match_analysis['tactical_insights'] != "Data unavailable":
            context_parts.append(f"Tactics: {match_analysis['tactical_insights']}")
            
        if match_analysis.get('momentum_factors') and match_analysis['momentum_factors'] != "Data unavailable":
            context_parts.append(f"Momentum: {match_analysis['momentum_factors']}")
            
        # If no meaningful context found, return fallback
        if not context_parts:
            return f"Limited analysis data available for {team_a} vs {team_b}. Prediction confidence: {prediction_summary.get('confidence', 'unknown')}."
        
        analysis_context = "\n".join(context_parts)
        
        # Create OpenAI prompt
        prompt = f"""You are given cricket match analysis data. Your task is to generate a concise, well-structured detailed summary of minimum 200 words. The summary must:
            Be written in a professional and analytical tone.
            Be organized into two balanced paragraphs, with lines aligned horizontally for a clean presentation.
            Highlight the key insights and clearly explain the prediction rationale.
            Use clear, simple language and avoid overly technical jargon.
            Apply effective formatting for readability (e.g., consistent line breaks, neat structure).

Match: {team_a} vs {team_b}
Predicted Winner: {team_a if prediction_summary.get('winner') == 'A' else team_b}
Win Probability: {prediction_summary.get('winner_probability', 'N/A')}%
Confidence Level: {prediction_summary.get('confidence', 'unknown')}

Analysis Data:
{analysis_context}

Requirements:
- Generate a complete summary analysis based only on the provided data
- Focus on the most important factors influencing the prediction
- Mention key players if available
- Include the main reasons for the predicted outcome
- Professional, analytical tone
- No fabricated information

Generate summary:"""

        # Call OpenAI API
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system", 
                    "content": "You are a professional cricket analyst. Generate concise, accurate summaries based only on the provided data. Do not fabricate any information."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,  # Low temperature for consistency
            max_tokens=150,   # Limit tokens to ensure concise summary
        )
        
        summary = response.choices[0].message.content.strip()
        
        # Validate word count (aim for 200-300 words)
        words = summary.split()
        word_count = len(words)

        if word_count < 200:
            # Add filler/extra clarification sentence
            summary += f" This analysis is presented with {prediction_summary.get('confidence', 'moderate')} confidence, based on current data trends."
        elif word_count > 300:
            # Trim down to 300 words max
             summary = ' '.join(words[:300]) + "..."

        
        return summary
        
    except Exception as e:
        print(f"⚠️ Error generating AI summary: {e}")
        # Return fallback summary
        team_a = analysis_data.get('team_names', {}).get('team_a', 'Team A')
        team_b = analysis_data.get('team_names', {}).get('team_b', 'Team B')
        confidence = analysis_data.get('prediction_summary', {}).get('confidence', 'unknown')
        return f"Match analysis summary unavailable for {team_a} vs {team_b}. Prediction generated with {confidence} confidence level based on available data."