"""
Create (or update) a Revolut Merchant webhook with logging.

- Hard-coded config lives at the top of this file.
- Will:
  1) List existing webhooks
  2) If one matches WEBHOOK_URL, update its events if needed
  3) Otherwise create a new webhook
- Prints the signing secret to stdout (NOT to logs) so you can copy it to WEBHOOK_SIGNING_SECRET.

Log file: revolut_webhooks.log
"""

import json
import logging
from logging.handlers import RotatingFileHandler
from typing import List, Dict, Optional

import httpx

# ==========================
# HARD-CODED CONFIG — EDIT ME
# ==========================
REVOLUT_BASE_URL   = "https://sandbox-merchant.revolut.com"
REVOLUT_SECRET_KEY = "sk_zcpzuxIV_sT0SDglN3vNJxRIdqjz2tjfxXLWPsnUKK5_ZR7WeQN_i05CGEf7LTjI"
REVOLUT_API_VERSION = "2024-09-01"   # not required for /api/1.0, harmless if present

# Set this to your actual public webhook URL
WEBHOOK_URL = "https://5af04b459489.ngrok-free.app/subscriptions/webhook"

# Minimum events for this flow
WEBHOOK_EVENTS = ["ORDER_COMPLETED", "ORDER_AUTHORISED"]

LOG_LEVEL = "INFO"
LOG_FILE  = "revolut_webhooks.log"
# ==========================


# ---------- Logging ----------
def setup_logging() -> logging.Logger:
    logger = logging.getLogger("revolut.webhooks")
    logger.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))
    logger.propagate = False

    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        "%Y-%m-%d %H:%M:%S",
    )

    sh = logging.StreamHandler()
    sh.setFormatter(fmt)
    logger.addHandler(sh)

    fh = RotatingFileHandler(LOG_FILE, maxBytes=1_000_000, backupCount=3)
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    return logger

log = setup_logging()


def _headers() -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {REVOLUT_SECRET_KEY}",
        "Content-Type": "application/json",
        # Including the version header is safe, though /api/1.0 usually doesn't require it.
        "Revolut-Api-Version": REVOLUT_API_VERSION,
    }


def _log_resp(resp: httpx.Response):
    text = resp.text
    preview = (text[:600] + "…") if len(text) > 600 else text
    log.info("HTTP %s %s -> %s | %s",
             resp.request.method, str(resp.request.url), resp.status_code, preview)


def list_webhooks(client: httpx.Client) -> List[Dict]:
    url = f"{REVOLUT_BASE_URL.rstrip('/')}/api/1.0/webhooks"
    resp = client.get(url)
    _log_resp(resp)
    resp.raise_for_status()
    try:
        data = resp.json()
    except Exception:
        data = []
    return data if isinstance(data, list) else []


def find_webhook_by_url(webhooks: List[Dict], url: str) -> Optional[Dict]:
    want = url.rstrip("/")
    for wh in webhooks:
        if (wh.get("url") or "").rstrip("/") == want:
            return wh
    return None


def update_webhook(client: httpx.Client, webhook_id: str, *, url: Optional[str] = None, events: Optional[List[str]] = None) -> Dict:
    payload: Dict[str, object] = {}
    if url:
        payload["url"] = url
    if events:
        payload["events"] = events

    endpoint = f"{REVOLUT_BASE_URL.rstrip('/')}/api/1.0/webhooks/{webhook_id}"
    log.info("Updating webhook id=%s with %s", webhook_id, payload)
    resp = client.patch(endpoint, content=json.dumps(payload))
    _log_resp(resp)
    resp.raise_for_status()
    return resp.json() if resp.text else {}


def create_webhook(client: httpx.Client, url: str, events: List[str]) -> Dict:
    endpoint = f"{REVOLUT_BASE_URL.rstrip('/')}/api/1.0/webhooks"
    payload = {"url": url, "events": events}
    log.info("Creating webhook: %s events=%s", url, events)
    resp = client.post(endpoint, content=json.dumps(payload))
    _log_resp(resp)
    resp.raise_for_status()
    created = resp.json()
    # Do NOT log the signing_secret
    if "signing_secret" in created:
        log.info("Webhook created (id=%s). Signing secret returned (hidden).", created.get("id"))
    else:
        log.warning("Webhook created but no signing_secret in response.")
    return created


def ensure_webhook() -> Dict:
    """
    Idempotent create/update so you don't end up with duplicates.
    Returns a dict containing:
      - action: "created" | "updated" | "noop"
      - webhook: the webhook object from Revolut (signing_secret may be present on create)
    """
    if not WEBHOOK_URL.startswith("https://"):
        raise SystemExit("WEBHOOK_URL must be an HTTPS URL (publicly reachable). Edit this file and set WEBHOOK_URL.")

    with httpx.Client(headers=_headers(), timeout=30) as client:
        # 1) list existing
        existing = list_webhooks(client)
        current = find_webhook_by_url(existing, WEBHOOK_URL)

        # 2) if exists, update events if needed
        if current:
            cur_events = [e.upper() for e in current.get("events", [])]
            want_events = [e.upper() for e in WEBHOOK_EVENTS]
            if set(cur_events) == set(want_events):
                log.info("Webhook already up to date (id=%s)", current.get("id"))
                return {"action": "noop", "webhook": current}
            updated = update_webhook(client, current["id"], events=WEBHOOK_EVENTS)
            log.info("Updated webhook events (id=%s)", current["id"])
            return {"action": "updated", "webhook": updated or current}

        # 3) otherwise, create
        created = create_webhook(client, WEBHOOK_URL, WEBHOOK_EVENTS)
        return {"action": "created", "webhook": created}


if __name__ == "__main__":
    try:
        result = ensure_webhook()
        wh = result.get("webhook", {})
        # DO NOT log the signing secret; print to stdout once for you to copy.
        signing_secret = wh.get("signing_secret")
        print(json.dumps({
            "action": result.get("action"),
            "id": wh.get("id"),
            "url": wh.get("url"),
            "events": wh.get("events"),
        }, indent=2))
        if signing_secret:
            print("\nSigning secret (copy this into WEBHOOK_SIGNING_SECRET):")
            print(signing_secret)
            print()
        else:
            print("\nNo signing secret in response (this is normal on update/noop). If you lost it, delete & recreate the webhook.\n")
    except httpx.HTTPStatusError as e:
        _log_resp(e.response)
        log.error("HTTP error: %s", e)
        raise
    except Exception as e:
        log.exception("Unexpected error")
        raise
