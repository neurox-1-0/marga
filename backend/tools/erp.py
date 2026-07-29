"""
backend/tools/erp.py

LangChain tool that queries the Mock ERP API (port 8001) for Purchase Orders
affected by a disrupted vessel/route.

The mock API now models ERPNext/Frappe REST conventions:
  - Auth: Authorization: token {api_key}:{api_secret}
  - Endpoint: /exposure (internal bridge that applies ERPNext-style filtering)

The tool's external signature and return shape are unchanged — only the
internal HTTP call now uses the ERPNext auth header pattern.
Falls back to empty result on connection error so the graph doesn't crash.
"""

import os
import requests
from langchain_core.tools import tool
from typing import Dict, Any

ERP_API_URL = os.getenv("ERP_API_URL", "http://localhost:8001")

# ERPNext auth credentials — in production these would come from secrets management
ERP_API_KEY = os.getenv("ERP_API_KEY", "mock_api_key")
ERP_API_SECRET = os.getenv("ERP_API_SECRET", "mock_api_secret")


def _erp_auth_headers() -> Dict[str, str]:
    """Build ERPNext-style Authorization header: token {key}:{secret}"""
    return {"Authorization": f"token {ERP_API_KEY}:{ERP_API_SECRET}"}


@tool
def query_erp(vessel_id: str, route: str = "Suez") -> Dict[str, Any]:
    """
    Queries the ERP system for Purchase Orders affected by a given vessel and route.
    Returns matched PO IDs and the total inventory value at risk.
    """
    try:
        resp = requests.get(
            f"{ERP_API_URL}/exposure",
            params={"vessel_id": vessel_id, "route": route},
            headers=_erp_auth_headers(),
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()

        # Extract just the PO IDs for the agent state (keeps state lightweight)
        po_ids = [po["po_id"] for po in data.get("matched_pos", [])]

        return {
            "status": "success",
            "matched_pos": po_ids,
            "total_inventory_value_usd": data.get("total_inventory_value_usd", 0.0),
            "data_quality_note": data.get("data_quality_note"),
        }
    except requests.exceptions.ConnectionError:
        return {
            "status": "error",
            "matched_pos": [],
            "total_inventory_value_usd": 0.0,
            "error": "ERP service unavailable (is mock_erp_api running on port 8001?)",
        }
    except Exception as e:
        return {
            "status": "error",
            "matched_pos": [],
            "total_inventory_value_usd": 0.0,
            "error": str(e),
        }
