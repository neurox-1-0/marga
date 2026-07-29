"""
backend/mocks/erp_api.py — Mock ERP HTTP service (port 8001)

Models ERPNext/Frappe REST conventions:
  - Endpoint: GET /api/resource/Purchase Order
  - Auth:     Authorization: token {api_key}:{api_secret}
  - Filters:  JSON-encoded list of [field, operator, value] triples
  - Response: { "data": [ <ERPNext-shaped doc>, ... ] }

The internal translation function maps ERPNext field names → our PurchaseOrder
schema so everything downstream stays unchanged.
"""

import json
import uuid
import uvicorn
from pathlib import Path
from fastapi import FastAPI, Query, Header, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional

from backend.schemas.mock_schemas import ERPExposureResponse, PurchaseOrder

app = FastAPI(
    title="Mock ERP API (ERPNext conventions)",
    description="GET /api/resource/Purchase Order — mimics ERPNext/Frappe REST shape.",
)

DATA_PATH = Path(__file__).parent.parent.parent / "data" / "purchase_orders.json"

# ---------------------------------------------------------------------------
# Auth helper
# ---------------------------------------------------------------------------

def _check_auth(authorization: Optional[str]) -> None:
    """
    ERPNext uses:  Authorization: token {api_key}:{api_secret}
    We just verify the header is present and has the right format —
    no real key validation needed for a mock.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    if not authorization.startswith("token "):
        raise HTTPException(
            status_code=401,
            detail="Invalid auth format. Expected: Authorization: token {api_key}:{api_secret}",
        )
    token_part = authorization[len("token "):]
    if ":" not in token_part:
        raise HTTPException(
            status_code=401,
            detail="Invalid token format. Expected colon-separated key:secret",
        )


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def _load_docs():
    if not DATA_PATH.exists():
        return []
    with open(DATA_PATH, "r") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Translation layer: ERPNext doc → our internal PurchaseOrder schema
# ---------------------------------------------------------------------------

def _erpnext_doc_to_purchase_order(doc: dict) -> PurchaseOrder:
    """
    Maps an ERPNext-shaped Purchase Order document into our internal
    PurchaseOrder Pydantic model. This is the ONLY place the vendor
    field names appear — everything past this function uses our schema.
    """
    # Sum up total line value from the items child table
    items = doc.get("items", [])
    # Use first item's code/name as the SKU / product_name for our model
    first_item = items[0] if items else {}

    total_qty = sum(item.get("qty", 0) for item in items)
    # For multi-line POs, compute a weighted average rate
    total_value = sum(item.get("qty", 0) * item.get("rate", 0.0) for item in items)
    avg_rate = total_value / total_qty if total_qty else 0.0

    return PurchaseOrder(
        po_id=doc["name"],                                  # ERPNext uses "name" as PK
        sku=first_item.get("item_code", "UNKNOWN"),
        product_name=first_item.get("item_name", "Unknown Product"),
        quantity=total_qty,
        unit_value_usd=avg_rate,
        vessel_id=doc.get("custom_vessel_id", ""),
        route=doc.get("custom_route", ""),
        customer_order_ids=doc.get("custom_customer_order_ids", []),
        match_confidence=doc.get("custom_match_confidence", 1.0),
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/api/resource/Purchase Order")
def get_purchase_orders(
    filters: str = Query(default="[]", description='JSON-encoded filter triples, e.g. [["custom_vessel_id","=","Evergreen"]]'),
    fields: str = Query(default='["name"]', description='JSON-encoded list of field names to return'),
    authorization: Optional[str] = Header(default=None),
):
    """
    ERPNext-style document list endpoint.
    Returns matched Purchase Orders wrapped in the ERPNext `data` envelope.
    Internally translates to our PurchaseOrder schema and returns ERPExposureResponse
    via the /exposure helper used by the agent tool.
    """
    _check_auth(authorization)

    try:
        filter_list = json.loads(filters)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="'filters' must be a valid JSON array")

    docs = _load_docs()

    # Apply filters — each filter is [field, operator, value]
    # We support "=" and "like" operators for our mock
    matched_docs = []
    for doc in docs:
        # Only treat submitted (docstatus=1) documents as real active POs
        if doc.get("docstatus", 0) != 1:
            continue

        passes = True
        for f in filter_list:
            if len(f) != 3:
                continue
            field, operator, value = f
            doc_val = str(doc.get(field, "")).lower()
            filter_val = str(value).lower()

            if operator == "=":
                # Partial match to handle vessel naming variations
                if filter_val not in doc_val and doc_val not in filter_val:
                    passes = False
                    break
            elif operator == "like":
                # SQL LIKE — strip % wildcards for simple substring match
                filter_val = filter_val.strip("%")
                if filter_val not in doc_val:
                    passes = False
                    break

        if passes:
            matched_docs.append(doc)

    # Return the raw ERPNext-shaped envelope (vendor format)
    return JSONResponse(content={"data": matched_docs})


@app.get("/exposure")
def get_exposure_internal(
    vessel_id: str,
    route: str,
    authorization: Optional[str] = Header(default=None),
):
    """
    Internal helper endpoint used by the agent tool (backend/tools/erp.py).
    Applies ERPNext-style filters internally and returns our ERPExposureResponse schema.
    This is the bridge: it calls the ERPNext-style data pipeline and
    runs the translation layer before returning.
    """
    _check_auth(authorization)

    docs = _load_docs()
    matched_pos = []
    has_low_confidence = False

    for doc in docs:
        if doc.get("docstatus", 0) != 1:
            continue

        v_match = (
            vessel_id.lower() in doc.get("custom_vessel_id", "").lower()
            or doc.get("custom_vessel_id", "").lower() in vessel_id.lower()
        )
        r_match = route.lower() == doc.get("custom_route", "").lower()

        if v_match and r_match:
            po = _erpnext_doc_to_purchase_order(doc)
            matched_pos.append(po)
            if po.match_confidence < 1.0:
                has_low_confidence = True

    total_value = sum(po.quantity * po.unit_value_usd for po in matched_pos)
    note = (
        "WARNING: Some purchase orders matched with low confidence due to discrepancies in vessel naming."
        if has_low_confidence
        else None
    )

    return ERPExposureResponse(
        matched_pos=matched_pos,
        total_inventory_value_usd=total_value,
        data_quality_note=note,
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
