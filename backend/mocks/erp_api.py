"""
backend/mocks/erp_api.py — Mock ERP HTTP service (port 8001)

Serves purchase order data from data/purchase_orders.json.
Run with: python -m backend.mocks.erp_api
"""

import json
import uvicorn
from pathlib import Path
from fastapi import FastAPI
from backend.schemas.mock_schemas import ERPExposureResponse, PurchaseOrder

app = FastAPI(title="Mock ERP API", description="Returns POs affected by a vessel/route disruption.")

DATA_PATH = Path(__file__).parent.parent.parent / "data" / "purchase_orders.json"


def load_pos():
    if not DATA_PATH.exists():
        return []
    with open(DATA_PATH, "r") as f:
        return json.load(f)


@app.get("/exposure", response_model=ERPExposureResponse)
def get_exposure(vessel_id: str, route: str):
    pos_data = load_pos()
    matched_pos = []
    has_low_confidence = False

    for po_dict in pos_data:
        v_match = vessel_id.lower() in po_dict["vessel_id"].lower() or po_dict["vessel_id"].lower() in vessel_id.lower()
        r_match = route.lower() == po_dict["route"].lower()

        if v_match and r_match:
            po = PurchaseOrder(**po_dict)
            matched_pos.append(po)
            if po.match_confidence < 1.0:
                has_low_confidence = True

    total_value = sum(po.quantity * po.unit_value_usd for po in matched_pos)
    note = (
        "WARNING: Some purchase orders matched with low confidence due to discrepancies in vessel naming."
        if has_low_confidence else None
    )

    return ERPExposureResponse(
        matched_pos=matched_pos,
        total_inventory_value_usd=total_value,
        data_quality_note=note,
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
