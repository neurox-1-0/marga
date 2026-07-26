from langchain_core.tools import tool
from typing import Dict, Any

@tool
def calculate_stockout_cost(inventory_value: float, delay_days: int) -> Dict[str, Any]:
    """Calculates estimated stockout costs based on delay and inventory value."""
    # Simplified formula for demo
    daily_penalty_rate = 0.05
    estimated_cost = inventory_value * daily_penalty_rate * delay_days
    return {
        "stockout_cost_usd": estimated_cost,
        "recommendation": "High risk of stockout. Expedite via air freight." if estimated_cost > 100000 else "Accept delay, ocean freight acceptable."
    }
