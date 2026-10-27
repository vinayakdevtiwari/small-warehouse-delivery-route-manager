"""N-Queens backtracking solution (standalone syllabus demonstration).

This problem is not a direct warehouse feature, so it is kept as a Unit 4
demonstration instead of being forced into the delivery workflow.
"""


def solve_n_queens(n: int) -> list[list[int]]:
    """Return solutions where each row maps to a zero-based queen column."""
    if n < 1:
        raise ValueError("n must be at least 1")
    solutions: list[list[int]] = []
    placement: list[int] = []
    columns: set[int] = set()
    diagonal_down: set[int] = set()
    diagonal_up: set[int] = set()

    def backtrack(row: int) -> None:
        if row == n:
            solutions.append(placement[:])
            return
        for col in range(n):
            if col in columns or row - col in diagonal_down or row + col in diagonal_up:
                continue
            placement.append(col)
            columns.add(col)
            diagonal_down.add(row - col)
            diagonal_up.add(row + col)
            backtrack(row + 1)
            placement.pop()
            columns.remove(col)
            diagonal_down.remove(row - col)
            diagonal_up.remove(row + col)
    backtrack(0)
    return solutions


if __name__ == "__main__":
    solutions = solve_n_queens(4)
    print("Unit 4 — N-Queens (standalone syllabus demonstration)")
    print("Number of solutions for n=4:", len(solutions))
    print("First solution:", solutions[0] if solutions else None)
