import numpy as np
import requests
from scipy.stats import poisson

API_BASE   = "https://api.sportmonks.com/v3/football"
API_TOKEN  = "EowWj4NnMhCihlx2acWj13J4AXSYpJJtPXjCcMM9BprYsttIl1PlcMHPAVcg"


def get_fixture_details(fid: int):
    """Fetch fixture + participants to get team IDs & season_id."""
    resp = requests.get(
        f"{API_BASE}/fixtures/{fid}",
        params={"api_token": API_TOKEN, "include": "participants"}
    )
    resp.raise_for_status()
    return resp.json()["data"]


def fetch_h2h(team1_id: int, team2_id: int):
    """Return list of past fixtures between team1 and team2."""
    resp = requests.get(
        f"{API_BASE}/fixtures/head-to-head/{team1_id}/{team2_id}",
        params={"api_token": API_TOKEN}
    )
    resp.raise_for_status()
    return resp.json().get("data", [])


def compute_draw_rate(fixtures: list) -> float:
    """Compute draw_rate = draws / total fixtures."""
    if not fixtures:
        return 0.0
    draws = sum(
        1 for f in fixtures
        if f.get("scores", {}).get("localteam_score")
           == f.get("scores", {}).get("visitorteam_score")
    )
    return draws / len(fixtures)


def fetch_standings(season_id: int):
    """Fetch the full league table for a given season."""
    resp = requests.get(
        f"{API_BASE}/standings/seasons/{season_id}",
        params={"api_token": API_TOKEN}
    )
    resp.raise_for_status()
    return resp.json().get("data", [])


def find_team_position(standings: list, team_id: int) -> int:
    """Scan standings list for this team’s 'position'."""
    for entry in standings:
        if entry.get("team_id") == team_id:
            return entry.get("position")
    return None


def fixture_stats(fixture_id: int) -> dict:
    """Fetch and extract possession and SOT for home/away."""
    resp = requests.get(
        f"{API_BASE}/fixtures/{fixture_id}",
        params={"api_token": API_TOKEN, "include": "statistics.type"}
    )
    resp.raise_for_status()
    data = resp.json()["data"]

    stat_map = {}
    for stat in data["statistics"]:
        code = stat["type"]["code"]    # e.g. "ball-possession"
        loc  = stat["location"]        # "home" or "away"
        val  = stat["data"]["value"]
        stat_map.setdefault(code, {})[loc] = val

    return {
        "poss_home": stat_map.get("ball-possession", {}).get("home", 0),
        "poss_away": stat_map.get("ball-possession", {}).get("away", 0),
        "sot_home":  stat_map.get("shots-on-target", {}).get("home", 0),
        "sot_away":  stat_map.get("shots-on-target", {}).get("away", 0),
    }


def compute_poisson_probs(mu_home, mu_away, max_goals=10):
    """Poisson matrix → raw P(home), P(draw), P(away)."""
    probs = np.zeros((max_goals+1, max_goals+1))
    for i in range(max_goals+1):
        for j in range(max_goals+1):
            probs[i,j] = poisson.pmf(i, mu_home) * poisson.pmf(j, mu_away)
    p_draw = np.trace(probs)
    p_home = np.sum(np.tril(probs, -1))
    p_away = np.sum(np.triu(probs, 1))
    return p_home, p_draw, p_away


def draw_rule_score(xg_h, xg_a, poss_h, poss_a, sot_h, sot_a, h2h_draw, pos_h, pos_a, mid_table_min=6):
    """Score the six draw conditions, skipping position rule if unknown."""
    score = 0
    if abs(xg_h - xg_a) < 0.3:           score += 10
    if (xg_h + xg_a) < 2.0:              score += 5
    if abs(poss_h - poss_a) <= 4:        score += 3
    if abs(sot_h - sot_a) < 2:           score += 3
    if h2h_draw > 0.30:                  score += 2
    # only apply the mid-table rule if both positions are known
    if pos_h is not None and pos_a is not None:
        if pos_h >= mid_table_min and pos_a >= mid_table_min:
            score += 2
    return score


def calibrated_probs(xg_h, xg_a, poss_h, poss_a, sot_h, sot_a, h2h_draw, pos_h, pos_a):
    p_h, p_d_raw, p_a = compute_poisson_probs(xg_h, xg_a)
    score = draw_rule_score(xg_h, xg_a, poss_h, poss_a, sot_h, sot_a, h2h_draw, pos_h, pos_a)
    draw_prob = 0.35 if score > 20 else 0.15
    non_draw = p_h + p_a
    if non_draw > 0:
        factor = (1 - draw_prob) / non_draw
        p_h, p_a = p_h * factor, p_a * factor
    else:
        p_h = p_a = (1 - draw_prob) / 2
    return p_h, draw_prob, p_a, score


def apply_logic(record, poss_h, poss_a, sot_h, sot_a, h2h_draw, home_pos, away_pos):
    """Mutates record: re-computes probabilities and appends draw_score."""
    home_team, away_team = record['fixture'].split(' vs ')
    xg_h = record['expected_goals'][home_team]
    xg_a = record['expected_goals'][away_team]

    p_h, p_d, p_a, score = calibrated_probs(
        xg_h, xg_a, poss_h, poss_a, sot_h, sot_a, h2h_draw, home_pos, away_pos
    )
    record['probabilities'] = {
        'home': int(round(p_h * 100, 1)),
        'draw': int(round(p_d * 100, 1)),
        'away': int(round(p_a * 100, 1)),
    }
    record['draw_score'] = score
    return record

def check_draw(raw):

    fid = int(raw.get("fixture_id"))

    # 1) Fixture details & team IDs
    fx = get_fixture_details(fid)
    parts = fx["participants"]
    home_id = next(p["id"] for p in parts if p["meta"]["location"] == "home")
    away_id = next(p["id"] for p in parts if p["meta"]["location"] == "away")
    season_id = fx["season_id"]

    # Compute H2H draw rate
    h2h_fixtures = fetch_h2h(home_id, away_id)
    h2h_rate     = compute_draw_rate(h2h_fixtures)
    print(f"h2h_draw_rate = {h2h_rate:.2%}")

    # Fetch standings & positions
    standings = fetch_standings(season_id)
    home_pos  = find_team_position(standings, home_id)
    away_pos  = find_team_position(standings, away_id)
    print(f"home_pos = {home_pos}, away_pos = {away_pos}")

    # Fetch possession & SOT
    stats   = fixture_stats(fid)
    poss_h, poss_a = stats["poss_home"], stats["poss_away"]
    sot_h, sot_a   = stats["sot_home"],  stats["sot_away"]

    updated = apply_logic(raw, poss_h, poss_a, sot_h, sot_a, h2h_rate, home_pos, away_pos)
    print("Updated probabilities:", updated['probabilities'])
    print("Draw score:", updated['draw_score'])

    return {
        "h2h_fixtures":  h2h_fixtures,
        "h2h_draw_rate": h2h_rate,
        "probabilities": updated['probabilities'] or None,
        "draw_score"  : updated['draw_score'] or None

    }
