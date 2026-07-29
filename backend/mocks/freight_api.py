"""
backend/mocks/freight_api.py — Mock Freight HTTP service (port 8002)

Serves freight quotes from data/freight_rates.json.
Run with: python -m backend.mocks.freight_api
"""

import json
import uuid
import uvicorn
from pathlib import Path
from fastapi import FastAPI
from backend.schemas.mock_schemas import FreightQuoteResponse, FreightQuote

app = FastAPI(title="Mock Freight API", description="Returns alternative freight routing quotes.")

DATA_PATH = Path(__file__).parent.parent.parent / "data" / "freight_rates.json"


def load_rates():
    if not DATA_PATH.exists():
        return []
    with open(DATA_PATH, "r") as f:
        return json.load(f)


@app.get("/quotes", response_model=FreightQuoteResponse)
def get_quotes(origin: str, destination: str, weight_kg: float):
    rates_data = load_rates()
    quotes = []

    for rate in rates_data:
        if origin.lower() in rate["origin"].lower() and destination.lower() in rate["destination"].lower():
            cost = rate["rate_per_kg_usd"] * weight_kg
            quotes.append(FreightQuote(
                quote_id=f"QT-{uuid.uuid4().hex[:8].upper()}",
                mode=rate["mode"],
                carrier=rate["carrier"],
                cost_usd=cost,
                transit_days=rate["transit_days"],
            ))

    return FreightQuoteResponse(origin=origin, destination=destination, quotes=quotes)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
