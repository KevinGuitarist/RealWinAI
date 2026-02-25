import requests
import http.client
import json
from datetime import datetime, timedelta
import pytz
import sys
import time
import ast
from typing import Dict, List, Set, Any, Optional, Tuple
import openai
from bs4 import BeautifulSoup
from urllib.parse import quote
import difflib
import os

# --- CONFIGURATION ---
PROJECT_ID = "RS_P_1942111570733699074"
BASE_URL = "https://api.sports.roanuz.com/v5/cricket"
CRICKET_API_KEY = "RS5:836fe0c1a85d44000f7ebe67f9d730c4"
API_URL = f'https://api.sports.roanuz.com/v5/cricket/{PROJECT_ID}/featured-tournaments/'
OPENAI_API_KEY = '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'
openai.api_key = OPENAI_API_KEY

# === NEW FUNCTIONS FOR AI SUMMARY ===

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

# --- ENHANCED TOKEN MANAGEMENT ---
def token_create_or_get():
    """Gets a temporary token from Roanuz with improved error handling."""
    try:
        conn = http.client.HTTPSConnection("api.sports.roanuz.com")
        payload = json.dumps({"api_key": CRICKET_API_KEY})
        headers = {'Content-Type': 'application/json'}
        conn.request("POST", f"/v5/core/{PROJECT_ID}/auth/", payload, headers)
        res = conn.getresponse()
        data = res.read()
        
        response_json = json.loads(data.decode("utf-8"))
        if response_json.get("data") and "token" in response_json["data"]:
            print("✅ Token generated successfully")
            return response_json["data"]["token"]
        else:
            print(f"❌ Token fetch failed: {response_json.get('error', 'Unknown error')}")
            return None
    except Exception as e:
        print(f"❌ Fatal error in token_create_or_get: {e}")
        return None

