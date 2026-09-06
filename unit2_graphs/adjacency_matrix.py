"""Weighted adjacency-matrix graph for a compact delivery network."""
from __future__ import annotations

from typing import Generic, Hashable, Iterator, TypeVar

V = TypeVar("V", bound=Hashable)


class AdjacencyMatrixGraph(Generic[V]):
    """Weighted graph represented by a square matrix.

    add_vertex is O(V^2) because rows grow; add/remove/has_edge are O(1).
    Enumerating neighbours is O(V), and memory use is O(V^2). This suits a
    small, dense network such as 2–3 warehouses plus 8–12 destinations.
    """

    def __init__(self, *, directed: bool = False) -> None:
        self.directed = directed
        self._vertices: list[V] = []
        self._index: dict[V, int] = {}
        self._matrix: list[list[float | None]] = []

    @property
    def vertices(self) -> tuple[V, ...]:
        return tuple(self._vertices)

    def add_vertex(self, vertex: V) -> None:
        """Add a unique location: O(V^2)."""
        if vertex in self._index:
            raise KeyError(f"vertex already exists: {vertex!r}")
        self._index[vertex] = len(self._vertices)
        self._vertices.append(vertex)
        for row in self._matrix:
            row.append(None)
        self._matrix.append([None] * len(self._vertices))

    def add_edge(self, source: V, destination: V, weight: float) -> None:
        """Create or replace a weighted route: O(1)."""
        self._validate_edge(source, destination, weight)
        self._matrix[self._index[source]][self._index[destination]] = weight
        if not self.directed:
            self._matrix[self._index[destination]][self._index[source]] = weight

    def remove_edge(self, source: V, destination: V) -> None:
        """Remove a route; raises KeyError if it does not exist: O(1)."""
        self._validate_vertices(source, destination)
        if not self.has_edge(source, destination):
            raise KeyError("edge does not exist")
        self._matrix[self._index[source]][self._index[destination]] = None
        if not self.directed:
            self._matrix[self._index[destination]][self._index[source]] = None

    def has_edge(self, source: V, destination: V) -> bool:
        """Test whether a route exists: O(1)."""
        self._validate_vertices(source, destination)
        return self._matrix[self._index[source]][self._index[destination]] is not None

    def weight(self, source: V, destination: V) -> float:
        """Return a route distance/cost: O(1)."""
        self._validate_vertices(source, destination)
        value = self._matrix[self._index[source]][self._index[destination]]
        if value is None:
            raise KeyError("edge does not exist")
        return value

    def neighbours(self, vertex: V) -> Iterator[tuple[V, float]]:
        """Yield adjacent (location, weight) pairs: O(V)."""
        if vertex not in self._index:
            raise KeyError(f"unknown vertex: {vertex!r}")
        for index, weight in enumerate(self._matrix[self._index[vertex]]):
            if weight is not None:
                yield self._vertices[index], weight

    def edges(self) -> Iterator[tuple[V, V, float]]:
        """Yield each logical edge once (twice only for directed reverse routes): O(V^2)."""
        for source_index, source in enumerate(self._vertices):
            for destination_index, weight in enumerate(self._matrix[source_index]):
                if weight is not None and (self.directed or source_index <= destination_index):
                    yield source, self._vertices[destination_index], weight

    def display(self) -> str:
        """Return a human-readable matrix; no route is shown as `-`."""
        labels = [str(vertex) for vertex in self._vertices]
        width = max(8, *(len(label) + 1 for label in labels)) if labels else 8
        lines = ["".ljust(width) + "".join(label.rjust(width) for label in labels)]
        for vertex, row in zip(labels, self._matrix):
            values = ("-" if weight is None else str(weight) for weight in row)
            lines.append(vertex.ljust(width) + "".join(value.rjust(width) for value in values))
        return "\n".join(lines)

    def _validate_vertices(self, source: V, destination: V) -> None:
        if source not in self._index or destination not in self._index:
            raise KeyError("both vertices must be added before adding an edge")

    def _validate_edge(self, source: V, destination: V, weight: float) -> None:
        self._validate_vertices(source, destination)
        if not isinstance(weight, (int, float)) or isinstance(weight, bool) or weight < 0:
            raise ValueError("weight must be a non-negative number")


if __name__ == "__main__":
    network = AdjacencyMatrixGraph[str](directed=False)
    for location in ("Warehouse A", "Warehouse B", "Customer 1", "Customer 2"):
        network.add_vertex(location)
    network.add_edge("Warehouse A", "Customer 1", 6.5)
    network.add_edge("Warehouse A", "Customer 2", 9.0)
    network.add_edge("Warehouse B", "Customer 2", 4.0)
    print("Simulated delivery-distance matrix (km):")
    print(network.display())
    print("A to Customer 1 connected:", network.has_edge("Warehouse A", "Customer 1"))
    print("A to Customer 1 distance:", network.weight("Warehouse A", "Customer 1"), "km")
