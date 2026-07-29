"""
backend/mocks/freight_api.py — Mock Freight HTTP service (port 8002)

Models project44 Multi-Modal Rating & Booking API conventions:
  - OAuth2 client-credentials: POST /oauth/token → Bearer token
  - Rate request:  POST /services/rating/v1/rate-requests
  - Retrieve:      GET  /services/rating/v1/rate-requests/{id}
  - Book:          POST /services/booking/v1/bookings
  - Get booking:   GET  /services/booking/v1/bookings/{bookingId}
  - Cancel:        POST /services/booking/v1/bookings/{bookingId}/cancellations

Auth on rating/booking endpoints: Authorization: Bearer {token}
Response shape for quotes nests cost under totalCharge.amount/currency.

The internal translation function maps project44-shaped quotes → our
FreightQuote schema so everything downstream stays unchanged.
"""

import json
import uuid
import uvicorn
from datetime import datetime
from pathlib import Path
from typing import Optional, List
from fastapi import FastAPI, Header, HTTPException, Path as FPath
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from backend.schemas.mock_schemas import FreightQuote, FreightQuoteResponse

app = FastAPI(
    title="Mock Freight API (project44 conventions)",
    description="Mimics project44 Multi-Modal Rating & Booking API shape.",
)

DATA_PATH = Path(__file__).parent.parent.parent / "data" / "freight_rates.json"

# In-memory stores for mock state
_rate_requests: dict = {}
_bookings: dict = {}

# Static dummy token (no real validation — keeps auth *flow* realistic)
DUMMY_TOKEN = "p44_mock_access_token_abc123"


# ---------------------------------------------------------------------------
# Pydantic models matching project44 request shapes
# ---------------------------------------------------------------------------

class P44Location(BaseModel):
    city: str
    country: Optional[str] = None

class P44Stop(BaseModel):
    location: P44Location
    stopType: str  # "PICKUP" or "DELIVERY"

class P44Shipment(BaseModel):
    stops: List[P44Stop]

class P44Identifier(BaseModel):
    type: str   # e.g. "PURCHASE_ORDER"
    value: str

class P44RateRequest(BaseModel):
    identifiers: List[P44Identifier] = []
    shipment: P44Shipment
    expirationDateTime: Optional[str] = None

class P44BookingRequest(BaseModel):
    rateRequestId: str
    quoteId: str
    identifiers: List[P44Identifier] = []
    managerNote: Optional[str] = None


# ---------------------------------------------------------------------------
# Auth helper
# ---------------------------------------------------------------------------

def _check_bearer(authorization: Optional[str]) -> None:
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Expected: Authorization: Bearer {token}")
    token = authorization[len("Bearer "):]
    if token != DUMMY_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid bearer token")


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def _load_rates():
    if not DATA_PATH.exists():
        return []
    with open(DATA_PATH, "r") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Translation layer: project44 quote → our internal FreightQuote schema
# ---------------------------------------------------------------------------

def _p44_quote_to_freight_quote(quote: dict, weight_kg: float) -> FreightQuote:
    """
    Maps a project44-shaped quote object into our internal FreightQuote
    Pydantic model. This is the ONLY place the project44 field names
    appear — everything past this function uses our schema.
    """
    charge = quote.get("totalCharge", {})
    rate_per_kg = charge.get("amount", 0.0)
    total_cost = rate_per_kg * weight_kg

    # Map project44 mode codes to our readable strings
    mode_map = {"AIR": "air", "OCN": "alt_ocean", "LTL": "ltl", "FTL": "ftl"}
    mode_raw = quote.get("mode", "AIR")
    mode = mode_map.get(mode_raw, mode_raw.lower())

    # Map capacityProviderId to a human-readable carrier name
    carrier_map = {
        "FEDEX": "FedEx",
        "DHL": "DHL",
        "MAERSK_REROUTE": "Maersk (Reroute)",
    }
    provider_id = quote.get("capacityProviderId", "UNKNOWN")
    carrier = carrier_map.get(provider_id, provider_id)

    return FreightQuote(
        quote_id=quote.get("quoteId", f"QT-{uuid.uuid4().hex[:8].upper()}"),
        mode=mode,
        carrier=carrier,
        cost_usd=round(total_cost, 2),
        transit_days=quote.get("transitDays", 0),
    )


def _build_p44_quotes(rates: list, origin: str, destination: str, weight_kg: float) -> list:
    """Build project44-shaped quote objects from our raw rate data."""
    quotes = []
    for rate in rates:
        if (
            origin.lower() in rate.get("origin", "").lower()
            and destination.lower() in rate.get("destination", "").lower()
        ):
            quotes.append({
                "quoteId": f"QT-{uuid.uuid4().hex[:8].upper()}",
                "capacityProviderId": rate.get("capacityProviderId", "UNKNOWN"),
                "mode": rate.get("mode", "AIR"),
                "totalCharge": rate.get("totalCharge", {"amount": 0.0, "currency": "USD"}),
                "transitDays": rate.get("transitDays", 0),
            })
    return quotes


