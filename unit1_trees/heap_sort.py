"""In-place heap-sort utility for report data."""
from __future__ import annotations

from typing import Callable, MutableSequence, Optional, TypeVar

T = TypeVar("T")


def heap_sort(items: MutableSequence[T], *, key: Optional[Callable[[T], object]] = None,
              reverse: bool = False) -> MutableSequence[T]:
    """Sort `items` in place with heap sort and return it.

    Time is O(n log n) in best/average/worst cases; auxiliary space is O(1)
    beyond the input. Heap sort is not stable. `key` selects the sortable field.
    """
    key_function: Callable[[T], object] = key if key is not None else lambda value: value

    def sift_down(start: int, end: int) -> None:
        root = start
        while 2 * root + 1 <= end:
            child = 2 * root + 1
            swap = root
            if key_function(items[swap]) < key_function(items[child]):
                swap = child
            if child + 1 <= end and key_function(items[swap]) < key_function(items[child + 1]):
                swap = child + 1
            if swap == root:
                return
            items[root], items[swap] = items[swap], items[root]
            root = swap

    last = len(items) - 1
    for start in range((last - 1) // 2, -1, -1):
        sift_down(start, last)
    for end in range(last, 0, -1):
        items[0], items[end] = items[end], items[0]
        sift_down(0, end - 1)
    if reverse:
        items.reverse()
    return items


if __name__ == "__main__":
    simulated_products = [
        {"id": 101, "name": "Box", "stock": 42},
        {"id": 102, "name": "Tape", "stock": 18},
        {"id": 103, "name": "Label", "stock": 9},
    ]
    heap_sort(simulated_products, key=lambda product: product["stock"])
    print("Products by stock (low to high):", simulated_products)
