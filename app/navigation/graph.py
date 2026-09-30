import json
import os
import networkx as nx
from typing import Dict, Any, List
from app.config import settings

class CampusGraph:
    def __init__(self):
        self.graph = nx.Graph()
        self.nodes_data = {}
        self.edges_data = []
        self._load_data()
        
    def _load_data(self):
        nodes_file = os.path.join(settings.DATA_DIR, "nodes.json")
        edges_file = os.path.join(settings.DATA_DIR, "edges.json")
        
        if os.path.exists(nodes_file):
            with open(nodes_file, "r") as f:
                nodes = json.load(f)
                for n in nodes:
                    self.nodes_data[n["id"]] = n
                    self.graph.add_node(n["id"], **n)
                    
        if os.path.exists(edges_file):
            with open(edges_file, "r") as f:
                edges = json.load(f)
                self.edges_data = edges
                for e in edges:
                    if e.get("walkable", True) and not e.get("restricted", False):
                        self.graph.add_edge(e["from"], e["to"], weight=e["distance_m"], **e)

    def get_node_by_location_id(self, loc_id: str) -> str | None:
        """Find the entrance node for a given location ID."""
        for node_id, data in self.nodes_data.items():
            if data.get("location_id") == loc_id:
                return node_id
        return None

campus_graph = CampusGraph()
