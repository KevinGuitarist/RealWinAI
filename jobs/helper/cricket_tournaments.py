import requests
import http.client

from datetime import datetime
import pytz
import time
import ast
import json
from typing import Any, Dict
import openai
from bs4 import BeautifulSoup
from urllib.parse import quote


OPENAI_API_KEY = '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'
openai.api_key = OPENAI_API_KEY


# Configuration
TOKEN = "v5sRS_P_1942111570733699074s1954013287012261718"
PROJECT_ID = "RS_P_1942111570733699074"
BASE_URL = "https://api.sports.roanuz.com/v5/cricket"
API_URL     = f'https://api.sports.roanuz.com/v5/cricket/{PROJECT_ID}/featured-tournaments/'
CRICKET_API_KEY= "RS5:836fe0c1a85d44000f7ebe67f9d730c4"
# HEADERS = {"rs-token": TOKEN}




def google_search(query, num_results=5):
    url = "https://serpapi.com/search"
    params = {
        "engine": "google",
        "q": query,
        "num": 5,
        "api_key": "73172a5f6685e982cb5f434ca7e922076f84b2424c540eb83b5e7ec79ca4905a"
    }
    res = requests.get(url, params=params)
    data = res.json()
    links = [item["link"] for item in data.get("organic_results", [])]
    print(f"Links : {links}")
    return links

def fetch_article(url):
    """Fetch and extract text from an article"""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        html = requests.get(url, headers=headers, timeout=10).text
        soup = BeautifulSoup(html, "html.parser")
        paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")]
        return "\n".join(paragraphs)
    except Exception as e:
        return f"Error fetching {url}: {e}"
    
def get_pre_match_public_information(team_a,team_b,match_date,venue,text):

    prompt = f"""
    You are a cricket analyst providing a detailed pre-match prediction and analysis.

    Match Details:
    - Teams: {team_a} vs {team_b}
    - Date: {match_date}
    - Venue: {venue} 

    From the following cricket prediction articles, summarize:
            - Win probability percentages from each source
            - Key recent form details for both teams
            - Head-to-head or venue stats
            - Expert verdict on the likely winner
            - Cite the sources.

        Articles:
        {text}
    """

    prompt += """
        Please include the following in your analysis:
        - Head-to-head records and historical matchups.
        - Recent form of both teams.
        - Key players to watch.
        - Pitch and weather conditions impacting the game.
        - Strengths and weaknesses of both teams.
        - Probability or prediction of the likely winner with reasoning.

        IMPORTANT: Only use verified, publicly available data or official statistics.
        Do NOT generate or fabricate any fake data, stats, or percentages.
        If certain information is unavailable, clearly state that instead of guessing.
    """

    prompt = prompt.strip()

    model="gpt-4o-mini"
    temperature=0.7
    max_tokens=700

    openai.api_key = OPENAI_API_KEY
    if not openai.api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set.")


    response = openai.chat.completions.create(model=model,
    messages=[{"role": "user", "content": prompt}],
    temperature=temperature,
    max_tokens=max_tokens,
    n=1,
    stop=None)
    return response.choices[0].message.content.strip()

