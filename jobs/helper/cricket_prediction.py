#!/usr/bin/env python3
"""
generate_and_test_cricket_prompt.py: Generate ChatGPT prompts for cricket analytics and test them via a hardcoded example,
including a live OpenAI API call. All match metrics (win probabilities, percentages, form, H2H, odds, pitch conditions, and game changers) are computed by GPT, with instructions to fetch accurate player data via web sources and associate players with their teams.
"""
import openai
import sys
import datetime
import json

# Sample API key
OPENAI_API_KEY = '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'


def normalize_to_utc(date_str: str) -> str:
    """
    Normalize a date string to an ISO 8601 UTC datetime.
    If only YYYY-MM-DD given, returns YYYY-MM-DDT00:00:00+00:00.
    """
    try:
        if 'T' not in date_str:
            dt = datetime.datetime.strptime(date_str, '%Y-%m-%d')
            dt = dt.replace(tzinfo=datetime.timezone.utc)
        else:
            dt = datetime.datetime.fromisoformat(date_str)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=datetime.timezone.utc)
            dt = dt.astimezone(datetime.timezone.utc)
        return dt.isoformat()
    except Exception as e:
        print(f"Warning: unable to parse date '{date_str}': {e}", file=sys.stderr)
        return date_str


def generate_cricket_prompt(team_a: str, team_b: str, match_datetime: str) -> str:
    """
    Build a prompt instructing GPT to compute all match analytics dynamically:
    win probability, win percentages, recent form, head-to-head, bookmaker odds, pitch conditions,
    potential game-changing players, accurate player stats for the current playing XI fetched via web sources,
    with explanation for probability vs percentages.
    """
    utc_datetime = normalize_to_utc(match_datetime)
    return f"""
You are a cricket analytics assistant. For the cricket match scheduled on {match_datetime} (UTC: {utc_datetime}):
- Teams: \"{team_a}\" vs \"{team_b}\"

Compute and include the following entirely within the response, sourcing data from reputable cricket platforms (e.g., ESPNcricinfo, Cricbuzz):
1. **Predicted winner**: identify the team most likely to win.
2. **Probability percent**: an integer 0-100 indicating win probability for the predicted winner.
3. **Winning percentages** for both teams (integers summing to 100).

**Important**: Compute these metrics using a weighted combination of:
- **Head-to-head record** (past fixtures).
- **Recent performance**: results from each side’s last 10 matches.
- **Bookmaker odds**: fetch live odds from major platforms (e.g., Betfair, DraftKings).
- **Pitch conditions**: include pitch characteristics (e.g., spin-friendly, batting track) and match-day conditions.
Specify assumed weightings for each factor or justify chosen weights.

Specify assumed weightings for each factor or justify chosen weights.

- Treat **consensus bookmaker/exchange odds as a prior**. Convert decimal odds → implied probs, **remove the vig** (no-vig), and anchor predictions to these priors.
- **Evidence-based adjustments only** (form, H2H, venue/toss bias, weather, XIs, injuries). Quantify each adjustment (±pp) and cite a reputable source for it.
- **Deviation cap**: Do not move any team's probability **> ±8 percentage points** away from the no-vig prior unless you have ≥2 independent sources supporting it. If exceeded, include "deviation_reason" explaining why.
- **Scenario modeling (pre-toss)**: Provide probabilities **conditional on who bats first** and an aggregated **pre-toss** probability (50/50 toss assumption). Note chasing bias.
- **Calibration & uncertainty**: Report a 0'100 **confidence_level** derived from probability entropy and input completeness (odds coverage, XI confirmation, weather certainty).
- **No fabrication**: If any data (odds/news/XIs/stats) is unavailable, leave fields `null` or "Data unavailable" and say why.


Additionally include:
4. **Recent form** details (last 10 matches: wins/losses counts for each team).
5. **Head-to-head** summary (total matches, individual wins).
6. **Bookmaker odds** found (platform names and odds up to two decimal places) Also provide a **consensus** (median) across ≥3 reputable sources (e.g., Betfair exchange, Pinnacle, Oddschecker), show implied probs and **no-vig** probs. Include source names and URLs.

7. **Pitch conditions** explanation.
8. **Potential game-changing players**: list 2–3 key batters and bowlers from each team's current playing XI, including their team names, who could significantly influence the match outcome.
9. **Weather forecast** at the venue and kickoff.
10. **Recent news** affecting either side.
11. **Key player stats**: for each team's current playing XI, fetch top 3 batters and top 3 bowlers' stats (runs, strike rate, wickets, economy) from cricket data websites. Include each player's team affiliation.

Computation method (show your work):
1) Implied probs: p_raw = 1 / odds. 2) No-vig: p = p_raw / Σ p_raw.
3) Stats model: compute p_stats from form/H2H/venue/news (state weights).
4) **Blended**: blended = w_market * p_no_vig + w_model * p_stats
   • T20 default: w_market=0.70, w_model=0.30
   • ODI default: w_market=0.60, w_model=0.40
   • Lower w_model when uncertainty is high (unconfirmed XIs, high rain/DLS risk, volatile venue).
5) Deviation check vs p_no_vig (±pp) and justify if >8pp.
6) Scenario split: {team_a} bats first vs {team_b} bats first; aggregate pre-toss.
7) Edge vs market: edge_percent = 100 * (blended - p_no_vig).

Include a brief **explanation**:
- Justify why the predicted winner was chosen based on the weighted factors.
- Clarify why **probability percent** may differ from **winning percentages** (rounding, weighting emphasis).

Return a single JSON object with this structure:
```json
{{
  "match": {{
    "event": "<string>",
    "date_local": "<YYYY-MM-DDTHH:MM:SS±HH:MM>",
    "date_utc": "<YYYY-MM-DDTHH:MM:SS+00:00>",
    "venue": "<string>",
    "teams": ["<string>", "<string>"]
  }},
  "predicted_winner": {{
    "team": "<string>",
    "probability_percent": <int>,
    "explanation": "<string>"
  }},
  "winning_percentages": {{
    "<team1>": <int>,
    "<team2>": <int>
  }},
  "recent_form": {{
    "<team1>": {{"matches": 10, "wins": <int>, "losses": <int>}},
    "<team2>": {{"matches": 10, "wins": <int>, "losses": <int>}}
  }},
  "head_to_head": {{
    "total": <int>,
    "wins": {{"<team1>": <int>, "<team2>": <int>}}
  }},
  "bookmaker_odds": [
    {{"platform": "<string>", "odds": {{"<team1>": "<decimal>", "<team2>": "<decimal>"}}}}
  ],
  "pitch_conditions": "<string>",
  "game_changers": {{
    "batters": [{{"name": "<string>", "team": "<string>"}}],
    "bowlers": [{{"name": "<string>", "team": "<string>"}}]
  }},
  "weather": {{"condition": "<string>", "temperature_c": <number>}},
  "recent_news": [
    {{"headline": "<string>", "source": "<string>", "date": "<YYYY-MM-DD>"}}
  ],
  "player_stats": {{
    "{team_a}": {{"top_batters": [{{"name": "<string>", "runs": <int>, "strike_rate": <number>}}], "top_bowlers": [{{"name": "<string>", "wickets": <int>, "economy": <number>}}]}},
    "{team_b}": {{"top_batters": [{{"name": "<string>", "runs": <int>, "strike_rate": <number>}}], "top_bowlers": [{{"name": "<string>", "wickets": <int>, "economy": <number>}}]}}
  }}
  
   "market_consensus": {{
        "sources": [
        {{"platform": "<string>", "odds": {{"<team1>": "<decimal>", "<team2>": "<decimal>"}}, "url": "<string>"}}
        ],
        "implied_probs_raw": {{"<team1>": <number>, "<team2>": <number>}},
        "no_vig_probs": {{"<team1>": <number>, "<team2>": <number>}}
    }},
    "probability_model": {{
        "stats_model_probs": {{"<team1>": <number>, "<team2>": <number>}},
        "weights": {{"w_market": <number>, "w_model": <number>}},
        "scenario_pre_toss": {{
        "<team1>_bats_first": {{"<team1>": <number>, "<team2>": <number>}},
        "<team2>_bats_first": {{"<team1>": <number>, "<team2>": <number>}}
        }},
        "blended_pre_toss": {{"<team1>": <number>, "<team2>": <number>}},
        "deviation_from_market_pp": {{"<team1>": <number>, "<team2>": <number>}},
        "deviation_reason": "<string|null>"
    }},
    "edges": [
        {{"platform": "<string>", "team": "<string>", "edge_percent": <number>, "price": "<decimal>"}}
    ],
    "confidence": {{
        "confidence_level": <int>,
        "uncertainty_factors": ["<toss_impact>", "<lineup_uncertainty>", "<weather/DLS>", "<sample_size>", "<strength_of_schedule>"]
    }}
}}
```"""


def call_openai(prompt: str) -> str:
    """
    Send the prompt to OpenAI and return the reply.
    """
    try:
        resp = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        print(f"API error: {e}", file=sys.stderr)
        sys.exit(1)


def get_cricket_pred(team_a, team_b, match_datetime):
    # team_a, team_b, match_datetime = "Kuwait Swedish", "CECC", "2025-08-06"
    prompt = generate_cricket_prompt(team_a, team_b, match_datetime)
    print("---- Generated Prompt ----")
    # print(prompt)

    result = call_openai(prompt)

    print("\n---- API Response ----")

    result = call_openai(prompt)

    clean = result.strip("`").lstrip("json").strip()

    result = json.loads(clean)

    return result

