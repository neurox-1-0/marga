"""
backend/tools/freight.py

LangChain tool that queries the real Mock Freight API (port 8002) for
alternative routing quotes given an origin, destination, and cargo weight.
Falls back to an empty list on connection error.
"""

import requests
from langchain_core.tools import tool
from typing import Dict, Any, List

FREIGHT_API_URL = "http://localhost:8002"


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
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("quotes", [])
    except requests.exceptions.ConnectionError:
        return [{"error": "Freight service unavailable (is mock_freight_api running on port 8002?)"}]
    except Exception as e:
        return [{"error": str(e)}]
