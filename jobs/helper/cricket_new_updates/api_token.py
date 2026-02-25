"""
API Token Management for Roanuz Cricket API
"""

import http.client
import json
from config import CRICKET_API_KEY, PROJECT_ID


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