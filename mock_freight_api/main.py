import json
import uuid
from pathlib import Path
from fastapi import FastAPI, Query
import sys

sys.path.append(str(Path(__file__).parent.parent))
from shared.schemas import FreightQuoteResponse, FreightQuote

app = FastAPI(title="Mock Freight API")

def load_rates():
    data_path = Path(__file__).parent.parent / "data" / "freight_rates.json"
    if not data_path.exists():
        return []
    with open(data_path, "r") as f:
        return json.load(f)

@app.get("/quotes", response_model=FreightQuoteResponse)
def get_quotes(origin: str, destination: str, weight_kg: float):
    rates_data = load_rates()
    quotes = []
    
    for rate in rates_data:
        # Simple match
        if origin.lower() in rate["origin"].lower() and destination.lower() in rate["destination"].lower():
            cost = rate["rate_per_kg_usd"] * weight_kg
            q = FreightQuote(
                quote_id=f"QT-{uuid.uuid4().hex[:8].upper()}",
                mode=rate["mode"],
                carrier=rate["carrier"],
                cost_usd=cost,
                transit_days=rate["transit_days"]
            )
            quotes.append(q)

    return FreightQuoteResponse(
        origin=origin,
        destination=destination,
        quotes=quotes
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
