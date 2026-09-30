from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from pydantic import BaseModel
from app.locations.places_engine import places_engine
from app.ai.intent_parser import parse_navigation_intent

router = APIRouter()

class PlaceSearchRequest(BaseModel):
    query: str
    current_location: Optional[str] = None

@router.get("/")
def get_all_places():
    return places_engine.places

@router.get("/nearby")
def get_nearby_places(
    location_id: str,
    category: Optional[str] = None,
    service: Optional[str] = None,
    limit: int = 5
):
    # Here we should resolve location_id to a node.
    # For simplicity, if it matches a node id, we use it, otherwise we prepend N_
    node_id = location_id if location_id.startswith("N_") else f"N_{location_id}"
    results = places_engine.get_nearest_places(node_id, category=category, service=service, limit=limit)
    return results

@router.post("/search")
def search_places_nlp(req: PlaceSearchRequest):
    intent = parse_navigation_intent(req.query)
    
    if "error" in intent:
        raise HTTPException(status_code=500, detail="Failed to parse intent")
        
    intent_type = intent.get("intent")
    
    if intent_type in ["nearest_place", "category_search", "service_search", "place_search"]:
        near = intent.get("near") or req.current_location
        category = intent.get("category")
        service = intent.get("service")
        
        if intent_type == "nearest_place" and not near:
             return {
                "success": False,
                "needs_clarification": True,
                "clarification_question": "Where are you currently located to find the nearest one?"
            }
            
        if near:
            node_id = near if near.startswith("N_") else f"N_{near}"
            results = places_engine.get_nearest_places(node_id, category=category, service=service)
        else:
            results = places_engine.search_places(query="", category=category, service=service)
            
        return {
            "intent": intent_type,
            "category": category,
            "service": service,
            "near": near,
            "results": results
        }
    
    return {"success": False, "detail": "Intent not handled by places API"}

@router.get("/{place_id}")
def get_place(place_id: str):
    place = places_engine.get_place_by_id(place_id)
    if not place:
        raise HTTPException(status_code=404, detail="Place not found")
    return place
