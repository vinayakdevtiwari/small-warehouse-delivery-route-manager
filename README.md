# Small Warehouse and Delivery Route Manager

**DSA-II PBL · Python · Streamlit · SQLite**

An educational warehouse and delivery management prototype that demonstrates how data structures and algorithms can support product lookup, warehouse stock checks, dispatch prioritization, weighted route planning and vehicle-capacity decisions. Initial records and route distances are simulated for academic use.

## Run the application locally

Use Python 3.10 or newer. From the repository root:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

The application opens in your browser. SQLite creates a local database under `data/` on first run. The database is intentionally gitignored.

## Application features

- **Inventory:** Product catalog, stock by warehouse, stock adjustments, add products, Red-Black Tree search and B+ Tree product-ID range queries.
- **Order processing:** Validates quantity, checks warehouse stock, calculates routes with Dijkstra, selects the closest eligible warehouse, and reserves stock transactionally.
- **Dispatch:** Uses the existing stable binary-heap Priority Queue to display urgent orders first; supports Confirmed → Dispatched → Delivered and cancellation of Confirmed orders with stock restoration.
- **Route planner:** Dijkstra shortest path for a single delivery and Unit 4 TSP with Branch & Bound for a small closed multi-stop tour.
- **Vehicle capacity:** 0/1 Knapsack selects a high-value combination of confirmed orders from one warehouse within the selected vehicle capacity.
- **DSA Concept Lab:** Demonstrations for graph colouring, Hamiltonian cycle, sum of subsets, N-Queens, B-Tree and advanced heap extraction.

## DSA-II mapping

| Unit | Topics | Project role |
|---|---|---|
| 1 | BST, AVL, Binary Heap, Priority Queue, Heap Sort, Threaded Tree | Existing reusable modules; Priority Queue is used by dispatch |
| 2 | Matrix/List, BFS, DFS, Connected Components, Spanning Tree, Prim, Kruskal, Transitive Closure, Dijkstra, Bellman-Ford, Floyd-Warshall | Existing modules; Dijkstra is used for single-order route calculation |
| 3 | 0/1 Knapsack, LCS, Matrix Chain Multiplication, Resource Allocation | Existing DP modules; Knapsack is used by vehicle-capacity planner |
| 4 | TSP with Branch & Bound, Graph Colouring, Hamiltonian Cycle, Sum of Subsets, N-Queens | TSP is used by multi-stop route planning; other concepts are standalone scheduling/learning demonstrations |
| 5 | Red-Black Tree, B-Tree, B+ Tree, Binomial Heap, Fibonacci Heap | Red-Black and B+ Tree support product indexing/range scans; B-Tree and advanced heaps are demonstrated in the DSA Lab |

## Important boundaries

- Dijkstra requires non-negative route weights.
- TSP is exponential; the UI caps the tour at the starting warehouse plus six stops and uses shortest-path distances between selected stops.
- The Knapsack planner considers confirmed orders assigned to a single warehouse. It recommends a load; dispatching selected orders changes their status to Dispatched.
- Binomial and Fibonacci heaps are available for Unit 5 study; the operational dispatch queue uses the simpler stable binary heap.
- N-Queens is a standalone syllabus demonstration, not a warehouse function.
- This academic prototype is not connected to live GPS, Google Maps, traffic feeds or real logistics services.

## Repository layout

```text
unit1_trees/                 Unit 1 trees and heaps
unit2_graphs/                Unit 2 graph representations and algorithms
unit3_dynamic_programming/   Unit 3 DP algorithms
unit4_backtracking/          Unit 4 backtracking / Branch & Bound
unit5_advanced/              Unit 5 advanced trees and heaps
warehouse_app/               SQLite persistence and application services
tests/                       Unit 4 / Unit 5 algorithm tests
app.py                       Streamlit interface
requirements.txt             Runtime dependencies
```

## Run tests

```bash
python -m unittest discover -s tests -v
```

Author: Vinayak Dev Tiwari. This project applies standard DSA-II concepts to a simulated small-warehouse problem; it does not claim to invent new algorithms or reproduce the referenced research papers.