# --- ENHANCED MATCH KEY FINDER CLASS ---
class EnhancedMatchKeyFinder:
    """Enhanced match key finder with improved search strategies and team matching."""
    
    def __init__(self, project_id: str, token: str):
        self.project_id = project_id
        self.token = token
        self.headers = {"rs-token": token}
        self.seen_match_keys: Set[str] = set()
        self.all_matches: List[Dict] = []
        
    def normalize_team_name(self, name: str) -> str:
        """Normalize team names for better matching."""
        # Remove common prefixes/suffixes and normalize
        common_removes = [" Cricket Club", " CC", " FC", " United", " XI"]
        normalized = name.strip()
        
        for remove in common_removes:
            if normalized.endswith(remove):
                normalized = normalized[:-len(remove)].strip()
                
        return normalized.lower()
    
    def calculate_team_similarity(self, team1: str, team2: str) -> float:
        """Calculate similarity between team names using difflib."""
        return difflib.SequenceMatcher(None, 
                                     self.normalize_team_name(team1), 
                                     self.normalize_team_name(team2)).ratio()
    
    def is_team_match(self, api_team_name: str, search_team_name: str, 
                     threshold: float = 0.6) -> Tuple[bool, float]:
        """Check if team names match with similarity scoring."""
        similarity = self.calculate_team_similarity(api_team_name, search_team_name)
        
        # Direct substring match gets priority
        if search_team_name.lower() in api_team_name.lower() or \
           api_team_name.lower() in search_team_name.lower():
            return True, max(similarity, 0.8)
            
        return similarity >= threshold, similarity
    
    def add_match_if_unique(self, match: Dict):
        """Add match to collection if not already seen."""
        match_key = match.get("key")
        if match_key and match_key not in self.seen_match_keys:
            self.all_matches.append(match)
            self.seen_match_keys.add(match_key)
    
    def fetch_fixtures_api_comprehensive(self, date_range: List[datetime]) -> int:
        """Strategy 1: NEW - Comprehensive Fixtures API search (MG100 and MG101)."""
        print("📋 [Strategy 1/5] Searching Comprehensive Fixtures API...")
        count = 0
        
        try:
            # Get unique year-months from date range
            year_months = list({d.strftime("%Y-%m") for d in date_range})
            
            for year_month in year_months:
                # MG100: Monthly fixtures
                try:
                    mg100_url = f"{BASE_URL}/{self.project_id}/fixtures/date/{year_month}/"
                    mg100_resp = requests.get(mg100_url, headers=self.headers, timeout=15)
                    mg100_resp.raise_for_status()
                    
                    mg100_data = mg100_resp.json().get("data", {})
                    month_data = mg100_data.get("month", {})
                    
                    for day_data in month_data.get("days", []):
                        for match in day_data.get("matches", []):
                            self.add_match_if_unique(match)
                            count += 1
                    
                    print(f"   MG100: Found {len(month_data.get('days', []))} days with matches for {year_month}")
                    
                except Exception as e:
                    print(f"   ⚠️ MG100 Error for {year_month}: {e}")
                
                # MG101: Day-by-day fixtures (more granular)
                try:
                    # Get specific days from date range for this month
                    month_dates = [d for d in date_range if d.strftime("%Y-%m") == year_month]
                    
                    for date_obj in month_dates:
                        day = date_obj.day
                        mg101_url = f"{BASE_URL}/{self.project_id}/fixtures/mg/MG101/date/{year_month}/page/{day}/"
                        
                        try:
                            mg101_resp = requests.get(mg101_url, headers=self.headers, timeout=10)
                            mg101_resp.raise_for_status()
                            
                            mg101_data = mg101_resp.json().get("data", {})
                            day_matches = mg101_data.get("matches", [])
                            
                            for match in day_matches:
                                self.add_match_if_unique(match)
                                count += 1
                                
                        except requests.exceptions.HTTPError as he:
                            if he.response.status_code == 404:
                                # No matches for this day, continue
                                continue
                            else:
                                print(f"   ⚠️ MG101 HTTP Error for {year_month}/{day}: {he}")
                        except Exception as e:
                            print(f"   ⚠️ MG101 Error for {year_month}/{day}: {e}")
                            
                except Exception as e:
                    print(f"   ⚠️ MG101 processing error for {year_month}: {e}")
                    
        except Exception as e:
            print(f"   ⚠️ Error in comprehensive fixtures search: {e}")
            
        return count
    
    def fetch_featured_matches_direct(self) -> int:
        """Strategy 2: Get matches directly from Featured Matches API."""
        print("📋 [Strategy 2/5] Searching Featured Matches API...")
        count = 0
        
        try:
            url = f"{BASE_URL}/{self.project_id}/featured-matches/"
            resp = requests.get(url, headers=self.headers, timeout=10)
            resp.raise_for_status()
            
            data = resp.json().get("data", {})
            matches = data.get("matches", [])
            
            for match in matches:
                self.add_match_if_unique(match)
                count += 1
                
            print(f"   Found {count} featured matches")
            
        except Exception as e:
            print(f"   ⚠️ Error in featured matches: {e}")
            
        return count
    
    def fetch_tournament_featured_matches(self) -> int:
        """Strategy 3: Get matches from Tournament Featured Matches."""
        print("📋 [Strategy 3/5] Searching Tournament Featured Matches...")
        count = 0
        
        try:
            # First get featured tournaments
            tournaments_url = f"{BASE_URL}/{self.project_id}/featured-tournaments/"
            resp = requests.get(tournaments_url, headers=self.headers, timeout=10)
            resp.raise_for_status()
            
            tournaments = resp.json().get('data', {}).get('tournaments', [])
            ongoing_tournaments = self.get_ongoing_tournaments(tournaments)
            
            print(f"   Found {len(ongoing_tournaments)} ongoing tournaments")
            
            for tournament in ongoing_tournaments:
                try:
                    tkey = tournament.get('key')
                    if not tkey:
                        continue
                        
                    # Get featured matches for this tournament
                    featured_url = f"{BASE_URL}/{self.project_id}/tournament/{tkey}/featured-matches/"
                    tr_resp = requests.get(featured_url, headers=self.headers, timeout=10)
                    tr_resp.raise_for_status()
                    
                    matches = tr_resp.json().get("data", {}).get("matches", [])
                    for match in matches:
                        self.add_match_if_unique(match)
                        count += 1
                        
                except Exception as e:
                    print(f"   ⚠️ Error fetching featured matches for tournament {tkey}: {e}")
                    continue
                    
        except Exception as e:
            print(f"   ⚠️ Error in tournament featured matches: {e}")
            
        return count
    
    def fetch_tournament_fixtures(self) -> int:
        """Strategy 4: Get matches from Tournament Fixtures (comprehensive)."""
        print("📋 [Strategy 4/5] Searching Tournament Fixtures...")
        count = 0
        
        try:
            # Get all tournament keys from multiple sources
            all_tournament_keys = set()
            
            # Featured tournaments
            tournaments_url = f"{BASE_URL}/{self.project_id}/featured-tournaments/"
            resp = requests.get(tournaments_url, headers=self.headers, timeout=10)
            resp.raise_for_status()
            tournaments = resp.json().get('data', {}).get('tournaments', [])
            
            for t in tournaments:
                if t.get('key'):
                    all_tournament_keys.add(t['key'])
            
            # Country-specific tournaments
            popular_countries = ["IND", "AUS", "GBR", "PAK", "NZL", "LKA", "BGD", 
                               "ZAF", "WIN", "AFG", "IRE", "SCO", "ARE", "ZWE", "CAN"]
            country_keys = self.get_tournament_keys_by_countries(popular_countries)
            
            for keys in country_keys.values():
                all_tournament_keys.update(keys)
            
            print(f"   Searching {len(all_tournament_keys)} tournament fixtures")
            
            for tkey in all_tournament_keys:
                try:
                    fixtures_url = f"{BASE_URL}/{self.project_id}/tournament/{tkey}/fixtures/"
                    tr_resp = requests.get(fixtures_url, headers=self.headers, timeout=10)
                    tr_resp.raise_for_status()
                    
                    matches = tr_resp.json().get("data", {}).get("matches", [])
                    for match in matches:
                        self.add_match_if_unique(match)
                        count += 1
                        
                except Exception as e:
                    print(f"   ⚠️ Error fetching fixtures for tournament {tkey}: {e}")
                    continue
                    
        except Exception as e:
            print(f"   ⚠️ Error in tournament fixtures: {e}")
            
        return count
    
    def fetch_monthly_fixtures_legacy(self, date_range: List[datetime]) -> int:
        """Strategy 5: Monthly fixtures fallback (legacy method)."""
        print("📋 [Strategy 5/5] Searching Legacy Monthly Fixtures...")
        count = 0
        
        try:
            year_months = list({d.strftime("%Y-%m") for d in date_range})
            
            for year_month in year_months:
                try:
                    url = f"{BASE_URL}/{self.project_id}/fixtures/date/{year_month}/"
                    resp = requests.get(url, headers=self.headers, timeout=10)
                    resp.raise_for_status()
                    
                    data = resp.json().get("data", {})
                    for day in data.get("month", {}).get("days", []):
                        for match in day.get("matches", []):
                            self.add_match_if_unique(match)
                            count += 1
                            
                except Exception as e:
                    print(f"   ⚠️ Error fetching monthly data for {year_month}: {e}")
                    continue
                    
        except Exception as e:
            print(f"   ⚠️ Error in monthly fixtures: {e}")
            
        return count
    
    def get_ongoing_tournaments(self, tournaments: List[Dict]) -> List[Dict]:
        """Filter tournaments that are currently ongoing."""
        now = time.time()
        return [
            t for t in tournaments
            if t.get('start_date', 0) <= now <= t.get('last_scheduled_match_date', 0)
        ]
    
    def get_tournament_keys_by_countries(self, countries: List[str]) -> Dict[str, List[str]]:
        """Get tournament keys for specific countries."""
        result = {}
        
        for country in countries:
            try:
                assoc_url = f"{BASE_URL}/{self.project_id}/association/list-by-country/{country}/"
                resp = requests.get(assoc_url, headers=self.headers, timeout=10)
                resp.raise_for_status()
                payload = resp.json()

                associations = payload.get("associations") or payload.get("data") or {}
                assoc_list = associations.get("associations", [])

                keys = []
                for assoc in assoc_list:
                    try:
                        assoc_key = assoc.get("key")
                        if not assoc_key:
                            continue

                        tourn_url = f"{BASE_URL}/{self.project_id}/association/{assoc_key}/featured-tournaments/"
                        tr_resp = requests.get(tourn_url, headers=self.headers, timeout=10)
                        tr_resp.raise_for_status()
                        tr_payload = tr_resp.json()

                        tournaments = tr_payload.get("data", {})
                        for tourn in tournaments.get("tournaments", []):
                            key = tourn.get("key")
                            if key:
                                keys.append(key)
                    except Exception:
                        continue

                result[country] = keys

            except Exception:
                result[country] = []

        return result
    
    def filter_matches_by_teams_and_date(self, team1_name: str, team2_name: str, 
                                       target_dates: Set, min_similarity: float = 0.6) -> Tuple[List[Dict], List[Dict]]:
        """Filter matches by team names and date with improved matching."""
        perfect_matches = []
        partial_matches = []
        
        for match in self.all_matches:
            try:
                # Check date first
                match_date = datetime.fromtimestamp(match.get("start_at", 0), tz=pytz.utc).date()
                if match_date not in target_dates:
                    continue
                
                team_a = match['teams']['a']['name']
                team_b = match['teams']['b']['name']
                
                # Check team matching with similarity scores
                team1_matches_a, sim1a = self.is_team_match(team_a, team1_name, min_similarity)
                team1_matches_b, sim1b = self.is_team_match(team_b, team1_name, min_similarity)
                team2_matches_a, sim2a = self.is_team_match(team_a, team2_name, min_similarity)
                team2_matches_b, sim2b = self.is_team_match(team_b, team2_name, min_similarity)
                
                # Perfect match: both teams match (in either order)
                if (team1_matches_a and team2_matches_b) or (team1_matches_b and team2_matches_a):
                    match['_similarity_score'] = max(sim1a + sim2b, sim1b + sim2a)
                    perfect_matches.append(match)
                # Partial match: at least one team matches
                elif team1_matches_a or team1_matches_b or team2_matches_a or team2_matches_b:
                    match['_similarity_score'] = max(sim1a, sim1b, sim2a, sim2b)
                    partial_matches.append(match)
                    
            except (KeyError, TypeError) as e:
                print(f"   ⚠️ Error processing match data: {e}")
                continue
        
        # Sort by similarity score (highest first)
        perfect_matches.sort(key=lambda x: x.get('_similarity_score', 0), reverse=True)
        partial_matches.sort(key=lambda x: x.get('_similarity_score', 0), reverse=True)
        
        return perfect_matches, partial_matches
    
    def filter_matches_by_date(self, target_dates: Set) -> List[Dict]:
        """Filter matches by date only (for finding all matches on a specific date)."""
        filtered_matches = []
        
        for match in self.all_matches:
            try:
                # Check date first
                match_date = datetime.fromtimestamp(match.get("start_at", 0), tz=pytz.utc).date()
                if match_date in target_dates:
                    filtered_matches.append(match)
            except (KeyError, TypeError) as e:
                print(f"   ⚠️ Error processing match data: {e}")
                continue
        
        return filtered_matches

    def find_all_matches_on_date(self, date_str: str) -> List[Dict]:
        """
        Find all matches on a specific date (without requiring team names).
        Now uses the comprehensive Fixtures API as the primary source.
        
        Args:
            date_str: Date in YYYY-MM-DD format
            
        Returns:
            List of match info dictionaries for all matches found on the date
        """
        print(f"🔍 Finding all matches on {date_str}...")

        # Parse date and create search window
        try:
            center_date = datetime.strptime(date_str, "%Y-%m-%d")
            target_dates = {center_date.date()}
            date_range = [center_date]
        except ValueError:
            print("❌ Invalid date format. Please use YYYY-MM-DD.")
            return []

        # Reset collections
        self.seen_match_keys.clear()
        self.all_matches.clear()

        # Execute all strategies with Fixtures API as primary
        strategy_counts = [
            self.fetch_fixtures_api_comprehensive(date_range),  # NEW: Primary comprehensive search
            self.fetch_featured_matches_direct(),
            self.fetch_tournament_featured_matches(),
            self.fetch_tournament_fixtures(),
            self.fetch_monthly_fixtures_legacy(date_range),     # Fallback legacy method
        ]

        total_found = len(self.all_matches)
        print(f"📊 Search completed: {total_found} total unique matches found.")
        print(f"   Strategy breakdown → {strategy_counts}")

        # Filter by date only
        date_matches = self.filter_matches_by_date(target_dates)
        
        if not date_matches:
            print(f"❌ No matches found for date {date_str}")
            return []

        print(f"✅ Found {len(date_matches)} matches on {date_str}")
        
        # Convert matches to structured format
        matches_with_insights = []
        seen_match_keys_final = set()
        for match in date_matches:
            try:
                match_key = match.get('key')
                if match_key in seen_match_keys_final:
                    continue

                match_info = {
                    'match_key': match_key,
                    'teams': {
                        'team_a': match.get('teams', {}).get('a', {}).get('name', 'Unknown'),
                        'team_b': match.get('teams', {}).get('b', {}).get('name', 'Unknown')
                    },
                    'match_date': date_str,
                    'venue': match.get('venue', {}).get('name', 'Unknown Venue') if match.get('venue') else 'Unknown Venue',
                    'tournament': match.get('tournament', {}).get('name', 'Unknown Tournament') if match.get('tournament') else 'Unknown Tournament',
                    'format': match.get('format', 'Unknown'),
                    'status': match.get('status', 'Unknown'),
                    'match_time': datetime.fromtimestamp(match.get("start_at", 0), tz=pytz.utc).strftime("%Y-%m-%d %H:%M UTC"),
                    'insights': match
                }
                matches_with_insights.append(match_info)
                seen_match_keys_final.add(match_key)
            except Exception as e:
                print(f"   ⚠️ Error processing match: {e}")
                continue
        
        return matches_with_insights

    def find_match_key_automatically(self, team1_name: str, team2_name: str, date_str: str) -> Tuple[Optional[str], float, bool]:
        """
        Main automated match key finder for specific teams.
        Now uses the comprehensive Fixtures API as the primary source.
        Returns the best match key if found, None otherwise.
        """
        print(f"🔍 Searching match key for '{team1_name}' vs '{team2_name}' on {date_str}...")

        # Parse exact date only
        try:
            center_date = datetime.strptime(date_str, "%Y-%m-%d")
            target_dates = {center_date.date()}
        except ValueError:
            print("❌ Invalid date format. Please use YYYY-MM-DD.")
            return None, 0.0, False

        # Reset collections
        self.seen_match_keys.clear()
        self.all_matches.clear()

        # Execute all strategies with Fixtures API as primary
        strategy_counts = [
            self.fetch_fixtures_api_comprehensive([center_date]),  # NEW: Primary comprehensive search
            self.fetch_featured_matches_direct(),
            self.fetch_tournament_featured_matches(),
            self.fetch_tournament_fixtures(),
            self.fetch_monthly_fixtures_legacy([center_date]),     # Fallback legacy method
        ]

        total_found = len(self.all_matches)
        print(f"📊 Search completed: {total_found} total unique matches found.")
        print(f"   Strategy breakdown → {strategy_counts}")

        # Filter by teams and date with enhanced matching
        perfect_matches, partial_matches = self.filter_matches_by_teams_and_date(
            team1_name, team2_name, target_dates, min_similarity=0.6
        )

        # Return best match with metadata
        if perfect_matches:
            best_match = perfect_matches[0]
            match_key = best_match["key"]
            similarity = best_match.get("_similarity_score", 0)

            print(f"✅ Perfect match (similarity: {similarity:.2f})")
            print(f"   Teams: {best_match['teams']['a']['name']} vs {best_match['teams']['b']['name']}")
            print(f"   Match Key: {match_key}")
            return match_key, similarity, True

        elif partial_matches:
            best_match = partial_matches[0]
            match_key = best_match["key"]
            similarity = best_match.get("_similarity_score", 0)

            print(f"⚠️ Partial match (similarity: {similarity:.2f})")
            print(f"   Teams: {best_match['teams']['a']['name']} vs {best_match['teams']['b']['name']}")
            print(f"   Match Key: {match_key}")
            print("   Note: Names don't perfectly match but this is the closest result.")
            return match_key, similarity, False

        else:
            # No matches found
            print(f"❌ No matches found for '{team1_name}' vs '{team2_name}' on {date_str}")
            print("   Try alternate team name variations or check the date.")
            return None, 0.0, False

