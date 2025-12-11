# functional_helpers.py file
# PARADIGM NOTE: Functional style uses immutable tuple-of-tuples for boards.
# Higher-order programming is achieved via custom_* helpers (map/filter/reduce/all/any)
# and domain-specific helpers like map_2d, filter_and_transform, fold_board.
from typing import Tuple, List, Callable, TypeVar

# Types
Board = Tuple[Tuple[int, ...], ...]                # immutable 9x9 board
CandidatesBoard = Tuple[Tuple[Tuple[int, ...], ...], ...]  # 9x9 of candidate tuples

# Generic type variables for higher-order functions
T = TypeVar('T')
U = TypeVar('U')


# ============================================================================
# CORE CUSTOM HIGHER-ORDER HELPERS (replace built-in map/filter/reduce/all/any)
# ============================================================================

def custom_map(func: Callable[[T], U], items) -> Tuple[U, ...]:
    """
    custom_map applies a given function `func` to each element in the input
    sequence `items`, returning an immutable tuple with all results.
    It's a recursive, functional-style replacement for Python's built-in map,
    but always returns a tuple (never a list or generator).
    
    Example:
        custom_map(lambda x: x * 2, [1, 2, 3])  # returns (2, 4, 6)
    """
    items_tuple = tuple(items)
    if not items_tuple:
        return ()
    return (func(items_tuple[0]),) + custom_map(func, items_tuple[1:])


def custom_filter(predicate: Callable[[T], bool], items) -> Tuple[T, ...]:
    """
    custom_filter retains only those elements from `items` for which the
    function `predicate` returns True. Like the built-in filter, but
    always returns a tuple, not an iterator.
    
    Example:
        custom_filter(lambda x: x > 0, [-1, 0, 1, 2])  # returns (1, 2)
    """
    items_tuple = tuple(items)
    if not items_tuple:
        return ()
    head, *tail = items_tuple
    filtered_tail = custom_filter(predicate, tail)
    if predicate(head):
        return (head,) + filtered_tail
    return filtered_tail


def custom_reduce(func: Callable[[U, T], U], items, initializer: U) -> U:
    """
    custom_reduce reduces the sequence `items` into a single value by
    recursively applying the binary function `func`, starting from
    `initializer`. Like functools.reduce but functional and always explicit.
    
    Example:
        custom_reduce(lambda acc, x: acc + x, [1,2,3], 0)  # returns 6
    """
    items_tuple = tuple(items)
    if not items_tuple:
        return initializer
    return custom_reduce(func, items_tuple[1:], func(initializer, items_tuple[0]))


def custom_all(items) -> bool:
    """
    custom_all returns True if every value in the iterable `items`
    evaluates as True, otherwise returns False. It's like built-in all()
    but implemented recursively.
    
    Example:
        custom_all([1, True, "nonempty"])  # returns True
        custom_all([1, 0, 2])              # returns False
    """
    items_tuple = tuple(items)
    if not items_tuple:
        return True
    return bool(items_tuple[0]) and custom_all(items_tuple[1:])


def custom_any(items) -> bool:
    """
    custom_any returns True if any value in the iterable `items`
    evaluates as True, otherwise returns False. Equivalent to built-in any()
    but recursively implemented.
    
    Example:
        custom_any([0, 0, 3])  # returns True
        custom_any([0, None])  # returns False
    """
    items_tuple = tuple(items)
    if not items_tuple:
        return False
    return bool(items_tuple[0]) or custom_any(items_tuple[1:])


# ============================================================================
# CUSTOM HIGHER-ORDER FUNCTION #1: map_2d
# PARADIGM: Higher-Order Function (takes function as parameter)
# WHY: Demonstrates custom higher-order function in functional paradigm
# HOW: Takes a transformation function and applies it to every element in 2D structure
# This is our own implementation instead of nested built-in map() calls
# ============================================================================
def map_2d(func: Callable[[int, int], T], rows: int = 9, cols: int = 9) -> Tuple[Tuple[T, ...], ...]:
    """
    map_2d applies a given function `func` to every (row, col) coordinate
    in a 2D grid of the specified shape (default 9x9). It returns an
    immutable 2D tuple of tuples structure.
    
    Example:
        # Fill 2D board with coordinate sums:
        map_2d(lambda r, c: r + c, rows=2, cols=3)
        # returns ((0,1,2), (1,2,3))
    """
    def build_row(r: int) -> Tuple[T, ...]:
        def build_cell(c: int) -> T:
            return func(r, c)
        return tuple(build_cell(c) for c in range(cols))
    
    return tuple(build_row(r) for r in range(rows))


