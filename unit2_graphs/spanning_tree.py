"""Spanning Tree construction and properties for delivery networks.

Algorithm Role:
- Supporting / Learning Implementation.
- Constructs a cycle-free subgraph spanning all vertices with exactly V - 1 edges.
- Provides baseline topological connectivity between warehouse facilities and hubs.
- Demonstrates Cayley's Formula (N^(N-2) spanning trees for complete graphs) from lecture syllabus.

Complexity:
- Time Complexity: O(V + E) with Adjacency List.
  BFS or DFS traversal visits each vertex and tree edge once.
- Space Complexity: O(V) auxiliary space for visited tracking and tree edge list.
"""
from __future__ import annotations

from collections import deque
from typing import Hashable, TypeVar

try:
    from unit2_graphs.adjacency_list import AdjacencyListGraph
except ImportError:
    from adjacency_list import AdjacencyListGraph  # type: ignore

V = TypeVar("V", bound=Hashable)


def bfs_spanning_tree(graph, root: V | None = None) -> list[tuple[V, V, float]]:
    """Construct a spanning tree using Breadth First Search (BFS tree edges).

    Returns:
        List of edges (u, v, weight) that form the spanning tree.
    Raises:
        ValueError if the graph is disconnected or empty.
    """
    vertices = graph.vertices
    if not vertices:
        return []

    start = root if root is not None else vertices[0]
    if start not in vertices:
        raise KeyError(f"unknown root vertex: {start!r}")

    visited: set[V] = {start}
    queue: deque[V] = deque([start])
    tree_edges: list[tuple[V, V, float]] = []

    while queue:
        u = queue.popleft()
        for v, weight in graph.neighbours(u):
            if v not in visited:
                visited.add(v)
                tree_edges.append((u, v, weight))
                queue.append(v)

    if len(visited) != len(vertices):
        raise ValueError("Spanning tree does not exist for a disconnected graph.")

    return tree_edges


def dfs_spanning_tree(graph, root: V | None = None) -> list[tuple[V, V, float]]:
    """Construct a spanning tree using Depth First Search (DFS tree edges).

    Returns:
        List of edges (u, v, weight) that form the spanning tree.
    Raises:
        ValueError if the graph is disconnected or empty.
    """
    vertices = graph.vertices
    if not vertices:
        return []

    start = root if root is not None else vertices[0]
    if start not in vertices:
        raise KeyError(f"unknown root vertex: {start!r}")

    visited: set[V] = set()
    tree_edges: list[tuple[V, V, float]] = []

    def _dfs(u: V) -> None:
        visited.add(u)
        for v, weight in graph.neighbours(u):
            if v not in visited:
                tree_edges.append((u, v, weight))
                _dfs(v)

    _dfs(start)

    if len(visited) != len(vertices):
        raise ValueError("Spanning tree does not exist for a disconnected graph.")

    return tree_edges


def cayley_formula(num_vertices: int) -> int:
    """Calculate the number of possible spanning trees in a complete graph K_n.

    Formula: N^(N - 2) (as taught in DSA-II Lecture Unit 2 Slide 61).
    """
    if num_vertices < 1:
        return 0
    if num_vertices in (1, 2):
        return 1
    return num_vertices ** (num_vertices - 2)


if __name__ == "__main__":
    network = AdjacencyListGraph[str](directed=False)

    # 4 interconnected warehouse depots
    hubs = ["Depot 1", "Depot 2", "Depot 3", "Depot 4"]
    for hub in hubs:
        network.add_vertex(hub)

    network.add_edge("Depot 1", "Depot 2", 4.0)
    network.add_edge("Depot 1", "Depot 3", 5.0)
    network.add_edge("Depot 2", "Depot 3", 2.0)
    network.add_edge("Depot 2", "Depot 4", 6.0)
    network.add_edge("Depot 3", "Depot 4", 3.0)

    print("=== Spanning Tree Exploration ===")
    bfs_tree = bfs_spanning_tree(network, "Depot 1")
    print(f"BFS Spanning Tree (Edges: {len(bfs_tree)}, Required: {len(hubs) - 1}):")
    for u, v, w in bfs_tree:
        print(f"  {u} -- {v} (weight: {w})")

    dfs_tree = dfs_spanning_tree(network, "Depot 1")
    print(f"\nDFS Spanning Tree (Edges: {len(dfs_tree)}):")
    for u, v, w in dfs_tree:
        print(f"  {u} -- {v} (weight: {w})")

    print(f"\nCayley's Formula for Complete Graph with N=4 vertices: {cayley_formula(4)} possible spanning trees.")
