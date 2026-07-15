from typing import List, Optional
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from shared.schemas import ERPExposureResponse, FreightQuote, CostComparison

# Simple assumed metrics
RISK_MULTIPLIER = 0.05      # Base risk coefficient per day
LOST_SALE_FACTOR = 0.50     # Margin lost if stockout occurs

def analyze_costs(exposure: ERPExposureResponse, delay_days: int, quotes: List[FreightQuote]) -> CostComparison:
    inventory_val = exposure.total_inventory_value_usd
    
    # Simple stockout cost calculation
    # Example logic: cost = value * delay * risk_multiplier * lost_sale_factor
    stockout_cost = inventory_val * delay_days * RISK_MULTIPLIER * LOST_SALE_FACTOR
    
    basis = (
        f"Inventory Value (${inventory_val:,.2f}) * "
        f"Delay ({delay_days} days) * "
        f"Risk Multiplier ({RISK_MULTIPLIER}) * "
        f"Lost Sale Factor ({LOST_SALE_FACTOR})"
    )
    
    best_option: Optional[FreightQuote] = None
    if quotes:
        # Find the cheapest quote
        best_option = min(quotes, key=lambda q: q.cost_usd)
        
    reroute_savings = 0.0
    recommendation = ""
    
    if best_option:
        # Calculate if rerouting is worth it
        reroute_savings = stockout_cost - best_option.cost_usd
        if reroute_savings > 0:
            recommendation = f"Reroute recommended using {best_option.carrier} ({best_option.mode}). Estimated savings: ${reroute_savings:,.2f} over doing nothing."
        else:
            recommendation = f"Do not reroute. Rerouting costs (${best_option.cost_usd:,.2f}) exceed projected stockout costs (${stockout_cost:,.2f})."
    else:
        recommendation = "No reroute options available."

    return CostComparison(
        stockout_cost_usd=stockout_cost,
        stockout_cost_basis=basis,
        best_reroute_option=best_option,
        reroute_savings_usd=reroute_savings,
        recommendation=recommendation
    )
