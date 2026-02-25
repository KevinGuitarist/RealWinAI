"""
Main Cricket Match Prediction System
Enhanced with AI Summaries and Comprehensive Analysis
"""

import sys
import json
from datetime import datetime
from typing import List, Dict

from api_token import token_create_or_get
from match_finder import EnhancedMatchKeyFinder
from data_fetchers import google_search, fetch_article, get_match_insights
from prediction_engine import (
    match_prediction_with_summary, 
    calculate_data_availability_score, 
    calculate_confidence_level
)
from result_formatter import (
    write_to_result_file, 
    format_prediction_for_result, 
    format_legacy_prediction_for_result
)
from config import PROJECT_ID


def get_prediction_flag(model_prob_A: float, market_prob_A: float) -> str:
    """
    Assigns a standard prediction flag based on the model's probability
    estimates and a comparison with market odds.
    """
    is_A_market_underdog = market_prob_A < 50.0
    model_prob_B = 100.0 - model_prob_A

    # 1. Special case: Model identifies a potential upset where it favors the market underdog
    if is_A_market_underdog and 50.0 < model_prob_A < 55.0:
        return "Upset Alert"
    if not is_A_market_underdog and 50.0 < model_prob_B < 55.0:
        return "Upset Alert"

    # 2. Classify based on the stronger side's probability into four tiers
    favorite_prob = max(model_prob_A, model_prob_B)

    if favorite_prob >= 75.0:
        return "Overwhelming Favorite"
    elif 60.0 <= favorite_prob < 75.0:
        return "Likely Winner"
    elif 55.0 <= favorite_prob < 60.0:
        return "Slight Edge"
    else:  # Covers probabilities from 50.0 up to 55.0
        return "Tight Game"


