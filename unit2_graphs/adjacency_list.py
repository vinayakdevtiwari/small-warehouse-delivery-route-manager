"""Weighted adjacency-list graph for a sparse delivery network."""
from __future__ import annotations

from typing import Generic, Hashable, Iterator, TypeVar

V = TypeVar("V", bound=Hashable)


class AdjacencyListGraph(Generic[V]):
    """Weighted graph stored as a vertex-to-neighbour dictionary.

    add_vertex is O(1) average; add/remove/has_edge are O(1) average;
    enumerating a vertex's neighbours is O(degree). Memory is O(V + E), making
    it appropriate for a sparse set of possible delivery routes.
    """

    def __init__(self, *, directed: bool = False) -> None:
        self.directed = directed
        self._adjacency: dict[V, dict[V, float]] = {}

    @property
    def vertices(self) -> tuple[V, ...]:
        return tuple(self._adjacency)

    def add_vertex(self, vertex: V) -> None:
        """Add a unique location: O(1) average."""
        if vertex in self._adjacency:
            raise KeyError(f"vertex already exists: {vertex!r}")
        self._adjacency[vertex] = {}

    def add_edge(self, source: V, destination: V, weight: float) -> None:
        """Create or replace a weighted route: O(1) average."""
        self._validate_edge(source, destination, weight)
        self._adjacency[source][destination] = weight
        if not self.directed:
            self._adjacency[destination][source] = weight

    def remove_edge(self, source: V, destination: V) -> None:
        """Remove a route: O(1) average."""
        self._validate_vertices(source, destination)
        if destination not in self._adjacency[source]:
            raise KeyError("edge does not exist")
        del self._adjacency[source][destination]
        if not self.directed:
            del self._adjacency[destination][source]

    def has_edge(self, source: V, destination: V) -> bool:
        """Test whether a route exists: O(1) average."""
        self._validate_vertices(source, destination)
        return destination in self._adjacency[source]

    def weight(self, source: V, destination: V) -> float:
        """Return a route distance/cost: O(1) average."""
        self._validate_vertices(source, destination)
        try:
            return self._adjacency[source][destination]
        except KeyError as error:
            raise KeyError("edge does not exist") from error

    def neighbours(self, vertex: V) -> Iterator[tuple[V, float]]:
        """Yield adjacent (location, weight) pairs: O(degree)."""
        if vertex not in self._adjacency:
            raise KeyError(f"unknown vertex: {vertex!r}")
        yield from self._adjacency[vertex].items()

    def edges(self) -> Iterator[tuple[V, V, float]]:
        """Yield each logical edge once: O(V + E)."""
        seen: set[frozenset[V]] = set()
        for source, destinations in self._adjacency.items():
            for destination, weight in destinations.items():
                identity = frozenset((source, destination))
                if self.directed or identity not in seen:
                    yield source, destination, weight
                    seen.add(identity)

    def display(self) -> str:
        """Return a readable adjacency-list representation."""
        lines = []
        for vertex, destinations in self._adjacency.items():
            rendered = ", ".join(f"{destination} ({weight})" for destination, weight in destinations.items())
            lines.append(f"{vertex}: {rendered or '-'}")
        return "\n".join(lines)

    def _validate_vertices(self, source: V, destination: V) -> None:
        if source not in self._adjacency or destination not in self._adjacency:
            raise KeyError("both vertices must be added before adding an edge")

    def _validate_edge(self, source: V, destination: V, weight: float) -> None:
        self._validate_vertices(source, destination)
        if not isinstance(weight, (int, float)) or isinstance(weight, bool) or weight < 0:
            raise ValueError("weight must be a non-negative number")


if __name__ == "__main__":
    network = AdjacencyListGraph[str](directed=False)
    for location in ("Warehouse A", "Warehouse C", "Customer 3", "Customer 4"):
        network.add_vertex(location)
    network.add_edge("Warehouse A", "Customer 3", 5.5)
    network.add_edge("Warehouse C", "Customer 3", 7.0)
    network.add_edge("Warehouse C", "Customer 4", 3.5)
    print("Simulated delivery-distance adjacency list (km):")
    print(network.display())
    print("Warehouse C routes:", list(network.neighbours("Warehouse C")))
    network.remove_edge("Warehouse C", "Customer 3")
    print("After closing C-Customer 3 route:", network.display())
