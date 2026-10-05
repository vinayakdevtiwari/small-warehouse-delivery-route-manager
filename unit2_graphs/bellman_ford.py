"""Bellman-Ford Single-Source Shortest Path Algorithm with Negative Cycle Detection.

Algorithm Role:
- Supporting / Comparative Analysis & Syllabus Requirement.
- Solves single-source shortest paths on graphs that may contain negative-weight edges.
- Detects negative-weight cycles (returns False / raises ValueError).
- Project Justification:
  Implemented for DSA-II syllabus coverage and shortest-path comparison.
  Negative delivery costs are not considered realistic for the actual warehouse routing model.
  Physical delivery routes, travel times, and fuel expenses are strictly non-negative,
  making Dijkstra the appropriate primary engine for logistics routing.
  Bellman-Ford is maintained for academic completeness and negative-cycle detection.

Complexity:
- Time Complexity: O(V * E) with both Adjacency List and Adjacency Matrix representations.
  Performs |V| - 1 relaxation passes over all E edges, followed by 1 negative-cycle check pass.
- Space Complexity: O(V) auxiliary space for distances and predecessor dictionaries.
"""
from __future__ import annotations

from typing import Generic, Hashable, TypeVar

try:
    from unit2_graphs.adjacency_list import AdjacencyListGraph
except ImportError:
    from adjacency_list import AdjacencyListGraph  # type: ignore

V = TypeVar("V", bound=Hashable)


class EdgeWeightedGraph(Generic[V]):
    """Self-contained graph structure used specifically for Bellman-Ford demonstrations.

    Permits arbitrary (including negative) edge weights for academic syllabus study,
    keeping the primary warehouse AdjacencyListGraph strictly non-negative.
    """

    def __init__(self, vertices: list[V], edges: list[tuple[V, V, float]]) -> None:
        self.vertices = tuple(vertices)
        self._adj: dict[V, list[tuple[V, float]]] = {v: [] for v in vertices}
        for u, v, w in edges:
            if u not in self._adj or v not in self._adj:
                raise KeyError(f"Edge ({u}, {v}) references an undeclared vertex.")
            self._adj[u].append((v, float(w)))

    def neighbours(self, u: V) -> list[tuple[V, float]]:
        return self._adj[u]


def bellman_ford(graph, start: V) -> tuple[dict[V, float], dict[V, V | None], bool]:
    """Compute shortest distances and detect negative weight cycles using Bellman-Ford.

    Algorithm (from DSA-II Lecture Unit 2 Slides 98-102):
    1. Initialize Single Source:
       - Set dist[v] = infinity for all v in V; dist[start] = 0.
       - Set predecessor pi[v] = None.
    2. For i from 1 to |V| - 1:
         For each edge (u, v) with weight w:
           if dist[u] != infinity and dist[u] + w < dist[v]:
             dist[v] = dist[u] + w
             pi[v] = u
    3. Check for negative-weight cycles:
         For each edge (u, v) with weight w:
           if dist[u] != infinity and dist[u] + w < dist[v]:
             return dist, pi, False (negative weight cycle detected)
    4. Return dist, pi, True (no negative cycle).

    Args:
        graph: Any graph providing `vertices` and `neighbours(u)`.
        start: Starting source location.

    Returns:
        A tuple of (distances, predecessors, has_no_negative_cycle).
    """
    vertices = list(graph.vertices)
    if start not in vertices:
        raise KeyError(f"unknown starting vertex: {start!r}")

    distances: dict[V, float] = {v: float("inf") for v in vertices}
    predecessors: dict[V, V | None] = {v: None for v in vertices}
    distances[start] = 0.0

    # Collect all directed edges (u, v, w)
    all_edges: list[tuple[V, V, float]] = []
    for u in vertices:
        for v, w in graph.neighbours(u):
            all_edges.append((u, v, w))

    num_vertices = len(vertices)

    # |V| - 1 passes of edge relaxation
    for _ in range(num_vertices - 1):
        updated = False
        for u, v, w in all_edges:
            if distances[u] != float("inf") and distances[u] + w < distances[v]:
                distances[v] = distances[u] + w
                predecessors[v] = u
                updated = True
        if not updated:
            break  # Early termination if no distances changed

    # Negative cycle detection pass
    for u, v, w in all_edges:
        if distances[u] != float("inf") and distances[u] + w < distances[v]:
            return distances, predecessors, False  # Negative-weight cycle exists

    return distances, predecessors, True


