import os
import json
import time
import math
import requests
import openai
from bs4 import BeautifulSoup
from urllib.parse import quote


OPENAI_API_KEY = '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'
openai.api_key = OPENAI_API_KEY

API_BASE   = "https://api.sportmonks.com/v3/football"
API_TOKEN  = "EowWj4NnMhCihlx2acWj13J4AXSYpJJtPXjCcMM9BprYsttIl1PlcMHPAVcg"



def google_search(query, num_results=5):
    url = "https://serpapi.com/search"
    params = {
        "engine": "google",
        "q": query,
        "num": 5,
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
        headers = {"User-Agent": "Mozilla/5.0"}
        html = requests.get(url, headers=headers, timeout=10).text
        soup = BeautifulSoup(html, "html.parser")
        paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")]
        return "\n".join(paragraphs)
    except Exception as e:
        return f"Error fetching {url}: {e}"
    

def get_pre_match_public_information(team_a,team_b,match_date,prediction,h2h,performance):

    prompt = f"""
    You are a football analyst providing a detailed pre-match prediction and analysis.

    Match Details:
    - Teams: {team_a} vs {team_b}
    - Date: {match_date}

    From the following football prediction articles, summarize:
            - Win probability percentages from each source
            - Key recent form details for both teams
            - Head-to-head or venue stats
            - Expert verdict on the likely winner
            - Each player and team performance stats
            - Ball possession and shots on target
            - Goals scored/conceded per game
            - Team news (injuries, suspensions, home/away strength)

        Articles:
        {prediction}
        {h2h}
        {performance}
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

def load_fixture(fixture_id):
    resp = requests.get(
        f"{API_BASE}/fixtures/{fixture_id}",
        params={
            "api_token": API_TOKEN,
            "include": "statistics;scores;weatherReport;odds;trends;metadata;participants"
        }
    )
    resp.raise_for_status()
    return resp.json()["data"]

def aggregate_match_winner(data):
    odds = data.get("odds", [])
    entries = [e for e in odds if e.get("market_id") == 1]
    grouped = {}
    for e in entries:
        lbl = e.get("label")
        odd = float(e.get("dp3") or e.get("value"))
        # grouped.setdefault(lbl, []).append(1.0 / odd)
        if odd and odd != 0:
            grouped.setdefault(lbl, []).append(1.0 / odd)
        else:
            # fallback when odd is 0 or None
            grouped.setdefault(lbl, []).append(0.0)
    avg = {lbl: sum(vals)/len(vals) for lbl, vals in grouped.items()}
    total = sum(avg.values())
    norm = {lbl: p/total for lbl, p in avg.items()}
    return norm

def compute_xg_from_odds(data, loc):
    mid = 20 if loc == "home" else 21
    entries = [
        e for e in data.get("odds", [])
        if e.get("market_id") == mid and e.get("total") == "0.5" and e.get("label") == "Under"
    ]
    if not entries:
        return None
    probs = []
    for e in entries:
        try:
            odd = float(e.get("dp3") or e.get("value"))
            probs.append(1.0 / odd)
        except:
            continue
    if not probs:
        return None
    p0 = sum(probs)/len(probs)
    return p0, -math.log(p0)

def fetch_recent_fixtures(team_id, limit=10):
    resp = requests.get(
        f"{API_BASE}/fixtures",
        params={
            "api_token": API_TOKEN,
            "team_id": team_id,
            "sort": "desc",
            "limit": limit,
            "status_id": 5,  # finished
            "include": "scores"
        }
    )
    resp.raise_for_status()
    return resp.json().get("data", [])

def compute_poisson_from_form(data, loc):
    # identify team IDs
    participants = data.get("participants", [])
    try:
        home_id = next(p["id"] for p in participants if p["meta"]["location"]=="home")
        away_id = next(p["id"] for p in participants if p["meta"]["location"]=="away")
    except StopIteration:
        return None

    team_id = home_id if loc=="home" else away_id
    fixtures = fetch_recent_fixtures(team_id)
    if not fixtures:
        return None

    scored = []
    # collect goals scored by this team
    for fx in fixtures:
        for s in fx.get("scores", []):
            if s["participant_id"] == team_id:
                scored.append(s["score"]["goals"])

    # if no scored data, cannot compute
    if not scored:
        return None

    # compute average goals scored
    avg_scored = sum(scored) / len(scored)
    if loc == "home":
        avg_scored *= 1.1  # home-field boost

    # P(0 goals) under Poisson
    p0 = math.exp(-avg_scored)
    return p0, avg_scored

def poisson_win_probs(home_xg, away_xg, max_goals=6):
    pmf_h = [math.exp(-home_xg) * home_xg**k / math.factorial(k) for k in range(max_goals+1)]
    pmf_a = [math.exp(-away_xg) * away_xg**k / math.factorial(k) for k in range(max_goals+1)]
    p_home = p_draw = p_away = 0.0
    for i in range(max_goals+1):
        for j in range(max_goals+1):
            prob = pmf_h[i] * pmf_a[j]
            if i > j:
                p_home += prob
            elif i == j:
                p_draw += prob
            else:
                p_away += prob
    return p_home, p_draw, p_away

def call_openai(payload, max_retries=5):
    api_key = OPENAI_API_KEY
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    messages = [
        {"role":"system", "content":"You are a football betting analyst"},
        {"role":"user",   "content":payload}
    ]
    data = {"model":"gpt-4o-mini","messages":messages,"temperature":0,"response_format": {"type": "json_object"}}
    backoff = 1
    for _ in range(max_retries):
        r = requests.post(url, headers=headers, json=data)
        if r.status_code == 429:
            retry = int(r.headers.get("Retry-After", backoff))
            time.sleep(retry)
            backoff *= 2
            continue
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
    raise RuntimeError("Rate limit retries exhausted")



def call_odds_openai(system_prompt: str, user_content: str, model: str = "gpt-4o-mini", max_retries: int = 5):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ],
        "max_tokens": 5000,
        "temperature": 0
    }
    backoff = 1
    for attempt in range(max_retries):
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", backoff))
            print(f"Rate limited. Retrying in {retry_after}s...")
            time.sleep(retry_after)
            backoff *= 2
            continue
        if response.status_code == 413:
            raise RuntimeError("Payload too large. Consider reducing the input size.")
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    raise RuntimeError("Exceeded maximum retry attempts due to rate limiting.")

def ai_prediction_without_odds(fixture):

    # Enhanced system prompt with odds and fallback logic
    system_prompt = """
            You are a football betting analyst.

            1. If the fixture JSON includes an 'odds' list with market_id=1 entries:
            - Aggregate the implied probabilities (1/odd) across all bookmakers for Home, Draw, and Away.
            - Compute raw averages (no normalization so the overround remains).
            - For each team, compute xG ≈ -ln(P0), using P0 from the Under 0.5 team-total-goals market (market_id=20 for Home, 21 for Away).

            2. If no odds are available:
            a. From the fixture's 'statistics' field, fetch each team's last 10 matches, gathering goals scored and conceded.
            b. Compute each team's average goals scored (λ_scored) and conceded (λ_conceded).
            c. Apply a home-field boost of +10% to the home team's λ_scored.
            d. Model goals with independent Poisson distributions.
            e. Calculate P(Home win), P(Draw), P(Away win) via the Poisson scoreline matrix.
            f. Use λ_scored as the xG estimate for each team.

            Always return a single JSON object with:
            - predicted_winner
            - win_probabilities: { "home": ..., "draw": ..., "away": ... }
            - xg_estimates: { "<HomeTeam>": { "p0": ..., "xg": ... }, "<AwayTeam>": { "p0": ..., "xg": ... } }
            - explanation: brief justification (either "highest bookmaker implied" or "highest Poisson probability based on recent form").
            """

    user_content = json.dumps(fixture)

    # Call OpenAI and print the result
    result = call_odds_openai(system_prompt, user_content)

    print(result)
    
    return result

def predict_fixture_result(fixture_id,match_date):
    data = load_fixture(fixture_id)
    teams = {p["meta"]["location"]: p["name"] for p in data["participants"]}

    raw_probs = aggregate_match_winner(data)
    if raw_probs:
        # odds-based path
        win_breakdown = {
            "home": round(raw_probs.get("Home",0)*100,1),
            "draw": round(raw_probs.get("Draw",0)*100,1),
            "away": round(raw_probs.get("Away",0)*100,1)
        }
        home_x = compute_xg_from_odds(data, "home")
        away_x = compute_xg_from_odds(data, "away")
        explanation = "highest bookmaker implied probability"
    else:
        # Poisson fallback
        home_x = compute_poisson_from_form(data, "home")
        away_x = compute_poisson_from_form(data, "away")
        if not home_x or not away_x:

            print("No odds and insufficient recent form to predict.")
            return False
        p_home, p_draw, p_away = poisson_win_probs(home_x[1], away_x[1])
        win_breakdown = {
            "home": round(p_home*100,1),
            "draw": round(p_draw*100,1),
            "away": round(p_away*100,1)
        }
        explanation = "highest Poisson probability based on recent form"

    # determine winner
    winner_label = max(win_breakdown, key=win_breakdown.get)
    winner_name = teams[winner_label]



    print(teams)

    print(f"{teams['home']} vs {teams['away']} {match_date} {fixture_id}")

    # metrics = {
    #     "predicted_winner": winner_name,
    #     "win_probabilities": win_breakdown,
    #     "xg_estimates": {
    #         teams["home"]: {"p0": round((home_x[0]*100) if raw_probs else home_x[0]*100,1),
    #                          "xg": round(home_x[1],2)},
    #         teams["away"]: {"p0": round((away_x[0]*100) if raw_probs else away_x[0]*100,1),
    #                          "xg": round(away_x[1],2)}
    #     },
    #     "explanation": explanation
    # }

    # --- guards & coercions up front ---
    def _coerce_pair(x) -> tuple[float, float]:
        """Return (p0, xg). Accepts None, shorter tuples, strings, etc."""
        if x is None:
            return (0.0, 0.0)
        try:
            a, b = x  # will raise if not 2 items
        except Exception:
            return (0.0, 0.0)
        try:
            return (float(a or 0.0), float(b or 0.0))
        except Exception:
            return (0.0, 0.0)

    # teams can be None; also sometimes you have nested shapes — normalize here if needed
    teams = teams or {}
    home_name = teams.get("home") or "Home"
    away_name = teams.get("away") or "Away"

    home_x = _coerce_pair(home_x)
    away_x = _coerce_pair(away_x)

    # If your p0 is in decimals (0..1), convert to %; if it's already percent (e.g. 64.2), keep it.
    def _to_pct(p0: float, raw_probs: bool | None) -> float:
        if raw_probs is None:
            # auto-detect: treat <=1.0 as decimal probability
            mult = 100.0 if 0.0 <= p0 <= 1.0 else 1.0
        else:
            mult = 100.0 if raw_probs else 1.0
        return round(p0 * mult, 1)

    p0_home = _to_pct(home_x[0], raw_probs)
    p0_away = _to_pct(away_x[0], raw_probs)

    metrics = {
        "predicted_winner": winner_name,
        "win_probabilities": win_breakdown or {},  # don’t subscript win_breakdown here, so None is fine
        "xg_estimates": {
            home_name: {"p0": p0_home, "xg": round(home_x[1], 2)},
            away_name: {"p0": p0_away, "xg": round(away_x[1], 2)},
        },
        "explanation": explanation or "",
    }

    query = (
        f"{teams['home']} vs {teams['away']} match prediction OR preview OR betting odds "
        "(site:talksport.com OR site:numbersgame.uk OR site:footballwhispers.com OR site:oddschecker.com "
        "OR site:bbc.com/sport OR site:espn.com OR site:sofascore.com OR site:flashscore.com OR site:goal.com)"
    )
    match_prediction_urls = google_search(query)
    print("Match Prediction Found URLs:", match_prediction_urls)

    all_text_match_prediction = ""
    for url in match_prediction_urls:
        article_text_match_predictions = fetch_article(url)
        all_text_match_prediction += f"\n\nSOURCE: {url}\n{article_text_match_predictions}"


    query = (
        f"{teams['home']} vs {teams['away']} "
        "head to head, recent form, match stats, possession, shots on target, penalty kicks"
    )
    h2h_urls = google_search(query)
    print("Match h2h Found URLs:", h2h_urls)

    all_text_h2h = ""
    for url in h2h_urls:
        article_text_h2h = fetch_article(url)
        all_text_h2h += f"\n\nSOURCE: {url}\n{article_text_h2h}"


    query = (
        f"{teams['home']} vs {teams['away']} "
        "team news, player performances, injuries, match preview, lineup"
    )
    p_urls = google_search(query)
    print("Match Performance Found URLs:", p_urls)

    all_text_p = ""
    for url in p_urls:
        article_text_p = fetch_article(url)
        all_text_p += f"\n\nSOURCE: {url}\n{article_text_p}"

    payload = f"""

    You are a professional football betting analyst.

    Here are the football match metrics:

    {json.dumps(metrics, indent=2)}

     TASK:
        - Use both **team stats** (H2H, recent performance, xG, possession, shots, goals scored/conceded, injuries, home/away strength)
        and **market odds** to predict the match outcome.
        - Treat odds as an information prior. Convert bookmaker odds into **implied probabilities** and then remove the overround (**no-vig**).
        *If only Home/Away odds are provided, normalize across 2 outcomes; if Home/Draw/Away are provided, normalize across 3 outcomes.*
        - Compute **model/statistical probabilities** from the supplied metrics (do not make up missing data).
        - **Blending rule (logit space preferred, but probability space acceptable if you can't do logits):**
          Let p_mkt be the no-vig market probability and p_mdl be the stats/model probability.
          Choose a market weight w in [0.3, 0.7] (closer to 0.6 near kickoff, ~0.4 if early market).
          Then:
              logit(p_blend) = w*logit(p_mkt) + (1-w)*logit(p_mdl)
          If you cannot use logits safely, approximate with:
              p_blend = clamp( w*p_mkt + (1-w)*p_mdl, 0.01, 0.99 )

        - **Dynamic market weight & deviation cap:**
          Set w using both **time_to_kickoff** and **data_quality** (scale 0-1):
              w = clip(0.35 + 0.35*(proximity_to_kickoff) + 0.30*(data_quality_market), 0.40, 0.80)
          After computing p_blend, apply **shrinkage toward market**:
              max_dev = 0.12 for Home/Away, 0.10 for 3-way.
              p_final = p_mkt + clip(p_blend - p_mkt, -max_dev, +max_dev)

        - **Data-quality gating for stats boost:**
          Only apply the **+15% relative stats boost** if:
            (a) shots+xG dominance persists across ≥3 matches,
            (b) no major injury/rotation risk,
            (c) strength-of-schedule does not erase the edge.
          Otherwise, limit boost to **+5% relative**.

        - **Contrarian safeguard:**
          If p_mkt(favourite) ≥ 0.60 and p_mdl favours the other side,
          require ≥2 independent confirmations (e.g. injury + tactical mismatch)
          AND cap |p_final - p_mkt| for the favourite at 0.08.

        - **Lineup/late news adjustment:**
          Within T-90m to kickoff, if a top 3 xG/xA player or key GK is OUT,
          allow a one-time **+7% relative** swing against that team (re-normalize).

        - **Steam/odds-drift signal:**
          If odds moved ≥5% toward one side in last 24h across ≥2 books,
          add **+3% absolute** to that side, only if |p_mdl - p_mkt| < 0.10.

        - **Upset risk floor/ceiling:**
          Enforce 0.08 ≤ p_final(outcome) ≤ 0.88 pre-kickoff unless live metrics justify more.

        - **Live refinement:**
          If live and Emotional/Managerial Tensions or pressure/composure clearly favour a side,
          cap this boost to **+8% absolute** and only if xThreat/xG trend confirms.

        MATH TO SHOW (for each outcome you have odds for: Home, Draw, Away):
        1) Raw implied probability: q = 1 / odds
        2) No-vig normalization: p_mkt = q / sum(q for quoted outcomes)
        3) Fair odds from model/blend: fair_odds = 1 / p_blend
        4) Expected Value (EV) if staking 1 unit at price O:
            EV = p_blend * (O - 1) - (1 - p_blend)
        5) Value gap (percent): value_gap_% = 100 * (O - fair_odds) / fair_odds
        6) Deviation from market: dev = p_final - p_mkt
        7) Odds drift 24h: drift_% = 100 * (O_24h_ago - O_now) / O_24h_ago
        8) Market weight used (w) and max_dev applied

        DECISION:
        - **predicted_winner** = argmax of p_final (prefer Home/Away over Draw unless Draw clearly highest).
        - **value_recommendation** = outcome with highest positive EV (if none, return "No value").
        - If max(|dev|) > 6pp, downgrade confidence or add justification.
        - Provide short justification tying stats signals to the market signal.

        PRE_MATCH_PUBLIC_VERIFIED_INFORMATION_START

        {get_pre_match_public_information(
            teams['home'],
            teams['away'],
            match_date,
            all_text_match_prediction,
            all_text_h2h,
            all_text_p
        )}

        PRE_MATCH_PUBLIC_VERIFIED_INFORMATION_END

        IMPORTANT NOTES:
        - All analysis and probabilities must be grounded only in the provided metrics or verified pre-match/live information.Do **NOT** fabricate, simulate, or assume missing data — leave as "Data unavailable".
        - If any data (H2H, recent form, stats, win percentages) is **not available**, do **NOT** invent it. Leave "Data unavailable".
        - Realistic AI probability will be 50-90%.
        - Always re-normalize probabilities after boosts/nudges.
        - Increase w by +0.05 (max 0.80) when inputs are missing/incomplete.
        - Down-weight stats vs weak opponents by 10-25%.
        - If Draw p_mkt ≥ 0.28, forbid shifting Draw by more than ±0.06 without explicit tactical evidence.
        - If finished or ongoing, analyse real-time odds + match performance; explain key reason for win/loss.
        - Include Emotional & Managerial Tensions and pressure/composure if live.

        Probability fields MUST be returned as PERCENTAGES (0-100).

        Always include:
            "confidence": number (0-100),
            "confidence_level": "High" | "Medium" | "Low",
            "confidence_breakdown": "prob_separation": <number>, "market_agreement": <number>, "ev_separation": <number>, "data_quality": <number>

    Return a single JSON object with these keys:
    - predicted_winner
    - win_probabilities
    - xg_estimates
    - brief_explanation → about predicted winner (based on h2h, player performances, and odds)
    - value_gap → calculate value gap percentage between the two teams based on the provided analysis
    - match_odds → bookmaker odds for each team
    - value_recommendation // "home" | "draw" | "away" | "No value"
    - no_vig_probabilities // market no-vig probs for the same outcomes
    - blended_probabilities // final p_blend after stats boost + odds nudge + normalization
    - fair_odds          // 1 / blended_probabilities, same outcome keys
    - ev                 // EV per outcome for a 1-unit stake, same keys
    - confidence             // 0-100 number
    - confidence_level       // "High" | "Medium" | "Low"
    - confidence_breakdown   // prob_separation, market_agreement, ev_separation, data_quality 
    - match_explanation → big detailed long match summary including comparison of H2H matches | recent performances | individual player impact | ball possession & shots on target if available | goals scored/conceded trends | team strengths/weaknesses (injuries, suspensions, home/away) | performance in current match if match is finished or ongoing:
    - deviation_from_market
    - market_weight_used
    - max_deviation_cap
    - odds_drift_24h
    - lineup_news_flag
    - data_quality
    """

    result = call_openai(payload)

    print(result)
    
    # clean = result.strip("`").lstrip("json").strip()

    result = json.loads(result)

    resp = {
        "predicted_winner":result["predicted_winner"],
        "probabilitiesr":result["win_probabilities"],
        "teams":teams,
        "xg_estimates": result["xg_estimates"],
        "explanation": result["brief_explanation"],
        "value_gap": result["value_gap"],
        "fair_odds": result["fair_odds"],
        "no_vig_probabilities": result["no_vig_probabilities"],
        "blended_probabilities": result["blended_probabilities"],
        "ev": result["ev"],
        "match_explanation": result["match_explanation"],
        "match_odds": result["match_odds"],
        "raw": result,
    }

    return resp


# if __name__ == "__main__":
#     predict_fixture_result(19362150,"2025-08-16 00:00:00")