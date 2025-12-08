# functional_solver.py
from typing import Optional, Tuple
from functional.utlils_functional import (
    Board,
    CandidatesBoard,
    all_candidates,
    is_solved,
    to_immutable,
    from_immutable,
    cell_has_no_candidates,
)

# Immutable board helper: set a single cell's value and return a new Board
def set_cell(board: Board, r: int, c: int, val: int) -> Board:
    # build new rows immutably
    new_rows = []
    for rr in range(9):
        if rr != r:
            new_rows.append(board[rr])
        else:
            # replace row rr with a new tuple
            row = tuple(board[rr][cc] if cc != c else val for cc in range(9))
            new_rows.append(row)
    return tuple(new_rows)  # type: ignore

# Constraint propagation: fill all singletons repeatedly until stable
def propagate(board: Board) -> Optional[Board]:
    def loop(b: Board) -> Optional[Board]:
        cands = all_candidates(b)
        # if any cell has zero candidates -> contradiction
        if cell_has_no_candidates(cands):
            return None
        # find singleton candidates to fix
        singles = []
        for r in range(9):
            for c in range(9):
                if b[r][c] == 0 and len(cands[r][c]) == 1:
                    singles.append((r, c, cands[r][c][0]))
        if not singles:
            return b  # stable
        # apply all singles at once (immutably)
        b2 = b
        for (r, c, v) in singles:
            b2 = set_cell(b2, r, c, v)
        # repeat
        return loop(b2)
    return loop(board)

# Choose cell with MRV (fewest candidates >1)
def choose_mrv_cell(board: Board) -> Optional[Tuple[int, int, Tuple[int, ...]]]:
    cands = all_candidates(board)
    best = None  # (r,c,cands)
    for r in range(9):
        for c in range(9):
            if board[r][c] == 0:
                length = len(cands[r][c])
                if length == 0:
                    return None  # dead end
                if length == 1:
                    # If there's singleton, MRV would choose it, but propagate should have fixed it.
                    # Still handle safely by considering it.
                    return (r, c, cands[r][c])
                if best is None or length < len(best[2]):
                    best = (r, c, cands[r][c])
    return best

# Recursive search with propagation + MRV
def search(board: Board) -> Optional[Board]:
    # first propagate constraints
    p = propagate(board)
    if p is None:
        return None
    if is_solved(p):
        return p
    choice = choose_mrv_cell(p)
    if choice is None:
        return None
    r, c, candidates = choice
    # try each candidate
    for val in candidates:
        new_board = set_cell(p, r, c, val)
        result = search(new_board)
        if result is not None:
            return result
    return None

# Public solve function: accepts list-of-lists or tuple-of-tuples
def solve(input_board) -> Optional[list]:
    # normalize to immutable Board
    if isinstance(input_board, list):
        b = to_immutable(input_board)
    else:
        b = input_board  # assume already immutable
    # quick conflict check
    from functional.functional_helpers import has_conflict
    if has_conflict(b):
        return None
    res = search(b)
    if res is None:
        return None
    return from_immutable(res)
