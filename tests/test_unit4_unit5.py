"""Unit tests for applicable Unit 4 and Unit 5 DSA-II implementations."""
import unittest

from unit4_backtracking.graph_coloring import color_graph
from unit4_backtracking.hamiltonian_cycle import find_hamiltonian_cycle
from unit4_backtracking.n_queens import solve_n_queens
from unit4_backtracking.sum_of_subsets import sum_of_subsets
from unit4_backtracking.tsp_branch_bound import tsp_branch_and_bound
from unit5_advanced.b_tree import BTree
from unit5_advanced.b_plus_tree import BPlusTree
from unit5_advanced.binomial_heap import BinomialHeap
from unit5_advanced.fibonacci_heap import FibonacciHeap
from unit5_advanced.red_black_tree import RedBlackTree


class Unit4Tests(unittest.TestCase):
    def test_tsp_branch_and_bound_finds_minimum_closed_tour(self):
        graph = {
            "W": {"A": 4, "B": 2, "C": 9},
            "A": {"W": 4, "B": 1, "C": 5},
            "B": {"W": 2, "A": 1, "C": 3},
            "C": {"W": 9, "A": 5, "B": 3},
        }
        route, cost = tsp_branch_and_bound(graph, "W")
        self.assertEqual(route[0], "W")
        self.assertEqual(route[-1], "W")
        self.assertEqual(set(route[:-1]), set(graph))
        self.assertAlmostEqual(cost, 14.0)

    def test_graph_coloring_respects_edges(self):
        adjacency = {"A": ["B"], "B": ["A", "C"], "C": ["B"]}
        assignment = color_graph(adjacency, ["AM", "PM"])
        self.assertIsNotNone(assignment)
        for u, neighbours in adjacency.items():
            for v in neighbours:
                self.assertNotEqual(assignment[u], assignment[v])

    def test_graph_coloring_returns_none_when_impossible(self):
        triangle = {"A": ["B", "C"], "B": ["A", "C"], "C": ["A", "B"]}
        self.assertIsNone(color_graph(triangle, ["AM", "PM"]))

    def test_hamiltonian_cycle(self):
        graph = {"W": ["A", "C"], "A": ["W", "B"], "B": ["A", "C"], "C": ["B", "W"]}
        cycle = find_hamiltonian_cycle(graph, "W")
        self.assertIsNotNone(cycle)
        self.assertEqual(cycle[0], cycle[-1])
        self.assertEqual(set(cycle[:-1]), set(graph))

    def test_sum_of_subsets(self):
        solutions = sum_of_subsets([2, 3, 5, 7, 8], 10)
        self.assertTrue(solutions)
        self.assertTrue(all(sum(s) == 10 for s in solutions))

    def test_n_queens_four_queens_has_two_solutions(self):
        self.assertEqual(len(solve_n_queens(4)), 2)


class Unit5Tests(unittest.TestCase):
    def test_red_black_tree_search_and_sorted_traversal(self):
        tree = RedBlackTree()
        for key in [40, 10, 30, 20, 50, 60, 5]:
            tree.insert(key, str(key))
        self.assertEqual(tree.search(30), "30")
        self.assertEqual([key for key, _ in tree.inorder_items()], [5, 10, 20, 30, 40, 50, 60])
        with self.assertRaises(KeyError):
            tree.search(99)

    def test_b_tree_split_search_and_range(self):
        tree = BTree(minimum_degree=2)
        keys = [15, 8, 22, 4, 11, 18, 25, 2, 6, 9, 13, 30, 27, 17, 19]
        for key in keys:
            tree.insert(key, f"SKU-{key}")
        self.assertEqual(tree.search(18), "SKU-18")
        self.assertEqual([k for k, _ in tree.range_search(8, 18)], sorted(k for k in keys if 8 <= k <= 18))

    def test_b_plus_tree_splits_and_range_queries(self):
        tree = BPlusTree(order=4)
        keys = [18, 4, 10, 2, 7, 15, 20, 25, 9, 12, 30, 1, 5, 8, 11, 14, 22]
        for key in keys:
            tree.insert(key, f"SKU-{key}")
        self.assertEqual(tree.search(15), "SKU-15")
        self.assertEqual([k for k, _ in tree.range_search(7, 20)], [7, 8, 9, 10, 11, 12, 14, 15, 18, 20])
        tree.insert(15, "SKU-15-UPDATED")
        self.assertEqual(tree.search(15), "SKU-15-UPDATED")

    def test_binomial_heap_extracts_in_order(self):
        heap = BinomialHeap()
        values = [(3, "C"), (1, "A"), (2, "B"), (1, "D"), (8, "H"), (4, "E")]
        for value in values:
            heap.insert(value)
        count = len(heap)
        self.assertEqual([heap.extract_min() for _ in range(count)], sorted(values))

    def test_fibonacci_heap_extracts_in_order(self):
        heap = FibonacciHeap()
        values = [(3, "C"), (1, "A"), (2, "B"), (1, "D"), (8, "H"), (4, "E")]
        for value in values:
            heap.insert(value)
        count = len(heap)
        self.assertEqual([heap.extract_min() for _ in range(count)], sorted(values))


if __name__ == "__main__":
    unittest.main()
