"""Red-Black Tree key/value index for inventory records.

Supports insert, search and ordered traversal. It uses a black NIL sentinel,
standard rotations and insertion fix-up. Deletion is intentionally not included
because the application can rebuild this small index from its database records.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Generic, Iterator, TypeVar, Optional

K = TypeVar("K")
V = TypeVar("V")


@dataclass
class _Node(Generic[K, V]):
    key: Optional[K]
    value: Optional[V]
    red: bool
    left: "_Node[K, V]"
    right: "_Node[K, V]"
    parent: "_Node[K, V]"


class RedBlackTree(Generic[K, V]):
    """Ordered key/value index with O(log n) worst-case search and insertion."""
    def __init__(self) -> None:
        nil = _Node(None, None, False, None, None, None)  # type: ignore[arg-type]
        nil.left = nil.right = nil.parent = nil
        self.nil = nil
        self.root = nil
        self.size = 0

    def search(self, key: K) -> V:
        node = self.root
        while node is not self.nil:
            if key == node.key:
                return node.value  # type: ignore[return-value]
            node = node.left if key < node.key else node.right
        raise KeyError(f"key not found: {key!r}")

    def get(self, key: K, default: Optional[V] = None) -> Optional[V]:
        try:
            return self.search(key)
        except KeyError:
            return default

    def insert(self, key: K, value: V) -> None:
        parent = self.nil
        node = self.root
        while node is not self.nil:
            parent = node
            if key == node.key:
                raise KeyError(f"key already exists: {key!r}")
            node = node.left if key < node.key else node.right
        fresh = _Node(key, value, True, self.nil, self.nil, parent)
        if parent is self.nil:
            self.root = fresh
        elif key < parent.key:  # type: ignore[operator]
            parent.left = fresh
        else:
            parent.right = fresh
        self.size += 1
        self._fix_insert(fresh)

    def _rotate_left(self, x: _Node[K, V]) -> None:
        y = x.right
        x.right = y.left
        if y.left is not self.nil:
            y.left.parent = x
        y.parent = x.parent
        if x.parent is self.nil:
            self.root = y
        elif x is x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y
        y.left = x
        x.parent = y

    def _rotate_right(self, y: _Node[K, V]) -> None:
        x = y.left
        y.left = x.right
        if x.right is not self.nil:
            x.right.parent = y
        x.parent = y.parent
        if y.parent is self.nil:
            self.root = x
        elif y is y.parent.right:
            y.parent.right = x
        else:
            y.parent.left = x
        x.right = y
        y.parent = x

    def _fix_insert(self, z: _Node[K, V]) -> None:
        while z.parent.red:
            if z.parent is z.parent.parent.left:
                uncle = z.parent.parent.right
                if uncle.red:
                    z.parent.red = False
                    uncle.red = False
                    z.parent.parent.red = True
                    z = z.parent.parent
                else:
                    if z is z.parent.right:
                        z = z.parent
                        self._rotate_left(z)
                    z.parent.red = False
                    z.parent.parent.red = True
                    self._rotate_right(z.parent.parent)
            else:
                uncle = z.parent.parent.left
                if uncle.red:
                    z.parent.red = False
                    uncle.red = False
                    z.parent.parent.red = True
                    z = z.parent.parent
                else:
                    if z is z.parent.left:
                        z = z.parent
                        self._rotate_right(z)
                    z.parent.red = False
                    z.parent.parent.red = True
                    self._rotate_left(z.parent.parent)
        self.root.red = False
        self.root.parent = self.nil

    def inorder_items(self) -> Iterator[tuple[K, V]]:
        def walk(node: _Node[K, V]) -> Iterator[tuple[K, V]]:
            if node is not self.nil:
                yield from walk(node.left)
                yield (node.key, node.value)  # type: ignore[misc]
                yield from walk(node.right)
        yield from walk(self.root)


if __name__ == "__main__":
    tree: RedBlackTree[int, str] = RedBlackTree()
    for product_id in [40, 10, 30, 20, 50, 60, 5]:
        tree.insert(product_id, f"Product-{product_id}")
    print("Unit 5 — Red-Black Tree inventory index")
    print("Search product 30:", tree.search(30))
    print("Sorted index:", list(tree.inorder_items()))
