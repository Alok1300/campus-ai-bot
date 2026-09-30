from typing import Dict, Any
from app.locations.resolver import resolver
from app.navigation.graph import campus_graph
from app.navigation.astar import find_shortest_path
from app.navigation.instructions import generate_instructions
from app.navigation.route_validator import validate_route
from app.config import settings

def get_route(source_name: str, destination_name: str) -> Dict[str, Any]:
    src_loc, src_conf = resolver.resolve(source_name)
    dst_loc, dst_conf = resolver.resolve(destination_name)
    
    if not src_loc:
        return {"error": "Source location not found or ambiguous."}
    if not dst_loc:
        return {"error": "Destination location not found or ambiguous."}
        
    src_node = campus_graph.get_node_by_location_id(src_loc["id"])
    dst_node = campus_graph.get_node_by_location_id(dst_loc["id"])
    
    if not src_node:
        return {"error": f"No navigable entrance found for {src_loc['name']}."}
    if not dst_node:
        return {"error": f"No navigable entrance found for {dst_loc['name']}."}
        
    path, distance, time_min = find_shortest_path(src_node, dst_node)
    
    if not path or not validate_route(path, src_node, dst_node):
        return {"error": "No valid route found between these locations."}
        
    instructions = generate_instructions(path)
    
    return {
        "success": True,
        "source": {
            "id": src_loc["id"],
            "name": src_loc["name"]
        },
        "destination": {
            "id": dst_loc["id"],
            "name": dst_loc["name"]
        },
        "distance_m": distance,
        "estimated_time_min": time_min,
        "mode": "walking",
        "route_nodes": path,
        "instructions": instructions
    }
