"""
Map router — serves dynamic route and port data derived from the actual
purchase_orders.json data file. No external API keys required.
"""
from fastapi import APIRouter
import json
import pathlib

router = APIRouter(prefix="/map", tags=["Map"])

# ---------------------------------------------------------------------------
# Known port coordinates (expanded registry)
# [longitude, latitude] — matches deck.gl convention
# ---------------------------------------------------------------------------
PORT_REGISTRY: dict = {
    # Asia-Pacific
    "Shanghai":   {"name": "Port of Shanghai",   "code": "CNSHA", "coords": [121.47, 31.23],   "region": "Asia"},
    "Shenzhen":   {"name": "Port of Shenzhen",    "code": "CNSZX", "coords": [114.12, 22.52],   "region": "Asia"},
    "Guangzhou":  {"name": "Port of Guangzhou",   "code": "CNGUZ", "coords": [113.26, 23.12],   "region": "Asia"},
    "Ningbo":     {"name": "Port of Ningbo",      "code": "CNNBO", "coords": [121.55, 29.87],   "region": "Asia"},
    "Tianjin":    {"name": "Port of Tianjin",     "code": "CNTXG", "coords": [117.72, 38.98],   "region": "Asia"},
    "Busan":      {"name": "Port of Busan",       "code": "KRPUS", "coords": [129.04, 35.10],   "region": "Asia"},
    "Tokyo":      {"name": "Port of Tokyo",       "code": "JPTYO", "coords": [139.77, 35.62],   "region": "Asia"},
    "Singapore":  {"name": "Port of Singapore",   "code": "SGSIN", "coords": [103.82, 1.27],    "region": "Asia"},
    "Hong Kong":  {"name": "Port of Hong Kong",   "code": "HKHKG", "coords": [114.17, 22.30],   "region": "Asia"},
    # Middle East
    "Dubai":      {"name": "Port of Jebel Ali",   "code": "AEJEA", "coords": [55.01, 24.98],    "region": "Middle East"},
    "Suez":       {"name": "Suez Canal Hub",      "code": "EGSUE", "coords": [32.33, 30.57],    "region": "Middle East"},
    # Europe
    "Rotterdam":  {"name": "Port of Rotterdam",   "code": "NLRTM", "coords": [4.49, 51.90],     "region": "Europe"},
    "Hamburg":    {"name": "Port of Hamburg",     "code": "DEHAM", "coords": [9.99, 53.54],     "region": "Europe"},
    "Antwerp":    {"name": "Port of Antwerp",     "code": "BEANR", "coords": [4.40, 51.23],     "region": "Europe"},
    "Felixstowe": {"name": "Port of Felixstowe",  "code": "GBFXT", "coords": [1.35, 51.96],     "region": "Europe"},
    # Americas
    "Los Angeles":{"name": "Port of Los Angeles", "code": "USLAX", "coords": [-118.26, 33.73],  "region": "Americas"},
    "Long Beach": {"name": "Port of Long Beach",  "code": "USLGB", "coords": [-118.22, 33.76],  "region": "Americas"},
    "New York":   {"name": "Port of New York",    "code": "USNYC", "coords": [-74.05, 40.65],   "region": "Americas"},
    "Seattle":    {"name": "Port of Seattle",     "code": "USSEA", "coords": [-122.34, 47.60],  "region": "Americas"},
    "Houston":    {"name": "Port of Houston",     "code": "USHOU", "coords": [-95.06, 29.73],   "region": "Americas"},
    "Savannah":   {"name": "Port of Savannah",    "code": "USSAV", "coords": [-80.91, 32.08],   "region": "Americas"},
}

