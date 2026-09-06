# Project Guide: DSA-II Foundation

## Folder structure

```text
DSA-PBL/
├── README.md
├── PROJECT_GUIDE.md
├── unit1_trees/
│   ├── binary_tree.py
│   ├── bst.py
│   ├── binary_heap.py
│   ├── threaded_binary_tree.py
│   ├── avl_tree.py
│   ├── priority_queue.py
│   └── heap_sort.py
└── unit2_graphs/
    ├── adjacency_matrix.py
    ├── adjacency_list.py
    └── README.md
```

All `__main__` examples use simulated labels and values. They are separate from
the reusable classes, so they can be removed or changed without affecting the
project code.

## Unit 1 modules

### `BinaryTree`

`BinaryTreeNode` holds a value and two child references. `BinaryTree` inserts
values in level order, then provides `contains`, `level_order`, `inorder`,
`preorder`, and `postorder`. This is a general syllabus implementation; it is
not a natural primary data structure for product lookup because it does not
sort keys. It could model a fixed hierarchy such as a warehouse department
layout, if that becomes useful.

### `BinarySearchTree`

`BSTNode` holds a sortable key (such as a product ID), its value (such as a
product record), and child links. `BinarySearchTree.insert`, `search`,
`get`, `update`, `delete`, and `inorder_items` implement an unbalanced ordered
map. Delete handles leaf, one-child, and two-child nodes; the latter replaces
the node with its inorder successor. This is directly applicable to an
inventory index. Store a product dictionary or `Product` object as the value;
then update its stock with `update(product_id, changed_record)`.

### `BinaryHeap`

`BinaryHeap` is an array-backed min- or max-heap. `push` inserts an item,
`pop` removes the root-priority item, `peek` reads it, and `to_list` exposes a
safe copy of the heap-array order. It is directly applicable to prioritised
deliveries; use the min-heap when a lower number means greater urgency.

### `PriorityQueue`

`PriorityQueue` wraps `BinaryHeap` and adds delivery-friendly behaviour.
`enqueue(item, priority)`, `dequeue()`, and `peek()` return a `QueueEntry`
containing the priority and order. It is stable: orders with the same priority
are processed in the order received. This is directly applicable to a dispatch
queue; for example, priority 1 can mean urgent/medical, 2 fragile, and 3
normal. The numerical rules belong in the eventual application layer, not the
data structure.

### `heap_sort`

`heap_sort(items, key=..., reverse=...)` builds a max-heap in the supplied
mutable sequence and sorts it in place. The `key` argument makes it useful for
lists of records: `key=lambda p: p["stock"]` sorts products by stock. This is
directly applicable for stock, price, quantity, or delivery-priority reports.
It is intentionally not stable, so use Python's stable `sorted` only when
preserving original order for tied values is a requirement outside the DSA
exercise.

### `ThreadedBinarySearchTree`

`ThreadedNode` has a `right_is_thread` flag. When it has no ordinary right
child, `right` can refer to its inorder successor. `insert`, `contains`, and
`inorder` demonstrate this. Its inorder traversal does not use recursion or a
stack. It is a genuine syllabus implementation but not necessary for this PBL;
the normal BST or AVL tree is clearer for product records.

### `AVLTree`

`AVLNode` includes its `height`. `AVLTree` implements `insert`, `search`,
`update`, `delete`, and `inorder_items`, with automatic single/double rotations
through `_rotate_left`, `_rotate_right`, and `_rebalance`. This is a strong
alternative to the plain BST when product IDs may arrive in sorted order and
consistent search speed matters. It is project-capable, but it is reasonable
to start with `BinarySearchTree` for a 20–50-product system because it is
easier to explain.

## Unit 2 modules

### `AdjacencyMatrixGraph`

Locations are added by `add_vertex`. `add_edge(source, destination, weight)`
stores a non-negative route distance/cost; `remove_edge`, `has_edge`, `weight`,
`neighbours`, `edges`, and `display` read or modify it. Pass `directed=False`
for two-way roads or `directed=True` for one-way streets. This is directly
applicable to 2–3 warehouses and 8–12 delivery locations. Matrix lookup is
particularly convenient for checking a route between any selected pair.

### `AdjacencyListGraph`

It has the same public purpose and nearly the same API as the matrix graph,
but each vertex stores only its actual outgoing routes. This makes it a better
fit for a sparse delivery map. It is directly applicable to the PBL; choose
one graph representation as the primary implementation, then retain the other
as a syllabus comparison.

