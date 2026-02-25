"""
Core Match Prediction Engine with AI Integration
"""

import json
import openai
from typing import Dict, Any, Tuple
from config import OPENAI_API_KEY
# Import the odds calculation function from data_fetchers
from data_fetchers import get_pre_match_public_information, validate_and_extract_real_players, fetch_additional_bookmaker_odds
from ai_summary import extract_analysis_data_for_summary, generate_analysis_summary


# Set OpenAI API key
openai.api_key = OPENAI_API_KEY


def calculate_data_availability_score(prediction_json: str) -> Tuple[int, int]:
    """Calculate data availability score from prediction result."""
    key_data_fields = ['recent_form_summary', 'h2h_summary', 'venue_analysis', 'team_analysis',
                      'key_player_matchups', 'pitch_conditions', 'momentum_factors', 'tactical_insights',
                      'injury_impacts', 'injury_reports', 'weather_conditions', 'key_players_a', 'key_players_b']
    available_fields_count = 0
    total_fields_to_check = len(key_data_fields)

    try:
        parsed = json.loads(prediction_json)
        if 'supporting' in parsed:
            for field in key_data_fields:
                if field in parsed['supporting'] and parsed['supporting'][field] != "Data unavailable":
                    # Additional check for empty arrays
                    field_value = parsed['supporting'][field]
                    if isinstance(field_value, list) and len(field_value) == 0:
                        continue  # Empty array counts as unavailable
                    available_fields_count += 1
    except json.JSONDecodeError:
        pass

    return available_fields_count, total_fields_to_check


def calculate_confidence_level(similarity_score: float, available_fields: int,
                             total_fields: int, has_perfect_match: bool) -> str:
    """Calculate confidence level based on match quality and data availability."""
    data_availability_ratio = available_fields / total_fields if total_fields > 0 else 0

    # Enhanced confidence rules
    if has_perfect_match and similarity_score >= 0.95 and data_availability_ratio >= 0.7:
        return "high"
    elif has_perfect_match and similarity_score >= 0.8 and data_availability_ratio >= 0.5:
        return "medium"
    elif similarity_score >= 0.7 and data_availability_ratio >= 0.6:
        return "medium"
    else:
        return "low"


