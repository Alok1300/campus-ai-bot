from app.navigation.astar import find_shortest_path
from app.navigation.graph import campus_graph

def test_astar_valid_route():
    src_node = campus_graph.get_node_by_location_id("D1")
    dst_node = campus_graph.get_node_by_location_id("D2")
    
    path, dist, time_min = find_shortest_path(src_node, dst_node)
    
    assert len(path) > 0
    assert path[0] == src_node
    assert path[-1] == dst_node
    assert dist > 0

def test_astar_no_route():
    # Adding an isolated node
    campus_graph.graph.add_node("ISOLATED")
    src_node = campus_graph.get_node_by_location_id("D1")
    
    path, dist, time_min = find_shortest_path(src_node, "ISOLATED")
    
    assert len(path) == 0
    assert dist == 0
