from typing import List, Optional, Tuple

# Types for mutable boards
Board = List[List[int]]              # mutable 9x9 board
CandidatesBoard = List[List[List[int]]]  # 9x9 of candidate lists


def copy_board(board: Board) -> Board:
    """Deep copy a 9x9 board."""
    return [row[:] for row in board]


def row_values(board: Board, r: int) -> List[int]:
    return [v for v in board[r] if v != 0]


def col_values(board: Board, c: int) -> List[int]:
    return [board[r][c] for r in range(9) if board[r][c] != 0]


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
    used = set(row_values(board, r)) | set(col_values(board, c)) | set(box_values(board, r, c))
    return [x for x in range(1, 10) if x not in used]


def all_candidates(board: Board) -> CandidatesBoard:
    return [[candidates_for(board, r, c) for c in range(9)] for r in range(9)]


def is_solved(board: Board) -> bool:
    return all(all(cell != 0 for cell in row) for row in board)


def has_conflict(board: Board) -> bool:
    def dup(xs: List[int]) -> bool:
        xs2 = [x for x in xs if x != 0]
        return len(xs2) != len(set(xs2))

    for r in range(9):
        if dup(board[r]):
            return True
    for c in range(9):
        if dup([board[r][c] for r in range(9)]):
            return True
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
