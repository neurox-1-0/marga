from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class DisruptionEvent(BaseModel):
    event_id: str
    source: str
    vessel_id: Optional[str] = None
    route: Optional[str] = None
    description: str
    delay_days_estimate: int
    confidence: float
    detected_at: datetime

class PurchaseOrder(BaseModel):
    po_id: str
    sku: str
    product_name: str
    quantity: int
    unit_value_usd: float
    vessel_id: str
    route: str
    customer_order_ids: List[str]
    match_confidence: float

class ERPExposureResponse(BaseModel):
    matched_pos: List[PurchaseOrder]
    total_inventory_value_usd: float
    data_quality_note: Optional[str] = None

class FreightQuote(BaseModel):
    quote_id: str
    mode: str
    carrier: str
    cost_usd: float
    transit_days: int

class FreightQuoteResponse(BaseModel):
    origin: str
    destination: str
    quotes: List[FreightQuote]

class CostComparison(BaseModel):
    stockout_cost_usd: float
    stockout_cost_basis: str
    best_reroute_option: Optional[FreightQuote]
    reroute_savings_usd: float
    recommendation: str

class ApprovalCard(BaseModel):
    event: DisruptionEvent
    exposure: ERPExposureResponse
    freight_options: FreightQuoteResponse
    cost_analysis: CostComparison
    status: str = "pending"  # pending, approved, rejected, redirected
    chosen_quote_id: Optional[str] = None

class ApprovalDecision(BaseModel):
    event_id: str
    decision: str  # approved, rejected, redirected
    chosen_quote_id: Optional[str] = None
    manager_note: Optional[str] = None

class BookingRequest(BaseModel):
    event_id: str
    po_ids: List[str]
    quote_id: str
    decision: ApprovalDecision  # structurally enforcing decision inclusion

class BookingResponse(BaseModel):
    booking_reference: str
    status: str
    message: str
