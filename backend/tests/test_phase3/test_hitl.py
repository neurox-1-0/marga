import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_hitl_pending_cards():
    response = client.get("/cards/pending")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_hitl_record_decision():
    response = client.post(
        "/cards/EVT-1/decision",
        json={
            "event_id": "EVT-1",
            "decision": "approved",
            "chosen_quote_id": "Q-001"
        }
    )
    assert response.status_code == 200
    assert response.json()["status"] == "recorded"
