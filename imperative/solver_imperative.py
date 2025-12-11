from typing import List, Optional, Tuple, Callable
# PARADIGM NOTE: Imperative solver works on mutable list-of-lists boards.
# Higher-order programming appears via helpers from utils (apply_to_cells,
# collect_from_cells) and the factory create_backtracking_solver.
from imperative.utils_imperative import (
    Board,
    CandidatesBoard,
    all_candidates,
    cell_has_no_candidates,
    copy_board,
    has_conflict,
    is_solved,
    apply_to_cells,
    collect_from_cells,
)


# ============================================================================
# CUSTOM HIGHER-ORDER FUNCTION: create_backtracking_solver
# PARADIGM: Higher-Order Function (returns a function)
# WHY: Demonstrates function factories in imperative paradigm
# HOW: Takes configuration and returns a customized solver function
# Shows that imperative code can also use functional patterns like closures
# ============================================================================
def create_backtracking_solver(
    max_depth: Optional[int] = None
) -> Callable[[Board], Optional[Board]]:
    """
    Higher-order function that creates a customized solver.
    Takes optional configuration (like max_depth) and returns a solver function.
    Demonstrates function factory pattern in imperative code.
    """
    depth_counter = [0]  # Mutable counter (imperative style)
    
    def solver(board: Board) -> Optional[Board]:
        if max_depth is not None and depth_counter[0] >= max_depth:
            return None
        depth_counter[0] += 1
        return search(board)
    
    return solver

# Immutable board helper: set a single cell's value
def set_cell(board: Board, r: int, c: int, val: int) -> None:
    board[r][c] = val

# Constraint propagation: fill all singletons repeatedly until stable
def propagate(board: Board) -> Optional[Board]:
    """
    Apply constraint propagation using custom higher-order function.
    Uses collect_from_cells to find singleton candidates.
    """
    while True:
        cands = all_candidates(board)
        if cell_has_no_candidates(cands):
            return None

        # Use our custom higher-order function collect_from_cells
        # It takes a function and collects non-None results
        def find_single(r: int, c: int) -> Optional[Tuple[int, int, int]]:
            if board[r][c] == 0 and len(cands[r][c]) == 1:
                return (r, c, cands[r][c][0])
            return None
        
        # Higher-order function in action!
        singles = collect_from_cells(find_single)

        if not singles:
            return board

        for r, c, v in singles:
            set_cell(board, r, c, v)

# Choose cell with minimum remaining values (MRV)
def choose_mrv_cell(board: Board) -> Optional[Tuple[int, int, List[int]]]:
    cands = all_candidates(board)
    best: Optional[Tuple[int, int, List[int]]] = None
    for r in range(9):
        for c in range(9):
            if board[r][c] == 0:
                cand_list = cands[r][c]
                length = len(cand_list)
                if length == 0:
                    return None
                if length == 1:
                    return (r, c, cand_list)
                if best is None or length < len(best[2]):
                    best = (r, c, cand_list)
    return best

# search with propagation + MRV
def search(board: Board) -> Optional[Board]:
    p_board = copy_board(board)
    p = propagate(p_board)
    if p is None:
        return None
    if is_solved(p):
        return p

    choice = choose_mrv_cell(p)
    if choice is None:
        return None

    r, c, candidates = choice
    for val in candidates:
        next_board = copy_board(p)
        set_cell(next_board, r, c, val)
        result = search(next_board)
        if result is not None:
            return result
    return None


def solve(input_board: List[List[int]]) -> Optional[List[List[int]]]:
    board = copy_board(input_board)
    if has_conflict(board):
        return None
    result = search(board)
    if result is None:
        return None
    return result