def google_search(query, num_results=5):
    url = "https://serpapi.com/search"
    params = {
        "engine": "google",
        "q": query,
        "num": 10,
        "api_key": "f07ed032504d460515109d6fb520ee7514d87cbe0efcbe3d8f5bae7717ae520e"
    }
    res = requests.get(url, params=params)
    data = res.json()
    links = [item["link"] for item in data.get("organic_results", [])]
    print(f"Links : {links}")
    return links

def fetch_article(url):
    """Fetch and extract text from an article"""
    try:
        headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36"
}
        html = requests.get(url, headers=headers, timeout=10).text
        soup = BeautifulSoup(html, "html.parser")
        paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")]
        return "\n".join(paragraphs)
    except Exception as e:
        return f"Error fetching {url}: {e}"

def fetch_player_stats(team_name, match_date):
    """Fetch recent player performance stats with actual squad members."""
    try:
        # Try multiple sources for actual squad data
        search_queries = [
            f"{team_name} cricket team playing XI {match_date}",
            f"{team_name} cricket team players list {match_date}",
            f"{team_name} playing XI squad {match_date}"
        ]
        
        for query in search_queries:
            urls = google_search(query, num_results=3)
            for url in urls:
                article_text = fetch_article(url)
                
                # Look for actual player names in the content
                if len(article_text) > 100 and "error" not in article_text.lower():
                    # Extract potential player names (basic heuristic)
                    lines = article_text.split('\n')
                    players = []
                    for line in lines[:50]:  # Check first 50 lines
                        if any(keyword in line.lower() for keyword in ['captain', 'batsman', 'bowler', 'wicket-keeper']):
                            # Extract names from these lines
                            words = line.split()
                            potential_names = [w for w in words if w.istitle() and len(w) > 2]
                            players.extend(potential_names[:3])
                    
                    if len(players) >= 3:
                        return f"Key players for {team_name}: {', '.join(players[:5])}"
        
        return "Data unavailable"
        
    except Exception as e:
        return "Data unavailable"
    