def match_prediction(insights: Dict[str, Any], team_a: str, team_b: str, match_date: str, venue: str, all_text: str) -> str:
    """Build the user prompt for advanced cricket match prediction with enhanced accuracy."""

    # Extract additional context from insights if available
    match_type = insights.get("data", {}).get("match", {}).get("format", "Unknown")
    tournament = insights.get("data", {}).get("match", {}).get("tournament", "Unknown")

    prompt = f"""
You are an elite cricket match prediction AI with authoritative access to verified real-time sports data, expert analysis, betting markets, and advanced statistical models. Your predictions must be highly accurate, logically consistent, and based ONLY on reliable, real-world information.

MATCH CONTEXT:
- Team A: {team_a}
- Team B: {team_b}
- Date: {match_date}
- Venue: {venue}
- Format: {match_type}
- Tournament: {tournament}

PREDICTION METHODOLOGY:
1. **Data Collection & Verification**:
   - Expert insights from ESPNCricinfo, Wisden, and trusted cricket analysts
   - Real-time betting odds from Roanuz (both live and pre-match)
   - AI projections from CricViz, Smart Stats, and predictive sports models
   - Venue analysis (pitch behavior, weather, historical match outcomes at ground)
   - Team dynamics: squad composition, injury updates, player availability
   - Key player matchups (batsman vs bowler records, recent duels)
   - Momentum indicators: last 5 matches, recent series/tournament form

2. **Advanced Probability Modelling**:
   - Head-to-head records → **30% weight**
   - Last 15 matches historical performance → **25% weight**
   - Recent form (last 5 matches) → **25% weight**
   - Venue-specific history → **20% weight**
   - Team balance and squad strength → **15% weight**
   - Key player availability and impact → **15% weight**
   - Contextual factors (weather, pitch, tournament stage) → **10% weight**

3. **Statistical Validation & Consistency**:
   - Cross-verify probabilities against betting market consensus
   - Refine probabilities via Bayesian inference
   - Logical rule: favorite probability > underdog probability
   - Acceptable probability ranges:
     - Favorite: **52–85%**
     - Underdog: **15–48%**
   - **Probabilities MUST sum to exactly 100%**

4. **Data Integrity & Transparency Rules**:
   - **NEVER fabricate or assume data**
   - If head-to-head unavailable → state explicitly "Data unavailable"
   - If recent form unavailable → cite "Data unavailable"
   - Player names must be real, active squad members only
   - No placeholders (e.g., "Player A", "Bowler 1") are permitted

5. **Confidence Calibration**:
   - HIGH: Complete, consistent data with clear favorite
   - MEDIUM: Most data available, moderate signals
   - LOW: Limited data, conflicting indicators, or weak insights
   - MANDATORY LOW: If PRE_MATCH_PUBLIC_VERIFIED_INFORMATION is empty/generic
   - **CRITICAL RULE**: Use the Data Availability Score (0–7). If < 5/7 → final confidence MUST be LOW

6. **Player Data Validation**:
   - Use only real, verifiable squad players
   - If unavailable → return empty arrays:
     - "key_players_a": []
     - "key_players_b": []
   - For matchups: use real names or explicitly state "Data unavailable"
   - Validate player names to ensure they are current, active professionals

VALIDATED_PLAYER_DATA:
Team A ({team_a}): {validate_and_extract_real_players(team_a, insights)}
Team B ({team_b}): {validate_and_extract_real_players(team_b, insights)}

7. **Result Format** (STRICT JSON only - DO NOT include bookmaker_odds section as it will be added separately):
```json
{{
    "match_key": "string_from_insights_or_generated",
    "teams": {{
        "a_code": "3-letter_code",
        "b_code": "3-letter_code",
        "a_name": "{team_a}",
        "b_name": "{team_b}"
    }},
    "prediction": {{
        "winner": "A_or_B",
        "a_win_pct": "float_0_to_100",
        "b_win_pct": "float_0_to_100",
        "method_confidence": "statistical_model_reliability"
    }},
    "confidence": "high_medium_or_low",
    "supporting": {{
        "recent_form_summary": "last_5_matches_analysis_or_data_unavailable",
        "h2h_summary": "historical_matchups_analysis_or_data_unavailable",
        "key_players_a": ["actual_player_name1", "actual_player_name2"] or [],
        "key_players_b": ["actual_player_name1", "actual_player_name2"] or [],
        "key_player_matchups": "actual_player1_vs_actual_player2_or_data_unavailable",
        "venue_analysis": "pitch_weather_historical_performance",
        "team_analysis": "team_strengths_weaknesses",
        "injury_impacts": "key_injuries_and_their_effects",
        "weather_conditions": "detailed_forecast_impact",
        "pitch_conditions": "surface_behavior_expectations",
        "tactical_insights": "strategic_advantages_weaknesses",
        "injury_reports": "key_player_availability_status",
        "momentum_factors": "current_form_psychological_edge"
    }},
    "explanation": "comprehensive_reasoning_for_prediction",
    "risk_factors": "potential_upset_scenarios",
    "betting_recommendation": "value_betting_insights"
}}
```

ANALYSIS INPUTS:

INSIGHTS_DATA:
{json.dumps(insights, ensure_ascii=False, indent=2)}

PRE_MATCH_VERIFIED_INFORMATION:
{get_pre_match_public_information(team_a, team_b, match_date, venue, all_text)}

CRITICAL INSTRUCTIONS:
- Return ONLY the JSON object - no markdown, no explanatory text
- DO NOT include bookmaker_odds section in your response as it will be added separately
- Ensure mathematical consistency in all probability calculations
- Validate that winner has higher win percentage than loser
- Apply conservative confidence scoring when data is limited
- Cross-reference all information sources for accuracy
- Focus on actionable insights for prediction reliability

Generate the prediction analysis now:
""".strip()

    try:
        completion = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a precision sports analytics AI. Return only valid JSON with accurate cricket match predictions. Never fabricate data. Ensure mathematical consistency in all probability calculations. DO NOT include bookmaker_odds section."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2500,
            response_format={"type": "json_object"}
        )

        content = completion.choices[0].message.content

        # Enhanced JSON validation and error handling
        try:
            parsed = json.loads(content)
            
            # Default win percentages
            a_pct = 0
            b_pct = 0

            # Validate key prediction logic and get win percentages
            if "prediction" in parsed and isinstance(parsed["prediction"], dict):
                a_pct = parsed["prediction"].get("a_win_pct", 0)
                b_pct = parsed["prediction"].get("b_win_pct", 0)

                # Ensure probabilities sum to ~100% and winner has higher percentage
                total = a_pct + b_pct
                if abs(total - 100) > 5:  # Allow 5% tolerance
                    parsed["validation_warning"] = f"Probability sum: {total}% (expected ~100%)"

                winner = parsed["prediction"].get("winner")
                if winner == "A" and a_pct <= b_pct:
                    parsed["validation_warning"] = "Logic error: Team A predicted winner but has lower win percentage"
                elif winner == "B" and b_pct <= a_pct:
                    parsed["validation_warning"] = "Logic error: Team B predicted winner but has lower win percentage"

            # Calculate custom bookmaker odds based on the AI's predicted win probability
            # This ensures the odds system is strictly aligned with data_fetchers.py
            win_prob_a = a_pct / 100.0 if a_pct > 0 else 0.5 # Default to 0.5 if no prediction
            custom_odds = fetch_additional_bookmaker_odds(team_a, team_b, match_date, win_probability_a=win_prob_a)
            team_a_odds = custom_odds.get(team_a, 0)
            team_b_odds = custom_odds.get(team_b, 0)
            
            # Add bookmaker odds directly, with implied probabilities matching the prediction
            parsed["bookmaker_odds"] = {
                "team_a_odds": team_a_odds,
                "team_b_odds": team_b_odds,
                "implied_probability_a": a_pct,
                "implied_probability_b": b_pct
            }

            # Validate player names
            if "supporting" in parsed:
                for team_key in ["key_players_a", "key_players_b"]:
                    players = parsed["supporting"].get(team_key, [])
                    if isinstance(players, list):
                        # Remove placeholder names
                        real_players = [p for p in players if not any(placeholder in p.lower()
                                      for placeholder in ["player a", "player b", "player c", "player d", "player e",
                                                        "batsman 1", "bowler 1", "all-rounder 1", "captain a", "captain b"])]
                        if len(real_players) < len(players):
                            parsed["supporting"][team_key] = real_players if real_players else []

                # Validate key player matchups
                matchups = parsed["supporting"].get("key_player_matchups", "")
                if any(placeholder in matchups.lower() for placeholder in ["player a", "player b", "player c", "player d"]):
                    parsed["supporting"]["key_player_matchups"] = "Data unavailable"

        except json.JSONDecodeError as e:
            # Fallback for JSON parsing error
            parsed = {
                "error": "Invalid JSON response from model",
                "json_error": str(e),
                "raw_content": content[:500] + "..." if len(content) > 500 else content,
                "teams": {"a_name": team_a, "b_name": team_b},
                "bookmaker_odds": fetch_additional_bookmaker_odds(team_a, team_b, match_date), # Default 50-50 odds
                "confidence": "low",
                "explanation": "Model result parsing failed - unable to generate reliable prediction"
            }

    except Exception as api_error:
        # Fallback for API call error
        parsed = {
            "error": "API call failed",
            "api_error": str(api_error),
            "teams": {"a_name": team_a, "b_name": team_b},
            "bookmaker_odds": fetch_additional_bookmaker_odds(team_a, team_b, match_date), # Default 50-50 odds
            "confidence": "low",
            "explanation": "Unable to connect to prediction model - no analysis available"
        }

    return json.dumps(parsed, ensure_ascii=False)


