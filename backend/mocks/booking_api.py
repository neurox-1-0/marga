"""
backend/mocks/booking_api.py — Booking confirmation HTTP service (port 8003)

Validates and confirms freight bookings. Called by the execute_node after approval.
Run with: python -m backend.mocks.booking_api
"""

import uuid
import uvicorn
from fastapi import FastAPI, HTTPException
from backend.schemas.mock_schemas import BookingRequest, BookingResponse

app = FastAPI(title="Booking API", description="Confirms approved freight reroute bookings.")


@app.post("/book", response_model=BookingResponse)
def book_freight(request: BookingRequest):
    if request.decision.event_id != request.event_id:
        raise HTTPException(status_code=400, detail="Decision event_id does not match request event_id")

    if request.decision.decision not in ["approved", "redirected"]:
        raise HTTPException(status_code=403, detail="Booking rejected: No valid approval decision provided")

    if request.decision.chosen_quote_id != request.quote_id:
        raise HTTPException(status_code=400, detail="Decision chosen_quote_id does not match request quote_id")

    booking_ref = f"BK-{uuid.uuid4().hex[:8].upper()}"

    return BookingResponse(
        booking_reference=booking_ref,
        status="confirmed",
        message=f"Successfully booked {len(request.po_ids)} POs on quote {request.quote_id}. Note: {request.decision.manager_note}",
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)