def match_prediction(insights: Dict[str, Any], team_a: str, team_b: str, match_date: str,venue: str,all_text:str) -> str:
    """
    Build the user prompt for match prediction with fallback to deep web search if insights are insufficient.
    """
    prompt = f"""
        You are an advanced cricket match prediction model with access to live sports data, expert analysis, betting odds, and AI-based projections.

You will be given:
- Match details (TEAM_A, TEAM_B, MATCH_DATE)
- Optional insights JSON that may contain match_key and other metadata.

    Your task:
    1. Gather and analyze:
    - Expert predictions from cricket analysts and websites.
    - Betting odds from reputable platforms (Betfair, OddsChecker, Stoiximan, or country-specific top bookmakers).
    - AI model projections or score predictions from reliable cricket data sources.
    - Venue pitch report, weather, and historical trends.
    - Head-to-head and recent form summaries.
    - Key players for each team.
    - Realistic AI probablity will be from 50-90 percent 
    - if team_a in stats higher than team_b give them 15% additional weightage else to team_b
    - Consider pre-match verified information provide and use it for better and accurate prediction

    2. If any data (head-to-head, recent form, stats, win percentages) is **not available**, do **NOT** generate fake or simulated data. Instead, leave those fields empty or set their values to "Data unavailable".

    3. Adjust win probability if there is a manual “edge” bias provided — this bias will be toward the predicted winner and will range from 1–20%. Apply it after calculating initial probabilities.

    4. Convert win probabilities to **fair odds** for both teams.

    5. Combine all sources into a **reasoned prediction** for which team is more likely to win.

    6. Important Notes:
       - Please consider only those squad players who are playing the match not the ones who are retired or not playing in case of international match
       - if recent_form_summary not available then it should be from PRE_MATCH_PUBLIC_VERIFIED_INFORMATION
       - if h2h_summary not available then it should be from PRE_MATCH_PUBLIC_VERIFIED_INFORMATION
       - if weakness_and strength not available then it should be from PRE_MATCH_PUBLIC_VERIFIED_INFORMATION
       - Do NOT generate or fabricate any fake data, stats, or percentages. Everything should be provided stuff or instructions provided
       - win percentages should not be flawed and predicted winner should have higher percentage then losing team
    7. Final Output Requirements:
    - STRICT JSON object, no markdown, no extra text.
    - Required keys:
            - "match_key" (from insights["data"]["match"]["key"], if available)
            - "teams": {{"a_code": str, "b_code": str, "a_name": str, "b_name": str}}
            - "prediction": {{"winner": "A" or "B", "a_win_pct": float, "b_win_pct": float}}
            - "bookmaker_odds": {{"team_a_name": float, "team_b_name": float}}
            - "confidence": "high" | "low"
            - "supporting": {{
                "recent_form_summary": str or "data unavailable",
                "h2h_summary": str or "data unavailable",
                "key_players_a": [str] or [],
                "key_players_b": [str] or [],
                "venue": str or "data unavailable",
                "weather_conditions": str or "data unavailable",
                "pitch_conditions": str or "data unavailable",
                "projection": str or "data unavailable"
                "weakness_and_strength": str
            }}
            - "explanation": str

    Inputs for this match:
    TEAM_A: {team_a}
    TEAM_B: {team_b}
    MATCH_DATE: {match_date}
    VENUE: {venue}

        INSIGHTS_START
        {json.dumps(insights, ensure_ascii=False)}
        INSIGHTS_END


        PRE_MATCH_PUBLIC_VERIFIED_INFORMATION_START

        {get_pre_match_public_information(team_a,team_b,match_date,venue,all_text)}
           
        PRE_MATCH_PUBLIC_VERIFIED_INFORMATION_END

        Output only the JSON object, nothing else.
        """.strip()

    completion = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a careful sports prediction model that outputs strict JSON only."},
            {"role": "user", "content": prompt}
        ],
        temperature=1.0,
        response_format={"type": "json_object"}
    )

    content = completion.choices[0].message.content
    try:
        parsed = json.loads(content)
    except Exception:
        parsed = {"error": "Model did not return valid JSON", "raw": content}

    print("Prediction:", json.dumps(parsed,indent=4))


    return json.dumps(parsed, ensure_ascii=False)

def token_create_or_get():
    try:
        conn = http.client.HTTPSConnection("api.sports.roanuz.com")
        payload = json.dumps({
            "api_key": CRICKET_API_KEY
        })
        headers = {
            'Content-Type': 'application/json'
        }

        conn.request("POST", f"/v5/core/{PROJECT_ID}/auth/", payload, headers)
        res = conn.getresponse()
        data = res.read()

        print(f"Data: {data}")

        try:
            response_json = json.loads(data.decode("utf-8"))
            if response_json.get("data") and "token" in response_json["data"]:
                return response_json["data"]["token"]
            else:
                print("❌ Token fetch failed:", response_json.get("error", "Unknown error"))
                return None
        except json.JSONDecodeError:
            print("❌ Failed to decode token response.")
            return None
    except BaseException as e:  # Catch everything, including SystemExit
        print(f"❌ Fatal error in token_create_or_get: {e}")
        return None

