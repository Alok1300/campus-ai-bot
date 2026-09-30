from typing import List
from app.navigation.graph import campus_graph

def generate_instructions(path: List[str]) -> List[str]:
    if not path:
        return []
        
    instructions = []
    
    # Very basic instruction generator
    # In a real scenario, this would use geometry, angles, and landmark nodes.
    
    start_node = path[0]
    start_data = campus_graph.nodes_data.get(start_node, {})
    start_loc_id = start_data.get("location_id")
    
    if start_loc_id:
        instructions.append(f"Start at {start_loc_id} entrance.")
    else:
        instructions.append("Start your route.")
        
    for i in range(len(path) - 1):
        curr_node = path[i]
        next_node = path[i+1]
        
        edge_data = campus_graph.graph.get_edge_data(curr_node, next_node)
        dist = edge_data.get("weight", 0)
        
        node_data = campus_graph.nodes_data.get(next_node, {})
        
        if node_data.get("type") == "building_entrance":
            loc_id = node_data.get("location_id")
            instructions.append(f"Continue for {dist}m towards {loc_id} entrance.")
        elif node_data.get("type") == "gate":
            loc_id = node_data.get("location_id")
            instructions.append(f"Continue for {dist}m towards {loc_id}.")
        else:
            instructions.append(f"Walk for {dist}m to the next junction.")
            
    instructions.append("You have reached your destination.")
    return instructions
