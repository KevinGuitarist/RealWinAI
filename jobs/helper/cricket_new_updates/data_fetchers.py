"""
Data Fetching Functions for Cricket Match Analysis - Optimized Version
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
from typing import Dict, List, Any
from config import PROJECT_ID, CRICKET_API_KEY
from match_finder import EnhancedMatchKeyFinder
import time
import hashlib


# Global caches to prevent repetitive operations
_search_cache = {}
_odds_cache = {}
_player_stats_cache = {}
_injury_cache = {}
_pitch_cache = {}
_weather_cache = {}
_last_pre_match_odds = None


def _get_cache_key(*args):
    """Generate cache key from arguments"""
    return hashlib.md5(str(args).encode()).hexdigest()


def google_search(query, num_results=5):
    """Google search with basic caching"""
    cache_key = _get_cache_key(query, num_results)
    if cache_key in _search_cache:
        print(f"🔄 Using cached search results for: {query[:50]}...")
        return _search_cache[cache_key]
    
    url = "https://serpapi.com/search"
    params = {
        "engine": "google",
        "q": query,
        "num": 10,
        "api_key": "f07ed032504d460515109d6fb520ee7514d87cbe0efcbe3d8f5bae7717ae520e"
    }
    try:
        res = requests.get(url, params=params, timeout=10)
        data = res.json()
        links = [item["link"] for item in data.get("organic_results", [])]
        print(f"🔍 Found {len(links)} links for: {query[:50]}...")
        _search_cache[cache_key] = links
        return links
    except Exception as e:
        print(f"❌ Search error for {query}: {e}")
        return []


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
    """Fetch recent player performance stats with caching."""
    cache_key = _get_cache_key(team_name, match_date)
    if cache_key in _player_stats_cache:
        print(f"🔄 Using cached player stats for: {team_name}")
        return _player_stats_cache[cache_key]
    
    try:
        # Single focused search query
        query = f"{team_name} cricket team playing XI squad {match_date}"
        urls = google_search(query, num_results=5)

        for url in urls[:5]:  # Only check first 5 URLs
            article_text = fetch_article(url)
            
            # Look for actual player names in the content
            if len(article_text) > 100 and "error" not in article_text.lower():
                # Extract potential player names (basic heuristic)
                lines = article_text.split('\n')
                players = []
                for line in lines[:100]: # Check first 100 lines
                    if any(keyword in line.lower() for keyword in ['captain', 'batsman', 'bowler', 'wicket-keeper', 'key player', 'all-rounder']):
                        # Extract names from these lines
                        words = line.split()
                        potential_names = [w for w in words if w.istitle() and len(w) > 2]
                        players.extend(potential_names[:5])
                
                if len(players) >= 3:
                    result = f"Key players for {team_name}: {', '.join(players[:5])}"
                    _player_stats_cache[cache_key] = result
                    return result
        
        result = "Data unavailable"
        _player_stats_cache[cache_key] = result
        return result
        
    except Exception as e:
        result = "Data unavailable"
        _player_stats_cache[cache_key] = result
        return result

    
def fetch_injury_updates(team_name):
    """Fetch injury/availability info with caching."""
    if team_name in _injury_cache:
        print(f"🔄 Using cached injury data for: {team_name}")
        return _injury_cache[team_name]
    
    try:
        query = f"{team_name} cricket injury player unavailable today"
        results = []

        # Get top 3 URLs from Google search
        urls = google_search(query, num_results=3)
        for url in urls:
            try:
                html = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=8).text
                soup = BeautifulSoup(html, "html.parser")
                
                # Extract text paragraphs containing injury-related keywords
                updates = [p.text.strip() for p in soup.find_all("p") if "injury" in p.text.lower() or "unavailable" in p.text.lower()]
                
                if updates:
                    results.append({"url": url, "updates": updates[:2]})  # Reduced from 3
            except Exception as inner_e:
                results.append({"url": url, "error": str(inner_e)})
        
        result = results if results else "No injury updates found."
        _injury_cache[team_name] = result
        return result
    
    except Exception as e:
        result = f"Data unavailable: {e}"
        _injury_cache[team_name] = result
        return result


def fetch_pitch_conditions(venue):
    """Fetch pitch report with caching."""
    if venue in _pitch_cache:
        print(f"🔄 Using cached pitch data for: {venue}")
        return _pitch_cache[venue]
    
    try:
        search_url = f"https://www.espncricinfo.com/search?q={quote(venue+' pitch report')}"
        html = requests.get(search_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=8).text
        soup = BeautifulSoup(html, "html.parser")
        paragraphs = [p.text.strip() for p in soup.find_all("p")]
        report = next((p for p in paragraphs if "pitch" in p.lower()), None)
        result = report if report else "Data unavailable"
        _pitch_cache[venue] = result
        return result
    except Exception as e:
        result = f"Data unavailable: {e}"
        _pitch_cache[venue] = result
        return result


def fetch_weather_forecast(venue, match_date):
    """Fetch weather forecast with robust location extraction and caching."""
    cache_key = _get_cache_key(venue, match_date)
    if cache_key in _weather_cache:
        print(f"🔄 Using cached weather data for: {venue}")
        return _weather_cache[cache_key]
    
    def clean_location(location):
        """Clean location string for better API results"""
        venue_words = ['stadium', 'ground', 'cricket', 'oval', 'park', 'arena', 'sports']
        cleaned = location.lower()
        for word in venue_words:
            cleaned = cleaned.replace(word, '')
        return cleaned.strip()
    
    def get_weather_for_location(location):
        """Get weather data for a specific location"""
        try:
            url = f"https://wttr.in/{quote(location)}?format=j1"
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                forecast = data.get("weather", [{}])[0].get("hourly", [{}])[0]
                if forecast and forecast.get('tempC') is not None:
                    return forecast
            return None
        except:
            return None
    
    def extract_known_cricket_location(venue):
        """Extract known cricket cities from venue string"""
        cricket_locations = {
            'mumbai', 'delhi', 'kolkata', 'chennai', 'bangalore', 'hyderabad',
            'pune', 'jaipur', 'mohali', 'indore', 'ahmedabad', 'lucknow',
            'london', 'manchester', 'birmingham', 'leeds', 'nottingham',
            'cardiff', 'edinburgh', 'dublin', 'sydney', 'melbourne', 'perth',
            'adelaide', 'brisbane', 'auckland', 'wellington', 'christchurch',
            'cape town', 'johannesburg', 'durban', 'port elizabeth',
            'karachi', 'lahore', 'islamabad', 'dhaka', 'chittagong',
            'colombo', 'kandy', 'galle', 'dubai', 'sharjah', 'abu dhabi',
            'brisbane', 'canberra', 'hobart', 'geelong', 'ballarat'
        }
        
        venue_lower = venue.lower()
        for location in cricket_locations:
            if location in venue_lower:
                return location.title()
        return None
    
    try:
        # Generate multiple location candidates
        candidates = []
        
        # Add original venue
        candidates.append(venue.strip())
        
        # Add known cricket location if found
        known_location = extract_known_cricket_location(venue)
        if known_location:
            candidates.append(known_location)
        
        # Parse venue by comma separation
        if "," in venue:
            parts = [part.strip() for part in venue.split(",")]
            # Add all individual parts
            candidates.extend(parts)
            
            # Add combinations
            if len(parts) >= 2:
                candidates.append(f"{parts[-2]} {parts[-1]}")  # Last two parts
                candidates.append(parts[-1])  # Last part (usually country/state)
                candidates.append(parts[-2])  # Second last part (usually city)
        
        # Add cleaned versions (remove cricket-specific terms)
        for candidate in candidates[:]:
            cleaned = clean_location(candidate)
            if cleaned and cleaned not in candidates:
                candidates.append(cleaned)
        
        # Remove empty strings and duplicates while preserving order
        seen = set()
        unique_candidates = []
        for candidate in candidates:
            if candidate and candidate.strip() and candidate not in seen:
                unique_candidates.append(candidate)
                seen.add(candidate)
        
        # Try each candidate until we get weather data
        for location in unique_candidates:
            forecast = get_weather_for_location(location)
            if forecast:
                weather_desc = forecast.get('weatherDesc', [{'value': 'Data unavailable'}])[0]['value']
                temp = forecast.get('tempC', 'N/A')
                result = f"Weather on {match_date}: {weather_desc}, temp {temp}°C"
                _weather_cache[cache_key] = result
                return result
        
        result = "Data unavailable"
        _weather_cache[cache_key] = result
        return result
        
    except Exception as e:
        result = f"Data unavailable: {e}"
        _weather_cache[cache_key] = result
        return result


# Single global instance of EnhancedMatchKeyFinder to prevent re-initialization
_match_finder_instance = None



def calculate_custom_odds(team_a: str, team_b: str, win_probability_a: float) -> Dict[str, float]:
    """
    Calculate custom betting odds based on win probability.
    
    Formula: Decimal Odds = 1 / Probability
    - If Team A has 60% win probability (0.60), odds = 1/0.60 = 1.67
    - If Team B has 40% win probability (0.40), odds = 1/0.40 = 2.50
    
    Args:
        team_a: Name of team A
        team_b: Name of team B
        win_probability_a: Win probability for team A (0.0 to 1.0)
    
    Returns:
        Dictionary with team names as keys and decimal odds as values
    """
    # Ensure probability is between 0.01 and 0.99 to avoid division errors
    win_probability_a = max(0.01, min(0.99, win_probability_a))
    win_probability_b = 1.0 - win_probability_a
    
    # Calculate decimal odds
    odds_a = round(1.0 / win_probability_a, 2)
    odds_b = round(1.0 / win_probability_b, 2)
    
    print(f"📊 Custom Odds Calculation:")
    print(f"   {team_a}: {win_probability_a*100:.1f}% win probability → {odds_a} odds")
    print(f"   {team_b}: {win_probability_b*100:.1f}% win probability → {odds_b} odds")
    
    return {
        team_a: odds_a,
        team_b: odds_b
    }


def extract_win_probability_from_analysis(analysis_text: str, team_a: str, team_b: str) -> float:
    """
    Extract win probability from analysis text.
    Looks for patterns like "60% chance", "70% probability", etc.
    
    Args:
        analysis_text: The analysis text containing predictions
        team_a: Name of team A
        team_b: Name of team B
    
    Returns:
        Win probability for team A (default: 0.50 if not found)
    """
    import re
    
    # Look for percentage patterns
    patterns = [
        r'(\d+)%\s+(?:chance|probability|likely)',
        r'win\s+probability.*?(\d+)%',
        r'(\d+)%.*?(?:win|victory)',
        r'{}\s+(?:has|have)\s+(\d+)%'.format(re.escape(team_a)),
    ]
    
    probabilities = []
    for pattern in patterns:
        matches = re.findall(pattern, analysis_text, re.IGNORECASE)
        probabilities.extend([int(m) for m in matches if m.isdigit()])
    
    if probabilities:
        # Use the first found probability
        prob = probabilities[0] / 100.0
        print(f"📈 Extracted win probability from analysis: {prob*100:.1f}%")
        return prob
    
    # Default to 50-50 if no probability found
    print(f"⚠️ No win probability found in analysis, defaulting to 50-50")
    return 0.50


def fetch_additional_bookmaker_odds(team_a, team_b, match_date, win_probability_a=None):
    """
    Generate custom betting odds based on win probability instead of fetching from API.
    
    Args:
        team_a: Name of team A
        team_b: Name of team B
        match_date: Date of the match
        win_probability_a: Win probability for team A (0.0 to 1.0). If None, defaults to 0.50
    
    Returns:
        Dictionary with team names as keys and decimal odds as values
    """
    print(f"🎲 Generating custom odds for: {team_a} vs {team_b} on {match_date}")
    
    # Use provided probability or default to 50-50
    if win_probability_a is None:
        win_probability_a = 0.50
        print(f"⚠️ No win probability provided, using default 50-50")
    
    # Calculate custom odds
    custom_odds = calculate_custom_odds(team_a, team_b, win_probability_a)
    
    return custom_odds


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


def get_pre_match_public_information(team_a, team_b, match_date, venue, text, win_probability_a=None):
    """Returns a detailed pre-match analysis with custom odds based on predictions."""
    print(f"📊 Generating analysis for: {team_a} vs {team_b}")
    
    # Fetch all data in parallel concept (though Python doesn't truly parallel here)
    articles_summary = text
    player_stats_a = fetch_player_stats(team_a, match_date)
    player_stats_b = fetch_player_stats(team_b, match_date)
    injury_a = fetch_injury_updates(team_a)
    injury_b = fetch_injury_updates(team_b)
    pitch = fetch_pitch_conditions(venue)
    weather = fetch_weather_forecast(venue, match_date)
    
    # Generate custom odds (will be updated after analysis if probability is extracted)
    additional_odds = fetch_additional_bookmaker_odds(team_a, team_b, match_date, win_probability_a)

    prompt = f"""
