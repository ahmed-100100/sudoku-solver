from typing import List, Optional, Callable, TypeVar

# PARADIGM NOTE: Imperative code uses mutable list-of-lists for boards.
# Higher-order programming here is via custom helpers (apply_to_cells,
# collect_from_cells, collect_with_predicate) while still mutating state.

# Types for mutable boards
Board = List[List[int]]              # mutable 9x9 board
CandidatesBoard = List[List[List[int]]]  # 9x9 of candidate lists

T = TypeVar('T')


# ============================================================================
# CUSTOM HIGHER-ORDER FUNCTION #1: apply_to_cells
# PARADIGM: Higher-Order Function (takes function as parameter)
# WHY: Abstracts the pattern of iterating over all cells
# HOW: Takes a function (r, c) -> None and applies it to every cell
# This allows us to inject different behaviors without repeating loops
# ============================================================================
def apply_to_cells(func: Callable[[int, int], None]) -> None:
    """
    Higher-order function that applies a given function to all board cells.
    Takes a function that accepts (row, col) coordinates.
    Useful for imperative operations that mutate state or collect data.
    """
    for r in range(9):
        for c in range(9):
            func(r, c)


# ============================================================================
# CUSTOM HIGHER-ORDER FUNCTION #2: collect_from_cells
# PARADIGM: Higher-Order Function (takes predicate, returns list)
# WHY: Combines iteration and collection with a predicate
# HOW: Takes a function (r, c) -> Optional[T] and collects non-None results
# More flexible than apply_to_cells - it returns collected values
# ============================================================================
def collect_from_cells(func: Callable[[int, int], Optional[T]]) -> List[T]:
    """
    Higher-order function that collects values from cells based on a function.
    Takes a function (row, col) -> Optional[value].
    Returns a list of all non-None values collected.
    """
    results: List[T] = []
    for r in range(9):
        for c in range(9):
            result = func(r, c)
            if result is not None:
                results.append(result)
    return results


# ============================================================================
# CUSTOM HIGHER-ORDER FUNCTION #3: collect_with_predicate
# PARADIGM: Higher-Order Function (takes predicate and extractor)
# WHY: Separates filtering logic from extraction logic
# HOW: Takes predicate (r,c)->bool and extractor (r,c)->T, returns filtered results
# Demonstrates higher-order function taking multiple function parameters
# ============================================================================
def collect_with_predicate(
    predicate: Callable[[int, int], bool],
    extractor: Callable[[int, int], T]
) -> List[T]:
    """
    Higher-order function that filters and extracts values from cells.
    Takes two functions: predicate to test cells, extractor to get values.
    Returns list of extracted values for cells where predicate is True.
    """
    results: List[T] = []
    for r in range(9):
        for c in range(9):
            if predicate(r, c):
                results.append(extractor(r, c))
    return results

def copy_board(board: Board) -> Board:
    new_board: Board = []
    for row in board:
        new_row = []
        for v in row:
            new_row.append(v)
        new_board.append(new_row)
    return new_board

def row_values(board: Board, r: int) -> List[int]:
    vals: List[int] = []
    for v in board[r]:
        if v != 0:
            vals.append(v)
    return vals


def col_values(board: Board, c: int) -> List[int]:
    vals: List[int] = []
    for r in range(9):
        v = board[r][c]
        if v != 0:
            vals.append(v)
    return vals


def box_values(board: Board, r: int, c: int) -> List[int]:
    br = (r // 3) * 3
    bc = (c // 3) * 3
    vals: List[int] = []
    for rr in range(br, br + 3):
        for cc in range(bc, bc + 3):
            v = board[rr][cc]
            if v != 0:
                vals.append(v)
    return vals


def candidates_for(board: Board, r: int, c: int) -> List[int]:
    if board[r][c] != 0:
        return [board[r][c]]
    used: List[int] = []
    for x in row_values(board, r):
        if x not in used:
            used.append(x)

    for x in col_values(board, c):
        if x not in used:
            used.append(x)

    for x in box_values(board, r, c):
        if x not in used:
            used.append(x)

    cands: List[int] = []
    for x in range(1, 10):
        if x not in used:
            cands.append(x)
    return cands


def all_candidates(board: Board) -> CandidatesBoard:
    cboard: CandidatesBoard = []
    for r in range(9):
        row_list: List[List[int]] = []
        for c in range(9):
            row_list.append(candidates_for(board, r, c))
        cboard.append(row_list)
    return cboard


def is_solved(board: Board) -> bool:
    for r in range(9):
        for c in range(9):
            if board[r][c] == 0:
                return False
    return True


def has_conflict(board: Board) -> bool:
    """
    Check if board has any conflicts (duplicate values in row/col/box).
    Uses custom higher-order functions for cleaner implementation.
    """
    def dup(xs: List[int]) -> bool:
        xs2 = []
        for x in xs:
            if x != 0:
                xs2.append(x)
        return len(xs2) != len(set(xs2))

    # Check rows
    for r in range(9):
        if dup(board[r]):
            return True
    
    # Check columns using our custom higher-order function
    for c in range(9):
        # Use collect_with_predicate instead of awkward apply_to_cells
        col_vals = collect_with_predicate(
            predicate=lambda r, col: col == c,  # Only cells in this column
            extractor=lambda r, col: board[r][col]  # Extract the value
        )
        if dup(col_vals):
            return True

    # Check 3x3 boxes
    for br in (0, 3, 6):
        for bc in (0, 3, 6):
            vals: List[int] = []
            for rr in range(br, br + 3):
                for cc in range(bc, bc + 3):
                    v = board[rr][cc]
                    if v != 0:
                        vals.append(v)
            if len(vals) != len(set(vals)):
                return True
    return False


def cell_has_no_candidates(cands_board: CandidatesBoard) -> bool:
    for r in range(9):
        for c in range(9):
            if len(cands_board[r][c]) == 0:
                return True
    return False
