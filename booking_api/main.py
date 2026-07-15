import uuid
from fastapi import FastAPI, HTTPException
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from shared.schemas import BookingRequest, BookingResponse

app = FastAPI(title="Booking API")

@app.post("/book", response_model=BookingResponse)
def book_freight(request: BookingRequest):
    # Enforce structural rule: decision must be present and valid
    if request.decision.event_id != request.event_id:
        raise HTTPException(status_code=400, detail="Decision event_id does not match request event_id")
    
    if request.decision.decision not in ["approved", "redirected"]:
        raise HTTPException(status_code=403, detail="Booking rejected: No valid approval decision provided")
        
    if request.decision.chosen_quote_id != request.quote_id:
        raise HTTPException(status_code=400, detail="Decision chosen_quote_id does not match request quote_id")

    # In a real system, we would book with the external API here.
    # For the mock, we just return success.
    
    booking_ref = f"BK-{uuid.uuid4().hex[:8].upper()}"
    
    return BookingResponse(
        booking_reference=booking_ref,
        status="confirmed",
        message=f"Successfully booked {len(request.po_ids)} POs on quote {request.quote_id}. Decision note: {request.decision.manager_note}"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
