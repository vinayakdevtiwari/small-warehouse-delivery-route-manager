"""Travelling Salesperson Problem using Branch & Bound.

Project fit: supporting route-planning module for a small batch of delivery stops.
It optimizes a closed tour over a supplied distance graph. Use Dijkstra first if
road distances between stops need to be derived from an underlying road network.
"""
from __future__ import annotations
from math import inf
from typing import Hashable, Mapping


def tsp_branch_and_bound(graph: Mapping[Hashable, Mapping[Hashable, float]], start: Hashable) -> tuple[list[Hashable], float]:
    """Return the minimum-cost closed tour and its cost."""
    vertices = list(graph)
    if start not in graph:
        raise KeyError(f"unknown start vertex: {start!r}")
    if len(vertices) < 2:
        raise ValueError("TSP requires at least two vertices")
    clean: dict[Hashable, dict[Hashable, float]] = {}
    for u in vertices:
        clean[u] = {}
        for v, weight in graph[u].items():
            if v not in graph:
                raise ValueError(f"edge points to unknown vertex: {v!r}")
            if u == v:
                continue
            if not isinstance(weight, (int, float)) or isinstance(weight, bool) or weight < 0:
                raise ValueError("TSP edge weights must be non-negative numbers")
            clean[u][v] = float(weight)
        if not clean[u]:
            raise ValueError(f"vertex {u!r} has no outgoing edge")
    min_out = {u: min(clean[u].values()) for u in vertices}
    best_cost = inf
    best_path: list[Hashable] = []
    path = [start]
    visited = {start}

    def search(current: Hashable, cost_so_far: float) -> None:
        nonlocal best_cost, best_path
        if len(visited) == len(vertices):
            total = cost_so_far + clean[current].get(start, inf)
            if total < best_cost:
                best_cost, best_path = total, path[:] + [start]
            return
        remaining = [v for v in vertices if v not in visited]
        lower_bound = cost_so_far + min_out[current] + sum(min_out[v] for v in remaining)
        if lower_bound >= best_cost:
            return
        candidates = sorted(((w, v) for v, w in clean[current].items() if v not in visited), key=lambda item: item[0])
        for weight, nxt in candidates:
            if cost_so_far + weight >= best_cost:
                continue
            visited.add(nxt)
            path.append(nxt)
            search(nxt, cost_so_far + weight)
            path.pop()
            visited.remove(nxt)

    search(start, 0.0)
    if not best_path:
        raise ValueError("no closed tour visits every vertex exactly once")
    return best_path, best_cost


if __name__ == "__main__":
    route_graph = {
        "Warehouse": {"North Hub": 4, "South Hub": 2, "Customer": 9},
        "North Hub": {"Warehouse": 4, "South Hub": 1, "Customer": 5},
        "South Hub": {"Warehouse": 2, "North Hub": 1, "Customer": 3},
        "Customer": {"Warehouse": 9, "North Hub": 5, "South Hub": 3},
    }
    route, distance = tsp_branch_and_bound(route_graph, "Warehouse")
    print("Unit 4 — TSP with Branch & Bound")
    print("Best closed tour:", " -> ".join(route))
    print("Total tour distance:", distance, "km")