def predict_all_matches_on_date(date_str: str, venue_name: str = None):
    """
    MAIN FUNCTION: Automatically finds ALL matches on a given date and generates detailed predictions with AI summaries.
    """
    print(f"🚀 Starting comprehensive match prediction with AI summaries for date: {date_str}")
    
    # Step 1: Get API token
    token = token_create_or_get()
    if not token:
        print("❌ Could not obtain API token. Exiting.")
        return None
    
    # Step 2: Find all matches on the specified date using the NEW method
    print(f"🔍 Finding all matches on {date_str}...")
    match_finder = EnhancedMatchKeyFinder(PROJECT_ID, token)
    matches_with_insights = match_finder.find_all_matches_on_date(date_str)
    
    if not matches_with_insights:
        print(f"❌ No matches found for date {date_str}")
        return None
    
    print(f"✅ Found {len(matches_with_insights)} matches on {date_str}")
    
    # Write header to result file
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    header = f"COMPREHENSIVE MATCH PREDICTIONS WITH AI SUMMARIES FOR {date_str}\nGenerated on: {timestamp}\nTotal matches found: {len(matches_with_insights)}"
    write_to_result_file(header, is_header=True)
    
    # Step 3: Generate predictions with summaries for each match
    all_predictions = []
    
    for i, match_info in enumerate(matches_with_insights, 1):
        print(f"\n{'='*60}")
        print(f"🎯 PROCESSING MATCH {i}/{len(matches_with_insights)}")
        print(f"🏏 {match_info['teams']['team_a']} vs {match_info['teams']['team_b']}")
        print(f"🗝️  Match Key: {match_info['match_key']}")
        print(f"🏟️  Tournament: {match_info['tournament']}")
        print(f"📍 Venue: {match_info['venue']}")
        print(f"⏰ Time: {match_info['match_time']}")
        print(f"🎮 Format: {match_info['format']}")
        print(f"📊 Status: {match_info['status']}")
        print(f"{'='*60}")
        
        try:
            # Step 4: Search for expert predictions and articles for this specific match
            print("🔍 Gathering expert predictions and articles...")
            team_a = match_info['teams']['team_a']
            team_b = match_info['teams']['team_b']
            
            query = f'"{team_a}" vs "{team_b}" cricket prediction {match_info["match_date"]}'
            urls = google_search(query)
            all_text = ""
            for url in urls:
                article_text = fetch_article(url)
                all_text += f"\n\nSOURCE: {url}\n{article_text}"
            
            # Step 5: Generate AI-powered prediction WITH SUMMARY
            print("🎯 Generating AI-powered prediction with summary...")
            prediction_json, ai_summary = match_prediction_with_summary(
                match_info['insights'], 
                team_a, 
                team_b, 
                match_info['match_date'], 
                match_info['venue'], 
                all_text
            )
            
            # Step 6: Display AI Summary in Console
            print(f"📝 AI SUMMARY: {ai_summary}")
            
            # Step 7: Calculate data availability and similarity scores
            available_fields, total_fields = calculate_data_availability_score(prediction_json)
            
            # Since we have the actual match from API, similarity score is perfect
            similarity_score = 1.0  # Perfect match from API
            has_perfect_match = True
            
            # Step 8: Calculate confidence level
            calculated_confidence = calculate_confidence_level(
                similarity_score, available_fields, total_fields, has_perfect_match
            )
            
            # Step 9: Override confidence in the prediction result
            try:
                prediction_dict = json.loads(prediction_json)
                original_confidence = prediction_dict.get('confidence', 'unknown')
                                # This block now calls the function we just added to this file.
                
                model_prob_a = prediction_dict.get('prediction', {}).get('a_win_pct', 0)
                market_prob_a = prediction_dict.get('bookmaker_odds', {}).get('implied_probability_a', 50.0)

                # Get the prediction flag using the new function
                prediction_flag = get_prediction_flag(model_prob_a, market_prob_a)
                
                # Add the flag to the prediction dictionary
                prediction_dict['prediction_flag'] = prediction_flag
                
                print(f"🚩 Prediction Flag: {prediction_flag}")
                prediction_dict['confidence'] = calculated_confidence
                
                # Add enhanced metadata
                prediction_dict['match_metadata'] = {
                    'match_key': match_info['match_key'],
                    'tournament': match_info['tournament'],
                    'format': match_info['format'],
                    'status': match_info['status'],
                    'match_time': match_info['match_time'],
                    'data_availability_score': f"{available_fields}/{total_fields}",
                    'similarity_score': similarity_score,
                    'has_perfect_match': has_perfect_match,
                    'confidence_override': {
                        'original': original_confidence,
                        'calculated': calculated_confidence,
                        'reasoning': f"Perfect API match (similarity={similarity_score:.2f}), {available_fields}/{total_fields} data fields available"
                    }
                }
                
                prediction_json = json.dumps(prediction_dict, ensure_ascii=False)
                
                print(f"📊 Match Quality: Similarity={similarity_score:.2f}, Perfect Match={has_perfect_match}")
                print(f"📊 Data Availability: {available_fields}/{total_fields} fields")
                print(f"📊 Calculated Confidence: {calculated_confidence.upper()}")
                print(f"🎯 Confidence Override: {original_confidence} → {calculated_confidence}")
                
            except json.JSONDecodeError:
                print("⚠️ Could not parse prediction JSON for confidence override")
            
            # Add the enhanced prediction to results
            all_predictions.append({
                'match_number': i,
                'match_info': match_info,
                'prediction': prediction_json,
                'ai_summary': ai_summary,  # Store summary separately for easy access
                'scores': {
                    'data_availability': f"{available_fields}/{total_fields}",
                    'similarity_score': similarity_score,
                    'confidence_level': calculated_confidence,
                    'has_perfect_match': has_perfect_match
                }
            })
            
            print(f"✅ Prediction {i} with AI Summary completed successfully!")
            
            # Write formatted prediction to result file
            formatted_result = format_prediction_for_result(all_predictions[-1], date_str)
            write_to_result_file(formatted_result)
            
        except Exception as e:
            print(f"❌ Error generating prediction for match {i}: {e}")
            # Add error entry to maintain consistency
            all_predictions.append({
                'match_number': i,
                'match_info': match_info,
                'prediction': json.dumps({
                    "error": f"Prediction generation failed: {str(e)}",
                    "teams": {"a_name": team_a, "b_name": team_b},
                    "confidence": "low",
                    "explanation": "Error occurred during prediction generation"
                }),
                'ai_summary': f"Analysis unavailable for {team_a} vs {team_b} due to prediction error.",
                'scores': {
                    'data_availability': "0/13",
                    'similarity_score': 1.0,
                    'confidence_level': 'low',
                    'has_perfect_match': True
                }
            })
            continue
            
            # Write error to result file too
            error_result = format_prediction_for_result(all_predictions[-1], date_str)
            write_to_result_file(error_result)
    
    print(f"\n{'='*60}")
    print(f"🏆 ALL PREDICTIONS WITH AI SUMMARIES COMPLETED!")
    print(f"📊 Successfully processed {len(all_predictions)} matches for {date_str}")
    print(f"📁 All detailed results with summaries saved to 'result' file")
    print(f"{'='*60}")
    
    return all_predictions


