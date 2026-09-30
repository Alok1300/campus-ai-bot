from app.locations.resolver import resolver

def test_resolve_exact():
    loc, conf = resolver.resolve("D1")
    assert loc is not None
    assert loc["id"] == "D1"
    assert conf == 1.0

def test_resolve_alias():
    loc, conf = resolver.resolve("library")
    assert loc is not None
    assert loc["id"] == "LIBRARY"

def test_resolve_partial():
    loc, conf = resolver.resolve("Apex Institute")
    assert loc is not None
    assert loc["id"] in ["D1", "D8"] # Depends on departments match order, D1 comes first

def test_resolve_invalid():
    loc, conf = resolver.resolve("NonExistentPlace")
    assert loc is None
    assert conf == 0.0
