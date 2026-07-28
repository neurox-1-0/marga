from langchain_core.tools import tool
from typing import Dict, Any, List

@tool
def get_freight_quotes(origin: str, destination: str) -> List[Dict[str, Any]]:
    """Gets alternative freight quotes for a rerouted shipment."""
    return [
        {
            "quote_id": "Q-001",
            "carrier": "FedEx",
            "mode": "Air",
            "cost_usd": 45000.00,
            "transit_days": 3
        },
        {
            "quote_id": "Q-002",
            "carrier": "Maersk",
            "mode": "Sea (Alternative Route)",
            "cost_usd": 15000.00,
            "transit_days": 18
        }
    ]
