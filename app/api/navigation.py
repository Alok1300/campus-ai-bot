from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.ai.intent_parser import parse_navigation_intent
from app.navigation.route_engine import get_route
from app.navigation.graph import campus_graph
from app.locations.places_engine import places_engine

router = APIRouter()

class NavigationRequest(BaseModel):
    message: str
    current_location: Optional[str] = None
    mode: str = "walking"

class RouteRequest(BaseModel):
    source: str
    destination: str

@router.post("/navigate")
def navigate(req: NavigationRequest):
    intent = parse_navigation_intent(req.message)
    
    if "error" in intent:
        raise HTTPException(status_code=500, detail="Failed to parse intent")
        
    if intent.get("needs_clarification"):
        return {
            "success": False,
            "needs_clarification": True,
            "clarification_question": intent.get("clarification_question", "Could you clarify your request?")
        }

    intent_type = intent.get("intent")
    
    # Handle Place search / Nearest place without navigation intent
    if intent_type in ["category_search", "service_search", "place_search"]:
        near = intent.get("near") or req.current_location
        category = intent.get("category")
        service = intent.get("service")
        
        results = places_engine.search_places(query=intent.get("destination", ""), category=category, service=service)
        if near:
            node_id = near if near.startswith("N_") else f"N_{near}"
            results = places_engine.get_nearest_places(node_id, category=category, service=service)

        return {
            "success": True,
            "type": "places",
            "results": results
        }

    # Handle Navigation to Nearest Place
    if intent_type == "nearest_place":
        source = intent.get("source") or req.current_location
        if not source:
            return {
                "success": False,
                "needs_clarification": True,
                "clarification_question": "Where are you starting from?"
            }
            
        node_id = source if source.startswith("N_") else f"N_{source}"
        category = intent.get("category")
        service = intent.get("service")
        nearest_places = places_engine.get_nearest_places(node_id, category=category, service=service, limit=1)
        
        if not nearest_places:
            return {
                "success": False,
                "detail": "Could not find any nearby matching places."
            }
            
        destination = nearest_places[0]["entrance_node"]
        route_result = get_route(source, destination)
        route_result["destination_place"] = nearest_places[0]
        return route_result

    # Default Navigation Intent
    source = intent.get("source") or req.current_location
    destination = intent.get("destination")
    
    if not source:
        return {
            "success": False,
            "needs_clarification": True,
            "clarification_question": "Where are you starting from?"
        }
        
    if not destination:
        return {
            "success": False,
            "needs_clarification": True,
            "clarification_question": "Where do you want to go?"
        }
        
    route_result = get_route(source, destination)
    
    if "error" in route_result:
        raise HTTPException(status_code=400, detail=route_result["error"])
        
    return route_result

@router.post("/route")
def calculate_route(req: RouteRequest):
    result = get_route(req.source, req.destination)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.get("/campus/graph")
def get_graph():
    return {
        "nodes": list(campus_graph.nodes_data.values()),
        "edges": campus_graph.edges_data
    }
