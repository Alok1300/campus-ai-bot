from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.locations.resolver import resolver

router = APIRouter()

class ResolveRequest(BaseModel):
    query: str

@router.get("/locations")
def get_all_locations():
    return list(resolver.locations.values())

@router.get("/locations/{location_id}")
def get_location(location_id: str):
    loc = resolver.get_location_by_id(location_id.upper())
    if not loc:
        raise HTTPException(status_code=404, detail="Location not found")
    return loc

@router.post("/resolve-location")
def resolve_location(req: ResolveRequest):
    loc, conf = resolver.resolve(req.query)
    if not loc:
        return {"resolved": False, "confidence": conf}
    return {
        "resolved": True,
        "location": loc,
        "confidence": conf
    }
