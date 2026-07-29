"""
backend/tools/erp.py

LangChain tool that queries the real Mock ERP API (port 8001) for
Purchase Orders affected by a disrupted vessel/route.
Falls back to empty result on connection error so the graph doesn't crash
if the mock service isn't running.
"""

import requests
import os
from langchain_core.tools import tool
from typing import Dict, Any

ERP_API_URL = os.getenv("ERP_API_URL", "http://localhost:8001")


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
