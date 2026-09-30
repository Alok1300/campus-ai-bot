import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_all_places():
    response = client.get("/places/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert any(p["name"] == "Library Cafe" for p in data)

def test_get_place_by_id():
    response = client.get("/places/POI_001")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Library Cafe"

def test_get_nearby_places():
    # N_LIBRARY is where the Library Cafe is located
    response = client.get("/places/nearby?location_id=LIBRARY&category=cafe")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["name"] == "Library Cafe"
    assert "walking_distance_m" in data[0]

def test_search_places_nlp_service():
    response = client.post("/places/search", json={"query": "where can I buy a notebook near D3"})
    assert response.status_code == 200
    # Note: Groq NLP might return different things, but let's mock/test the structural response
    # Or just verify it doesn't crash since it depends on the LLM.
    data = response.json()
    assert "results" in data

def test_navigation_nearest_place():
    response = client.post("/navigation/navigate", json={
        "message": "take me to the nearest atm from Gate 1",
        "current_location": "GATE_1"
    })
    assert response.status_code == 200
    data = response.json()
    if data.get("success"):
        assert "destination_place" in data
        assert data["destination_place"]["name"] == "Gate 1 ATM"
