# Unit 3: Dynamic Programming (DP)

This module contains modular, well-tested Python implementations for all Unit 3 Dynamic Programming topics specified in the official DSA-II syllabus and lecture slides for the **Small Warehouse and Delivery Route Manager** project.

---

## Academic Foundation & Core Concepts

As formulated by Richard Bellman (1950s), Dynamic Programming solves complex optimization problems by decomposing them into overlapping subproblems and storing subsolutions to avoid redundant re-computation.

Two essential properties determine if a problem can be solved by Dynamic Programming:
1. **Optimal Substructure**: An optimal solution contains within it optimal solutions to its subproblems.
2. **Overlapping Subproblems**: A recursive formulation encounters the same subproblems repeatedly rather than continuously generating new subproblems.

### Two Standard DP Approaches:
- **Top-Down with Memoization**: Solves recursively, caching answers in a table/dictionary.
- **Bottom-Up with Tabulation (Used here)**: Iteratively solves subproblems from base cases upward, populating an explicit lookup matrix.

---

## Implemented Topics Summary

| Topic / Algorithm | Module File | Classification | Time Complexity | Space Complexity |
|---|---|---|---|---|
| **0/1 Knapsack Problem** | `knapsack.py` | Project-relevant / planned integration | $\Theta(n \cdot W)$ | $\Theta(n \cdot W)$ |
| **Longest Common Subsequence (LCS)** | `lcs.py` | Supporting | $O(m \cdot n)$ | $O(m \cdot n)$ |
| **Matrix Chain Multiplication (MCM)** | `matrix_chain.py` | Supporting | $\Theta(n^3)$ | $\Theta(n^2)$ |
| **Resource Allocation (Assembly Line & Discrete)** | `resource_allocation.py` | Supporting | $\Theta(n)$ / $\Theta(N \cdot M^2)$ | $\Theta(n)$ / $\Theta(N \cdot M)$ |

---

## Detailed Algorithm Descriptions & Project Justification

### 1. 0/1 Knapsack Problem
- **File**: `knapsack.py`
- **Current Status**: Implemented and tested.
- **Project Relevance**: Vehicle/package selection under limited capacity.
- **Classification**: Project-relevant / planned integration.
- **Integration Note**: Demonstrated as a standalone tested module for package payload optimization. Full integration into the complete warehouse order workflow remains planned future work.
- **Logistics Modeling**: Delivery vehicles operate under a payload capacity limit ($W$). Given customer orders with weights ($w_i$) and delivery values ($p_i$), 0/1 Knapsack determines the optimal combination of parcels to load without exceeding vehicle capacity. Parcels cannot be split fractionally (0/1 choice).
- **Recurrence**:
  $$c[i, w] = \begin{cases} c[i-1, w] & \text{if } w_i > w \\ \max(c[i-1, w], p_i + c[i-1, w - w_i]) & \text{if } w_i \le w \end{cases}$$
- **Complexity**: Time $\Theta(n \cdot W)$, Space $\Theta(n \cdot W)$ for 2D tabulation table and backtracking.

### 2. Longest Common Subsequence (LCS)
- **File**: `lcs.py`
- **Classification**: Supporting / Learning Implementation.
- **Logistics Purpose**: Compares planned vs. executed driver delivery stop sequences, audits deviations from recommended stops, and matches warehouse SKU barcodes.
- **Why Supporting?**: Road delivery routes follow geographical road links where Dijkstra is the actual physical routing algorithm. LCS compares sequences and is studied for syllabus completeness rather than physical distance optimization.
- **Recurrence**:
  $$L[i][j] = \begin{cases} 0 & \text{if } i=0 \text{ or } j=0 \\ 1 + L[i-1][j-1] & \text{if } X[i-1] = Y[j-1] \\ \max(L[i-1][j], L[i][j-1]) & \text{if } X[i-1] \ne Y[j-1] \end{cases}$$
- **Complexity**: Time $O(m \cdot n)$, Space $O(m \cdot n)$ for table and arrow tracking.

### 3. Matrix Chain Multiplication (MCM)
- **File**: `matrix_chain.py`
- **Classification**: Supporting / Learning Implementation.
- **Logistics Purpose**: Finds the minimum number of scalar multiplications required to multiply a chain of matrices $A_1 \dots A_n$. Can model multi-period inventory state transitions.
- **Why Supporting?**: Physical delivery trucks navigate roads, not matrix products. MCM is a core academic DP topic demonstrating interval tabulation and optimal parenthesization.
- **Recurrence**:
  $$m[i, j] = \min_{i \le k < j} \{m[i, k] + m[k+1, j] + p_{i-1} p_k p_j\} \quad (i < j)$$
- **Complexity**: Time $\Theta(n^3)$, Space $\Theta(n^2)$ for cost table $m$ and split table $s$.

### 4. Resource Allocation Problem
- **File**: `resource_allocation.py`
- **Classification**: Supporting / Learning Implementation.
- **Logistics Purpose**: Implements both canonical models presented in the lecture slides:
  1. **Assembly Line Scheduling (Slides 61–66)**: Conceptual dual packaging lines (standard vs. express) with station processing times and transfer times.
  2. **Discrete Resource Allocation (Slides 68–69, 75)**: Distribution of $M$ discrete resources (e.g., delivery vans or budget units) across $N$ regional warehouses using profit matrix $P[i][k]$.
- **Why Supporting?**: While both models offer theoretical logistics relevance, neither is currently wired into the primary warehouse inventory/routing dispatch pipeline. Both are provided as clean, standalone DSA demonstrations for syllabus compliance.
- **Recurrences**:
  - Assembly line: $f_1[j] = \min(f_1[j-1] + a_{1, j}, f_2[j-1] + t_{2, j-1} + a_{1, j})$
  - Discrete allocation: $dp[i][j] = \max_{0 \le k \le j} (P[i][k] + dp[i-1][j-k])$
- **Complexity**: Assembly line $\Theta(n)$ time and space; Discrete allocation $\Theta(N \cdot M^2)$ time, $\Theta(N \cdot M)$ space.

---

## How to Run Demonstrations

From the repository root, run:

```powershell
python -m unit3_dynamic_programming.knapsack
python -m unit3_dynamic_programming.lcs
python -m unit3_dynamic_programming.matrix_chain
python -m unit3_dynamic_programming.resource_allocation
```