# ---------------------------------------------------------------------------
# OAuth endpoint
# ---------------------------------------------------------------------------

@app.post("/oauth/token")
def get_oauth_token(client_id: str = "", client_secret: str = ""):
    """
    project44 OAuth2 client-credentials flow.
    Returns a static dummy Bearer token — no real validation.
    Keeps the auth *flow* realistic for demo purposes.
    """
    return {
        "access_token": DUMMY_TOKEN,
        "token_type": "Bearer",
        "expires_in": 3600,
        "scope": "rating booking",
    }


# ---------------------------------------------------------------------------
# Rating endpoints
# ---------------------------------------------------------------------------

@app.post("/services/rating/v1/rate-requests")
def submit_rate_request(
    body: P44RateRequest,
    authorization: Optional[str] = Header(default=None),
):
    """
    Submit a rate request. project44 supports async polling — our mock
    resolves synchronously and stores results for GET retrieval.
    """
    _check_bearer(authorization)

    # Extract origin/destination from shipment stops
    origin = ""
    destination = ""
    for stop in body.shipment.stops:
        if stop.stopType == "PICKUP":
            origin = stop.location.city
        elif stop.stopType == "DELIVERY":
            destination = stop.location.city

    rates = _load_rates()
    # Default weight if not derivable from request
    weight_kg = 50000.0

    raw_quotes = _build_p44_quotes(rates, origin, destination, weight_kg)

    request_id = f"rate-req-{uuid.uuid4().hex[:8]}"
    now = datetime.utcnow().isoformat() + "Z"

    result = {
        "id": request_id,
        "createdDate": now,
        "lastModified": now,
        "status": "COMPLETED",
        "quotes": raw_quotes,
        "_meta": {"origin": origin, "destination": destination, "weight_kg": weight_kg},
    }

    _rate_requests[request_id] = result
    return JSONResponse(content=result)


@app.get("/services/rating/v1/rate-requests/{rate_request_id}")
def get_rate_request(
    rate_request_id: str = FPath(...),
    authorization: Optional[str] = Header(default=None),
):
    """Retrieve quotes for a previously submitted rate request."""
    _check_bearer(authorization)

    result = _rate_requests.get(rate_request_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Rate request '{rate_request_id}' not found")
    return JSONResponse(content=result)


# ---------------------------------------------------------------------------
# Internal helper endpoint (used by backend/tools/freight.py)
# Wraps the project44 pipeline and translates to our FreightQuoteResponse.
# ---------------------------------------------------------------------------

@app.get("/quotes")
def get_quotes_internal(
    origin: str,
    destination: str,
    weight_kg: float = 50000.0,
    authorization: Optional[str] = Header(default=None),
):
    """
    Internal bridge endpoint called by the agent tool.
    Runs the project44-shaped pipeline and translates the response
    into our FreightQuoteResponse schema.
    """
    _check_bearer(authorization)

    rates = _load_rates()
    raw_quotes = _build_p44_quotes(rates, origin, destination, weight_kg)

    internal_quotes = [
        _p44_quote_to_freight_quote(q, weight_kg) for q in raw_quotes
    ]

    return FreightQuoteResponse(origin=origin, destination=destination, quotes=internal_quotes)


# ---------------------------------------------------------------------------
# Booking endpoints
# ---------------------------------------------------------------------------

@app.post("/services/booking/v1/bookings")
def create_booking(
    body: P44BookingRequest,
    authorization: Optional[str] = Header(default=None),
):
    """Confirm a booking from a chosen quote."""
    _check_bearer(authorization)

    rate_req = _rate_requests.get(body.rateRequestId)
    if not rate_req:
        raise HTTPException(status_code=404, detail=f"Rate request '{body.rateRequestId}' not found")

    booking_id = f"BK-{uuid.uuid4().hex[:8].upper()}"
    now = datetime.utcnow().isoformat() + "Z"

    booking = {
        "bookingId": booking_id,
        "status": "CONFIRMED",
        "createdDate": now,
        "rateRequestId": body.rateRequestId,
        "quoteId": body.quoteId,
        "managerNote": body.managerNote,
    }
    _bookings[booking_id] = booking
    return JSONResponse(content=booking)


@app.get("/services/booking/v1/bookings/{booking_id}")
def get_booking(
    booking_id: str = FPath(...),
    authorization: Optional[str] = Header(default=None),
):
    """Retrieve booking status."""
    _check_bearer(authorization)

    booking = _bookings.get(booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail=f"Booking '{booking_id}' not found")
    return JSONResponse(content=booking)


@app.post("/services/booking/v1/bookings/{booking_id}/cancellations")
def cancel_booking(
    booking_id: str = FPath(...),
    authorization: Optional[str] = Header(default=None),
):
    """Cancel an existing booking."""
    _check_bearer(authorization)

    booking = _bookings.get(booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail=f"Booking '{booking_id}' not found")

    booking["status"] = "CANCELLED"
    now = datetime.utcnow().isoformat() + "Z"
    return JSONResponse(content={"bookingId": booking_id, "status": "CANCELLED", "cancelledDate": now})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
