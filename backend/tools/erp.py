from langchain_core.tools import tool
import json
from typing import Dict, Any

@tool
def query_erp(vessel_id: str) -> Dict[str, Any]:
    """Queries the ERP system for Purchase Orders affected by a given vessel."""
    # Mock ERP data for demo
    if vessel_id == "V-559":
        return {
            "status": "success",
            "matched_pos": ["PO-001", "PO-002"],
            "total_inventory_value_usd": 1500000.50
        }
    return {"status": "not_found", "matched_pos": [], "total_inventory_value_usd": 0.0}