# ---------------------------------------------------------------------------
# Pre-defined open-ocean waypoints for known trade lanes [lng, lat]
# ---------------------------------------------------------------------------
SEA_PATHS: dict = {
    "Shanghai-Los Angeles": [
        [121.47, 31.23], [123.5, 29.5], [130.0, 29.0],
        [145.0, 33.0], [170.0, 38.0], [200.0, 40.0],
        [220.0, 38.0], [235.0, 34.0], [-118.26, 33.73],
    ],
    "Shanghai-Long Beach": [
        [121.47, 31.23], [123.5, 29.5], [130.0, 29.0],
        [145.0, 33.0], [170.0, 38.0], [200.0, 40.0],
        [220.0, 38.0], [235.0, 34.0], [-118.22, 33.76],
    ],
    "Shanghai-Seattle": [
        [121.47, 31.23], [130.0, 36.0], [150.0, 44.0],
        [175.0, 50.0], [200.0, 50.0], [220.0, 48.0], [-122.34, 47.60],
    ],
    "Shanghai-New York": [
        [121.47, 31.23], [119.5, 24.5], [114.0, 15.0],
        [104.5, 3.0], [95.0, 5.0], [75.0, 5.0],
        [60.0, 15.0], [50.0, 12.0], [43.0, 12.5],
        [39.0, 21.0], [32.33, 30.57], [30.0, 31.5],
        [15.0, 35.0], [0.0, 36.0], [-5.5, 35.8],
        [-30.0, 38.0], [-55.0, 40.0], [-74.05, 40.65],
    ],
    "Rotterdam-New York": [
        [4.49, 51.9], [-2.0, 50.5], [-10.0, 49.0],
        [-20.0, 46.0], [-35.0, 42.0], [-50.0, 40.0],
        [-65.0, 40.0], [-74.05, 40.65],
    ],
    "Shanghai-Rotterdam": [
        [121.47, 31.23], [119.5, 24.5], [114.0, 15.0],
        [104.5, 3.0], [95.0, 5.0], [75.0, 5.0],
        [60.0, 15.0], [50.0, 12.0], [43.0, 12.5],
        [39.0, 21.0], [32.33, 30.57], [30.0, 31.5],
        [15.0, 35.0], [0.0, 36.0], [-5.5, 35.8],
        [-2.0, 44.0], [0.0, 50.5], [4.49, 51.9],
    ],
}


def _parse_route(route_text: str):
    """Parse 'Origin to Destination' route string into (origin_key, dest_key)."""
    parts = [p.strip() for p in route_text.lower().split(" to ")]
    if len(parts) != 2:
        return None

    def _match(city_lower: str):
        for key in PORT_REGISTRY:
            if key.lower() in city_lower or city_lower in key.lower():
                return key
        return None

    origin = _match(parts[0])
    dest = _match(parts[1])
    return (origin, dest) if (origin and dest) else None


def _get_sea_path(origin: str, dest: str) -> list:
    key = f"{origin}-{dest}"
    if key in SEA_PATHS:
        return SEA_PATHS[key]
    rev = f"{dest}-{origin}"
    if rev in SEA_PATHS:
        return list(reversed(SEA_PATHS[rev]))
    # Straight-line fallback
    return [PORT_REGISTRY[origin]["coords"], PORT_REGISTRY[dest]["coords"]]


@router.get("/routes")
def get_map_routes():
    """
    Reads purchase_orders.json and returns dynamic port pins and
    shipping arcs for the frontend map. No external API keys required.
    """
    data_path = (
        pathlib.Path(__file__).parent.parent.parent / "data" / "purchase_orders.json"
    )
    try:
        with open(data_path) as f:
            pos: list = json.load(f)
    except FileNotFoundError:
        pos = []

    active_pos = [p for p in pos if p.get("docstatus", 0) == 1]

    ports_seen: dict = {}
    arcs: list = []

    for po in active_pos:
        route_text = po.get("custom_route", "")
        parsed = _parse_route(route_text)
        if not parsed:
            continue

        origin_key, dest_key = parsed
        origin_info = PORT_REGISTRY[origin_key]
        dest_info = PORT_REGISTRY[dest_key]

        if origin_key not in ports_seen:
            ports_seen[origin_key] = {
                "id": f"port-{origin_key.lower().replace(' ', '-')}",
                "name": origin_info["name"],
                "code": origin_info["code"],
                "coordinates": origin_info["coords"],
                "type": "origin",
                "status": "normal",
                "details": f"Origin Port · {origin_info['region']}",
            }
        if dest_key not in ports_seen:
            ports_seen[dest_key] = {
                "id": f"port-{dest_key.lower().replace(' ', '-')}",
                "name": dest_info["name"],
                "code": dest_info["code"],
                "coordinates": dest_info["coords"],
                "type": "destination",
                "status": "normal",
                "details": f"Destination Hub · {dest_info['region']}",
            }

        arc_id = f"sea-{origin_key.lower().replace(' ', '')}-{dest_key.lower().replace(' ', '')}"
        if not any(a["id"] == arc_id for a in arcs):
            items = po.get("items", [])
            total_value = sum(i.get("qty", 0) * i.get("rate", 0) for i in items)
            arcs.append({
                "id": arc_id,
                "from": {"coordinates": origin_info["coords"]},
                "to": {"coordinates": dest_info["coords"]},
                "path": _get_sea_path(origin_key, dest_key),
                "type": "sea",
                "label": f"{origin_key} to {dest_key}",
                "vessel_id": po.get("custom_vessel_id", ""),
                "exposure_usd": round(total_value, 2),
            })

    return {
        "ports": list(ports_seen.values()),
        "arcs": arcs,
        "disruptions": [],
        "meta": {
            "total_active_pos": len(active_pos),
            "unique_routes": len(arcs),
            "source": "purchase_orders.json",
        },
    }

