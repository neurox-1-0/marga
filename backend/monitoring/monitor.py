"""
backend/monitoring/monitor.py — Disruption event sourcing

Fetches live weather-based disruption events from the NOAA API, or
generates a hardcoded demo event for reliable hackathon demos.
"""

import requests
import datetime
import uuid
from typing import List
from backend.schemas.mock_schemas import DisruptionEvent

NOAA_ALERTS_URL = "https://api.weather.gov/alerts/active"
KEYWORDS = ["typhoon", "storm", "flood", "hurricane", "tornado"]


def fetch_live_disruptions() -> List[DisruptionEvent]:
    events = []
    try:
        response = requests.get(NOAA_ALERTS_URL, timeout=10)
        response.raise_for_status()
        data = response.json()

        for feature in data.get("features", []):
            props = feature.get("properties", {})
            headline = props.get("headline", "").lower()
            desc = props.get("description", "").lower()

            if any(kw in headline or kw in desc for kw in KEYWORDS):
                events.append(DisruptionEvent(
                    event_id=f"EVT-{uuid.uuid4().hex[:8].upper()}",
                    source=f"NOAA Weather Alert: {props.get('event', 'Weather Event')}",
                    description=props.get("headline", "Severe weather detected."),
                    delay_days_estimate=3,
                    confidence=0.8,
                    detected_at=datetime.datetime.now(datetime.timezone.utc),
                ))
                if len(events) >= 3:
                    break
    except Exception as e:
        print(f"Error fetching NOAA alerts: {e}")

    return events


def manual_trigger() -> List[DisruptionEvent]:
    """Returns a hardcoded disruption event for reliable demoing."""
    return [
        DisruptionEvent(
            event_id=f"EVT-{uuid.uuid4().hex[:8].upper()}",
            source="Maritime Authority Alert",
            vessel_id="Evergreen",
            route="Shanghai to Los Angeles",
            description=(
                "Category 5 Typhoon forming in the Pacific, expected to intersect "
                "the planned routing for Vessel Evergreen."
            ),
            delay_days_estimate=7,
            confidence=0.95,
            detected_at=datetime.datetime.now(datetime.timezone.utc),
        )
    ]
