from typing import Optional, Tuple, Callable, TypeVar
from functional.utils_functional import (
    Board,
    CandidatesBoard,
    all_candidates,
    is_solved,
    to_immutable,
    from_immutable,
    cell_has_no_candidates,
    has_conflict,
    map_2d,
    fold_board,
    custom_map,
    custom_filter,
    custom_reduce,
)

T = TypeVar('T')

def try_each(test_func: Callable[[T], Optional[Board]]) -> Callable[[Tuple[T, ...]], Optional[Board]]:
    """
    Higher-order function that creates a 'try each' function.
    Takes a test function and returns a function that tries it on each item.
    Returns the first successful result or None.
    This demonstrates function composition and closures.
    """
    def try_all(items: Tuple[T, ...]) -> Optional[Board]:
        if not items:
            return None
        result = test_func(items[0])
        if result is not None:
            return result
        return try_all(items[1:])  # Fully recursive, no loops

    return try_all

def compose_board_transforms(
    *funcs: Callable[[Board], Optional[Board]]
) -> Callable[[Board], Optional[Board]]:
    """
    Higher-order function that composes board transformation functions.
    Takes multiple functions and returns their composition (right to left).
    If any function returns None, the whole composition returns None.
    Purely recursive, no loops.
    """
    def composed(board: Board) -> Optional[Board]:
        def apply_funcs(idx: int, result: Optional[Board]) -> Optional[Board]:
            if result is None:
                return None
            if idx < 0:
                return result
            return apply_funcs(idx - 1, funcs[idx](result))
        return apply_funcs(len(funcs) - 1, board)
    return composed


def set_cell(board: Board, r: int, c: int, val: int) -> Board:
    """
    Create a new board with a single cell updated (immutable update).
    Original board remains unchanged - core principle of functional programming.
    """
    def build_row(row_idx: int, row_data: Tuple[int, ...]) -> Tuple[int, ...]:
        if row_idx != r:
            return row_data
        return custom_map(
            lambda col_idx: val if col_idx == c else row_data[col_idx],
            range(9)
        )

    return custom_map(
        lambda row_idx: build_row(row_idx, board[row_idx]),
        range(9)
    )


def propagate(board: Board) -> Optional[Board]:
    """
    Apply constraint propagation: repeatedly fill cells that have only one candidate.
    Continues recursively until no more changes occur (fixed point reached).
    Returns None if contradiction detected (no solution possible).
    """
    def all_coords(r: int = 0, c: int = 0) -> Tuple[Tuple[int, int], ...]:
        # Recursively generate all board coordinates as a tuple of pairs
        if r == 9:
            return ()
        if c == 8:
            return ((r, c),) + all_coords(r + 1, 0)
        return ((r, c),) + all_coords(r, c + 1)

    def find_singletons(b: Board, cands: CandidatesBoard) -> Tuple[Tuple[int, int, int], ...]:
        coords = all_coords()
        singles_filtered = custom_filter(
            lambda rc: b[rc[0]][rc[1]] == 0 and len(cands[rc[0]][rc[1]]) == 1,
            coords
        )
        return custom_map(
            lambda rc: (rc[0], rc[1], cands[rc[0]][rc[1]][0]),
            singles_filtered
        )

    def apply_singles(b: Board, singles: Tuple[Tuple[int, int, int], ...]) -> Board:
        return custom_reduce(
            lambda acc_b, rcv: set_cell(acc_b, rcv[0], rcv[1], rcv[2]),
            singles,
            b
        )

    def loop(b: Board) -> Optional[Board]:
        cands = all_candidates(b)
        if cell_has_no_candidates(cands):
            return None
        singles = find_singletons(b, cands)
        if not singles:
            return b
        b2 = apply_singles(b, singles)
        return loop(b2)

    return loop(board)


def choose_mrv_cell(board: Board) -> Optional[Tuple[int, int, Tuple[int, ...]]]:
    """
    Choose cell with Minimum Remaining Values (MRV heuristic).
    Selects empty cell with fewest candidates to minimize search branching.
    Uses functional reduce to find minimum. No loops.
    """
    cands = all_candidates(board)

    def all_empty_cells(r: int = 0, c: int = 0) -> Tuple[Tuple[int, int, Tuple[int, ...]], ...]:
        # Recursively generate all empty cells (r, c, cands[r][c])
        if r == 9:
            return ()
        if c == 8:
            rest = all_empty_cells(r + 1, 0)
        else:
            rest = all_empty_cells(r, c + 1)
        if board[r][c] == 0:
            return ((r, c, cands[r][c]),) + rest
        else:
            return rest

    all_cells = all_empty_cells()
    if not all_cells:
        return None

    def min_candidates(acc: Optional[Tuple[int, int, Tuple[int, ...]]],
                       cell: Tuple[int, int, Tuple[int, ...]]) -> Optional[Tuple[int, int, Tuple[int, ...]]]:
        _, _, cell_cands = cell
        if len(cell_cands) == 0:
            return None
        if acc is None or len(cell_cands) < len(acc[2]):
            return cell
        return acc

    return custom_reduce(min_candidates, all_cells, None)

def search(board: Board) -> Optional[Board]:
    """
    Recursive backtracking search with constraint propagation.
    Tries each candidate value for the chosen cell, recursing on success.
    Backtracks (returns None) if a branch leads to contradiction.
    Pure functional approach - no state mutation, just recursive exploration.
    """
    p = propagate(board)
    if p is None:
        return None
    if is_solved(p):
        return p
    choice = choose_mrv_cell(p)
    if choice is None:
        return None
    r, c, candidates = choice
    test_candidate = lambda val: search(set_cell(p, r, c, val))
    try_all_candidates = try_each(test_candidate)
    return try_all_candidates(candidates)


def solve(input_board) -> Optional[list]:
    """
    Public API: solve a Sudoku puzzle.
    Accepts mutable list-of-lists or immutable tuple-of-tuples.
    Returns solution as list-of-lists, or None if no solution exists.
    Pure function - input never modified, always returns new structure.
    """
    b = to_immutable(input_board) if isinstance(input_board, list) else input_board
    if has_conflict(b):
        return None
    res = search(b)
    if res is None:
        return None
    return from_immutable(res)