## Time complexity reference

| Structure | Operation | Expected time |
|---|---|---:|
| Binary tree | level-order insert / search | O(n) |
| Binary tree | any traversal | O(n) |
| BST | search, insert, update, delete | O(h): average O(log n), worst O(n) |
| BST | inorder traversal | O(n) |
| Binary heap | build from iterable | O(n) |
| Binary heap | push / pop | O(log n) |
| Binary heap | peek | O(1) |
| Priority queue | enqueue / dequeue | O(log n) |
| Priority queue | peek | O(1) |
| Heap sort | sort | O(n log n), O(1) auxiliary space |
| Threaded BST | insert / search | O(h): average O(log n), worst O(n) |
| Threaded BST | inorder traversal | O(n), O(1) auxiliary space |
| AVL tree | search, insert, update, delete | O(log n) worst case |
| AVL tree | inorder traversal | O(n) |
| Matrix graph | add vertex | O(V²) |
| Matrix graph | add/remove/check edge, read weight | O(1) |
| Matrix graph | neighbours / all edges | O(V) / O(V²) |
| List graph | add vertex / add-remove-check edge / weight | O(1) average |
| List graph | neighbours / all edges | O(degree) / O(V+E) |

`h` is the current tree height; `V` is vertices and `E` is edges.

## Suggested integration later

1. Create a `Product` record (ID, name, stock, warehouse ID) and store it in
   `BinarySearchTree` or `AVLTree` by ID.
2. Put incoming delivery orders into `PriorityQueue`; define a documented
   priority policy in the application layer.
3. Add each warehouse and customer location to `AdjacencyListGraph` (sparse)
   or `AdjacencyMatrixGraph` (dense), then add road distance/cost edges.
4. When graph algorithms are covered, implement Dijkstra against the existing
   `neighbours`/`weight` API to select a shortest delivery route. Do not call a
   direct edge the "shortest route" before Dijkstra or equivalent is added.
5. Use `heap_sort` when displaying inventory or order reports.

## Exact evidence screenshots

Open a terminal in `DSA-PBL`, then run each command below. Screenshot the
named source file alongside the terminal output, so the evidence shows both
the actual implementation and its generated result.

1. `python -m unit1_trees.bst` — screenshot `unit1_trees/bst.py` around
   `insert`, `search`, `update`, and `delete`, with its terminal output.
   Caption: **Unit 1 — BST product ID search and inventory update.**
2. `python -m unit1_trees.priority_queue` — screenshot
   `unit1_trees/priority_queue.py` and priority-ordered dispatch output.
   Caption: **Unit 1 — Stable priority queue for delivery orders.**
3. `python -m unit1_trees.heap_sort` — screenshot `heap_sort.py` and sorted
   simulated product list. Caption: **Unit 1 — Heap sort by stock quantity.**
4. `python -m unit1_trees.avl_tree` — screenshot `avl_tree.py` and ordered
   output. Caption: **Unit 1 — AVL balancing for an indexed inventory.**
5. `python -m unit2_graphs.adjacency_matrix` — screenshot
   `adjacency_matrix.py` and the matrix/distance output. Caption:
   **Unit 2 — Weighted adjacency matrix of warehouse delivery routes.**
6. `python -m unit2_graphs.adjacency_list` — screenshot
   `adjacency_list.py` and output both before and after the removed route.
   Caption: **Unit 2 — Weighted adjacency list and route update.**
7. Optional syllabus evidence: run `binary_tree`, `binary_heap`, and
   `threaded_binary_tree` demos and take one screenshot for each if Unit 1
   coverage requires all listed tree variants.

If `python` is not on your Windows PATH, run the same commands with the Python
installation command configured in your IDE (for example, `py -m ...`).

## Add later when covered in the syllabus

- BFS and DFS for reachability/route exploration.
- Dijkstra for non-negative shortest delivery distances or costs.
- Prim and Kruskal for a minimum-cost network design exercise.
- Bellman-Ford if a future cost model permits negative edges (ordinary road
  distances should remain non-negative).
- Floyd-Warshall for all-pairs warehouse/location precomputation on the small
  map.
- A domain layer: `Product`, `Warehouse`, `DeliveryOrder`, persistence, and a
  menu or GUI. Keep these separate from the core DSA modules.
