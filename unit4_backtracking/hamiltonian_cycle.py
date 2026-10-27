"""Hamiltonian-cycle search using backtracking.

Project fit: supporting comparison for closed delivery tours. Unlike TSP, this
returns a cycle if one exists; it does not optimize route distance.
"""
from __future__ import annotations
from typing import Hashable, Mapping, Sequence


def find_hamiltonian_cycle(adjacency: Mapping[Hashable, Sequence[Hashable]], start: Hashable) -> list[Hashable] | None:
    """Return a cycle visiting each vertex once and ending at start."""
    if start not in adjacency:
        raise KeyError(f"unknown start vertex: {start!r}")
    vertices = list(adjacency)
    vertex_set = set(vertices)
    for vertex, neighbours in adjacency.items():
        if any(n not in vertex_set for n in neighbours):
            raise ValueError(f"{vertex!r} refers to an unknown vertex")
    path = [start]
    visited = {start}

    def backtrack(current: Hashable) -> bool:
        if len(path) == len(vertices):
            return start in adjacency[current]
        for neighbour in adjacency[current]:
            if neighbour not in visited:
                visited.add(neighbour)
                path.append(neighbour)
                if backtrack(neighbour):
                    return True
                path.pop()
                visited.remove(neighbour)
        return False
    return path + [start] if backtrack(start) else None


if __name__ == "__main__":
    adjacency = {
        "Warehouse": ["A", "C"],
        "A": ["Warehouse", "B"],
        "B": ["A", "C"],
        "C": ["B", "Warehouse"],
    }
    cycle = find_hamiltonian_cycle(adjacency, "Warehouse")
    print("Unit 4 — Hamiltonian Cycle")
    print("Closed tour:", " -> ".join(cycle) if cycle else "No Hamiltonian cycle")
