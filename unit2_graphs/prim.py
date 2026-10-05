"""Prim's Algorithm for Minimum Cost Spanning Tree (MST).

Algorithm Role:
- Supporting / Strategic Infrastructure Design.
- Grows an MST from an arbitrary root vertex by greedily adding the lowest-weight edge
  connecting a tree vertex to a non-tree (fringe) vertex.
- Application in Project: Designing minimum-cost transit network connecting all warehouses
  and customer hubs with minimum total road length.

Complexity:
- Time Complexity: O(E log V) with a binary min-heap (priority queue).
  Each vertex is added to the MST once, and edge relaxations push at most E edges onto the heap.
- Space Complexity: O(V + E) for priority queue, in-tree set, and result edge list.
"""
from __future__ import annotations

import heapq
from typing import Hashable, TypeVar

try:
    from unit2_graphs.adjacency_list import AdjacencyListGraph
except ImportError:
    from adjacency_list import AdjacencyListGraph  # type: ignore

V = TypeVar("V", bound=Hashable)


def prim_mst(graph, start: V | None = None) -> tuple[list[tuple[V, V, float]], float]:
    """Compute the Minimum Cost Spanning Tree using Prim's algorithm.

    Args:
        graph: An undirected graph providing `vertices` and `neighbours(u)`.
        start: Optional starting vertex. Defaults to first vertex in graph.

    Returns:
        A tuple of (mst_edges, total_weight) where mst_edges is a list of (u, v, weight).

    Raises:
        ValueError if the graph is disconnected and cannot form a full spanning tree.
    """
    vertices = graph.vertices
    if not vertices:
        return [], 0.0

    root = start if start is not None else vertices[0]
    if root not in vertices:
        raise KeyError(f"unknown starting vertex: {root!r}")

    in_tree: set[V] = {root}
    mst_edges: list[tuple[V, V, float]] = []
    total_weight: float = 0.0

    # Priority queue stores tuples of (weight, u, v)
    edge_heap: list[tuple[float, V, V]] = []

    # Initialize heap with edges incident to the root
    for neighbour, weight in graph.neighbours(root):
        heapq.heappush(edge_heap, (weight, root, neighbour))

    # Grow the tree until it contains all vertices
    while edge_heap and len(in_tree) < len(vertices):
        weight, u, v = heapq.heappop(edge_heap)

        if v in in_tree:
            continue

        # Add v to tree
        in_tree.add(v)
        mst_edges.append((u, v, weight))
        total_weight += weight

        # Push all edges from newly added vertex v to fringe vertices
        for next_nbr, next_weight in graph.neighbours(v):
            if next_nbr not in in_tree:
                heapq.heappush(edge_heap, (next_weight, v, next_nbr))

    if len(in_tree) != len(vertices):
        raise ValueError("Graph is disconnected; a full spanning tree cannot be formed.")

    return mst_edges, round(total_weight, 4)


if __name__ == "__main__":
    # Example from DSA-II Unit 2 PPT Slides 73-78
    network = AdjacencyListGraph[str](directed=False)

    nodes = ["A", "B", "C", "D", "E", "F"]
    for node in nodes:
        network.add_vertex(node)

    # Adding edges matching PPT example
    network.add_edge("A", "B", 3.0)
    network.add_edge("A", "E", 4.0)
    network.add_edge("A", "F", 7.0)
    network.add_edge("B", "C", 5.0)
    network.add_edge("B", "F", 8.0)
    network.add_edge("C", "D", 4.0)
    network.add_edge("C", "F", 6.0)
    network.add_edge("D", "E", 2.0)
    network.add_edge("D", "F", 8.0)
    network.add_edge("E", "F", 5.0)

    print("=== Prim's Minimum Spanning Tree (MST) ===")
    mst_edges, total_cost = prim_mst(network, start="A")

    print(f"Starting Vertex: A")
    print(f"MST Edges ({len(mst_edges)} edges for {len(nodes)} vertices):")
    for u, v, w in mst_edges:
        print(f"  {u} -- {v} (weight: {w})")
    print(f"Total Minimum Tree Cost: {total_cost}")
    print("Verification against PPT slide 78: Total weight is exactly 18.")
