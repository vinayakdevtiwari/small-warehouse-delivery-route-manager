"""Fibonacci min-heap supporting insert, minimum and extract_min.

Included as an advanced Unit 5 priority-queue implementation. It demonstrates
amortized-efficient heap operations; the production-sized PBL may keep the
simpler stable BinaryHeap priority queue as its primary dispatch structure.
"""
from __future__ import annotations
from dataclasses import dataclass
from math import inf
from typing import Generic, Optional, TypeVar

T = TypeVar("T")


@dataclass
class _Node(Generic[T]):
    key: T
    degree: int = 0
    mark: bool = False
    parent: Optional["_Node[T]"] = None
    child: Optional["_Node[T]"] = None
    left: Optional["_Node[T]"] = None
    right: Optional["_Node[T]"] = None

    def __post_init__(self) -> None:
        self.left = self.right = self


class FibonacciHeap(Generic[T]):
    """Fibonacci min-heap, with circular doubly-linked root and child lists."""
    def __init__(self) -> None:
        self.minimum_node: Optional[_Node[T]] = None
        self.size = 0

    def __len__(self) -> int:
        return self.size

    def is_empty(self) -> bool:
        return self.minimum_node is None

    @staticmethod
    def _remove(node: _Node[T]) -> None:
        assert node.left is not None and node.right is not None
        node.left.right = node.right
        node.right.left = node.left
        node.left = node.right = node

    @staticmethod
    def _insert_before(reference: _Node[T], node: _Node[T]) -> None:
        assert reference.left is not None
        node.left = reference.left
        node.right = reference
        reference.left.right = node
        reference.left = node

    def _add_root(self, node: _Node[T]) -> None:
        node.parent = None
        node.mark = False
        if self.minimum_node is None:
            node.left = node.right = node
            self.minimum_node = node
        else:
            self._insert_before(self.minimum_node, node)
            if node.key < self.minimum_node.key:
                self.minimum_node = node

    def insert(self, key: T) -> None:
        self._add_root(_Node(key))
        self.size += 1

    def minimum(self) -> T:
        if self.minimum_node is None:
            raise IndexError("minimum from empty Fibonacci heap")
        return self.minimum_node.key

    @staticmethod
    def _iterate(start: Optional[_Node[T]]) -> list[_Node[T]]:
        if start is None:
            return []
        nodes = [start]
        current = start.right
        while current is not None and current is not start:
            nodes.append(current)
            current = current.right
        return nodes

    def _link(self, child: _Node[T], parent: _Node[T]) -> None:
        self._remove(child)
        child.parent = parent
        child.mark = False
        if parent.child is None:
            parent.child = child
            child.left = child.right = child
        else:
            self._insert_before(parent.child, child)
        parent.degree += 1

    def _consolidate(self) -> None:
        if self.minimum_node is None:
            return
        roots = self._iterate(self.minimum_node)
        for root in roots:
            root.left = root.right = root
        degree_table: list[Optional[_Node[T]]] = [None] * (self.size.bit_length() * 2 + 4)
        for root in roots:
            x = root
            d = x.degree
            while d >= len(degree_table):
                degree_table.extend([None] * len(degree_table))
            while degree_table[d] is not None:
                y = degree_table[d]
                assert y is not None
                if y.key < x.key:
                    x, y = y, x
                degree_table[d] = None
                self._link(y, x)
                d = x.degree
                while d >= len(degree_table):
                    degree_table.extend([None] * len(degree_table))
            degree_table[d] = x
        self.minimum_node = None
        for node in degree_table:
            if node is not None:
                node.left = node.right = node
                self._add_root(node)

    def extract_min(self) -> T:
        z = self.minimum_node
        if z is None:
            raise IndexError("extract from empty Fibonacci heap")
        if z.child is not None:
            children = self._iterate(z.child)
            for child in children:
                self._remove(child)
                child.parent = None
                self._add_root(child)
            z.child = None
            z.degree = 0
        next_root = z.right if z.right is not z else None
        self._remove(z)
        self.size -= 1
        if next_root is None:
            self.minimum_node = None
        else:
            self.minimum_node = next_root
            self._consolidate()
        return z.key


if __name__ == "__main__":
    heap: FibonacciHeap[tuple[int, str]] = FibonacciHeap()
    for order in [(3, "ORD-103"), (1, "ORD-101"), (2, "ORD-102"), (1, "ORD-104")]:
        heap.insert(order)
    print("Unit 5 — Fibonacci Heap dispatch priority")
    print("Current minimum:", heap.minimum())
    while len(heap):
        print("Next:", heap.extract_min())
