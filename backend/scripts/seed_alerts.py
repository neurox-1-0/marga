import asyncio
import sys
import os

# Add the root directory to sys.path so we can import backend modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from datetime import datetime, timezone
from backend.models.database import AsyncSessionLocal
from backend.schemas.api import ApprovalCard, EventSchema, ExposureSchema, CostAnalysisSchema, FreightOptionsSchema, FreightQuoteSchema
from backend.db.crud import save_card

async def seed():
    async with AsyncSessionLocal() as db:
        # Mock 1: Suez Blockage
        card1 = ApprovalCard(
            event=EventSchema(event_id="MOCK-1", detected_at=datetime.now(timezone.utc), source="Reuters", vessel_id="Ever-Given", route="Shenzhen to Rotterdam", description="Suez Canal completely blocked by grounded vessel."),
            exposure=ExposureSchema(matched_pos=["PO-101", "PO-102"], total_inventory_value_usd=12500000),
            cost_analysis=CostAnalysisSchema(stockout_cost_usd=850000, reroute_savings_usd=230000, recommendation="Reroute via Cape of Good Hope"),
            freight_options=FreightOptionsSchema(quotes=[FreightQuoteSchema(quote_id="Q1", carrier="Maersk (Ocean)", mode="ocean", cost_usd=45000, transit_days=18)]),
            status="approved"
        )
        
        # Mock 2: Port Strike (Pending)
        card2 = ApprovalCard(
            event=EventSchema(event_id="MOCK-2", detected_at=datetime.now(timezone.utc), source="ILWU", vessel_id="Sea-Explorer", route="Shanghai to Long Beach", description="Flash port worker strike initiated at Long Beach terminal."),
            exposure=ExposureSchema(matched_pos=["PO-401", "PO-402", "PO-403"], total_inventory_value_usd=4500000),
            cost_analysis=CostAnalysisSchema(stockout_cost_usd=1200000, reroute_savings_usd=800000, recommendation="Divert to Port of Oakland"),
            freight_options=FreightOptionsSchema(quotes=[FreightQuoteSchema(quote_id="Q2", carrier="MSC (Ocean)", mode="ocean", cost_usd=12000, transit_days=4)]),
            status="pending"
        )
        
        # Mock 3: Typhoon Warning
        card3 = ApprovalCard(
            event=EventSchema(event_id="MOCK-3", detected_at=datetime.now(timezone.utc), source="NOAA", vessel_id="Pacific-Trader", route="Los Angeles to Tokyo", description="Category 4 Typhoon warning issued for Philippine Sea."),
            exposure=ExposureSchema(matched_pos=["PO-205"], total_inventory_value_usd=840000),
            cost_analysis=CostAnalysisSchema(stockout_cost_usd=95000, reroute_savings_usd=-15000, recommendation="Hold in port until storm passes"),
            freight_options=FreightOptionsSchema(quotes=[]),
            status="rejected"
        )
        
        # Mock 4: Baltic Ice
        card4 = ApprovalCard(
            event=EventSchema(event_id="MOCK-4", detected_at=datetime.now(timezone.utc), source="Bloomberg", vessel_id="Baltic-Queen", route="Hamburg to New York", description="Severe unexpected ice conditions halting Baltic Sea traffic."),
            exposure=ExposureSchema(matched_pos=["PO-801"], total_inventory_value_usd=210000),
            cost_analysis=CostAnalysisSchema(stockout_cost_usd=12000, reroute_savings_usd=-45000, recommendation="Accept delay"),
            freight_options=FreightOptionsSchema(quotes=[FreightQuoteSchema(quote_id="Q3", carrier="AirBridge (Air)", mode="air", cost_usd=48000, transit_days=2)]),
            status="rejected"
        )
        
        # Mock 5: Geopolitical Tension
        card5 = ApprovalCard(
            event=EventSchema(event_id="MOCK-5", detected_at=datetime.now(timezone.utc), source="Lloyds", vessel_id="Gulf-Star", route="Dubai to Singapore", description="Geopolitical tension forcing route closures in the Strait of Hormuz."),
            exposure=ExposureSchema(matched_pos=["PO-901", "PO-902"], total_inventory_value_usd=8800000),
            cost_analysis=CostAnalysisSchema(stockout_cost_usd=4200000, reroute_savings_usd=1100000, recommendation="Immediate Air Freight Reroute"),
            freight_options=FreightOptionsSchema(quotes=[FreightQuoteSchema(quote_id="Q4", carrier="Emirates SkyCargo", mode="air", cost_usd=185000, transit_days=1)]),
            status="approved"
        )
        
        for c in [card1, card2, card3, card4, card5]:
            await save_card(db, c)
            
        print("Successfully seeded 5 mock scenarios to Active Alerts!")

if __name__ == "__main__":
    asyncio.run(seed())