def fetch_injury_updates(team_name):
    """Fetch injury/availability info."""
    try:
        search_url = f"https://www.espncricinfo.com/search?q={quote(team_name+' injury')}"
        html = requests.get(search_url, headers={"User-Agent": "Mozilla/5.0"}).text
        soup = BeautifulSoup(html, "html.parser")
        news_items = [p.text.strip() for p in soup.select("p") if "injury" in p.text.lower()]
        return news_items[0] if news_items else "No major injuries reported."
    except Exception as e:
        return f"Data unavailable: {e}"

def fetch_pitch_conditions(venue):
    """Fetch pitch report."""
    try:
        search_url = f"https://www.espncricinfo.com/search?q={quote(venue+' pitch report')}"
        html = requests.get(search_url, headers={"User-Agent": "Mozilla/5.0"}).text
        soup = BeautifulSoup(html, "html.parser")
        paragraphs = [p.text.strip() for p in soup.find_all("p")]
        report = next((p for p in paragraphs if "pitch" in p.lower()), None)
        return report if report else "Data unavailable"
    except Exception as e:
        return f"Data unavailable: {e}"

def fetch_weather_forecast(venue, match_date):
    """Fetch weather forecast."""
    try:
        city = venue.split(",")[-2].strip()
        url = f"https://wttr.in/{quote(city)}?format=j1"
        resp = requests.get(url, timeout=5).json()
        forecast = resp.get("weather", [{}])[0].get("hourly", [{}])[0]
        if forecast:
            return f"Weather on {match_date}: {forecast.get('weatherDesc',[{'value':'Data unavailable'}])[0]['value']}, temp {forecast.get('tempC')}°C"
        return "Data unavailable"
    except Exception as e:
        return f"Data unavailable: {e}"

