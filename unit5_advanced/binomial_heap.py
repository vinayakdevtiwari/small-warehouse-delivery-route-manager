"""Binomial min-heap for advanced priority-queue study.

Priority is the first comparable value in each key (for example (priority, id)).
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Generic, Optional, TypeVar

T = TypeVar("T")


@dataclass
class _Node(Generic[T]):
    key: T
    degree: int = 0
    parent: Optional["_Node[T]"] = None
    child: Optional["_Node[T]"] = None
    sibling: Optional["_Node[T]"] = None


class BinomialHeap(Generic[T]):
    """Binomial min-heap with insert, peek_min and extract_min operations."""
    def __init__(self) -> None:
        self.head: Optional[_Node[T]] = None
        self.size = 0

    @staticmethod
    def _merge_roots(a: Optional[_Node[T]], b: Optional[_Node[T]]) -> Optional[_Node[T]]:
        dummy: _Node[T] = _Node(None)  # type: ignore[arg-type]
        tail = dummy
        while a is not None and b is not None:
            if a.degree <= b.degree:
                nxt, a = a, a.sibling
            else:
                nxt, b = b, b.sibling
            tail.sibling = nxt
            tail = nxt
        tail.sibling = a if a is not None else b
        return dummy.sibling

    @staticmethod
    def _link(child: _Node[T], parent: _Node[T]) -> None:
        child.parent = parent
        child.sibling = parent.child
        parent.child = child
        parent.degree += 1

    def _union(self, other_head: Optional[_Node[T]]) -> None:
        self.head = self._merge_roots(self.head, other_head)
        if self.head is None:
            return
        prev: Optional[_Node[T]] = None
        current = self.head
        nxt = current.sibling
        while nxt is not None:
            if current.degree != nxt.degree or (
                nxt.sibling is not None and nxt.sibling.degree == current.degree
            ):
                prev, current = current, nxt
            elif current.key <= nxt.key:
                current.sibling = nxt.sibling
                self._link(nxt, current)
            else:
                if prev is None:
                    self.head = nxt
                else:
                    prev.sibling = nxt
                self._link(current, nxt)
                current = nxt
            nxt = current.sibling

    def insert(self, key: T) -> None:
        node = _Node(key)
        self._union(node)
        self.size += 1

    def peek_min(self) -> T:
        if self.head is None:
            raise IndexError("peek from empty binomial heap")
        best = self.head.key
        node = self.head.sibling
        while node is not None:
            if node.key < best:
                best = node.key
            node = node.sibling
        return best

    def extract_min(self) -> T:
        if self.head is None:
            raise IndexError("extract from empty binomial heap")
        min_prev: Optional[_Node[T]] = None
        min_node = self.head
        prev: Optional[_Node[T]] = None
        node = self.head
        while node is not None:
            if node.key < min_node.key:
                min_node, min_prev = node, prev
            prev, node = node, node.sibling
        if min_prev is None:
            self.head = min_node.sibling
        else:
            min_prev.sibling = min_node.sibling
        child = min_node.child
        reversed_children: Optional[_Node[T]] = None
        while child is not None:
            nxt = child.sibling
            child.parent = None
            child.sibling = reversed_children
            reversed_children = child
            child = nxt
        self._union(reversed_children)
        self.size -= 1
        return min_node.key

    def __len__(self) -> int:
        return self.size


if __name__ == "__main__":
    heap: BinomialHeap[tuple[int, str]] = BinomialHeap()
    for order in [(3, "ORD-103"), (1, "ORD-101"), (2, "ORD-102"), (1, "ORD-104")]:
        heap.insert(order)
    print("Unit 5 — Binomial Heap dispatch priority")
    while len(heap):
        print("Next:", heap.extract_min())