def get_tournament_keys(project_id: str, countries: list[str],token: str) -> dict[str, list[str]]:
    """
    For each country code in `countries`, fetch all featured tournament keys
    across its associations, returning a mapping country -> [tournament_key...].
    """
    HEADERS = {"rs-token": token}

    result = {}
    for country in countries:
        try:
            # 1. List associations for the country
            assoc_url = f"{BASE_URL}/{project_id}/association/list-by-country/{country}/"
            resp = requests.get(assoc_url, headers=HEADERS, timeout=10)
            resp.raise_for_status()
            payload = resp.json()

            # Some endpoints return under "associations", others under "data"
            associations = payload.get("associations") or payload.get("data") or {}
            assoc_list = associations.get("associations", [])

            keys = []
            for assoc in assoc_list:
                try:
                    assoc_key = assoc.get("key")
                    if not assoc_key:
                        continue

                    # 2. Get featured tournaments for this association
                    tourn_url = f"{BASE_URL}/{project_id}/association/{assoc_key}/featured-tournaments/"
                    tr_resp = requests.get(tourn_url, headers=HEADERS, timeout=10)
                    tr_resp.raise_for_status()
                    tr_payload = tr_resp.json()

                    tournaments = tr_payload.get("data", {})
                    for tourn in tournaments.get("tournaments", []):
                        key = tourn.get("key")
                        if key:
                            keys.append(key)
                except requests.RequestException as e:
                    print(f"Error fetching tournaments for association {assoc_key} in {country}: {e}")
                except (ValueError, AttributeError) as e:
                    print(f"Invalid tournament data for association {assoc_key} in {country}: {e}")

            result[country] = keys

        except requests.RequestException as e:
            print(f"Error fetching associations for {country}: {e}")
            result[country] = []
        except (ValueError, AttributeError) as e:
            print(f"Invalid association data for {country}: {e}")
            result[country] = []

    return result

def format_as_set_literal(keys: list[str]) -> str:
    """
    Given a list of strings, returns a string like {"key1","key2",...}
    """
    return "{" + ",".join(f'"{k}"' for k in keys) + "}"
def fetch_tournaments(token):
    headers = {'rs-token': token}
    resp = requests.get(API_URL, headers=headers)
    resp.raise_for_status()
    return resp.json().get('data', {}).get('tournaments', [])

def get_ongoing(tournaments):
    now = time.time()
    return [
        t for t in tournaments
        if t.get('start_date', 0) <= now <= t.get('last_scheduled_match_date', 0)
    ]