# ============================================================================
# CUSTOM HIGHER-ORDER FUNCTION #2: filter_and_transform
# PARADIGM: Higher-Order Function (takes predicate and transformer functions)
# WHY: Combines filtering and transformation in one higher-order operation
# HOW: Takes a predicate and a transformation function, applies both
# More powerful than just filter - it's filter + map combined
# ============================================================================
def filter_and_transform(
    predicate: Callable[[T], bool],
    transformer: Callable[[T], U],
    items: Tuple[T, ...]
) -> Tuple[U, ...]:
    """
    filter_and_transform first filters `items` using the `predicate`, then applies
    `transformer` to each item that passed, returning a tuple of results.
    This is a higher-order function combining the logic of filter and map.
    
    Example:
        filter_and_transform(lambda x: x > 2, str, (1,2,3,4))  # returns ('3', '4')
    """
    def process_item(item: T) -> Tuple[U, ...]:
        if predicate(item):
            return (transformer(item),)
        return ()
    
    # Recursively process items
    def process_all(remaining: Tuple[T, ...]) -> Tuple[U, ...]:
        if not remaining:
            return ()
        return process_item(remaining[0]) + process_all(remaining[1:])
    
    return process_all(items)


# ============================================================================
# CUSTOM HIGHER-ORDER FUNCTION #3: fold_board
# PARADIGM: Higher-Order Function (fold/reduce over 2D structure)
# WHY: Custom fold implementation for board operations
# HOW: Takes accumulator function and applies it to all board cells
# This is like reduce() but specialized for 2D board structures
# ============================================================================
def fold_board(
    func: Callable[[T, int, int, int], T],
    board: Board,
    initial: T
) -> T:
    """
    Higher-order function that folds (reduces) over all board cells.
    Takes a function (accumulator, row, col, value) -> new_accumulator.
    Returns the final accumulated value.
    """
    def fold_row(acc: T, r: int, row_data: Tuple[int, ...]) -> T:
        def fold_col(acc_inner: T, c: int) -> T:
            return func(acc_inner, r, c, row_data[c])
        
        # Fold over columns recursively
        def fold_cols_recursive(acc_inner: T, col_idx: int) -> T:
            if col_idx >= 9:
                return acc_inner
            return fold_cols_recursive(fold_col(acc_inner, col_idx), col_idx + 1)
        
        return fold_cols_recursive(acc, 0)
    
    # Fold over rows recursively
    def fold_rows_recursive(acc: T, row_idx: int) -> T:
        if row_idx >= 9:
            return acc
        return fold_rows_recursive(fold_row(acc, row_idx, board[row_idx]), row_idx + 1)
    
    return fold_rows_recursive(initial, 0)


# ============================================================================
# PARADIGM: Functional Programming using custom_map (no built-ins)
# WHY: Uses our own map implementation across nested structures
# HOW: Transforms each row with an inner custom_map, then transforms all rows
# Higher-order achieved via custom_map taking a function
# ============================================================================
def to_immutable(board: List[List[int]]) -> Board:
    """Convert mutable list-of-lists -> immutable tuple-of-tuples"""
    return tuple(
        custom_map(lambda cell: int(cell), row) for row in board
    )


# ============================================================================
# PARADIGM: Functional Programming using custom_map (no built-ins)
# WHY: Uses custom_map to transform immutable structures back to mutable ones
# HOW: Applies list() constructor via custom_map to convert tuples to lists
# Higher-order achieved via custom_map taking a function
# ============================================================================
def from_immutable(board: Board) -> List[List[int]]:
    """Convert back to list-of-lists (for printing)"""
    return [list(row) for row in board]


# ============================================================================
# PARADIGM: Functional Programming using custom_filter (no built-ins)
# WHY: Declaratively selects values that meet a condition (non-zero)
# HOW: custom_filter takes a predicate function and returns matching values
# Higher-order achieved via predicate passed in
# ============================================================================
def row_values(board: Board, r: int) -> Tuple[int, ...]:
    """Get all non-zero values from a specific row"""
    return custom_filter(lambda v: v != 0, board[r])


# ============================================================================
# PARADIGM: Functional Programming using custom_filter (no built-ins)
# WHY: Declaratively extracts a column then filters zeros
# HOW: Builds the column with a comprehension, filters via custom_filter
# Higher-order achieved via predicate passed in
# ============================================================================
def col_values(board: Board, c: int) -> Tuple[int, ...]:
    """Get all non-zero values from a specific column"""
    column = tuple(board[r][c] for r in range(9))
    return custom_filter(lambda v: v != 0, column)


