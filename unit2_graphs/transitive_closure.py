"""Transitive Closure using Warshall's Algorithm.

Algorithm Role:
- Supporting / Route Verification & Audit.
- Computes an all-pairs reachability boolean matrix determining whether a delivery path
  exists from any location u to any location v (via direct edges or intermediate transit hubs).
- Useful for checking delivery serviceability across one-way or constrained road systems.

Complexity:
- Time Complexity: O(V^3) through three nested loops iterating over all intermediate vertices k.
- Space Complexity: O(V^2) to store the boolean reachability matrix.
"""
from __future__ import annotations

from typing import Hashable, TypeVar

try:
    from unit2_graphs.adjacency_matrix import AdjacencyMatrixGraph
except ImportError:
    from adjacency_matrix import AdjacencyMatrixGraph  # type: ignore

V = TypeVar("V", bound=Hashable)


def transitive_closure(graph) -> dict[V, dict[V, int]]:
    """Compute the reachability matrix for the graph using Warshall's Algorithm.

    Algorithm (from DSA-II Lecture Unit 2 Slides 82-83):
    1. Initialize reachability matrix transMat[i][j]:
       - transMat[i][i] = 1 (every vertex can reach itself)
       - transMat[i][j] = 1 if there is a direct edge from i to j, else 0.
    2. For each intermediate vertex k in 0..V-1:
         For each source vertex i in 0..V-1:
           For each destination vertex j in 0..V-1:
             transMat[i][j] = transMat[i][j] or (transMat[i][k] and transMat[k][j])
    3. Return transMat.

    Returns:
        A nested dictionary reachability[u][v] = 1 if reachable, 0 otherwise.
    """
    vertices = list(graph.vertices)
    n = len(vertices)
    index = {v: i for i, v in enumerate(vertices)}

    # Step 1: Initialize V x V reachability matrix
    reach = [[0] * n for _ in range(n)]

    for i in range(n):
        reach[i][i] = 1  # Self-reachability

    # Populate direct edges
    for u in vertices:
        for v, _ in graph.neighbours(u):
            reach[index[u]][index[v]] = 1

    # Step 2: Warshall's Algorithm
    for k in range(n):
        for i in range(n):
            for j in range(n):
                reach[i][j] = reach[i][j] or (reach[i][k] and reach[k][j])

    # Convert back to location labels dictionary
    result: dict[V, dict[V, int]] = {}
    for i, u in enumerate(vertices):
        result[u] = {}
        for j, v in enumerate(vertices):
            result[u][v] = reach[i][j]

    return result


def display_transitive_closure(reach_dict: dict[V, dict[V, int]]) -> str:
    """Format the transitive closure matrix into a readable table."""
    vertices = list(reach_dict.keys())
    width = max(8, *(len(str(v)) + 1 for v in vertices)) if vertices else 8
    lines = ["".ljust(width) + "".join(str(v).rjust(width) for v in vertices)]
    for u in vertices:
        row_str = "".join(str(reach_dict[u][v]).rjust(width) for v in vertices)
        lines.append(str(u).ljust(width) + row_str)
    return "\n".join(lines)


if __name__ == "__main__":
    # Example matching DSA-II Unit 2 PPT Slide 82
    network = AdjacencyMatrixGraph[str](directed=True)

    nodes = ["0", "1", "2", "3"]
    for node in nodes:
        network.add_vertex(node)

    # Directed edges from PPT slide 82 diagram:
    # 0 -> 1, 0 -> 2, 1 -> 2, 2 -> 0, 2 -> 3
    network.add_edge("0", "1", 1.0)
    network.add_edge("0", "2", 1.0)
    network.add_edge("1", "2", 1.0)
    network.add_edge("2", "0", 1.0)
    network.add_edge("2", "3", 1.0)

    print("=== Transitive Closure (Warshall's Algorithm) ===")
    print("Directed Network Adjacency Matrix:")
    print(network.display())

    closure = transitive_closure(network)
    print("\nTransitive Closure Reachability Matrix (1 = reachable, 0 = unreachable):")
    print(display_transitive_closure(closure))

    print("\nReachability Summary:")
    print("Can node 1 reach node 3?", bool(closure["1"]["3"]))
    print("Can node 3 reach node 0?", bool(closure["3"]["0"]))