def fetch_additional_bookmaker_odds(team_a, team_b):
    """Fetch live betting odds."""
    try:
        api_key = "YOUR_ODDSAPI_KEY"
        url = f"https://api.the-odds-api.com/v4/sports/cricket_odds/?apiKey={api_key}"
        resp = requests.get(url).json()
        for match in resp:
            if team_a in match.get("teams", []) and team_b in match.get("teams", []):
                odds = match.get("bookmakers", [{}])[0].get("markets", [{}])[0].get("outcomes", [])
                odds_dict = {o["name"]: o["price"] for o in odds}
                return {team_a: odds_dict.get(team_a, 0), team_b: odds_dict.get(team_b, 0)}
        return {team_a: 0, team_b: 0}
    except Exception as e:
        return {team_a: "Data unavailable", team_b: "Data unavailable"}

def validate_and_extract_real_players(team_name: str, insights_data: Dict[str, Any]) -> List[str]:
    """Extract real player names from API insights or return empty list."""
    try:
        # Try to get squad from insights data
        match_data = insights_data.get("data", {})
        if "squads" in match_data:
            team_key = None
            for team in match_data.get("teams", {}).values():
                if team.get("name", "").lower() in team_name.lower():
                    team_key = team.get("key")
                    break
            
            if team_key and team_key in match_data.get("squads", {}):
                squad = match_data["squads"][team_key]
                players = []
                for player in squad.get("players", []):
                    name = player.get("name", "").strip()
                    if name and len(name) > 2:
                        players.append(name)
                return players[:5]  # Return top 5 players
        
        return []
    except Exception:
        return []    

