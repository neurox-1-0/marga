"""
backend/services/noaa_poller.py

Background NOAA maritime weather polling service.

Polls the NOAA Weather API (https://api.weather.gov) for active marine
weather alerts on zones relevant to our tracked shipping routes.
Free, no API key required.

When a new significant alert is detected:
  1. Deduplicates against already-processed event IDs (stored in memory +
     persisted to the EventThreadDB table so it survives restarts).
  2. Maps the NOAA alert fields to our internal raw_event schema.
  3. Kicks off the LangGraph agent via graph.ainvoke() — exactly the same
     flow as the manual /trigger_disruption endpoint.

Runs as an asyncio background task started from main.py on_event("startup").
"""

import asyncio
import logging
import uuid
from datetime import datetime, timezone
from typing import Optional
import httpx

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Route → NOAA Marine Zone mapping
# NOAA publishes zone IDs for US coastal waters and major shipping lanes.
# Full list: https://api.weather.gov/zones?type=marine
# ---------------------------------------------------------------------------

TRACKED_ZONES = {
    "Shanghai to Los Angeles": ["PZZ150", "PZZ155", "PZZ535"],  # Pacific offshore zones
    "Rotterdam to New York":   ["ANZ338", "ANZ335", "AMZ070"],  # Atlantic / North Sea zones
}

# Which NOAA event types we consider "significant" enough to trigger the agent
SIGNIFICANT_EVENT_TYPES = {
    "Special Marine Warning",
    "Marine Weather Statement",
    "Gale Warning",
    "Storm Warning",
    "Hurricane Force Wind Warning",
    "Tropical Storm Warning",
    "Dense Fog Advisory",
    "High Surf Advisory",
}

NOAA_BASE_URL = "https://api.weather.gov"
POLL_INTERVAL_SECONDS = 300  # Poll every 5 minutes

# ---------------------------------------------------------------------------
# In-memory dedup set (also backed by DB on startup — see _load_seen_ids)
# ---------------------------------------------------------------------------
_seen_event_ids: set[str] = set()
_poller_status: dict = {
    "running": False,
    "last_polled_at": None,
    "last_alert_found": None,
    "alerts_triggered": 0,
    "errors": 0,
}


# ---------------------------------------------------------------------------
# NOAA alert → our raw_event schema
# ---------------------------------------------------------------------------

def _noaa_alert_to_raw_event(alert: dict, route: str) -> dict:
    """
    Maps a NOAA GeoJSON alert feature → our internal raw_event dict.
    This is the only place NOAA field names appear.
    """
    props = alert.get("properties", {})
    return {
        "source": "NOAA",
        "vessel_id": "NOAA-AUTO",       # No specific vessel — route-wide alert
        "route": route,
        "description": props.get("headline", props.get("description", "Unknown maritime alert")),
        "event_type": props.get("event", "Marine Weather Alert"),
        "severity": props.get("severity", "Unknown"),
        "onset": props.get("onset", ""),
        "expires": props.get("expires", ""),
        "area": props.get("areaDesc", ""),
    }


# ---------------------------------------------------------------------------
# Deduplication — backed by the EventThreadDB table
# ---------------------------------------------------------------------------

async def _load_seen_ids():
    """Pre-populate the in-memory set from the DB so we survive restarts."""
    try:
        from ..models.database import AsyncSessionLocal
        from ..db import crud
        async with AsyncSessionLocal() as db:
            seen = await crud.get_all_event_ids(db)
            _seen_event_ids.update(seen)
            logger.info(f"[NOAA Poller] Loaded {len(seen)} known event IDs from DB.")
    except Exception as e:
        logger.warning(f"[NOAA Poller] Could not load seen IDs from DB (will re-detect on restart): {e}")


# ---------------------------------------------------------------------------
# Core poll logic
# ---------------------------------------------------------------------------