def predict_match_automatically(team1_name: str, team2_name: str, match_date: str, venue_name: str = None):
    """
    LEGACY FUNCTION: Enhanced function with AI summary for specific team match.
    """
    print("🚀 Starting enhanced automated cricket match prediction with AI summary...")
    
    # Step 1: Get API token
    token = token_create_or_get()
    if not token:
        print("❌ Could not obtain API token. Exiting.")
        return None
    
    # Step 2: Initialize enhanced match key finder and search automatically
    print(f"🔑 Obtaining API token...")
    print(f"🔍 Searching for match key using enhanced finder...")
    
    match_finder = EnhancedMatchKeyFinder(PROJECT_ID, token)
    match_result = match_finder.find_match_key_automatically(team1_name, team2_name, match_date)
    
    if isinstance(match_result, tuple):
        match_key, similarity_score, has_perfect_match = match_result
    else:
        # Fallback for backward compatibility
        match_key = match_result
        similarity_score = 0.0
        has_perfect_match = False
    
    if not match_key:
        print("❌ Could not find match key with enhanced search. Prediction cannot proceed.")
        return None
    
    # Step 3: Get match insights using found match key
    print(f"📊 Fetching match insights from Roanuz API...")
    insights = get_match_insights(PROJECT_ID, token, match_key)
    
    # Step 4: Search for expert predictions and articles
    print("🔍 Gathering expert predictions and articles...")
    query = f'"{team1_name}" vs "{team2_name}" cricket prediction {match_date}'
    urls = google_search(query)
    all_text = ""
    for url in urls:
        article_text = fetch_article(url)
        all_text += f"\n\nSOURCE: {url}\n{article_text}"
    
    # Step 5: Determine venue (use from insights if not provided)
    if not venue_name:
        try:
            venue_name = insights.get("data", {}).get("match", {}).get("venue", {}).get("name", "Unknown Venue")
        except:
            venue_name = "Unknown Venue"
    
    # Step 6: Generate AI-powered prediction WITH SUMMARY
    print("🎯 Generating AI-powered prediction with summary...")
    prediction_json, ai_summary = match_prediction_with_summary(insights, team1_name, team2_name, match_date, venue_name, all_text)

    # Step 7: Display AI Summary in Console
    print(f"📝 AI SUMMARY: {ai_summary}")

    # Step 8: Calculate data availability from actual prediction result
    available_fields, total_fields = calculate_data_availability_score(prediction_json)

    # Step 9: Calculate confidence level using enhanced rules
    calculated_confidence = calculate_confidence_level(
        similarity_score, available_fields, total_fields, has_perfect_match
    )
    
    print(f"📊 Match Quality: Similarity={similarity_score:.2f}, Perfect Match={has_perfect_match}")
    print(f"📊 Data Availability: {available_fields}/{total_fields} fields")
    print(f"📊 Calculated Confidence: {calculated_confidence.upper()}")
    
    # Step 10: Override confidence in the prediction result
    try:
        prediction_dict = json.loads(prediction_json)
        original_confidence = prediction_dict.get('confidence', 'unknown')
        prediction_dict['confidence'] = calculated_confidence
        prediction_dict['confidence_override'] = {
            'original': original_confidence,
            'calculated': calculated_confidence,
            'similarity_score': similarity_score,
            'data_fields': f"{available_fields}/{total_fields}",
            'perfect_match': has_perfect_match
        }
        prediction_json = json.dumps(prediction_dict, ensure_ascii=False)
        
        print(f"🎯 Confidence Override: {original_confidence} → {calculated_confidence}")
        
    except json.JSONDecodeError:
        print("⚠️ Could not parse prediction JSON for confidence override")
    
    print("\n✅ AUTOMATED PREDICTION WITH AI SUMMARY COMPLETE!")
    print("=" * 60)
    
    # Write legacy prediction to result file
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    header = f"LEGACY MATCH PREDICTION WITH AI SUMMARY: {team1_name} vs {team2_name}\nGenerated on: {timestamp}"
    write_to_result_file(header, is_header=True)
    
    formatted_result = format_legacy_prediction_for_result(prediction_json, team1_name, team2_name, match_date, venue_name)
    write_to_result_file(formatted_result)
    
    print(f"📁 Detailed results with AI summary saved to 'result' file")
    
    return prediction_json


