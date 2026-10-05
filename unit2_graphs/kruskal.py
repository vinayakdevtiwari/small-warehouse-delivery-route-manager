"""Kruskal's Algorithm for Minimum Cost Spanning Tree (MST).

Algorithm Role:
- Supporting / Strategic Infrastructure Design.
- Sorts all candidate delivery links by cost/distance and greedily adds edges that do not
  create a cycle, using Disjoint Set Union (Union-Find).
- Application in Project: Finding the globally most economical road construction or maintenance
  plan to interconnect all delivery hubs.

Complexity:
- Time Complexity: O(E log E) or O(E log V) dominated by sorting the edges.
  Union-Find operations take near-constant O(alpha(V)) time using path compression and union by rank.
- Space Complexity: O(V + E) to store the edges, parent pointers, and rank arrays.
"""
from __future__ import annotations

from typing import Generic, Hashable, TypeVar

try:
    from unit2_graphs.adjacency_list import AdjacencyListGraph
except ImportError:
    from adjacency_list import AdjacencyListGraph  # type: ignore

V = TypeVar("V", bound=Hashable)


class DisjointSet(Generic[V]):
    """Disjoint Set Union (DSU) with path compression and union by rank."""

    def __init__(self, vertices: tuple[V, ...]) -> None:
        self.parent: dict[V, V] = {v: v for v in vertices}
        self.rank: dict[V, int] = {v: 0 for v in vertices}

    def find(self, item: V) -> V:
        """Find representative of the set containing item with path compression."""
        if self.parent[item] != item:
            self.parent[item] = self.find(self.parent[item])
        return self.parent[item]

    def union(self, u: V, v: V) -> bool:
        """Merge sets containing u and v. Returns True if merged, False if already in same set (cycle)."""
        root_u = self.find(u)
        root_v = self.find(v)

        if root_u == root_v:
            return False  # Same set: adding edge (u, v) would form a cycle

        # Union by rank
        if self.rank[root_u] < self.rank[root_v]:
            self.parent[root_u] = root_v
        elif self.rank[root_u] > self.rank[root_v]:
            self.parent[root_v] = root_u
        else:
            self.parent[root_v] = root_u
            self.rank[root_u] += 1

        return True


def kruskal_mst(graph) -> tuple[list[tuple[V, V, float]], float]:
    """Compute the Minimum Cost Spanning Tree using Kruskal's algorithm.

    Algorithm (as presented in DSA-II Lecture Unit 2 Slides 62-70):
    1. Sort all edges of the graph in ascending order of weight.
    2. Check the edge with minimum weight: if including it does not form a cycle,
       include it; otherwise discard it.
    3. Repeat until V - 1 edges have been chosen.

    Returns:
        A tuple of (mst_edges, total_weight).
    """
    vertices = graph.vertices
    if not vertices:
        return [], 0.0

    # Collect all unique undirected edges: (u, v, weight)
    all_edges = list(graph.edges())
    # Sort edges in ascending order of their weights
    all_edges.sort(key=lambda edge: edge[2])

    dsu = DisjointSet[V](vertices)
    mst_edges: list[tuple[V, V, float]] = []
    total_weight: float = 0.0
    required_edges = len(vertices) - 1

    for u, v, weight in all_edges:
        if dsu.union(u, v):
            mst_edges.append((u, v, weight))
            total_weight += weight
            if len(mst_edges) == required_edges:
                break

    if len(vertices) > 1 and len(mst_edges) < required_edges:
        raise ValueError("Graph is disconnected; cannot construct a full spanning tree.")

    return mst_edges, round(total_weight, 4)


if __name__ == "__main__":
    # Example from DSA-II Unit 2 PPT Slides 64-70
    network = AdjacencyListGraph[str](directed=False)

    nodes = ["A", "B", "C", "D", "E", "F"]
    for node in nodes:
        network.add_vertex(node)

    # Edge weights from PPT slide 64:
    # ED: 2, AB: 3, CD: 4, AE: 4, BC: 5, EF: 5, CF: 6, AF: 7, BF: 8, DF: 8
    network.add_edge("E", "D", 2.0)
    network.add_edge("A", "B", 3.0)
    network.add_edge("C", "D", 4.0)
    network.add_edge("A", "E", 4.0)
    network.add_edge("B", "C", 5.0)
    network.add_edge("E", "F", 5.0)
    network.add_edge("C", "F", 6.0)
    network.add_edge("A", "F", 7.0)
    network.add_edge("B", "F", 8.0)
    network.add_edge("D", "F", 8.0)

    print("=== Kruskal's Minimum Spanning Tree (MST) ===")
    mst_edges, total_cost = kruskal_mst(network)

    print(f"MST Edges Selected ({len(mst_edges)} edges):")
    for u, v, w in mst_edges:
        print(f"  {u} -- {v} (weight: {w})")
    print(f"Total Minimum Tree Cost: {total_cost}")
    print("Verification against PPT slide 70: Total weight is exactly 18.")
