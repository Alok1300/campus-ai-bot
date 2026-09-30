from typing import List, Dict, Any

def validate_route(path: List[str], start_node: str, end_node: str) -> bool:
    if not path:
        return False
    if path[0] != start_node:
        return False
    if path[-1] != end_node:
        return False
    return True