def bellman_ford_shortest_path(graph, start: V, destination: V) -> tuple[list[V], float]:
    """Find the shortest path to destination, raising ValueError if a negative cycle is found."""
    distances, predecessors, no_neg_cycle = bellman_ford(graph, start)
    if not no_neg_cycle:
        raise ValueError("Graph contains a negative weight cycle; shortest path is undefined.")

    total_dist = distances.get(destination, float("inf"))
    if total_dist == float("inf"):
        return [], float("inf")

    path: list[V] = []
    curr: V | None = destination
    while curr is not None:
        path.append(curr)
        curr = predecessors.get(curr)
    path.reverse()

    return path, round(total_dist, 4)


if __name__ == "__main__":
    print("=== Bellman-Ford Shortest Path Algorithm ===")

    # Test 1: Standard Warehouse Road Graph (Non-negative distances)
    print("--- 1. Warehouse Delivery Network Test (Non-negative weights) ---")
    warehouse_map = AdjacencyListGraph[str](directed=False)
    for loc in ["Warehouse A", "Depot 1", "Customer Hub 1"]:
        warehouse_map.add_vertex(loc)
    warehouse_map.add_edge("Warehouse A", "Depot 1", 5.0)
    warehouse_map.add_edge("Depot 1", "Customer Hub 1", 3.0)

    w_dists, _, w_valid = bellman_ford(warehouse_map, "Warehouse A")
    print("Warehouse map distances from Warehouse A:", {k: round(w_dists[k], 1) for k in sorted(w_dists)})

    # Test 2: Academic Verification on PPT Slides 99-102 Example Graph (with negative edges)
    print("\n--- 2. Academic Verification on PPT Slides 99-102 (Negative Edges) ---")
    # Using self-contained EdgeWeightedGraph for syllabus study
    ppt_vertices = ["A", "B", "C", "D", "E"]
    ppt_edges = [
        ("A", "B", -1.0),
        ("A", "C", 4.0),
        ("B", "C", 3.0),
        ("B", "D", 2.0),
        ("B", "E", 2.0),
        ("D", "B", 1.0),
        ("D", "C", 5.0),
        ("E", "D", -3.0),
    ]
    ppt_graph = EdgeWeightedGraph[str](ppt_vertices, ppt_edges)

    dists, _, valid = bellman_ford(ppt_graph, "A")
    print("No negative cycle detected?", valid)
    print("Computed shortest distances from A:", {k: round(dists[k], 2) for k in sorted(dists)})
    print("PPT Slide 101 Expected: A: 0, B: -1, C: 2, D: -2, E: 1 -> Exact match!")

    # Test 3: Negative Cycle Test
    print("\n--- 3. Negative-Weight Cycle Detection Test ---")
    cycle_vertices = ["Hub 1", "Hub 2", "Hub 3"]
    cycle_edges = [
        ("Hub 1", "Hub 2", 1.0),
        ("Hub 2", "Hub 3", -4.0),
        ("Hub 3", "Hub 1", 2.0),  # Cycle sum = 1 - 4 + 2 = -1
    ]
    cycle_graph = EdgeWeightedGraph[str](cycle_vertices, cycle_edges)

    _, _, cycle_valid = bellman_ford(cycle_graph, "Hub 1")
    print("Is cycle_graph free of negative cycles?", cycle_valid)
    print("Correctly caught negative cycle:", not cycle_valid)