def get_pre_match_public_information(team_a, team_b, match_date, venue, text):
    """Returns a detailed pre-match analysis."""
    articles_summary = text
    player_stats_a = fetch_player_stats(team_a, match_date)
    player_stats_b = fetch_player_stats(team_b, match_date)
    injury_a = fetch_injury_updates(team_a)
    injury_b = fetch_injury_updates(team_b)
    pitch = fetch_pitch_conditions(venue)
    weather = fetch_weather_forecast(venue, match_date)
    additional_odds = fetch_additional_bookmaker_odds(team_a, team_b)

    prompt = f"""
You are a cricket analyst providing a detailed pre-match prediction and analysis.

Match Details:
- Teams: {team_a} vs {team_b}
- Date: {match_date}
- Venue: {venue}

From the following cricket prediction articles, summarize:
    - Win probability percentages from each source
    - Key players to watch
    - Key recent form details for both teams
    - Head-to-head or venue stats
    - Strengths and weaknesses of both teams
    - Key player matchups to watch
    - Expert verdict on the likely winner
    - Cite the sources.

Articles:
{articles_summary}

Additional Verified Data:
- Player Stats:
    {team_a}: {player_stats_a}
    {team_b}: {player_stats_b}
- Injury Updates:
    {team_a}: {injury_a}
    {team_b}: {injury_b}
- Pitch Conditions: {pitch}
- Weather Forecast: {weather}
- Additional Bookmaker Odds: {additional_odds}

Please include:
- Head-to-head records and historical matchups
- Recent form of both teams
- Key players to watch
- Pitch and weather conditions impacting the game
- Strengths and weaknesses of both teams
- Probability or prediction of the likely winner with reasoning

IMPORTANT: Only use verified, publicly available data or official statistics.
Do NOT generate or fabricate any fake data, stats, or percentages.
If certain information is unavailable, clearly state that instead of guessing.
"""

    openai.api_key = OPENAI_API_KEY
    if not openai.api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set.")

    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=700,
        n=1,
        stop=None
    )

    return response.choices[0].message.content.strip()

def get_match_insights(project_key: str, access_token: str, match_key: str):
    """Fetches match insights from the Roanuz Cricket API."""
    url = f"https://api.sports.roanuz.com/v5/cricket/{project_key}/match/{match_key}/tournament/"
    headers = {'rs-token': access_token}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        return {"error": f"HTTP error occurred: {http_err}"}
    except Exception as err:
        return {"error": f"An error occurred: {err}"}

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
You are an elite cricket match prediction AI with comprehensive access to real-time sports data, expert analysis, betting markets, and advanced statistical models.

MATCH CONTEXT:
- Team A: {team_a}
- Team B: {team_b}  
- Date: {match_date}
- Venue: {venue}
- Format: {match_type}
- Tournament: {tournament}

PREDICTION METHODOLOGY:
1. **Data Collection & Analysis**:
   - Expert predictions from ESPNCricinfo, Wisden, cricket analysts
   - Live betting odds from Bet365, Betfair, 1xBet, and regional bookmakers
   - AI projections from CricViz, Smart Stats, and predictive models
   - Comprehensive venue analysis (pitch behavior, weather impact, historical trends)
   - Team dynamics, injury reports, and squad compositions
   - Key player matchups and tactical considerations
   - Recent performance metrics and momentum indicators

2. **Advanced Probability Calculation**:
   - Base probability from head-to-head records (30% weight)
   - Historical performance analysis (25% weight)
   - Recent form analysis - last 5 matches (25% weight)  
   - Venue-specific performance (20% weight)
   - Team strengths and weaknesses (20% weight)
   - Squad strength and key player availability (15% weight)
   - External factors: weather, pitch conditions, tournament context (10% weight)
   
3. **Statistical Validation**:
   - Cross-validate probabilities against betting market consensus
   - Apply Bayesian inference for probability refinement
   - Ensure logical consistency: winner probability > loser probability
   - Realistic probability range: 52-85% for favorite, 15-48% for underdog

4. **Data Integrity Rules**:
   - **NEVER fabricate statistics, percentages, or historical data**
   - If head-to-head data unavailable → use PRE_MATCH_PUBLIC_VERIFIED_INFORMATION
   - If recent form unavailable → extract from provided information sources
   - Missing data = explicitly state "Data unavailable" 
   - All player names must be currently active squad members only

5. **Confidence Calibration**:
   - HIGH: Complete data available, clear favorite, consistent indicators
   - MEDIUM: Most data available, moderate favorite, some conflicting signals  
   - LOW: Limited data, very close match, or insights contain "error" key
   - **MANDATORY LOW**: If PRE_MATCH_PUBLIC_VERIFIED_INFORMATION is empty/generic
   - **CRITICAL**: Use the 'Data Availability Score' to determine your confidence. If the score is low (e.g. less than 5/7 fields found), the final confidence rating MUST be 'low', regardless of other information

6. **Player Data Validation Rules**:
   - ONLY use real, verifiable player names from current squads
   - If real player data unavailable → use empty arrays: "key_players_a": [], "key_players_b": []
   - NEVER use placeholder names like "Player A", "Player B", "Batsman 1", etc.
   - For player matchups: use actual names or state "Data unavailable"
   - Validate all player names are realistic and currently active

VALIDATED_PLAYER_DATA:
Team A ({team_a}): {validate_and_extract_real_players(team_a, insights)}
Team B ({team_b}): {validate_and_extract_real_players(team_b, insights)}   