def box_values(board: Board, r: int, c: int) -> Tuple[int, ...]:
    """Get all non-zero values from the 3x3 box containing cell (r, c)"""
    br, bc = (r // 3) * 3, (c // 3) * 3
    
    # Recursive helper to collect box values row by row
    def collect_rows(row_idx: int) -> Tuple[int, ...]:
        if row_idx >= br + 3:
            return ()  # base case: no more rows
        # Get values from current row in the box, filter non-zeros via custom_filter
        row_vals = custom_filter(
            lambda v: v != 0,
            tuple(board[row_idx][col] for col in range(bc, bc + 3))
        )
        # Recursively process remaining rows and concatenate
        return row_vals + collect_rows(row_idx + 1)
    
    return collect_rows(br)


# ============================================================================
# PARADIGM: Functional Programming using custom_filter + Immutability
# WHY: Declaratively computes available candidates using set operations
# HOW: Uses custom_filter to select valid candidates, combines sets functionally
# Pure function - same input always produces same output, no side effects
# ============================================================================
def candidates_for(board: Board, r: int, c: int) -> Tuple[int, ...]:
    """Get all valid candidates for a cell (1-9 that don't violate constraints)"""
    if board[r][c] != 0:
        return (board[r][c],)  # Cell already filled
    
    # Functionally combine all used values from row, column, and box
    used = set(row_values(board, r)) | set(col_values(board, c)) | set(box_values(board, r, c))
    
    # Filter digits 1-9 to find available candidates
    return custom_filter(lambda x: x not in used, tuple(range(1, 10)))


# ============================================================================
# PARADIGM: Using Custom Higher-Order Function (map_2d)
# WHY: Uses our custom higher-order function instead of built-in map
# HOW: map_2d takes a function and applies it to every (row, col) position
# Demonstrates creating and using our own higher-order functions
# ============================================================================
def all_candidates(board: Board) -> CandidatesBoard:
    """Compute candidates for every cell in the board using custom higher-order function"""
    return map_2d(lambda r, c: candidates_for(board, r, c))


# ============================================================================
# PARADIGM: Using Custom Higher-Order Function (fold_board)
# WHY: Uses our custom fold to check all cells instead of built-in all()
# HOW: fold_board accumulates a boolean, checking each cell is non-zero
# Demonstrates functional folding/reduction with custom higher-order function
# ============================================================================
def is_solved(board: Board) -> bool:
    """Check if board is completely filled (no zeros remaining) using custom fold"""
    return fold_board(
        lambda acc, r, c, value: acc and (value != 0),
        board,
        True  # initial: assume solved until we find a zero
    )


# ============================================================================
# PARADIGM: Functional Programming using custom_any/custom_filter + Recursion
# WHY: Checks for conflicts using existential quantification (any violation exists)
# HOW: Uses recursive helper for boxes, custom_any/custom_filter for rows/cols
# Demonstrates functional approach to validation with custom higher-order helpers
# ============================================================================
def has_conflict(board: Board) -> bool:
    """Check if any row, column, or box has duplicate non-zero values (pure recursion, no loops)"""

    # Pure recursive function to check if a tuple has duplicate non-zero values
    def has_duplicates(values: Tuple[int, ...]) -> bool:
        # Filter out zeros using recursion
        def filter_nonzero(idx: int, acc: Tuple[int, ...]) -> Tuple[int, ...]:
            if idx == len(values):
                return acc
            val = values[idx]
            if val != 0:
                return filter_nonzero(idx + 1, acc + (val,))
            return filter_nonzero(idx + 1, acc)
        non_zero = filter_nonzero(0, ())
        # Check for duplicates recursively, not using set
        def has_dupe_rec(seq: Tuple[int, ...], seen: Tuple[int, ...]) -> bool:
            if not seq:
                return False
            if seq[0] in seen:
                return True
            return has_dupe_rec(seq[1:], seen + (seq[0],))
        return has_dupe_rec(non_zero, ())

    # Recursively check all rows for duplicates
    def rows_conflict_rec(idx: int) -> bool:
        if idx == 9:
            return False
        return has_duplicates(board[idx]) or rows_conflict_rec(idx + 1)

    # Recursively check all columns for duplicates
    def cols_conflict_rec(idx: int) -> bool:
        if idx == 9:
            return False
        # Construct the column recursively
        def build_col(ci: int, acc: Tuple[int, ...]) -> Tuple[int, ...]:
            if ci == 9:
                return acc
            return build_col(ci + 1, acc + (board[ci][idx],))
        col = build_col(0, ())
        return has_duplicates(col) or cols_conflict_rec(idx + 1)

    # Recursively check all 3x3 boxes for duplicates
    def boxes_conflict_rec(index: int) -> bool:
        if index == 9:
            return False
        br = (index // 3) * 3
        bc = (index % 3) * 3
        # Collect box values recursively
        def box_vals_rec(dr: int, dc: int, acc: Tuple[int, ...]) -> Tuple[int, ...]:
            if dr == 3:
                return acc
            if dc == 3:
                return box_vals_rec(dr + 1, 0, acc)
            return box_vals_rec(dr, dc + 1, acc + (board[br + dr][bc + dc],))
        vals = box_vals_rec(0, 0, ())
        return has_duplicates(vals) or boxes_conflict_rec(index + 1)

    return rows_conflict_rec(0) or cols_conflict_rec(0) or boxes_conflict_rec(0)


# ============================================================================
# PARADIGM: Using Custom Higher-Order Function (fold_board)
# WHY: Uses our custom fold to check for empty candidates instead of built-in any()
# HOW: fold_board accumulates a boolean, checking if any cell has no candidates
# Demonstrates existential quantification with custom higher-order function
# ============================================================================
def cell_has_no_candidates(cands_board: CandidatesBoard) -> bool:
    """Check if any cell has no valid candidates (unsolvable state) using custom fold"""
    return fold_board(
        lambda acc, r, c, cands: acc or (len(cands) == 0),
        cands_board,
        False  # initial: assume no empty candidates until we find one
    )