You are an expert cricket analyst providing a detailed pre-match prediction and analysis.

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
- Custom Betting Odds (based on prediction): {additional_odds}

Please include:
- Head-to-head records and historical matchups
- Recent form of both teams
- Key players to watch
- Pitch and weather conditions impacting the game
- Strengths and weaknesses of both teams
- Probability or prediction of the likely winner with reasoning (express as a percentage)

IMPORTANT: Only use verified, publicly available data or official statistics.
Do NOT generate or fabricate any fake data, stats, or percentages.
If certain information is unavailable, clearly state that instead of guessing.
When providing win probability, please state it clearly as "Team A has X% chance of winning"
"""

    import openai
    from config import OPENAI_API_KEY
    
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

    analysis = response.choices[0].message.content.strip()
    
    # Try to extract win probability from analysis and recalculate odds
    if win_probability_a is None:
        extracted_prob = extract_win_probability_from_analysis(analysis, team_a, team_b)
        # Recalculate odds with extracted probability
        additional_odds = fetch_additional_bookmaker_odds(team_a, team_b, match_date, extracted_prob)
        
        # Append odds to analysis
        analysis += f"\n\n**Updated Custom Betting Odds (based on analysis):**\n"
        analysis += f"- {team_a}: {additional_odds[team_a]}\n"
        analysis += f"- {team_b}: {additional_odds[team_b]}\n"
    
    return analysis


def get_match_insights(project_key: str, access_token: str, match_key: str):
    """Fetches match insights from the Roanuz Cricket API with caching."""
    cache_key = _get_cache_key("insights", project_key, match_key)
    if cache_key in _odds_cache:
        print(f"🔄 Using cached insights for match_key: {match_key}")
        return _odds_cache[cache_key]
    
    url = f"https://api.sports.roanuz.com/v5/cricket/{project_key}/match/{match_key}/tournament/"
    headers = {'rs-token': access_token}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        result = response.json()
        _odds_cache[cache_key] = result  # Cache the result
        return result
    except requests.exceptions.HTTPError as http_err:
        result = {"error": f"HTTP error occurred: {http_err}"}
        _odds_cache[cache_key] = result
        return result
    except Exception as err:
        result = {"error": f"An error occurred: {err}"}
        _odds_cache[cache_key] = result
        return result


def clear_all_caches():
    """Clear all caches - useful for testing or memory management"""
    global _search_cache, _odds_cache, _player_stats_cache, _injury_cache, _pitch_cache, _weather_cache, _match_finder_instance
    _search_cache.clear()
    _odds_cache.clear()
    _player_stats_cache.clear()
    _injury_cache.clear()
    _pitch_cache.clear()
    _weather_cache.clear()
    _match_finder_instance = None
    print("🧹 All caches cleared")


def get_cache_stats():
    """Get statistics about current cache usage"""
    return {
        "search_cache": len(_search_cache),
        "odds_cache": len(_odds_cache),
        "player_stats_cache": len(_player_stats_cache),
        "injury_cache": len(_injury_cache),
        "pitch_cache": len(_pitch_cache),
        "weather_cache": len(_weather_cache),
        "match_finder_initialized": _match_finder_instance is not None
    }