7. **result Format** (STRICT JSON only):
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
    "bookmaker_odds": {{
        "team_a_odds": "decimal_odds",
        "team_b_odds": "decimal_odds",
        "implied_probability_a": "float",
        "implied_probability_b": "float"
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
- result ONLY the JSON object - no markdown, no explanatory text
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
                    "content": "You are a precision sports analytics AI. result only valid JSON with accurate cricket match predictions. Never fabricate data. Ensure mathematical consistency in all probability calculations."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,  # Reduced for more consistent results
            max_tokens=2500,  # Increased for comprehensive analysis
            response_format={"type": "json_object"}
        )

        content = completion.choices[0].message.content
        
        # Enhanced JSON validation and error handling
        try:
            parsed = json.loads(content)
            
            # Validate key prediction logic
            if "prediction" in parsed:
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
            parsed = {
                "error": "Invalid JSON response from model",
                "json_error": str(e),
                "raw_content": content[:500] + "..." if len(content) > 500 else content,
                "teams": {"a_name": team_a, "b_name": team_b},
                "confidence": "low",
                "explanation": "Model result parsing failed - unable to generate reliable prediction"
            }
            
    except Exception as api_error:
        parsed = {
            "error": "API call failed",
            "api_error": str(api_error),
            "teams": {"a_name": team_a, "b_name": team_b},
            "confidence": "low", 
            "explanation": "Unable to connect to prediction model - no analysis available"
        }

    return json.dumps(parsed, ensure_ascii=False)

# === ENHANCED PREDICTION FUNCTION WITH SUMMARY ===
def match_prediction_with_summary(insights: Dict[str, Any], team_a: str, team_b: str, match_date: str, venue: str, all_text: str) -> Tuple[str, str]:
    """Enhanced match prediction function that returns both prediction and AI summary."""
    
    # First, get the original prediction
    prediction_json = match_prediction(insights, team_a, team_b, match_date, venue, all_text)
    
    # Extract analysis data for summary
    print("📝 Extracting analysis data for summary generation...")
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

def write_to_result_file(content: str, is_header: bool = False):
    """Write content to result file with proper formatting and append mode."""
    try:
        # Create result file if it doesn't exist
        if not os.path.exists("result"):
            with open("result", "w", encoding="utf-8") as f:
                f.write("CRICKET MATCH PREDICTION ANALYSIS LOG\n")
                f.write("=" * 80 + "\n")
                f.write(f"Generated by Enhanced Cricket Prediction System\n")
                f.write(f"First run: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 80 + "\n\n")
        
        # Append new content
        with open("result", "a", encoding="utf-8") as f:
            if is_header:
                f.write("\n" + "=" * 80 + "\n")
                f.write(content + "\n")
                f.write("=" * 80 + "\n")
            else:
                f.write(content + "\n")
                
    except Exception as e:
        print(f"⚠️ Warning: Could not write to result file: {e}")

def format_prediction_for_result(result: Dict, date_input: str) -> str:
    """Format prediction result with AI summary for readable result file."""
    match_info = result['match_info']
    scores = result['scores']
    
    result_lines = []
    result_lines.append(f"MATCH {result['match_number']}: {match_info['teams']['team_a']} vs {match_info['teams']['team_b']}")
    result_lines.append("-" * 60)
    result_lines.append(f"📅 Date: {date_input}")
    result_lines.append(f"🗝️  Match Key: {match_info['match_key']}")
    result_lines.append(f"🏟️  Tournament: {match_info['tournament']}")
    result_lines.append(f"📍 Venue: {match_info['venue']}")
    result_lines.append(f"⏰ Time: {match_info['match_time']}")
    result_lines.append(f"🎮 Format: {match_info['format']}")
    result_lines.append(f"📊 Status: {match_info['status']}")
    result_lines.append(f"📊 Data Quality: {scores['data_availability']} fields available")
    result_lines.append(f"📊 Similarity Score: {scores['similarity_score']:.2f}")
    result_lines.append(f"📊 Confidence Level: {scores['confidence_level'].upper()}")
    result_lines.append("")
    
    # Parse and display prediction details
    try:
        prediction = json.loads(result['prediction'])
        if 'prediction' in prediction and 'error' not in prediction:
            winner_team = match_info['teams']['team_a'] if prediction['prediction']['winner'] == 'A' else match_info['teams']['team_b']
            win_percentage = prediction['prediction']['a_win_pct'] if prediction['prediction']['winner'] == 'A' else prediction['prediction']['b_win_pct']
            
            result_lines.append(f"🎯 PREDICTION RESULT:")
            result_lines.append(f"   Winner: {winner_team} ({win_percentage}% chance)")
            result_lines.append(f"   Win Probabilities:")
            result_lines.append(f"     • {match_info['teams']['team_a']}: {prediction['prediction']['a_win_pct']}%")
            result_lines.append(f"     • {match_info['teams']['team_b']}: {prediction['prediction']['b_win_pct']}%")
            result_lines.append("")

            # === ADD AI SUMMARY DISPLAY ===
            if 'ai_summary' in prediction and prediction['ai_summary'].get('text'):
                result_lines.append("🤖 AI ANALYSIS SUMMARY:")
                result_lines.append(f"   {prediction['ai_summary']['text']}")
                result_lines.append("")
            
            # Add supporting analysis if available
            if 'supporting' in prediction:
                supporting = prediction['supporting']
                result_lines.append("📋 SUPPORTING ANALYSIS:")
                
                if supporting.get('recent_form_summary') and supporting['recent_form_summary'] != "Data unavailable":
                    result_lines.append(f"   Recent Form: {supporting['recent_form_summary']}")
                
                if supporting.get('h2h_summary') and supporting['h2h_summary'] != "Data unavailable":
                    result_lines.append(f"   Head-to-Head: {supporting['h2h_summary']}")
                
                if supporting.get('venue_analysis') and supporting['venue_analysis'] != "Data unavailable":
                    result_lines.append(f"   Venue Analysis: {supporting['venue_analysis']}")
                
                if supporting.get('key_players_a') and len(supporting['key_players_a']) > 0:
                    result_lines.append(f"   Key Players ({match_info['teams']['team_a']}): {', '.join(supporting['key_players_a'])}")
                
                if supporting.get('key_players_b') and len(supporting['key_players_b']) > 0:
                    result_lines.append(f"   Key Players ({match_info['teams']['team_b']}): {', '.join(supporting['key_players_b'])}")
                
                if supporting.get('weather_conditions') and supporting['weather_conditions'] != "Data unavailable":
                    result_lines.append(f"   Weather: {supporting['weather_conditions']}")
                
                if supporting.get('pitch_conditions') and supporting['pitch_conditions'] != "Data unavailable":
                    result_lines.append(f"   Pitch: {supporting['pitch_conditions']}")
                
                result_lines.append("")
            
            # Add explanation
            if 'explanation' in prediction:
                result_lines.append("💡 DETAILED EXPLANATION:")
                result_lines.append(f"   {prediction['explanation']}")
                result_lines.append("")
            
            # Add betting recommendation if available
            if 'betting_recommendation' in prediction:
                result_lines.append("💰 BETTING INSIGHTS:")
                result_lines.append(f"   {prediction['betting_recommendation']}")
                result_lines.append("")
            
            # Add risk factors if available
            if 'risk_factors' in prediction:
                result_lines.append("⚠️ RISK FACTORS:")
                result_lines.append(f"   {prediction['risk_factors']}")
                result_lines.append("")
        else:
            result_lines.append(f"❌ PREDICTION ERROR:")
            result_lines.append(f"   {prediction.get('error', 'Unknown error occurred')}")
            result_lines.append("")
            
    except json.JSONDecodeError:
        result_lines.append("❌ Could not parse prediction data")
        result_lines.append("")
    
    # Add full JSON for reference
    result_lines.append("📄 COMPLETE PREDICTION JSON:")
    try:
        parsed_prediction = json.loads(result['prediction'])
        formatted_json = json.dumps(parsed_prediction, indent=2, ensure_ascii=False)
        for line in formatted_json.split('\n'):
            result_lines.append(f"   {line}")
    except:
        result_lines.append(f"   {result['prediction']}")
    
    result_lines.append("")
    result_lines.append("-" * 80)
    result_lines.append("")
    
    return "\n".join(result_lines)

def format_legacy_prediction_for_result(prediction_json: str, team1: str, team2: str, date: str, venue: str = None) -> str:
    """Format legacy prediction result with AI summary for readable result file."""
    result_lines = []
    result_lines.append(f"LEGACY MATCH PREDICTION: {team1} vs {team2}")
    result_lines.append("-" * 60)
    result_lines.append(f"📅 Date: {date}")
    if venue:
        result_lines.append(f"📍 Venue: {venue}")
    result_lines.append("")
    
    try:
        prediction = json.loads(prediction_json)
        if 'prediction' in prediction and 'error' not in prediction:
            winner_team = team1 if prediction['prediction']['winner'] == 'A' else team2
            win_percentage = prediction['prediction']['a_win_pct'] if prediction['prediction']['winner'] == 'A' else prediction['prediction']['b_win_pct']
            
            result_lines.append(f"🎯 PREDICTION RESULT:")
            result_lines.append(f"   Winner: {winner_team} ({win_percentage}% chance)")
            result_lines.append(f"   Win Probabilities:")
            result_lines.append(f"     • {team1}: {prediction['prediction']['a_win_pct']}%")
            result_lines.append(f"     • {team2}: {prediction['prediction']['b_win_pct']}%")
            result_lines.append(f"   Confidence: {prediction.get('confidence', 'unknown').upper()}")
            result_lines.append("")

            # === ADD AI SUMMARY DISPLAY ===
            if 'ai_summary' in prediction and prediction['ai_summary'].get('text'):
                result_lines.append("🤖 AI ANALYSIS SUMMARY:")
                result_lines.append(f"   {prediction['ai_summary']['text']}")
                result_lines.append("")
            
            # Add explanation
            if 'explanation' in prediction:
                result_lines.append("💡 DETAILED EXPLANATION:")
                result_lines.append(f"   {prediction['explanation']}")
                result_lines.append("")
        else:
            result_lines.append(f"❌ PREDICTION ERROR:")
            result_lines.append(f"   {prediction.get('error', 'Unknown error occurred')}")
            result_lines.append("")
    except json.JSONDecodeError:
        result_lines.append("❌ Could not parse prediction data")
        result_lines.append("")
    
    # Add full JSON for reference
    result_lines.append("📄 COMPLETE PREDICTION JSON:")
    try:
        parsed_prediction = json.loads(prediction_json)
        formatted_json = json.dumps(parsed_prediction, indent=2, ensure_ascii=False)
        for line in formatted_json.split('\n'):
            result_lines.append(f"   {line}")
    except:
        result_lines.append(f"   {prediction_json}")
    
    result_lines.append("")
    result_lines.append("-" * 80)
    result_lines.append("")
    
    return "\n".join(result_lines)

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


def get_cricket_predictions(date):

    date_input = date
        
    try:
        datetime.strptime(date_input, '%Y-%m-%d')
    except ValueError:
        print("❌ Invalid date format. Please use YYYY-MM-DD.")
        sys.exit(1)
    
    print(f"🔍 Fetching ALL matches and predictions for {date_input}...")
    results = predict_all_matches_on_date(date_input)

    return results