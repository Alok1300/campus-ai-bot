import networkx as nx
from typing import List, Tuple, Dict, Any
from app.navigation.graph import campus_graph
from app.config import settings
import math

def calculate_time_min(distance_m: float, speed_kmh: float = settings.WALKING_SPEED_KMH) -> int:
    speed_ms = (speed_kmh * 1000) / 3600
    time_s = distance_m / speed_ms
    return max(1, math.ceil(time_s / 60))

def find_shortest_path(start_node: str, end_node: str) -> Tuple[List[str], float, int]:
    """
    Returns (path_nodes, distance_m, time_min)
    """
    try:
        path = nx.astar_path(campus_graph.graph, start_node, end_node, weight='weight')
        distance = nx.path_weight(campus_graph.graph, path, weight='weight')
        time_min = calculate_time_min(distance)
        return path, distance, time_min
    except nx.NetworkXNoPath:
        return [], 0.0, 0
    except nx.NodeNotFound:
        return [], 0.0, 0
