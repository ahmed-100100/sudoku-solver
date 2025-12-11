# functional_solver.py
# PARADIGM NOTE: Functional solver uses immutable tuple-of-tuples boards.
# Higher-order achieved via custom_* helpers (map/filter/reduce analogs) and
# function factories like try_each/compose_board_transforms.
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


# ============================================================================
# CUSTOM HIGHER-ORDER FUNCTION: try_each
# PARADIGM: Higher-Order Function (takes function, returns function)
# WHY: Demonstrates function composition and function factories
# HOW: Takes a test function and returns a new function that tries multiple values
# This is a higher-order function that RETURNS a function (closure)
# ============================================================================
def try_each(test_func: Callable[[T], Optional[Board]]) -> Callable[[Tuple[T, ...]], Optional[Board]]:
    """
    Higher-order function that creates a 'try each' function.
    Takes a test function and returns a function that tries it on each item.
    Returns the first successful result or None.
    This demonstrates function composition and closures.
    """
    def try_all(items: Tuple[T, ...]) -> Optional[Board]:
        """Try the test function on each item until one succeeds"""
        if not items:
            return None
        result = test_func(items[0])
        if result is not None:
            return result
        return try_all(items[1:])  # Recursive tail call
    
    return try_all


# ============================================================================
# CUSTOM HIGHER-ORDER FUNCTION: compose_board_transforms
# PARADIGM: Higher-Order Function (function composition)
# WHY: Composes multiple board transformation functions into one
# HOW: Takes multiple functions and returns their composition
# Classic functional programming pattern - building complex operations from simple ones
# ============================================================================
def compose_board_transforms(
    *funcs: Callable[[Board], Optional[Board]]
) -> Callable[[Board], Optional[Board]]:
    """
    Higher-order function that composes board transformation functions.
    Takes multiple functions and returns their composition (right to left).
    If any function returns None, the whole composition returns None.
    Implemented recursively to follow the functional paradigm (no loops).
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
    
    return composed

# ============================================================================
# PARADIGM: Immutability + Functional Programming using custom_map
# WHY: Board updates must be pure - no mutation, return new board instead
# HOW: Uses custom_map to transform each row, building immutable structure
# Higher-order achieved via custom_map taking a transformer function
# ============================================================================
def set_cell(board: Board, r: int, c: int, val: int) -> Board:
    """
    Create a new board with a single cell updated (immutable update).
    Original board remains unchanged - core principle of functional programming.
    """
    def build_row(row_idx: int, row_data: Tuple[int, ...]) -> Tuple[int, ...]:
        """Helper to build a row, updating column c if this is row r"""
        if row_idx != r:
            return row_data  # Keep original row unchanged
        # Use custom_map to transform the target row
        return custom_map(
            lambda col_idx: val if col_idx == c else row_data[col_idx],
            range(9)
        )
    
    # Map over all rows with their indices, building new board
    return custom_map(
        lambda row_idx: build_row(row_idx, board[row_idx]),
        range(9)
    )


# ============================================================================
# PARADIGM: Recursion + Functional Programming using custom_filter/custom_map/custom_reduce
# WHY: Constraint propagation is naturally recursive - keep applying until stable
# HOW: Tail-recursive function that finds singleton cells and fills them
# Uses custom_filter to find singletons, custom_reduce to apply updates immutably
# This is pure functional iteration - no loops, no mutation, just recursion
# ============================================================================
def propagate(board: Board) -> Optional[Board]:
    """
    Apply constraint propagation: repeatedly fill cells that have only one candidate.
    Continues recursively until no more changes occur (fixed point reached).
    Returns None if contradiction detected (no solution possible).
    """
    def find_singletons(b: Board, cands: CandidatesBoard) -> Tuple[Tuple[int, int, int], ...]:
        """Find all cells with exactly one candidate using functional approach"""
        # Generate all cell coordinates
        all_cells = [(r, c) for r in range(9) for c in range(9)]
        
        # Filter to cells that are empty and have exactly one candidate
        singleton_cells = custom_filter(
            lambda rc: b[rc[0]][rc[1]] == 0 and len(cands[rc[0]][rc[1]]) == 1,
            all_cells
        )
        
        # Map to (row, col, value) triples
        return custom_map(
            lambda rc: (rc[0], rc[1], cands[rc[0]][rc[1]][0]),
            singleton_cells
        )
    
    def apply_singles(b: Board, singles: Tuple[Tuple[int, int, int], ...]) -> Board:
        """Apply multiple cell updates using reduce (functional fold operation)"""
        # reduce applies set_cell for each singleton, threading board through
        return custom_reduce(
            lambda acc_board, rcv: set_cell(acc_board, rcv[0], rcv[1], rcv[2]),
            singles,
            b  # initial accumulator
        )
    
    # Tail-recursive propagation loop
    def loop(b: Board) -> Optional[Board]:
        cands = all_candidates(b)
        
        # Check for contradiction (cell with no candidates)
        if cell_has_no_candidates(cands):
            return None
        
        # Find all singleton cells
        singles = find_singletons(b, cands)
        
        if not singles:
            return b  # Fixed point reached - stable state
        
        # Apply all singletons and recurse (tail recursion)
        b2 = apply_singles(b, singles)
        return loop(b2)
    
    return loop(board)


# ============================================================================
# PARADIGM: Functional Programming using custom_reduce (fold operation)
# WHY: Finding minimum is a classic fold operation - accumulate best choice
# HOW: Uses custom_reduce to fold over all cells, accumulating the minimum
# Demonstrates functional aggregation without explicit loops or mutation
# ============================================================================
def choose_mrv_cell(board: Board) -> Optional[Tuple[int, int, Tuple[int, ...]]]:
    """
    Choose cell with Minimum Remaining Values (MRV heuristic).
    Selects empty cell with fewest candidates to minimize search branching.
    Uses functional reduce to find minimum without loops.
    """
    cands = all_candidates(board)
    
    # Generate all empty cell coordinates with their candidates
    all_cells = [
        (r, c, cands[r][c])
        for r in range(9)
        for c in range(9)
        if board[r][c] == 0
    ]
    
    if not all_cells:
        return None  # No empty cells
    
    # Use custom_reduce to find cell with minimum candidates (functional min operation)
    def min_candidates(acc: Optional[Tuple[int, int, Tuple[int, ...]]], 
                       cell: Tuple[int, int, Tuple[int, ...]]) -> Optional[Tuple[int, int, Tuple[int, ...]]]:
        r, c, cell_cands = cell
        cand_count = len(cell_cands)
        
        # Dead end - no candidates
        if cand_count == 0:
            return None
        
        # First cell or fewer candidates than current best
        if acc is None or cand_count < len(acc[2]):
            return (r, c, cell_cands)
        
        return acc
    
    # Fold over all empty cells to find the one with fewest candidates
    return custom_reduce(min_candidates, all_cells, None)


# ============================================================================
# PARADIGM: Recursion (backtracking) + Tail-Call Optimization Pattern
# WHY: Sudoku solving is inherently recursive - try choices and backtrack
# HOW: Recursive search tries each candidate value, returns on first success
# This is classic functional backtracking - no mutation, just recursive exploration
# Uses recursion for both propagation and candidate exploration
# ============================================================================
def search(board: Board) -> Optional[Board]:
    """
    Recursive backtracking search with constraint propagation.
    Tries each candidate value for the chosen cell, recursing on success.
    Backtracks (returns None) if a branch leads to contradiction.
    Pure functional approach - no state mutation, just recursive exploration.
    """
    # First apply constraint propagation (recursive)
    p = propagate(board)
    if p is None:
        return None  # Contradiction detected
    
    if is_solved(p):
        return p  # Base case - solution found!
    
    # Choose next cell to fill using MRV heuristic
    choice = choose_mrv_cell(p)
    if choice is None:
        return None  # Dead end - no valid choices
    
    r, c, candidates = choice
    
    # Use our custom higher-order function to try each candidate
    # try_each takes a test function and returns a function that tries all values
    test_candidate = lambda val: search(set_cell(p, r, c, val))
    try_all_candidates = try_each(test_candidate)  # Higher-order function returns a function!
    
    return try_all_candidates(candidates)


# ============================================================================
# PARADIGM: Pure Function + Referential Transparency
# WHY: Public API should be pure - no side effects, deterministic results
# HOW: Validates input, delegates to pure recursive search, converts result
# Maintains functional purity throughout - input board never modified
# ============================================================================
def solve(input_board) -> Optional[list]:
    """
    Public API: solve a Sudoku puzzle.
    Accepts mutable list-of-lists or immutable tuple-of-tuples.
    Returns solution as list-of-lists, or None if no solution exists.
    Pure function - input never modified, always returns new structure.
    """
    # Normalize to immutable Board (functional data structure)
    if isinstance(input_board, list):
        b = to_immutable(input_board)
    else:
        b = input_board  # Assume already immutable
    
    # Quick conflict check before starting (fail fast)
    if has_conflict(b):
        return None
    
    # Recursive search (pure functional backtracking)
    res = search(b)
    
    if res is None:
        return None  # No solution exists
    
    # Convert back to mutable format for external use
    return from_immutable(res)