def get_todays_fixtures(token):
    local_tz = pytz.timezone("Asia/Karachi")
    today_local = datetime.now(local_tz).date()
    year_month = today_local.strftime("%Y-%m")

    headers = {"rs-token": token}

    # 1. Fetch fixtures for the current month
    resp = requests.get(
        f"{BASE_URL}/{PROJECT_ID}/fixtures/date/{year_month}/",
        headers=headers
    )
    resp.raise_for_status()
    data = resp.json().get("data", {})

    # 2. Flatten all daily matches from data.month.days
    monthly_matches = []
    for day in data.get("month", {}).get("days", []):
        for m in day.get("matches", []):
            monthly_matches.append(m)

    if not monthly_matches:
        print("Warning: No matches found for this month (check response format).")
    
    # 3. Filter those starting today
    initial_today = [
        m for m in monthly_matches
        if datetime.fromtimestamp(m.get("start_at", 0), tz=local_tz).date() == today_local
    ]

    tournaments = fetch_tournaments(token)
    ongoing = get_ongoing(tournaments)

    if not ongoing:
        print("No featured tournaments are ongoing right now.")
        return

    # build a set of all keys
    keys = { t['key'] for t in ongoing }

    today_keys = {m["tournament"]["key"] for m in initial_today}

    # 4. Get unique tournament keys
    keys |= today_keys

    popular_countries = [
        "IND",  # India
        "AUS",  # Australia
        "GBR",  # England
        "PAK",  # Pakistan
        "NZL",  # New Zealand
        "LKA",   # Sri Lanka
        "BGD"   # Bangladesh
    ]
    # Fetch per-country keys
    tour_keys_by_country = get_tournament_keys(PROJECT_ID, popular_countries,token)

    # Merge all into one unique set
    all_keys = set(
        key
        for keys in tour_keys_by_country.values()
        for key in keys
    )

    if tour_keys_by_country:

        # Print merged set literal
        _ct_keys = format_as_set_literal(all_keys)

        if isinstance(_ct_keys, str):
            _ct_keys = ast.literal_eval(_ct_keys)

        # 3. Union the two sets
        merged = keys | _ct_keys

        tournament_keys = merged

    else:

        tournament_keys = keys


    # 5. Fetch full fixtures per tournament and de-duplicate
    seen_keys = set()
    todays_matches = []
    for tkey in tournament_keys:
        try:
            tr_resp = requests.get(
                f"{BASE_URL}/{PROJECT_ID}/tournament/{tkey}/fixtures/",
                headers=headers
            )
            tr_resp.raise_for_status()

            tf_matches = tr_resp.json().get("data", {}).get("matches", [])
            for m in tf_matches:
                match_date = datetime.fromtimestamp(m.get("start_at", 0), tz=local_tz).date()
                if match_date == today_local and m["key"] not in seen_keys:
                    seen_keys.add(m["key"])
                    todays_matches.append(m)

        except requests.exceptions.RequestException as e:
            print(f"Error fetching fixtures for tournament {tkey}: {e}")
            continue
        except (ValueError, KeyError, TypeError) as e:
            print(f"Error parsing fixtures for tournament {tkey}: {e}")

    return todays_matches

def get_match_insights(project_key: str, access_token: str, match_key: str):
    """
    Fetches match insights from the Roanuz Cricket API.
    
    Args:
        project_key (str): Your Roanuz project key.
        access_token (str): Your Roanuz API access token.
        match_key (str): The match key (e.g., 'rsaeng_2020_t20_03').

    Returns:
        dict: JSON response containing match insights.
    """
    url = f"https://api.sports.roanuz.com/v5/cricket/{project_key}/match/{match_key}/insights/"
    headers = {
        'rs-token': access_token
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise error for HTTP issues
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        return {"error": f"HTTP error occurred: {http_err}"}
    except Exception as err:
        return {"error": f"An error occurred: {err}"}

def get_tournament_matches(token = None):



    token = token_create_or_get()
    
    fixtures = get_todays_fixtures(token)

    matches  = []

    if not fixtures:
        print("No fixtures scheduled for today.")
    else:
        today_str = datetime.now(pytz.timezone("Asia/Karachi")).strftime('%Y-%m-%d')
        print(f"Fixtures on {today_str}:")
        seen_keys = set() 
        for match in fixtures:

            venue = f"{match['venue']['name']}, {match['venue']['city']}, {match['venue']['country']['name']}"
            print(f"Venue: {venue} ")

            print("==== Match ====")

            print(match)

            print("=======")

        
            match_key = match.get("key")

            insights  = get_match_insights(PROJECT_ID,token,match_key) 


            if match_key in seen_keys:
                continue  # Skip duplicates
            seen_keys.add(match_key)

            home = match["teams"]["a"]["name"]
            away = match["teams"]["b"]["name"]
            kickoff = datetime.fromtimestamp(match.get("start_at", 0), tz=pytz.timezone("Asia/Karachi"))

            print(f"  • {home} vs {away} at {kickoff.strftime('%H:%M')} (Asia/Karachi)")

            query = f"{home} vs {away} prediction site:crictracker.com OR site:sportscafe.in OR site:cricketworld.com"

            urls = google_search(query)
            print("Found URLs:", urls)

            all_text = ""
            for url in urls:
                article_text = fetch_article(url)
                all_text += f"\n\nSOURCE: {url}\n{article_text}"



            print("====== Insights =====")

           

            # print(insights)
            prediction = match_prediction(insights,home,away,match.get("start_at", 0),venue,all_text)

            time.sleep(10)

            matches.append({
                "match": match,
                "prediction": prediction
            })

            print("====== End Insights =====")

    return matches




            
        
    
