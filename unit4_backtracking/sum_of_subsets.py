"""Sum of Subsets using backtracking.

Project fit: supporting exact-weight order combination. 0/1 Knapsack remains
the primary model when maximizing value under a capacity limit.
"""


def sum_of_subsets(weights: list[int], target: int) -> list[list[int]]:
    """Return all subsets that sum exactly to target; duplicates are separate items."""
    if target < 0:
        raise ValueError("target must be non-negative")
    if any(not isinstance(w, int) or isinstance(w, bool) or w <= 0 for w in weights):
        raise ValueError("weights must be positive integers")
    ordered = sorted(weights)
    results: list[list[int]] = []
    chosen: list[int] = []

    def backtrack(index: int, total: int) -> None:
        if total == target:
            results.append(chosen[:])
            return
        if total > target or index == len(ordered):
            return
        weight = ordered[index]
        chosen.append(weight)
        backtrack(index + 1, total + weight)
        chosen.pop()
        backtrack(index + 1, total)
    backtrack(0, 0)
    return results


if __name__ == "__main__":
    weights, target = [2, 3, 5, 7, 8], 10
    print("Unit 4 — Sum of Subsets / Exact-Weight Order Selection")
    print(f"Candidate parcel weights: {weights}; target load: {target} kg")
    print("Matching combinations:", sum_of_subsets(weights, target))
