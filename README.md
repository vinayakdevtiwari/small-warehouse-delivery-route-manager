# Small Warehouse and Delivery Route Manager — DSA Foundation

This package contains reusable Python implementations for the DSA-II topics
covered so far.  The `if __name__ == "__main__"` blocks use **simulated**
warehouse data only; the data structures themselves do not depend on the
warehouse domain.

## Run the demos

From this `DSA-PBL` folder, run:

```powershell
python -m unit1_trees.bst
python -m unit1_trees.binary_heap
python -m unit1_trees.priority_queue
python -m unit1_trees.heap_sort
python -m unit1_trees.binary_tree
python -m unit1_trees.threaded_binary_tree
python -m unit1_trees.avl_tree
python -m unit2_graphs.adjacency_matrix
python -m unit2_graphs.adjacency_list
```

## Relevance to the PBL

Directly applicable: `BinarySearchTree` for keyed product records,
`BinaryHeap`/`PriorityQueue` for urgent delivery orders, `heap_sort` for
reports, and either graph representation for warehouses and delivery routes.

Learning implementations: `BinaryTree`, `ThreadedBinarySearchTree`, and
`AVLTree`. An AVL tree can replace the BST if consistently fast product lookup
is required; the other two are primarily useful for the Unit 1 syllabus.

The graph classes currently provide representations only. Their public vertex
and edge accessors intentionally make later BFS, DFS, Dijkstra, Prim, Kruskal,
Bellman-Ford, and Floyd-Warshall additions straightforward. Those algorithms
are **not** implemented in this submission.
