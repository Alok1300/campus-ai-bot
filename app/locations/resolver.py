import json
import os
from typing import List, Dict, Any, Tuple
from app.config import settings
from app.locations.aliases import resolve_alias

class LocationResolver:
    def __init__(self):
        self.locations = self._load_locations()
        
    def _load_locations(self) -> Dict[str, Any]:
        combined = {}
        
        loc_file = os.path.join(settings.DATA_DIR, "locations.json")
        if os.path.exists(loc_file):
            with open(loc_file, "r") as f:
                data = json.load(f)
                for item in data:
                    combined[item["id"]] = item
                    
        places_file = os.path.join(settings.DATA_DIR, "places.json")
        if os.path.exists(places_file):
            with open(places_file, "r") as f:
                data = json.load(f)
                for item in data:
                    combined[item["id"]] = item
                    
        return combined

    def get_location_by_id(self, loc_id: str) -> Dict[str, Any] | None:
        return self.locations.get(loc_id)

    def resolve(self, query: str) -> Tuple[Dict[str, Any] | None, float]:
        """
        Returns (location_dict, confidence)
        """
        if not query:
            return None, 0.0
            
        normalized = query.strip()
        
        # 1. Exact ID match
        if normalized.upper() in self.locations:
            return self.locations[normalized.upper()], 1.0
            
        # 2. Alias match
        resolved_id = resolve_alias(normalized)
        if resolved_id and resolved_id in self.locations:
            return self.locations[resolved_id], 0.95
            
        # 3. Partial match
        normalized_lower = normalized.lower()
        for loc_id, loc_data in self.locations.items():
            if normalized_lower in loc_data["name"].lower():
                return loc_data, 0.8
            for alias in loc_data.get("aliases", []):
                if normalized_lower in alias.lower():
                    return loc_data, 0.75
            for dept in loc_data.get("departments", []):
                if normalized_lower in dept.lower():
                    return loc_data, 0.85
                    
        return None, 0.0

resolver = LocationResolver()