def match_prediction_with_summary(insights: Dict[str, Any], team_a: str, team_b: str, match_date: str, venue: str, all_text: str) -> Tuple[str, str]:
    """Enhanced match prediction function that returns both prediction and AI summary."""

    # First, get the original prediction
    prediction_json = match_prediction(insights, team_a, team_b, match_date, venue, all_text)

    # Extract analysis data for summary
    print("🔍 Extracting analysis data for summary generation...")
    analysis_data = extract_analysis_data_for_summary(prediction_json)

    # Generate AI summary
    print("🤖 Generating AI-powered analysis summary...")
    summary = generate_analysis_summary(analysis_data)

    # Add summary to the prediction JSON
    try:
        prediction_dict = json.loads(prediction_json)
        prediction_dict['ai_summary'] = {
            'text': summary,
            'based_on_fields': list(analysis_data.get('match_analysis', {}).keys()) + list(analysis_data.get('key_players', {}).keys())
        }
        enhanced_prediction_json = json.dumps(prediction_dict, ensure_ascii=False)

        print(f"✅ AI Summary generated ({len(summary.split())} words)")
        return enhanced_prediction_json, summary

    except json.JSONDecodeError:
        print("⚠️ Could not add summary to prediction JSON")
        return prediction_json, summary

    except Exception as e:
        print(f"❌ Error generating AI summary: {str(e)}")
        return prediction_json, summary