"""B-Tree index for product catalog lookups and range listing."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Generic, Iterator, Optional, TypeVar

K = TypeVar("K")
V = TypeVar("V")


@dataclass
class _BNode(Generic[K, V]):
    keys: list[K] = field(default_factory=list)
    values: list[V] = field(default_factory=list)
    children: list["_BNode[K, V]"] = field(default_factory=list)

    @property
    def leaf(self) -> bool:
        return not self.children


class BTree(Generic[K, V]):
    """B-Tree with minimum degree t (each node holds at most 2t-1 keys)."""
    def __init__(self, minimum_degree: int = 2) -> None:
        if minimum_degree < 2:
            raise ValueError("minimum_degree must be at least 2")
        self.t = minimum_degree
        self.root: _BNode[K, V] = _BNode()
        self.size = 0

    def search(self, key: K) -> V:
        node = self.root
        while True:
            i = 0
            while i < len(node.keys) and key > node.keys[i]:
                i += 1
            if i < len(node.keys) and key == node.keys[i]:
                return node.values[i]
            if node.leaf:
                raise KeyError(f"key not found: {key!r}")
            node = node.children[i]

    def insert(self, key: K, value: V) -> None:
        try:
            self.search(key)
        except KeyError:
            pass
        else:
            raise KeyError(f"key already exists: {key!r}")
        root = self.root
        if len(root.keys) == 2 * self.t - 1:
            new_root: _BNode[K, V] = _BNode(children=[root])
            self.root = new_root
            self._split_child(new_root, 0)
            self._insert_nonfull(new_root, key, value)
        else:
            self._insert_nonfull(root, key, value)
        self.size += 1

    def _split_child(self, parent: _BNode[K, V], index: int) -> None:
        t = self.t
        child = parent.children[index]
        sibling: _BNode[K, V] = _BNode()
        median_key, median_value = child.keys[t - 1], child.values[t - 1]
        sibling.keys = child.keys[t:]
        sibling.values = child.values[t:]
        child.keys = child.keys[:t - 1]
        child.values = child.values[:t - 1]
        if not child.leaf:
            sibling.children = child.children[t:]
            child.children = child.children[:t]
        parent.children.insert(index + 1, sibling)
        parent.keys.insert(index, median_key)
        parent.values.insert(index, median_value)

    def _insert_nonfull(self, node: _BNode[K, V], key: K, value: V) -> None:
        i = len(node.keys) - 1
        if node.leaf:
            node.keys.append(key)
            node.values.append(value)
            while i >= 0 and key < node.keys[i]:
                node.keys[i + 1] = node.keys[i]
                node.values[i + 1] = node.values[i]
                i -= 1
            node.keys[i + 1], node.values[i + 1] = key, value
            return
        while i >= 0 and key < node.keys[i]:
            i -= 1
        i += 1
        if len(node.children[i].keys) == 2 * self.t - 1:
            self._split_child(node, i)
            if key > node.keys[i]:
                i += 1
        self._insert_nonfull(node.children[i], key, value)

    def items(self) -> Iterator[tuple[K, V]]:
        def walk(node: _BNode[K, V]) -> Iterator[tuple[K, V]]:
            for i, key in enumerate(node.keys):
                if not node.leaf:
                    yield from walk(node.children[i])
                yield key, node.values[i]
            if not node.leaf:
                yield from walk(node.children[-1])
        yield from walk(self.root)

    def range_search(self, low: K, high: K) -> list[tuple[K, V]]:
        if high < low:
            raise ValueError("high must be >= low")
        return [(key, value) for key, value in self.items() if low <= key <= high]


if __name__ == "__main__":
    tree: BTree[int, str] = BTree(minimum_degree=2)
    for key in [15, 8, 22, 4, 11, 18, 25, 2, 6, 9, 13]:
        tree.insert(key, f"SKU-{key:03d}")
    print("Unit 5 — B-Tree inventory index")
    print("Search 18:", tree.search(18))
    print("IDs 6..15:", tree.range_search(6, 15))
