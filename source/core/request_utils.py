from typing import Optional, Tuple
from fastapi import Request
import httpx
from datetime import datetime

def get_client_ip(request: Request) -> str:
    xff = request.headers.get("x-forwarded-for")
    if xff:
        # X-Forwarded-For can be a comma-separated list; take the first (original client)
        return xff.split(",")[0].strip()
    xri = request.headers.get("x-real-ip")
    if xri:
        return xri.strip()
    return request.client.host if request.client else None

async def geolocate_ip(ip: str) -> dict:
    """
    Uses ipapi.co (no key needed for basic usage).
    Returns dict with keys: country, region, city, latitude, longitude
    Gracefully degrades on failure.
    """
    if not ip:
        return {}
    # Skip private/reserved addresses
    private_prefixes = ("10.", "192.168.", "172.16.", "172.17.", "172.18.", "172.19.",
                        "172.20.", "172.21.", "172.22.", "172.23.", "172.24.",
                        "172.25.", "172.26.", "172.27.", "172.28.", "172.29.",
                        "172.30.", "172.31.", "127.", "::1")
    if ip.startswith(private_prefixes):
        return {}

    url = f"https://ipapi.co/{ip}/json/"
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            r = await client.get(url)
            r.raise_for_status()
            data = r.json()
            return {
                "country":   data.get("country_name"),
                "region":    data.get("region"),
                "city":      data.get("city"),
                "latitude":  (data.get("latitude")  if isinstance(data.get("latitude"), (int, float)) else None),
                "longitude": (data.get("longitude") if isinstance(data.get("longitude"), (int, float)) else None),
            }
    except Exception:
        return {}

def now_utc():
    return datetime.utcnow()
