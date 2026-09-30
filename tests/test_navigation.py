from app.navigation.route_engine import get_route

def test_get_route_d1_to_d2():
    res = get_route("D1", "D2")
    assert res.get("success") is True
    assert res["source"]["id"] == "D1"
    assert res["destination"]["id"] == "D2"
    assert res["distance_m"] > 0
    assert len(res["route_nodes"]) > 0

def test_get_route_b1_to_a1():
    res = get_route("B1", "A1")
    assert res.get("success") is True
    assert res["source"]["id"] == "B1"
    assert res["destination"]["id"] == "A1"

def test_invalid_source():
    res = get_route("InvalidSource", "A1")
    assert "error" in res

def test_invalid_destination():
    res = get_route("A1", "InvalidDestination")
    assert "error" in res
