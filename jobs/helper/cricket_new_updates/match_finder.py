"""
Enhanced Match Key Finder for Cricket Matches - Improved Date Filtering & Coverage
"""

import requests
import json
import time
import difflib
import pytz
from datetime import datetime, timedelta
from typing import Dict, List, Set, Any, Optional, Tuple
from config import BASE_URL


class EnhancedMatchKeyFinder:
    """Enhanced match key finder with improved date filtering and comprehensive search."""
    
    def __init__(self, project_id: str, token: str):
        self.project_id = project_id
        self.token = token
        self.headers = {"rs-token": token}
        self.seen_match_keys: Set[str] = set()
        self.all_matches: List[Dict] = []
        
        # Major cricket associations - expanded list
        self.major_associations = [
            "c__board__icc__c2ab7ee61",           # ICC
            "c__board__bcci__b13f0",             # BCCI (India)
            "c__board__ca__58678",               # Cricket Australia
            "c__board__england_and_wales_cricket_board__2e965", # ECB
            "c__board__pcb__83758",              # PCB (Pakistan)
            "c__board__sri_lanka_cricket_board__65294", # SLC
            "c__board__bcb__05ceb",              # BCB (Bangladesh)
            "c__board__csa__08532",              # CSA (South Africa)
            "c__board__nzc__7252b",              # NZC (New Zealand)
            "c__board__cwi__b3ce9",              # CWI (West Indies)
            "c__board__acb__af939",              # ACB (Afghanistan)
            "c__board__cricket_ireland__f27ef",  # Cricket Ireland
            "c__board__zcu__30d29",              # Zimbabwe Cricket
        ]
        
    def normalize_team_name(self, name: str) -> str:
        """Normalize team names for better matching."""
        common_removes = [" Cricket Club", " CC", " FC", " United", " XI", " Men", " Women"]
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
    
    def parse_match_date(self, match: Dict) -> Optional[datetime]:
        """Parse match date with multiple fallback methods."""
        try:
            # Primary: start_at timestamp
            if match.get("start_at"):
                return datetime.fromtimestamp(match["start_at"], tz=pytz.utc)
            
            # Fallback: start_date string
            if match.get("start_date"):
                try:
                    return datetime.strptime(match["start_date"], "%Y-%m-%d").replace(tzinfo=pytz.utc)
                except:
                    pass
            
            # Additional fallbacks for different date formats
            date_fields = ["date", "match_date", "scheduled_date"]
            for field in date_fields:
                if match.get(field):
                    try:
                        if isinstance(match[field], (int, float)):
                            return datetime.fromtimestamp(match[field], tz=pytz.utc)
                        elif isinstance(match[field], str):
                            # Try different date formats
                            for fmt in ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"]:
                                try:
                                    return datetime.strptime(match[field], fmt).replace(tzinfo=pytz.utc)
                                except:
                                    continue
                    except:
                        continue
                        
        except Exception as e:
            print(f"   ⚠️ Date parsing error: {e}")
            
        return None
    
    def fetch_direct_date_fixtures(self, date_str: str) -> int:
        """Strategy 0: Direct date-specific API calls."""
        print(f"📋 [Strategy 0/8] Direct Date Fixtures for {date_str}...")
        count = 0
        
        try:
            # Try direct date endpoint
            url = f"{BASE_URL}/{self.project_id}/fixtures/date/{date_str}/"
            resp = requests.get(url, headers=self.headers, timeout=10)
            if resp.status_code == 200:
                data = resp.json().get("data", {})
                matches = data.get("matches", [])
                for match in matches:
                    self.add_match_if_unique(match)
                    count += 1
                print(f"   Direct date endpoint: {len(matches)} matches")
            
            # Try with year-month format
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            year_month = date_obj.strftime("%Y-%m")
            
            url2 = f"{BASE_URL}/{self.project_id}/fixtures/date/{year_month}/"
            resp2 = requests.get(url2, headers=self.headers, timeout=10)
            if resp2.status_code == 200:
                data2 = resp2.json().get("data", {})
                month_data = data2.get("month", {})
                
                for day_data in month_data.get("days", []):
                    day_date = day_data.get("date")
                    if day_date == date_str:
                        for match in day_data.get("matches", []):
                            self.add_match_if_unique(match)
                            count += 1
                        print(f"   Month endpoint for {date_str}: {len(day_data.get('matches', []))} matches")
                        
        except Exception as e:
            print(f"   ⚠️ Error in direct date fixtures: {e}")
            
        return count
    
    def fetch_global_fixtures_api(self, date_range: List[datetime]) -> int:
        """Strategy 1: Global Fixtures API with better date handling."""
        print("📋 [Strategy 1/8] Searching Global Fixtures API...")
        count = 0
        
        try:
            # Multiple endpoints to try
            endpoints = ["fixtures/", "fixtures/current/", "fixtures/recent/", "fixtures/upcoming/"]
            
            for endpoint in endpoints:
                try:
                    url = f"{BASE_URL}/{self.project_id}/{endpoint}"
                    resp = requests.get(url, headers=self.headers, timeout=15)
                    if resp.status_code != 200:
                        continue
                        
                    data = resp.json().get("data", {})
                    
                    # Handle different response structures
                    if "month" in data:
                        month_data = data["month"]
                        for day_data in month_data.get("days", []):
                            for match in day_data.get("matches", []):
                                self.add_match_if_unique(match)
                                count += 1
                    elif "matches" in data:
                        for match in data["matches"]:
                            self.add_match_if_unique(match)
                            count += 1
                    elif "fixtures" in data:
                        for match in data["fixtures"]:
                            self.add_match_if_unique(match)
                            count += 1
                            
                    print(f"   Endpoint {endpoint}: Found matches")
                    
                except Exception as e:
                    continue
                
        except Exception as e:
            print(f"   ⚠️ Error in global fixtures: {e}")
            
        return count
    
    def fetch_all_association_tournaments(self) -> int:
        """Strategy 2: Enhanced association tournament search."""
        print("📋 [Strategy 2/8] Searching All Association Tournaments...")
        count = 0
        all_tournament_keys = set()
        
        for assoc_key in self.major_associations:
            try:
                # Multiple tournament endpoints
                endpoints = ["featured-tournaments/", "tournaments/", "recent-tournaments/"]
                
                for endpoint in endpoints:
                    try:
                        url = f"{BASE_URL}/{self.project_id}/association/{assoc_key}/{endpoint}"
                        resp = requests.get(url, headers=self.headers, timeout=8)
                        if resp.status_code != 200:
                            continue
                            
                        tournaments = resp.json().get("data", {}).get("tournaments", [])
                        
                        for tournament in tournaments:
                            tkey = tournament.get("key")
                            if tkey:
                                all_tournament_keys.add(tkey)
                                
                    except Exception:
                        continue
                
                print(f"   Association {assoc_key.split('__')[-2].upper()}: tournaments found")
                
            except Exception as e:
                continue
        
        print(f"   Total unique tournaments found: {len(all_tournament_keys)}")
        
        # Get fixtures for all tournaments with multiple endpoints
        for tkey in all_tournament_keys:
            try:
                fixture_endpoints = ["fixtures/", "matches/", "recent-matches/", "upcoming-matches/"]
                
                for endpoint in fixture_endpoints:
                    try:
                        fixtures_url = f"{BASE_URL}/{self.project_id}/tournament/{tkey}/{endpoint}"
                        tr_resp = requests.get(fixtures_url, headers=self.headers, timeout=6)
                        if tr_resp.status_code != 200:
                            continue
                            
                        data = tr_resp.json().get("data", {})
                        matches = data.get("matches", []) or data.get("fixtures", [])
                        
                        for match in matches:
                            self.add_match_if_unique(match)
                            count += 1
                            
                    except Exception:
                        continue
                        
            except Exception:
                continue
                
        return count

    def fetch_live_and_recent_matches(self) -> int:
        """Strategy 3: Live and recent matches endpoints."""
        print("📋 [Strategy 3/8] Searching Live and Recent Matches...")
        count = 0
        
        try:
            live_endpoints = [
                "matches/live/",
                "matches/recent/", 
                "matches/upcoming/",
                "live-matches/",
                "recent-matches/",
                "upcoming-matches/"
            ]
            
            for endpoint in live_endpoints:
                try:
                    url = f"{BASE_URL}/{self.project_id}/{endpoint}"
                    resp = requests.get(url, headers=self.headers, timeout=8)
                    if resp.status_code != 200:
                        continue
                        
                    data = resp.json().get("data", {})
                    matches = data.get("matches", [])
                    
                    for match in matches:
                        self.add_match_if_unique(match)
                        count += 1
                        
                    if matches:
                        print(f"   Endpoint {endpoint}: {len(matches)} matches")
                        
                except Exception:
                    continue
                    
        except Exception as e:
            print(f"   ⚠️ Error in live/recent matches: {e}")
            
        return count

    def fetch_featured_matches_v2(self) -> int:
        """Strategy 4: Enhanced Featured Matches."""
        print("📋 [Strategy 4/8] Searching Enhanced Featured Matches...")
        count = 0
        
        # Get all tournament keys first
        all_tournament_keys = set()
        
        for assoc_key in self.major_associations:
            try:
                url = f"{BASE_URL}/{self.project_id}/association/{assoc_key}/featured-tournaments/"
                resp = requests.get(url, headers=self.headers, timeout=8)
                if resp.status_code == 200:
                    tournaments = resp.json().get("data", {}).get("tournaments", [])
                    for tournament in tournaments:
                        tkey = tournament.get("key")
                        if tkey:
                            all_tournament_keys.add(tkey)
                            
            except Exception:
                continue
        
        # Try multiple featured endpoints for each tournament
        for tkey in list(all_tournament_keys)[:100]:  # Increased limit
            try:
                featured_endpoints = ["featured-matches-2/", "featured-matches/", "featured/"]
                
                for endpoint in featured_endpoints:
                    try:
                        url = f"{BASE_URL}/{self.project_id}/tournament/{tkey}/{endpoint}"
                        resp = requests.get(url, headers=self.headers, timeout=5)
                        if resp.status_code == 200:
                            matches = resp.json().get("data", {}).get("matches", [])
                            for match in matches:
                                self.add_match_if_unique(match)
                                count += 1
                            
                            if matches:
                                break  # If one endpoint works, skip others
                                
                    except Exception:
                        continue
                        
            except Exception:
                continue
                
        return count
    
    def fetch_season_matches(self, target_date: datetime) -> int:
        """Strategy 5: Season-based matches."""
        print("📋 [Strategy 5/8] Searching Season Matches...")
        count = 0
        
        try:
            # Try season endpoints
            season_endpoints = [
                f"season/{target_date.year}/matches/",
                f"season/{target_date.year}/fixtures/",
                "season/current/matches/",
                "season/current/fixtures/"
            ]
            
            for endpoint in season_endpoints:
                try:
                    url = f"{BASE_URL}/{self.project_id}/{endpoint}"
                    resp = requests.get(url, headers=self.headers, timeout=10)
                    if resp.status_code == 200:
                        data = resp.json().get("data", {})
                        matches = data.get("matches", []) or data.get("fixtures", [])
                        
                        for match in matches:
                            self.add_match_if_unique(match)
                            count += 1
                            
                        if matches:
                            print(f"   Season endpoint {endpoint}: {len(matches)} matches")
                            
                except Exception:
                    continue
                    
        except Exception as e:
            print(f"   ⚠️ Error in season matches: {e}")
            
        return count

    def fetch_comprehensive_date_range(self, target_date: datetime) -> int:
        """Strategy 6: Comprehensive date range search."""
        print("📋 [Strategy 6/8] Comprehensive Date Range Search...")
        count = 0
        
        try:
            # Create wider date range (±3 days to ensure we don't miss matches)
            date_range = []
            for offset in range(-3, 4):
                check_date = target_date + timedelta(days=offset)
                date_range.append(check_date)
            
            # Try different date formats and endpoints
            for check_date in date_range:
                date_formats = [
                    check_date.strftime("%Y-%m-%d"),
                    check_date.strftime("%Y%m%d"),
                    check_date.strftime("%d-%m-%Y"),
                ]
                
                for date_fmt in date_formats:
                    try:
                        endpoints = [
                            f"fixtures/date/{date_fmt}/",
                            f"matches/date/{date_fmt}/",
                            f"fixtures/{date_fmt}/",
                            f"matches/{date_fmt}/"
                        ]
                        
                        for endpoint in endpoints:
                            try:
                                url = f"{BASE_URL}/{self.project_id}/{endpoint}"
                                resp = requests.get(url, headers=self.headers, timeout=6)
                                if resp.status_code == 200:
                                    data = resp.json().get("data", {})
                                    
                                    # Handle different response structures
                                    matches = []
                                    if "matches" in data:
                                        matches = data["matches"]
                                    elif "fixtures" in data:
                                        matches = data["fixtures"]
                                    elif "month" in data and "days" in data["month"]:
                                        for day in data["month"]["days"]:
                                            matches.extend(day.get("matches", []))
                                    
                                    for match in matches:
                                        self.add_match_if_unique(match)
                                        count += 1
                                        
                            except Exception:
                                continue
                                
                    except Exception:
                        continue
                        
        except Exception as e:
            print(f"   ⚠️ Error in date range search: {e}")
            
        return count

    def fetch_regional_comprehensive(self) -> int:
        """Strategy 7: Comprehensive regional search."""
        print("📋 [Strategy 7/8] Comprehensive Regional Search...")
        count = 0
        
        try:
            # Get ALL associations
            url = f"{BASE_URL}/{self.project_id}/association/list/"
            resp = requests.get(url, headers=self.headers, timeout=10)
            if resp.status_code == 200:
                all_associations = resp.json().get("data", {}).get("associations", [])
                
                print(f"   Found {len(all_associations)} total associations")
                
                # Process all associations (not just major ones)
                for assoc in all_associations[:50]:  # Limit to prevent timeout
                    assoc_key = assoc.get("key")
                    if not assoc_key:
                        continue
                    
                    try:
                        # Try multiple tournament endpoints
                        tourn_endpoints = ["featured-tournaments/", "tournaments/", "active-tournaments/"]
                        
                        for endpoint in tourn_endpoints:
                            try:
                                tourn_url = f"{BASE_URL}/{self.project_id}/association/{assoc_key}/{endpoint}"
                                tr_resp = requests.get(tourn_url, headers=self.headers, timeout=4)
                                if tr_resp.status_code != 200:
                                    continue
                                    
                                tournaments = tr_resp.json().get("data", {}).get("tournaments", [])
                                
                                for tournament in tournaments[:3]:  # Limit per association
                                    tkey = tournament.get("key")
                                    if not tkey:
                                        continue
                                        
                                    # Try multiple match endpoints
                                    match_endpoints = ["fixtures/", "matches/", "recent-matches/"]
                                    
                                    for match_endpoint in match_endpoints:
                                        try:
                                            fix_url = f"{BASE_URL}/{self.project_id}/tournament/{tkey}/{match_endpoint}"
                                            fix_resp = requests.get(fix_url, headers=self.headers, timeout=3)
                                            if fix_resp.status_code == 200:
                                                matches = fix_resp.json().get("data", {}).get("matches", [])
                                                for match in matches:
                                                    self.add_match_if_unique(match)
                                                    count += 1
                                                    
                                        except Exception:
                                            continue
                                            
                            except Exception:
                                continue
                                
                    except Exception:
                        continue
                        
        except Exception as e:
            print(f"   ⚠️ Error in regional search: {e}")
            
        return count

    def fetch_legacy_and_fallback(self) -> int:
        """Strategy 8: Legacy and fallback methods."""
        print("📋 [Strategy 8/8] Legacy and Fallback Search...")
        count = 0
        
        try:
            # Comprehensive list of possible endpoints
            all_endpoints = [
                "featured-matches/",
                "matches/",
                "fixtures/", 
                "live-matches/",
                "recent-matches/",
                "upcoming-matches/",
                "today-matches/",
                "current-matches/",
                "active-matches/",
                "schedule/",
                "calendar/",
                "games/",
                "contests/",
            ]
            
            for endpoint in all_endpoints:
                try:
                    url = f"{BASE_URL}/{self.project_id}/{endpoint}"
                    resp = requests.get(url, headers=self.headers, timeout=5)
                    if resp.status_code == 200:
                        data = resp.json().get("data", {})
                        
                        # Try different data keys
                        possible_keys = ["matches", "fixtures", "games", "contests", "data"]
                        
                        for key in possible_keys:
                            if key in data and isinstance(data[key], list):
                                for match in data[key]:
                                    self.add_match_if_unique(match)
                                    count += 1
                                break
                                
                except Exception:
                    continue
                    
        except Exception as e:
            print(f"   ⚠️ Error in legacy fallback: {e}")
            
        return count
    
    def filter_matches_by_date(self, target_dates: Set, debug: bool = True) -> List[Dict]:
        """Enhanced date filtering with debug info."""
        filtered_matches = []
        date_parse_stats = {"success": 0, "failed": 0, "no_date": 0}
        
        for match in self.all_matches:
            try:
                match_datetime = self.parse_match_date(match)
                
                if match_datetime is None:
                    date_parse_stats["no_date"] += 1
                    if debug and len(filtered_matches) < 5:  # Show first few examples
                        print(f"   ⚠️ No date found in match: {match.get('key', 'unknown')}")
                    continue
                
                match_date = match_datetime.date()
                date_parse_stats["success"] += 1
                
                if match_date in target_dates:
                    filtered_matches.append(match)
                    if debug:
                        teams_info = "Unknown vs Unknown"
                        if match.get('teams'):
                            team_a = match['teams'].get('a', {}).get('name', 'Unknown')
                            team_b = match['teams'].get('b', {}).get('name', 'Unknown')
                            teams_info = f"{team_a} vs {team_b}"
                        print(f"   ✓ Match found: {teams_info} ({match_date})")
                        
            except Exception as e:
                date_parse_stats["failed"] += 1
                if debug:
                    print(f"   ⚠️ Error processing match: {e}")
                continue
        
        if debug:
            print(f"📊 Date filtering stats: {date_parse_stats}")
            print(f"   Total matches checked: {len(self.all_matches)}")
            print(f"   Matches with valid dates: {date_parse_stats['success']}")
            print(f"   Matches on target date: {len(filtered_matches)}")
        
        return filtered_matches

    def find_all_matches_on_date(self, date_str: str) -> List[Dict]:
        """Enhanced match finding with comprehensive search and better date handling."""
        print(f"🔍 Finding all matches on {date_str} using enhanced comprehensive search...")

        # Parse date and create search window
        try:
            center_date = datetime.strptime(date_str, "%Y-%m-%d")
            target_dates = {center_date.date()}
        except ValueError:
            print("❌ Invalid date format. Please use YYYY-MM-DD.")
            return []

        # Reset collections
        self.seen_match_keys.clear()
        self.all_matches.clear()

        # Execute ALL comprehensive search strategies
        strategy_counts = [
            self.fetch_direct_date_fixtures(date_str),           # Direct date API
            self.fetch_global_fixtures_api([center_date]),       # Global fixtures
            self.fetch_all_association_tournaments(),            # All associations
            self.fetch_live_and_recent_matches(),               # Live/recent
            self.fetch_featured_matches_v2(),                   # Featured matches
            self.fetch_season_matches(center_date),             # Season matches
            self.fetch_comprehensive_date_range(center_date),   # Date range
            self.fetch_regional_comprehensive(),                # Regional comprehensive
            self.fetch_legacy_and_fallback(),                  # Legacy fallback
        ]

        total_found = len(self.all_matches)
        print(f"📊 Enhanced search completed: {total_found} total unique matches found.")
        print(f"   Strategy breakdown → {strategy_counts}")

        # Enhanced date filtering with debug
        date_matches = self.filter_matches_by_date(target_dates, debug=True)
        
        if not date_matches:
            print(f"❌ No matches found for date {date_str}")
            print("🔍 Checking sample matches from total collection...")
            
            # Show sample dates from all matches for debugging
            sample_dates = set()
            for match in self.all_matches[:20]:
                match_dt = self.parse_match_date(match)
                if match_dt:
                    sample_dates.add(match_dt.date())
            
            print(f"   Sample dates found: {sorted(sample_dates)}")
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

                match_datetime = self.parse_match_date(match)
                match_time_str = match_datetime.strftime("%Y-%m-%d %H:%M UTC") if match_datetime else "Unknown time"

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
                    'match_time': match_time_str,
                    'association': match.get('association', {}).get('name', 'Unknown') if match.get('association') else 'Unknown',
                    'insights': match
                }
                matches_with_insights.append(match_info)
                seen_match_keys_final.add(match_key)
                
            except Exception as e:
                print(f"   ⚠️ Error processing match: {e}")
                continue
        
        return matches_with_insights
    


    def find_specific_team_match(self, team1: str, team2: str, date_str: str, venue: str = None) -> List[Dict]:

        print(f"🎯 Searching for {team1} vs {team2} on {date_str}")
        if venue:
            print(f"📍 Venue filter: {venue}")
        
        # First, get ALL matches on the specified date
        all_date_matches = self.find_all_matches_on_date(date_str)
        
        if not all_date_matches:
            print(f"❌ No matches found on {date_str}")
            return []
        
        print(f"📋 Found {len(all_date_matches)} total matches on {date_str}")
        
        # Filter matches by teams
        matching_games = []
        
        for match in all_date_matches:
            try:
                teams = match.get('teams', {})
                team_a = teams.get('team_a', '')
                team_b = teams.get('team_b', '')
                match_venue = match.get('venue', '').lower()
                
                # Check if both teams match (order doesn't matter)
                team1_match_a, sim1a = self.is_team_match(team_a, team1)
                team1_match_b, sim1b = self.is_team_match(team_b, team1)
                team2_match_a, sim2a = self.is_team_match(team_a, team2)
                team2_match_b, sim2b = self.is_team_match(team_b, team2)
                
                # Match found if:
                # (team1 matches team_a AND team2 matches team_b) OR
                # (team1 matches team_b AND team2 matches team_a)
                teams_match = (team1_match_a and team2_match_b) or (team1_match_b and team2_match_a)
                
                if teams_match:
                    # Calculate combined similarity score
                    if team1_match_a and team2_match_b:
                        combined_similarity = (sim1a + sim2b) / 2
                    else:
                        combined_similarity = (sim1b + sim2a) / 2
                    
                    # Venue filtering (if specified)
                    venue_match = True
                    venue_similarity = 1.0
                    
                    if venue:
                        venue_similarity = difflib.SequenceMatcher(
                            None, venue.lower(), match_venue
                        ).ratio()
                        venue_match = (
                            venue_similarity >= 0.6 or 
                            venue.lower() in match_venue or 
                            match_venue in venue.lower()
                        )
                    
                    if venue_match:
                        # Add match with similarity scores
                        match_with_scores = match.copy()
                        match_with_scores.update({
                            'team_similarity': combined_similarity,
                            'venue_similarity': venue_similarity,
                            'match_confidence': (combined_similarity + venue_similarity) / 2
                        })
                        
                        matching_games.append(match_with_scores)
                        
                        print(f"✅ Match found: {team_a} vs {team_b}")
                        print(f"   🎯 Team similarity: {combined_similarity:.2f}")
                        print(f"   📍 Venue: {match.get('venue', 'Unknown')} (similarity: {venue_similarity:.2f})")
                        print(f"   🏏 Tournament: {match.get('tournament', 'Unknown')}")
                        print(f"   🔑 Match key: {match.get('match_key', 'Unknown')}")
                        
            except Exception as e:
                print(f"⚠️ Error processing match: {e}")
                continue
        
        # Sort by match confidence (highest first)
        matching_games.sort(key=lambda x: x.get('match_confidence', 0), reverse=True)
        
        if not matching_games:
            print(f"❌ No matches found between {team1} and {team2} on {date_str}")
            if venue:
                print(f"   (with venue filter: {venue})")
            
            # Show what matches were found for debugging
            print("\n🔍 Matches found on this date:")
            for match in all_date_matches[:5]:  # Show first 5
                teams = match.get('teams', {})
                print(f"   • {teams.get('team_a', 'Unknown')} vs {teams.get('team_b', 'Unknown')}")
        else:
            print(f"🎉 Found {len(matching_games)} matching game(s)!")
            
            # Show best match details
            best_match = matching_games[0]
            print(f"\n🏆 Best match (confidence: {best_match.get('match_confidence', 0):.2f}):")
            print(f"   Teams: {best_match['teams']['team_a']} vs {best_match['teams']['team_b']}")
            print(f"   Venue: {best_match.get('venue', 'Unknown')}")
            print(f"   Time: {best_match.get('match_time', 'Unknown')}")
            print(f"   Key: {best_match.get('match_key', 'Unknown')}")
        
        return matching_games
