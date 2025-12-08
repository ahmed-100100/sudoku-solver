# functional_helpers.py file
from typing import Tuple, List

# Types
Board = Tuple[Tuple[int, ...], ...]                # immutable 9x9 board
CandidatesBoard = Tuple[Tuple[Tuple[int, ...], ...], ...]  # 9x9 of candidate tuples

# Convert mutable list-of-lists -> immutable tuple-of-tuples
def to_immutable(board: List[List[int]]) -> Board:
    return tuple(tuple(int(cell) for cell in row) for row in board)

# Convert back to list-of-lists (for printing)
def from_immutable(board: Board) -> List[List[int]]:
    return [list(row) for row in board]

# Raw values (non-zero)
def row_values(board: Board, r: int) -> Tuple[int, ...]:
    return tuple(v for v in board[r] if v != 0)

# Column values (non-zero)
def col_values(board: Board, c: int) -> Tuple[int, ...]:
    return tuple(board[r][c] for r in range(9) if board[r][c] != 0)

# Box values (non-zero)
def box_values(board: Board, r: int, c: int) -> Tuple[int, ...]:
    br = (r // 3) * 3
    bc = (c // 3) * 3
    vals = []
    for rr in range(br, br + 3):
        for cc in range(bc, bc + 3):
            v = board[rr][cc]
            if v != 0:
                vals.append(v)
    return tuple(vals)

# Candidates for a single cell (sorted tuple)
def candidates_for(board: Board, r: int, c: int) -> Tuple[int, ...]:
    if board[r][c] != 0:
        return (board[r][c],)
    used = set(row_values(board, r)) | set(col_values(board, c)) | set(box_values(board, r, c))
    cand = tuple(x for x in range(1, 10) if x not in used)
    return cand

# Full candidates board 9x9
def all_candidates(board: Board) -> CandidatesBoard:
    return tuple(
        tuple(candidates_for(board, r, c) for c in range(9))
        for r in range(9)
    )

# Check solved (no zeros)
def is_solved(board: Board) -> bool:
    return all(all(cell != 0 for cell in row) for row in board)

# Check any conflicts (duplicate non-zero in row/col/box)
def has_conflict(board: Board) -> bool:
    # Helper function to check for duplicates in a list
    def dup(xs):
        xs2 = [x for x in xs if x != 0]
        return len(xs2) != len(set(xs2))
    # rows
    for r in range(9):
        if dup(board[r]):
            return True
    # cols
    for c in range(9):
        if dup([board[r][c] for r in range(9)]):
            return True
    # boxes
    for br in (0, 3, 6):
        for bc in (0, 3, 6):
            vals = []
            for rr in range(br, br + 3):
                for cc in range(bc, bc + 3):
                    v = board[rr][cc]
                    if v != 0:
                        vals.append(v)
            if len(vals) != len(set(vals)):
                return True
    return False

# Check if any cell has zero candidates (dead state)

def cell_has_no_candidates(cands_board: CandidatesBoard) -> bool:
    return any(any(len(cands_board[r][c]) == 0 for c in range(9)) for r in range(9))
