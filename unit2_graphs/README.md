# Unit 2: Graphs

The graph modules use simulated locations and non-negative route distances.

- `AdjacencyMatrixGraph`: O(V²) storage; O(1) route/weight lookup.
- `AdjacencyListGraph`: O(V+E) storage; efficient neighbour iteration for a sparse delivery network.
- `bfs.py`, `dfs.py`, `connected_components.py`, `spanning_tree.py`, `prim.py`, `kruskal.py`, `transitive_closure.py`, `dijkstra.py`, `bellman_ford.py`, `floyd_warshall.py`: standalone graph algorithm implementations and simulated verification examples.

## Integration in the application

The Streamlit app uses `AdjacencyListGraph` and `dijkstra_shortest_path` in the actual order flow. When an order is placed, it checks which warehouses have enough stock, calculates a route to the destination from each eligible warehouse, selects the lowest-distance eligible option, and reserves stock inside a SQLite transaction.

The Route Planner tab also supports a small multi-stop closed tour: Dijkstra computes shortest-path distances between selected stops, then the Unit 4 Branch & Bound TSP module optimizes their visiting order.

Other graph algorithms remain reusable DSA demonstrations. Prim and Kruskal compute minimum spanning trees (network design), not source-to-destination shortest paths. Bellman-Ford is included for negative-edge/negative-cycle study; actual route distances should remain non-negative.

## Running examples

Run from the repository root:

```powershell
python -m unit2_graphs.adjacency_list
python -m unit2_graphs.adjacency_matrix
python -m unit2_graphs.dijkstra
python -m unittest discover -s tests -v
```
