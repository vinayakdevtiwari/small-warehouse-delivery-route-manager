# Project Guide — Small Warehouse and Delivery Route Manager

**Course:** Data Structures and Algorithms-II (CCSE0301)  
**Implementation:** Python, Streamlit, SQLite  
**Data:** Simulated warehouse, stock, location and route records for an academic prototype.

## 1. Run the project

From the repository root, with Python 3.10+ installed:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

SQLite creates `data/warehouse_manager.sqlite3` the first time the app runs. The DB file is gitignored; source code and tests remain in GitHub.

Run tests:

```powershell
python -m unittest discover -s tests -v
```

## 2. Actual end-to-end workflow

1. User chooses a product, quantity, destination and delivery priority.
2. The service checks stock at each warehouse for that product.
3. For every warehouse that can fulfil the quantity, Dijkstra calculates the lowest-distance path to the destination.
4. The nearest eligible warehouse is chosen; the stock reservation and order record are written transactionally. Failed orders do not reserve stock.
5. The stable Unit 1 Priority Queue orders confirmed shipments by priority (1 is highest; arrival order breaks ties).
6. Dispatch changes order status from Confirmed to Dispatched; delivery changes it to Delivered. Cancelling a Confirmed order restores its reserved stock.
7. The capacity planner runs 0/1 Knapsack on confirmed orders assigned to one warehouse and suggests a payload that maximizes listed order value within the entered integer capacity.
8. The multi-stop route planner calculates shortest-path distances between the selected stops, then uses the Unit 4 Branch & Bound TSP implementation to find a low-distance closed tour.

## 3. DSA-II topic mapping

### Unit 1 — Trees and heaps
- **BST:** ordered product-key lookup demonstration and general inventory-index concept.
- **AVL Tree:** self-balancing key/value index implementation for comparing balanced and unbalanced lookup.
- **Binary Heap / Priority Queue:** the stable priority queue is used by the dispatch queue.
- **Heap Sort:** standalone sorting/report example.
- **Threaded Binary Tree / Binary Tree:** retained as syllabus demonstrations; they are not forced into the order workflow.

### Unit 2 — Graphs
- **Adjacency List:** primary in-app route network; each location is a vertex and each route is a weighted edge.
- **Adjacency Matrix:** alternative representation demonstration.
- **Dijkstra:** used by the actual order creation and single-route planner; edge weights are non-negative kilometres.
- **BFS / DFS / Connected Components / Transitive Closure:** graph exploration and reachability demos.
- **Prim / Kruskal / Spanning Tree:** minimum-cost network design demonstrations, not shortest-route algorithms.
- **Bellman-Ford / Floyd-Warshall:** alternate shortest-path demonstrations and algorithm comparison.

### Unit 3 — Dynamic Programming
- **0/1 Knapsack:** integrated in the vehicle-capacity planner to choose a high-value subset of confirmed orders from one warehouse.
- **LCS:** sequence comparison demo.
- **Matrix Chain Multiplication / Resource Allocation:** supporting DP demonstrations.

### Unit 4 — Backtracking and Branch & Bound
- **TSP with Branch & Bound:** integrated into multi-stop tour planning. The UI limits the tour to the start plus at most six other stops because the search is exponential.
- **Graph Colouring:** standalone delivery-slot conflict demo; real deployment-zone conflict rules would need real business requirements.
- **Hamiltonian Cycle:** standalone closed-cycle feasibility demo; it does not optimize total distance.
- **Sum of Subsets:** finds exact-weight combinations; Knapsack is used for best-value under capacity.
- **N-Queens:** syllabus demonstration only, not a warehouse feature.

### Unit 5 — Advanced data structures
- **Red-Black Tree:** product lookup index used in the Inventory UI.
- **B+ Tree:** product-ID range query index used in the Inventory UI.
- **B-Tree:** product lookup/range demonstration in the DSA Concept Lab.
- **Binomial Heap / Fibonacci Heap:** standalone advanced priority queue implementations and demonstrations. The actual dispatch queue retains the simpler stable binary heap, which is easier to maintain for this small scope.

## 4. Key implementation boundaries

- SQLite is the source of truth for inventory and order status; in-memory tree indexes are rebuilt from product records.
- Stock quantities are non-negative and order placement reserves stock inside an immediate transaction.
- Dijkstra only operates on non-negative weights.
- The TSP route is a closed tour (returns to its start), built from Dijkstra shortest-path distances among selected stops.
- Knapsack's "value" is the stored illustrative order value, not a guarantee of profit.
- The system is not connected to live maps, GPS, traffic, real customers, or commercial logistics services.
- This project applies standard DSA algorithms; it does not claim to invent new algorithms or reproduce the referenced research papers.

## 5. Verification

Automated tests cover Unit 4 algorithm solutions, Unit 5 tree/heap ordering, order stock reservation and restoration, priority queue ordering, capacity bounds, multi-stop route closure and Streamlit app startup. CI runs compile checks and the test suite on pushes to the development branch and on pull requests into main.
