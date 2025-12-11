from typing import List, Optional, Tuple
from imperative.utils_imperative import (
    Board,
    CandidatesBoard,
    all_candidates,
    cell_has_no_candidates,
    copy_board,
    has_conflict,
    is_solved,
    apply_to_cells,
)


def set_cell(board: Board, r: int, c: int, val: int) -> None:
    board[r][c] = val


def propagate(board: Board) -> Optional[Board]:
    while True:
        cands = all_candidates(board)
        if cell_has_no_candidates(cands):
            return None

        singles: List[Tuple[int, int, int]] = []
        def check_single(r: int, c: int):
            if board[r][c] == 0 and len(cands[r][c]) == 1:
                singles.append((r, c, cands[r][c][0]))
        apply_to_cells(check_single) #the higher order function

        if not singles:
            return board

        for r, c, v in singles:
            set_cell(board, r, c, v)


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
