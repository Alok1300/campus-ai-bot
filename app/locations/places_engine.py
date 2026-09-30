import json
import os
from typing import List, Dict, Any
from app.navigation.astar import find_shortest_path
from app.navigation.graph import campus_graph

PLACES_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "places.json")

class PlacesEngine:
    def __init__(self):
        self.places = []
        self._load_places()

    def _load_places(self):
        try:
            with open(PLACES_FILE, 'r') as f:
                self.places = json.load(f)
        except Exception as e:
            print(f"Error loading places: {e}")
            self.places = []

    def get_place_by_id(self, place_id: str) -> Dict[str, Any]:
        for p in self.places:
            if p["id"] == place_id:
                return p
        return None

    def search_places(self, query: str, category: str = None, service: str = None) -> List[Dict[str, Any]]:
        query = query.lower() if query else ""
        results = []
        for p in self.places:
            if p.get("verification_status") != "verified":
                continue

            match = False
            if category and (p.get("category") == category or p.get("subcategory") == category):
                match = True
            
            if service and service in p.get("services", []):
                match = True

            if query:
                name_match = query in p["name"].lower()
                alias_match = any(query in alias.lower() for alias in p.get("aliases", []))
                service_match = any(query in s.lower() for s in p.get("services", []))
                if name_match or alias_match or service_match:
                    match = True
                elif category is None and service is None:
                    # If we only have query and no match found, skip
                    continue

            if match or (not query and not category and not service):
                results.append(p)
        return results

    def get_nearest_places(self, start_node_id: str, category: str = None, service: str = None, limit: int = 5) -> List[Dict[str, Any]]:
        candidates = self.search_places(query="", category=category, service=service)
        
        results = []
        for p in candidates:
            entrance_node = p.get("entrance_node")
            if not entrance_node:
                continue
            
            # calculate walking distance using find_shortest_path
            path, distance, time_min = find_shortest_path(start_node_id, entrance_node)
            if path:
                result_item = p.copy()
                result_item["walking_distance_m"] = round(distance)
                result_item["walking_time_min"] = time_min
                results.append(result_item)
                
        # Sort by walking distance
        results.sort(key=lambda x: x["walking_distance_m"])
        return results[:limit]

places_engine = PlacesEngine()