# --- MAIN CLI INTERFACE ---
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Enhanced Cricket Match Prediction System with AI Summaries')
        print('========================================================')
        print('')
        print('OPTION 1 - Predict ALL matches on a specific date:')
        print('  python main.py YYYY-MM-DD')
        print('  Example: python main.py "2025-01-25"')
        print('')
        print('OPTION 2 - Predict specific team match (legacy):')
        print('  python main.py "Team 1" "Team 2" YYYY-MM-DD [venue]')
        print('  Example: python main.py "India" "Australia" "2025-01-21" "MCG"')
        print('')
        print('🤖 NEW FEATURE: All predictions now include AI-generated 50-100 word summaries!')
        print('')
        sys.exit(1)
    
    # Check if user wants all matches on a date (new feature)
    if len(sys.argv) == 2:
        date_input = sys.argv[1]
        
        # Validate date format
        try:
            datetime.strptime(date_input, '%Y-%m-%d')
        except ValueError:
            print("❌ Invalid date format. Please use YYYY-MM-DD.")
            sys.exit(1)
        
        print(f"🔍 Fetching ALL matches and predictions with AI summaries for {date_input}...")
        results = predict_all_matches_on_date(date_input)
        
        if results:
            # Display summary in console
            print(f"\n✅ PREDICTION WITH AI SUMMARIES COMPLETE!")
            print(f"📊 Processed {len(results)} matches for {date_input}")
            print(f"📁 All detailed analysis with AI summaries saved to 'result' file")
            print(f"🤖 Each match includes a personalized 50-100 word AI summary!")
            
            # Show brief summary of each match
            for result in results:
                match_info = result['match_info']
                ai_summary = result.get('ai_summary', 'Summary unavailable')
                try:
                    prediction = json.loads(result['prediction'])
                    if 'prediction' in prediction and 'error' not in prediction:
                        winner_team = match_info['teams']['team_a'] if prediction['prediction']['winner'] == 'A' else match_info['teams']['team_b']
                        win_percentage = prediction['prediction']['a_win_pct'] if prediction['prediction']['winner'] == 'A' else prediction['prediction']['b_win_pct']
                        print(f"   🏏 {match_info['teams']['team_a']} vs {match_info['teams']['team_b']} → {winner_team} ({win_percentage}%)")
                        print(f"      📝 Summary: {ai_summary}")
                    else:
                        print(f"   🏏 {match_info['teams']['team_a']} vs {match_info['teams']['team_b']} → Error in prediction")
                        print(f"      📝 Summary: {ai_summary}")
                except:
                    print(f"   🏏 {match_info['teams']['team_a']} vs {match_info['teams']['team_b']} → Could not parse prediction")
                    print(f"      📝 Summary: {ai_summary}")
        else:
            print(f"❌ No predictions generated for {date_input}")
    
    # Legacy specific team match prediction
    elif len(sys.argv) >= 4:
        team1 = sys.argv[1]
        team2 = sys.argv[2]
        date = sys.argv[3]
        venue = sys.argv[4] if len(sys.argv) > 4 else None
        
        print(f"🎯 Legacy mode: Predicting specific match {team1} vs {team2} with AI summary")
        
        # Run the enhanced automated prediction
        result = predict_match_automatically(team1, team2, date, venue)
        
        if result:
            print("✅ Enhanced prediction with AI summary successful!")
            print(f"📁 Detailed analysis with AI summary saved to 'result' file")
            
            # Show brief summary in console
            try:
                parsed_result = json.loads(result)
                if 'prediction' in parsed_result and 'error' not in parsed_result:
                    winner_team = team1 if parsed_result['prediction']['winner'] == 'A' else team2
                    win_percentage = parsed_result['prediction']['a_win_pct'] if parsed_result['prediction']['winner'] == 'A' else parsed_result['prediction']['b_win_pct']
                    print(f"🎯 Prediction: {winner_team} ({win_percentage}% chance)")
                    print(f"📊 Confidence: {parsed_result.get('confidence', 'unknown').upper()}")
                    
                    # Display AI Summary
                    if 'ai_summary' in parsed_result and parsed_result['ai_summary'].get('text'):
                        print(f"📝 AI Summary: {parsed_result['ai_summary']['text']}")
                else:
                    print(f"❌ Prediction Error: {parsed_result.get('error', 'Unknown error')}")
            except:
                print("⚠️ Could not parse prediction summary")
        else:
            print("❌ Prediction failed. Please check the inputs and try again.")
    
    else:
        print("❌ Invalid arguments. Please check usage examples above.")
        sys.exit(1)