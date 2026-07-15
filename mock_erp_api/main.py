import json
from pathlib import Path
from fastapi import FastAPI, Query
from typing import Optional
import sys

# Add root directory to path to import shared schemas
sys.path.append(str(Path(__file__).parent.parent))
from shared.schemas import ERPExposureResponse, PurchaseOrder

app = FastAPI(title="Mock ERP API")

def load_pos():
    data_path = Path(__file__).parent.parent / "data" / "purchase_orders.json"
    if not data_path.exists():
        return []
    with open(data_path, "r") as f:
        return json.load(f)

@app.get("/exposure", response_model=ERPExposureResponse)
def get_exposure(vessel_id: str, route: str):
    pos_data = load_pos()
    matched_pos = []
    has_low_confidence = False

    for po_dict in pos_data:
        # Match logic: if vessel_id and route match. Also if route matches and vessel is a partial match.
        v_match = vessel_id.lower() in po_dict["vessel_id"].lower() or po_dict["vessel_id"].lower() in vessel_id.lower()
        r_match = route.lower() == po_dict["route"].lower()
        
        if v_match and r_match:
            po = PurchaseOrder(**po_dict)
            matched_pos.append(po)
            if po.match_confidence < 1.0:
                has_low_confidence = True

    total_value = sum(po.quantity * po.unit_value_usd for po in matched_pos)
    
    note = None
    if has_low_confidence:
        note = "WARNING: Some purchase orders matched with low confidence due to discrepancies in vessel naming."

    return ERPExposureResponse(
        matched_pos=matched_pos,
        total_inventory_value_usd=total_value,
        data_quality_note=note
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
