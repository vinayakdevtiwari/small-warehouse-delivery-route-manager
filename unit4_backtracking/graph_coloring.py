"""Backtracking graph colouring for delivery-slot conflict constraints.

Project fit: supporting scheduling demonstrator. Colours can represent delivery
time slots or vehicle groups when the app has explicit zone-conflict rules.
"""
from __future__ import annotations
from typing import Hashable, Mapping, Sequence


def color_graph(adjacency: Mapping[Hashable, Sequence[Hashable]], colors: Sequence[str]) -> dict[Hashable, str] | None:
    """Assign distinct colours to adjacent vertices, or return None."""
    if not colors:
        raise ValueError("at least one colour/slot is required")
    vertices = list(adjacency)
    vertex_set = set(vertices)
    for vertex, neighbours in adjacency.items():
        if any(n not in vertex_set for n in neighbours):
            raise ValueError(f"{vertex!r} refers to an unknown neighbour")
    order = sorted(vertices, key=lambda v: len(set(adjacency[v])), reverse=True)
    assigned: dict[Hashable, str] = {}

    def backtrack(index: int) -> bool:
        if index == len(order):
            return True
        vertex = order[index]
        forbidden = {assigned[n] for n in adjacency[vertex] if n in assigned}
        for color in colors:
            if color not in forbidden:
                assigned[vertex] = color
                if backtrack(index + 1):
                    return True
                del assigned[vertex]
        return False
    return dict(assigned) if backtrack(0) else None


if __name__ == "__main__":
    conflicts = {
        "North Zone": ["Central Zone"],
        "Central Zone": ["North Zone", "South Zone"],
        "South Zone": ["Central Zone"],
        "Remote Zone": [],
    }
    print("Unit 4 — Graph Colouring / Delivery Slot Scheduling")
    print(color_graph(conflicts, ["Morning", "Afternoon"]))
