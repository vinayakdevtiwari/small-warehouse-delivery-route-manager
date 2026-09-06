"""Array-backed binary min/max heap."""
from __future__ import annotations

from typing import Generic, Iterable, Optional, TypeVar

T = TypeVar("T")


class BinaryHeap(Generic[T]):
    """A min-heap or max-heap of comparable values.

    peek is O(1). push and pop are O(log n). Constructing from an iterable is
    O(n) through bottom-up heapification. Values must be mutually comparable.
    """

    def __init__(self, values: Optional[Iterable[T]] = None, *, kind: str = "min") -> None:
        if kind not in {"min", "max"}:
            raise ValueError("kind must be 'min' or 'max'")
        self.kind = kind
        self._items = list(values) if values is not None else []
        self._heapify()

    def __len__(self) -> int:
        return len(self._items)

    def is_empty(self) -> bool:
        return not self._items

    def peek(self) -> T:
        """Return the highest-priority item without removing it: O(1)."""
        if not self._items:
            raise IndexError("peek from empty heap")
        return self._items[0]

    def push(self, value: T) -> None:
        """Add a value and restore heap order: O(log n)."""
        self._items.append(value)
        self._sift_up(len(self._items) - 1)

    def pop(self) -> T:
        """Remove and return the root-priority value: O(log n)."""
        if not self._items:
            raise IndexError("pop from empty heap")
        root = self._items[0]
        final = self._items.pop()
        if self._items:
            self._items[0] = final
            self._sift_down(0)
        return root

    def to_list(self) -> list[T]:
        """Return a shallow copy of internal heap-array order, not sorted order."""
        return self._items.copy()

    def _before(self, first: T, second: T) -> bool:
        return first < second if self.kind == "min" else first > second

    def _heapify(self) -> None:
        for index in range((len(self._items) // 2) - 1, -1, -1):
            self._sift_down(index)

    def _sift_up(self, index: int) -> None:
        while index:
            parent = (index - 1) // 2
            if not self._before(self._items[index], self._items[parent]):
                return
            self._items[index], self._items[parent] = self._items[parent], self._items[index]
            index = parent

    def _sift_down(self, index: int) -> None:
        length = len(self._items)
        while True:
            left = 2 * index + 1
            right = left + 1
            candidate = index
            if left < length and self._before(self._items[left], self._items[candidate]):
                candidate = left
            if right < length and self._before(self._items[right], self._items[candidate]):
                candidate = right
            if candidate == index:
                return
            self._items[index], self._items[candidate] = self._items[candidate], self._items[index]
            index = candidate


if __name__ == "__main__":
    urgent_delivery_codes = BinaryHeap([4, 2, 7, 1], kind="min")
    urgent_delivery_codes.push(3)
    print("Heap array:", urgent_delivery_codes.to_list())
    print("Next priority code:", urgent_delivery_codes.peek())
    print("Processing order:", [urgent_delivery_codes.pop() for _ in range(len(urgent_delivery_codes))])
