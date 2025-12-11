from typing import List, Optional

# Types for mutable boards
Board = List[List[int]]              # mutable 9x9 board
CandidatesBoard = List[List[List[int]]]  # 9x9 of candidate lists


def apply_to_cells(func) -> None:
    for r in range(9):
        for c in range(9):
            func(r, c)

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
    def dup(xs: List[int]) -> bool:
        xs2 = []
        for x in xs:
            if x != 0:
                xs2.append(x)
        return len(xs2) != len(set(xs2))

    for r in range(9):
        if dup(board[r]):
            return True
    for c in range(9):
        col_vals = []
        def collect_col_vals(r: int, _):
            if _ == c:
                col_vals.append(board[r][c])
        apply_to_cells(collect_col_vals) # the higher order function
        if dup(col_vals):
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
