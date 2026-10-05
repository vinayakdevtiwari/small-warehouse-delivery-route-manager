"""Breadth First Search (BFS) for warehouse delivery route exploration.

Algorithm Role:
- Supporting / Learning Implementation.
- Explores delivery network level-by-level using a FIFO queue.
- Computes traversal order and minimum-hop route between warehouse and customer locations.

Complexity:
- Time Complexity: O(V + E) with Adjacency List, O(V^2) with Adjacency Matrix.
  Every reachable vertex is enqueued once, and every incident edge is inspected once.
- Space Complexity: O(V) auxiliary space for visited set and FIFO queue.
"""
from __future__ import annotations

from collections import deque
from typing import Hashable, TypeVar

try:
    from unit2_graphs.adjacency_list import AdjacencyListGraph
except ImportError:
    from adjacency_list import AdjacencyListGraph  # type: ignore

V = TypeVar("V", bound=Hashable)


def bfs(graph, start: V) -> list[V]:
    """Traverse the graph level by level starting from the `start` vertex.

    Returns:
        List of vertices in the order they were visited.
    """
    if start not in graph.vertices:
        raise KeyError(f"unknown starting vertex: {start!r}")

    visited: set[V] = {start}
    queue: deque[V] = deque([start])
    traversal_order: list[V] = []

    while queue:
        current = queue.popleft()
        traversal_order.append(current)

        for neighbour, _ in graph.neighbours(current):
            if neighbour not in visited:
                visited.add(neighbour)
                queue.append(neighbour)

    return traversal_order


def bfs_shortest_path(graph, start: V, destination: V) -> list[V] | None:
    """Find the route with the minimum number of hops (unweighted shortest path).

    Returns:
        List of locations along the path from `start` to `destination`,
        or None if destination is unreachable.
    """
    if start not in graph.vertices:
        raise KeyError(f"unknown starting vertex: {start!r}")
    if destination not in graph.vertices:
        raise KeyError(f"unknown destination vertex: {destination!r}")

    if start == destination:
        return [start]

    visited: set[V] = {start}
    queue: deque[V] = deque([start])
    parent: dict[V, V] = {}

    while queue:
        current = queue.popleft()
        if current == destination:
            break

        for neighbour, _ in graph.neighbours(current):
            if neighbour not in visited:
                visited.add(neighbour)
                parent[neighbour] = current
                queue.append(neighbour)

    if destination not in parent:
        return None

    # Reconstruct path by following parent pointers backward
    path: list[V] = []
    curr: V | None = destination
    while curr is not None:
        path.append(curr)
        curr = parent.get(curr)
    path.reverse()
    return path


if __name__ == "__main__":
    # Simulated Warehouse Delivery Network
    network = AdjacencyListGraph[str](directed=False)

    locations = [
        "Central Warehouse",
        "Sub-Depot North",
        "Sub-Depot South",
        "Customer Hub 1",
        "Customer Hub 2",
        "Customer Hub 3",
        "Isolated Outpost",
    ]

    for loc in locations:
        network.add_vertex(loc)

    network.add_edge("Central Warehouse", "Sub-Depot North", 8.0)
    network.add_edge("Central Warehouse", "Sub-Depot South", 6.0)
    network.add_edge("Sub-Depot North", "Customer Hub 1", 4.0)
    network.add_edge("Sub-Depot North", "Customer Hub 2", 7.0)
    network.add_edge("Sub-Depot South", "Customer Hub 2", 5.0)
    network.add_edge("Customer Hub 2", "Customer Hub 3", 3.0)

    print("=== Breadth First Search (BFS) Demonstration ===")
    traversal = bfs(network, "Central Warehouse")
    print("BFS Exploration Order from Central Warehouse:")
    print(" -> ".join(traversal))

    path = bfs_shortest_path(network, "Central Warehouse", "Customer Hub 3")
    print("\nMinimum Hop Route to Customer Hub 3:")
    if path:
        print(" -> ".join(path), f"({len(path) - 1} hops)")
    else:
        print("No route found.")

    isolated_check = bfs_shortest_path(network, "Central Warehouse", "Isolated Outpost")
    print("Reachability to Isolated Outpost:", "Reachable" if isolated_check else "Unreachable")