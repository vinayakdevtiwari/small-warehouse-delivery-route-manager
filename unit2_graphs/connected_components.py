"""Connected Components analysis for detecting partitioned delivery zones.

Algorithm Role:
- Supporting / Operational Analysis.
- Discovers maximal connected subgraphs in an undirected network using DFS.
- Identifies isolated delivery territories that cannot be serviced from specific warehouses.

Complexity:
- Time Complexity: O(V + E) with Adjacency List.
  Every vertex and edge is processed exactly once across the outer loop DFS calls.
- Space Complexity: O(V) auxiliary space for visited set and component storage.
"""
from __future__ import annotations

from typing import Hashable, TypeVar

try:
    from unit2_graphs.adjacency_list import AdjacencyListGraph
except ImportError:
    from adjacency_list import AdjacencyListGraph  # type: ignore

V = TypeVar("V", bound=Hashable)


def find_connected_components(graph) -> list[list[V]]:
    """Identify all connected components in an undirected graph.

    Algorithm (as specified in DSA-II Lecture Unit 2):
    1. Initialize Visited map/set for all vertices as False.
    2. For each vertex v in V:
         if not Visited[v]:
             run DFS to discover all vertices reachable from v
             record discovered vertices as a new connected component
    3. Return list of components.
    """
    visited: set[V] = set()
    components: list[list[V]] = []

    def _dfs_component(vertex: V, current_component: list[V]) -> None:
        visited.add(vertex)
        current_component.append(vertex)
        for neighbour, _ in graph.neighbours(vertex):
            if neighbour not in visited:
                _dfs_component(neighbour, current_component)

    for vertex in graph.vertices:
        if vertex not in visited:
            component: list[V] = []
            _dfs_component(vertex, component)
            components.append(component)

    return components


def count_connected_components(graph) -> int:
    """Return the total number of connected components in the graph."""
    return len(find_connected_components(graph))


def is_fully_connected(graph) -> bool:
    """Check if all locations form a single unified connected network."""
    if not graph.vertices:
        return True
    return count_connected_components(graph) == 1


if __name__ == "__main__":
    network = AdjacencyListGraph[str](directed=False)

    # Define 3 distinct delivery zones
    # Region 1: Metro North Zone
    network.add_vertex("Warehouse North")
    network.add_vertex("Metro Hub 1")
    network.add_vertex("Metro Hub 2")
    network.add_edge("Warehouse North", "Metro Hub 1", 5.0)
    network.add_edge("Metro Hub 1", "Metro Hub 2", 3.0)

    # Region 2: Industrial South Zone (across river, independent)
    network.add_vertex("Warehouse South")
    network.add_vertex("Factory A")
    network.add_vertex("Factory B")
    network.add_edge("Warehouse South", "Factory A", 8.0)
    network.add_edge("Factory A", "Factory B", 4.0)

    # Region 3: Isolated Outpost
    network.add_vertex("Remote Outpost Z")

    print("=== Connected Components Analysis ===")
    components = find_connected_components(network)
    print(f"Total Isolated Delivery Zones: {len(components)}")
    for i, comp in enumerate(components, start=1):
        print(f"  Zone {i} ({len(comp)} locations): {', '.join(comp)}")

    print(f"\nIs delivery network fully connected? {is_fully_connected(network)}")
    print("Action needed: Bridges or transit corridors required between isolated zones.")
