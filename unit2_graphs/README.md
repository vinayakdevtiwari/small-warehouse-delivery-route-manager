# Unit 2: Graph Representations

Both graphs accept any hashable location label and non-negative numeric edge
weights (for example kilometres or a calculated delivery cost). `directed=False`
models two-way roads; `directed=True` models one-way roads.

- `AdjacencyMatrixGraph`: O(V²) space, O(1) route lookup; a practical choice
  when the small network is fairly dense.
- `AdjacencyListGraph`: O(V+E) space and O(degree) neighbour scan; a practical
  choice when only some pairs have roads/routes.

Future algorithms can use `vertices`, `neighbours(vertex)`, `edges()`, and
`weight(source, destination)`. BFS, DFS, Dijkstra, Prim, Kruskal,
Bellman-Ford, and Floyd-Warshall have not yet been implemented.
