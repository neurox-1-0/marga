import json
from pathlib import Path

def generate_data():
    data_dir = Path(__file__).parent
    
    pos = [
        {
            "po_id": "PO-1001",
            "sku": "ELEC-001",
            "product_name": "High-End GPUs",
            "quantity": 500,
            "unit_value_usd": 1200.0,
            "vessel_id": "Evergreen",
            "route": "Shanghai to Los Angeles",
            "customer_order_ids": ["CO-991", "CO-992"],
            "match_confidence": 1.0
        },
        {
            "po_id": "PO-1002",
            "sku": "ELEC-002",
            "product_name": "Smartphones",
            "quantity": 2000,
            "unit_value_usd": 800.0,
            "vessel_id": "Evergreen",
            "route": "Shanghai to Los Angeles",
            "customer_order_ids": ["CO-993"],
            "match_confidence": 1.0
        },
        {
            "po_id": "PO-1003",
            "sku": "ACC-001",
            "product_name": "Phone Cases",
            "quantity": 10000,
            "unit_value_usd": 15.0,
            "vessel_id": "Evergreen",
            "route": "Shanghai to Los Angeles",
            "customer_order_ids": [],
            "match_confidence": 1.0
        },
        {
            "po_id": "PO-1004",
            "sku": "ELEC-003",
            "product_name": "Laptops",
            "quantity": 300,
            "unit_value_usd": 1500.0,
            "vessel_id": "Evergreen-V2",
            "route": "Shanghai to Los Angeles",
            "customer_order_ids": ["CO-994", "CO-995"],
            "match_confidence": 0.6  # Intentionally low for ambiguity demo
        },
        {
            "po_id": "PO-2001",
            "sku": "FURN-001",
            "product_name": "Office Chairs",
            "quantity": 100,
            "unit_value_usd": 150.0,
            "vessel_id": "MSC-Maersk",
            "route": "Rotterdam to New York",
            "customer_order_ids": ["CO-881"],
            "match_confidence": 1.0
        }
    ]

    with open(data_dir / "purchase_orders.json", "w") as f:
        json.dump(pos, f, indent=4)
        
    freight_rates = [
        {
            "origin": "Shanghai",
            "destination": "Los Angeles",
            "mode": "air",
            "carrier": "FedEx",
            "rate_per_kg_usd": 8.50,
            "transit_days": 2
        },
        {
            "origin": "Shanghai",
            "destination": "Los Angeles",
            "mode": "air",
            "carrier": "DHL",
            "rate_per_kg_usd": 9.00,
            "transit_days": 1
        },
        {
            "origin": "Shanghai",
            "destination": "Los Angeles",
            "mode": "alt_ocean",
            "carrier": "Maersk (Reroute)",
            "rate_per_kg_usd": 2.10,
            "transit_days": 14
        }
    ]

    with open(data_dir / "freight_rates.json", "w") as f:
        json.dump(freight_rates, f, indent=4)

    print(f"Generated synthetic data in {data_dir}")

if __name__ == "__main__":
    generate_data()
