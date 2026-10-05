"""Depth First Search (DFS) for warehouse route tracing and network inspection.

Algorithm Role:
- Supporting / Learning Implementation.
- Explores deep paths using recursion or an explicit LIFO stack.
- Performs graph traversal, path finding, and cycle/loop detection in road layouts.

Complexity:
- Time Complexity: O(V + E) with Adjacency List, O(V^2) with Adjacency Matrix.
  Visits every vertex and traverses every incident edge once.
- Space Complexity: O(V) auxiliary space for visited set and call stack / explicit stack.
"""
from __future__ import annotations

from typing import Hashable, TypeVar

try:
    from unit2_graphs.adjacency_list import AdjacencyListGraph
except ImportError:
    from adjacency_list import AdjacencyListGraph  # type: ignore

V = TypeVar("V", bound=Hashable)


def dfs_recursive(graph, start: V) -> list[V]:
    """Perform recursive DFS traversal starting from `start`.

    Returns:
        List of vertices in the order visited.
    """
    if start not in graph.vertices:
        raise KeyError(f"unknown starting vertex: {start!r}")

    visited: set[V] = set()
    order: list[V] = []

    def _dfs(vertex: V) -> None:
        visited.add(vertex)
        order.append(vertex)
        for neighbour, _ in graph.neighbours(vertex):
            if neighbour not in visited:
                _dfs(neighbour)

    _dfs(start)
    return order


def dfs_iterative(graph, start: V) -> list[V]:
    """Perform iterative DFS using an explicit LIFO stack (as in lecture PPT).

    Algorithm:
    1. Initialize stack with start vertex.
    2. While stack is not empty: pop vertex, mark visited if not already, and push unvisited neighbours.
    """
    if start not in graph.vertices:
        raise KeyError(f"unknown starting vertex: {start!r}")

    visited: set[V] = set()
    stack: list[V] = [start]
    order: list[V] = []

    while stack:
        current = stack.pop()
        if current not in visited:
            visited.add(current)
            order.append(current)
            # Push neighbours (reversed to visit in natural order)
            nbrs = [nbr for nbr, _ in graph.neighbours(current) if nbr not in visited]
            for nbr in reversed(nbrs):
                stack.append(nbr)

    return order


def has_path_dfs(graph, source: V, destination: V) -> bool:
    """Check if any valid delivery path exists between source and destination using DFS."""
    if source not in graph.vertices or destination not in graph.vertices:
        raise KeyError("both vertices must exist in graph")

    visited: set[V] = set()

    def _dfs(u: V) -> bool:
        if u == destination:
            return True
        visited.add(u)
        for v, _ in graph.neighbours(u):
            if v not in visited:
                if _dfs(v):
                    return True
        return False

    return _dfs(source)


def has_cycle_undirected(graph) -> bool:
    """Detect whether an undirected network contains any cycles (redundant alternative loops)."""
    visited: set[V] = set()

    def _dfs(vertex: V, parent: V | None) -> bool:
        visited.add(vertex)
        for neighbour, _ in graph.neighbours(vertex):
            if neighbour not in visited:
                if _dfs(neighbour, vertex):
                    return True
            elif neighbour != parent:
                # Visited neighbour that is not the parent indicates a back-edge (cycle)
                return True
        return False

    for v in graph.vertices:
        if v not in visited:
            if _dfs(v, None):
                return True
    return False


if __name__ == "__main__":
    network = AdjacencyListGraph[str](directed=False)

    locations = [
        "Warehouse North",
        "Depot Central",
        "Customer Zone 1",
        "Customer Zone 2",
        "Customer Zone 3",
        "Rural Stop X",
    ]

    for loc in locations:
        network.add_vertex(loc)

    network.add_edge("Warehouse North", "Depot Central", 10.0)
    network.add_edge("Depot Central", "Customer Zone 1", 4.0)
    network.add_edge("Customer Zone 1", "Customer Zone 2", 3.0)
    network.add_edge("Customer Zone 2", "Depot Central", 5.0)  # Creates a cycle/loop
    network.add_edge("Customer Zone 2", "Customer Zone 3", 6.0)

    print("=== Depth First Search (DFS) Demonstration ===")
    rec_order = dfs_recursive(network, "Warehouse North")
    print("DFS Recursive Traversal from Warehouse North:")
    print(" -> ".join(rec_order))

    iter_order = dfs_iterative(network, "Warehouse North")
    print("\nDFS Iterative (Stack) Traversal from Warehouse North:")
    print(" -> ".join(iter_order))

    print("\nPath Existence Checks:")
    print("Path to Customer Zone 3:", has_path_dfs(network, "Warehouse North", "Customer Zone 3"))
    print("Path to Rural Stop X:", has_path_dfs(network, "Warehouse North", "Rural Stop X"))

    print("\nCycle Detection:")
    print("Does the delivery network contain circular alternative loops?", has_cycle_undirected(network))
