"""B+ Tree for ordered product-ID lookup and inventory range queries.

Records live in linked leaves; internal nodes contain separator keys.
"""
from __future__ import annotations
from bisect import bisect_left, bisect_right
from dataclasses import dataclass, field
from typing import Generic, Iterator, Optional, TypeVar

K = TypeVar("K")
V = TypeVar("V")


@dataclass
class _Node(Generic[K, V]):
    leaf: bool
    keys: list[K] = field(default_factory=list)
    values: list[V] = field(default_factory=list)
    children: list["_Node[K, V]"] = field(default_factory=list)
    next: Optional["_Node[K, V]"] = None


class BPlusTree(Generic[K, V]):
    """B+ Tree with a configurable maximum number of children per internal node."""
    def __init__(self, order: int = 4) -> None:
        if order < 3:
            raise ValueError("order must be at least 3")
        self.order = order
        self.root: _Node[K, V] = _Node(leaf=True)

    def search(self, key: K) -> V:
        leaf = self._find_leaf(key)
        i = bisect_left(leaf.keys, key)
        if i < len(leaf.keys) and leaf.keys[i] == key:
            return leaf.values[i]
        raise KeyError(f"key not found: {key!r}")

    def insert(self, key: K, value: V) -> None:
        split = self._insert(self.root, key, value)
        if split is not None:
            separator, right = split
            self.root = _Node(leaf=False, keys=[separator], children=[self.root, right])

    def _find_leaf(self, key: K) -> _Node[K, V]:
        node = self.root
        while not node.leaf:
            node = node.children[bisect_right(node.keys, key)]
        return node

    def _insert(self, node: _Node[K, V], key: K, value: V) -> tuple[K, _Node[K, V]] | None:
        if node.leaf:
            i = bisect_left(node.keys, key)
            if i < len(node.keys) and node.keys[i] == key:
                node.values[i] = value
                return None
            node.keys.insert(i, key)
            node.values.insert(i, value)
            if len(node.keys) <= self.order - 1:
                return None
            mid = len(node.keys) // 2
            right = _Node(leaf=True, keys=node.keys[mid:], values=node.values[mid:], next=node.next)
            node.keys, node.values, node.next = node.keys[:mid], node.values[:mid], right
            return right.keys[0], right

        child_index = bisect_right(node.keys, key)
        split = self._insert(node.children[child_index], key, value)
        if split is None:
            return None
        separator, right_child = split
        node.keys.insert(child_index, separator)
        node.children.insert(child_index + 1, right_child)
        if len(node.children) <= self.order:
            return None
        mid = len(node.keys) // 2
        promoted = node.keys[mid]
        right = _Node(leaf=False, keys=node.keys[mid + 1:], children=node.children[mid + 1:])
        node.keys, node.children = node.keys[:mid], node.children[:mid + 1]
        return promoted, right

    def range_search(self, low: K, high: K) -> list[tuple[K, V]]:
        if high < low:
            raise ValueError("high must be >= low")
        node = self._find_leaf(low)
        result: list[tuple[K, V]] = []
        while node is not None:
            for key, value in zip(node.keys, node.values):
                if key < low:
                    continue
                if key > high:
                    return result
                result.append((key, value))
            node = node.next
        return result

    def items(self) -> Iterator[tuple[K, V]]:
        node = self.root
        while not node.leaf:
            node = node.children[0]
        while node is not None:
            yield from zip(node.keys, node.values)
            node = node.next


if __name__ == "__main__":
    tree: BPlusTree[int, str] = BPlusTree(order=4)
    for key in [18, 4, 10, 2, 7, 15, 20, 25, 9, 12, 30]:
        tree.insert(key, f"SKU-{key:03d}")
    print("Unit 5 — B+ Tree indexed inventory")
    print("Search 15:", tree.search(15))
    print("Range 7..20:", tree.range_search(7, 20))