async def _fetch_alerts_for_zone(client: httpx.AsyncClient, zone_id: str) -> list:
    """Fetch active alerts for a single NOAA marine zone."""
    try:
        resp = await client.get(
            f"{NOAA_BASE_URL}/alerts/active",
            params={"zone": zone_id},
            timeout=15.0,
            headers={"User-Agent": "marga-supply-chain-agent/1.0 (contact@marga.dev)"},
        )
        resp.raise_for_status()
        return resp.json().get("features", [])
    except Exception as e:
        logger.warning(f"[NOAA Poller] Failed to fetch zone {zone_id}: {e}")
        return []


async def _trigger_agent(raw_event: dict, noaa_event_id: str):
    """
    Kick off the LangGraph agent for a detected NOAA event.
    Same flow as the manual /trigger_disruption endpoint.
    """
    from ..graph.builder import graph
    from ..db import crud
    from ..models.database import AsyncSessionLocal

    event_id = f"NOAA-{noaa_event_id[:12]}"
    thread_id = f"{event_id}-{str(uuid.uuid4())[:8]}"
    config = {"configurable": {"thread_id": thread_id}}

    # Persist thread mapping to DB
    try:
        async with AsyncSessionLocal() as db:
            await crud.save_thread(db, event_id, thread_id)
    except Exception as e:
        logger.warning(f"[NOAA Poller] Could not persist thread to DB: {e}")

    initial_state = {
        "event_id": event_id,
        "raw_event": raw_event,
    }

    logger.info(f"[NOAA Poller] Auto-triggering agent for event {event_id} (thread {thread_id})")
    _poller_status["last_alert_found"] = datetime.now(timezone.utc).isoformat()
    _poller_status["alerts_triggered"] += 1

    try:
        await graph.ainvoke(initial_state, config=config)
        logger.info(f"[NOAA Poller] Agent completed for event {event_id}")
    except Exception as e:
        logger.error(f"[NOAA Poller] Agent error for event {event_id}: {e}")


async def _poll_once():
    """Single poll cycle across all tracked zones."""
    async with httpx.AsyncClient() as client:
        for route, zone_ids in TRACKED_ZONES.items():
            for zone_id in zone_ids:
                alerts = await _fetch_alerts_for_zone(client, zone_id)
                for alert in alerts:
                    props = alert.get("properties", {})
                    noaa_id = props.get("id", "")
                    event_type = props.get("event", "")

                    # Skip already-seen or non-significant alerts
                    if noaa_id in _seen_event_ids:
                        continue
                    if event_type not in SIGNIFICANT_EVENT_TYPES:
                        continue

                    logger.info(
                        f"[NOAA Poller] New significant alert detected: "
                        f"'{event_type}' in zone {zone_id} (route: {route})"
                    )

                    _seen_event_ids.add(noaa_id)
                    raw_event = _noaa_alert_to_raw_event(alert, route)

                    # Fire agent as a separate task so the poll loop isn't blocked
                    asyncio.create_task(_trigger_agent(raw_event, noaa_id))


# ---------------------------------------------------------------------------
# Background polling loop
# ---------------------------------------------------------------------------

async def run_poller():
    """
    Main polling loop. Started as an asyncio background task in main.py.
    Runs forever until the application shuts down.
    """
    logger.info(f"[NOAA Poller] Starting. Will poll every {POLL_INTERVAL_SECONDS}s.")
    _poller_status["running"] = True

    # Pre-populate seen IDs from DB to avoid re-triggering on restart
    await _load_seen_ids()

    while True:
        try:
            _poller_status["last_polled_at"] = datetime.now(timezone.utc).isoformat()
            await _poll_once()
        except Exception as e:
            logger.error(f"[NOAA Poller] Unexpected error in poll cycle: {e}")
            _poller_status["errors"] += 1

        await asyncio.sleep(POLL_INTERVAL_SECONDS)


def get_status() -> dict:
    """Return current poller status (for the /events/polling/status endpoint)."""
    return {**_poller_status, "seen_event_count": len(_seen_event_ids)}
