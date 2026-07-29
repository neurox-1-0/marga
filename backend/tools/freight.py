"""
backend/tools/freight.py

LangChain tool that queries the Mock Freight API (port 8002) for alternative
routing quotes given an origin, destination, and cargo weight.

The mock API now models project44 Multi-Modal Rating API conventions:
  - Auth: OAuth2 client-credentials → Bearer token via POST /oauth/token
  - Endpoint: /quotes (internal bridge that runs the p44 pipeline + translation)

The tool's external signature and return shape are unchanged — only the
internal HTTP call now fetches a bearer token first and uses it on the
freight endpoint.
Falls back to an empty list on connection error.
"""

import os
import requests
from langchain_core.tools import tool
from typing import Dict, Any, List

FREIGHT_API_URL = os.getenv("FREIGHT_API_URL", "http://localhost:8002")

# project44 OAuth credentials — in production from secrets management
P44_CLIENT_ID = os.getenv("P44_CLIENT_ID", "mock_client_id")
P44_CLIENT_SECRET = os.getenv("P44_CLIENT_SECRET", "mock_client_secret")

_cached_token: str = ""


def _get_bearer_token() -> str:
    """
    Implements project44's OAuth2 client-credentials flow.
    Fetches a bearer token from /oauth/token.
    Caches the token for the lifetime of the process (good enough for a demo).
    """
    global _cached_token
    if _cached_token:
        return _cached_token

    resp = requests.post(
        f"{FREIGHT_API_URL}/oauth/token",
        params={"client_id": P44_CLIENT_ID, "client_secret": P44_CLIENT_SECRET},
        timeout=10,
    )
    resp.raise_for_status()
    _cached_token = resp.json().get("access_token", "")
    return _cached_token


def _freight_auth_headers() -> Dict[str, str]:
    """Build project44-style Authorization header: Bearer {token}"""
    token = _get_bearer_token()
    return {"Authorization": f"Bearer {token}"}


@tool
def get_freight_quotes(
    origin: str,
    destination: str,
    weight_kg: float = 50000.0,
) -> List[Dict[str, Any]]:
    """
    Gets alternative freight routing quotes from the freight API.
    Returns a list of quotes with carrier, mode, cost, and transit time.
    weight_kg defaults to 50,000 kg (a typical container load).
    """
    try:
        resp = requests.get(
            f"{FREIGHT_API_URL}/quotes",
            params={"origin": origin, "destination": destination, "weight_kg": weight_kg},
            headers=_freight_auth_headers(),
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("quotes", [])
    except requests.exceptions.ConnectionError:
        return [{"error": "Freight service unavailable (is mock_freight_api running on port 8002?)"}]
    except Exception as e:
        return [{"error": str(e)}]
