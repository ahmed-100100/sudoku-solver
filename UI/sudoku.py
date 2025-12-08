# sudoku_gui.py
import tkinter as tk
from tkinter import messagebox
import random
import copy

# Functional solver imports
from functional_solver import solve as functional_solve
from functional_helpers import to_immutable, from_immutable, has_conflict

# Imperative solver imports
from utils_imperative import (
    Board,
    CandidatesBoard,
    all_candidates,
    cell_has_no_candidates,
    copy_board,
    has_conflict as has_conflict_imp,
    is_solved as is_solved_imp
)
from solver_imperative import solve as imperative_solve

GRID_SIZE = 9
BOX_SIZE = 3
REMOVED_CELLS = 40

class Sudoku:
    def __init__(self):
        self.board = [[0]*GRID_SIZE for _ in range(GRID_SIZE)]

    def generate_full_board(self):
        self.board = [[0]*GRID_SIZE for _ in range(GRID_SIZE)]

        def possible(r, c, val):
            for j in range(GRID_SIZE):
                if self.board[r][j] == val:
                    return False
            for i in range(GRID_SIZE):
                if self.board[i][c] == val:
                    return False
            br = (r // BOX_SIZE) * BOX_SIZE
            bc = (c // BOX_SIZE) * BOX_SIZE
            for i in range(br, br+BOX_SIZE):
                for j in range(bc, bc+BOX_SIZE):
                    if self.board[i][j] == val:
                        return False
            return True

        def fill():
            for i in range(GRID_SIZE):
                for j in range(GRID_SIZE):
                    if self.board[i][j] == 0:
                        nums = list(range(1, GRID_SIZE+1))
                        random.shuffle(nums)
                        for val in nums:
                            if possible(i, j, val):
                                self.board[i][j] = val
                                if fill():
                                    return True
                                self.board[i][j] = 0
                        return False
            return True

        fill()
        return self.board

    def make_puzzle(self, holes=REMOVED_CELLS):
        self.generate_full_board()
        positions = [(i,j) for i in range(GRID_SIZE) for j in range(GRID_SIZE)]
        random.shuffle(positions)
        removed = 0
        while removed < holes and positions:
            i, j = positions.pop()
            self.board[i][j] = 0
            removed += 1
        return self.board


class SudokuGUI(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.sudoku = Sudoku()
        self.original = None
        self.cells = {}
        self.selected = None
        self.use_functional = True  # default solver
        self.create_widgets()
        self.new_puzzle()

    def create_widgets(self):
        self.parent.title("Sudoku - Spyder / tkinter")
        top_frame = tk.Frame(self.parent)
        top_frame.pack(padx=10, pady=10)

        grid_frame = tk.Frame(top_frame)
        grid_frame.grid(row=0, column=0, padx=10, pady=10)

        self.box_frames = {}
        for box_row in range(BOX_SIZE):
            for box_col in range(BOX_SIZE):
                frame_bg = "#F5F5F5" if (box_row + box_col) % 2 == 0 else "white"
                frame = tk.Frame(grid_frame, highlightthickness=3, highlightbackground="black", bd=0, bg=frame_bg)
                frame.grid(row=box_row, column=box_col)
                self.box_frames[(box_row, box_col)] = frame

                for i in range(BOX_SIZE):
                    for j in range(BOX_SIZE):
                        r = box_row * BOX_SIZE + i
                        c = box_col * BOX_SIZE + j
                        e = tk.Entry(frame, width=2, font=("Helvetica",18), justify="center", bd=1)
                        e.grid(row=i, column=j, ipadx=6, ipady=6, padx=1, pady=1)
                        e.bind("<FocusIn>", self._make_focus_handler(r,c))
                        e.bind("<KeyRelease>", self._make_key_handler(r,c))
                        self.cells[(r,c)] = e

        # Buttons
        btn_frame = tk.Frame(top_frame)
        btn_frame.grid(row=1, column=0, pady=(5,0))
        btns = [
            ("New Puzzle", self.new_puzzle),
            ("Solve", self.solve_current),
            ("Validate", self.validate_current),
            ("Clear", self.clear_editable),
            ("Hint", self.give_hint)
        ]
        for i, (txt, cmd) in enumerate(btns):
            tk.Button(btn_frame, text=txt, command=cmd,
                      font=("Helvetica",12,"bold"),
                      bg="#4CAF50", fg="white",
                      activebackground="#45A049",
                      padx=10, pady=5, bd=3).grid(row=0, column=i, padx=5)

        # Solver choice (Functional / Imperative)
        solver_frame = tk.Frame(top_frame)
        solver_frame.grid(row=2, column=0, pady=(5,0))
        tk.Label(solver_frame, text="Choose Solver:").pack(side="left")
        tk.Button(solver_frame, text="Functional", command=lambda: self.set_solver(True),
                  bg="#2196F3", fg="white", padx=8, pady=3).pack(side="left", padx=5)
        tk.Button(solver_frame, text="Imperative", command=lambda: self.set_solver(False),
                  bg="#FF5722", fg="white", padx=8, pady=3).pack(side="left", padx=5)

        self.status_var = tk.StringVar(value="Ready")
        tk.Label(self.parent, textvariable=self.status_var, font=("Helvetica",12)).pack(pady=(5,10))
        self.parent.resizable(False, False)

    def set_solver(self, functional: bool):
        self.use_functional = functional
        mode = "Functional" if functional else "Imperative"
        self.status_var.set(f"{mode} solver selected")

    # Focus & key handlers
    def _make_focus_handler(self, r, c):
        def handler(_):
            self.selected = (r,c)
            self._update_cell_styles()
        return handler

    def _make_key_handler(self, r, c):
        def handler(_):
            entry = self.cells[(r,c)]
            txt = entry.get().strip()
            if txt == "":
                val = 0
            else:
                if not txt.isdigit() or txt == "0":
                    entry.delete(0, tk.END)
                    return
                if len(txt) > 1:
                    txt = txt[-1]
                    entry.delete(0, tk.END)
                    entry.insert(0, txt)
                val = int(txt)

            if self.original and self.original[r][c] == 0:
                self.sudoku.board[r][c] = val
            else:
                entry.delete(0, tk.END)
                entry.insert(0, str(self.original[r][c]))

            self._update_cell_styles()
        return handler

    # ------------------------ NEW PUZZLE ------------------------
    def new_puzzle(self):
        self.status_var.set("Generating puzzle...")
        self.parent.update_idletasks()

        puzzle = self.sudoku.make_puzzle()
        self.original = copy.deepcopy(puzzle)

        # Solve puzzle in background for hints / solve button
        if self.use_functional:
            solved = functional_solve(copy.deepcopy(puzzle))
        else:
            solved = imperative_solve(copy.deepcopy(puzzle))
        self.solved_board = solved

        for r in range(9):
            for c in range(9):
                e = self.cells[(r,c)]
                e.config(state="normal")
                e.delete(0, tk.END)
                v = puzzle[r][c]
                if v != 0:
                    e.insert(0, str(v))
                    e.config(state="readonly", readonlybackground="#DDDDDD")
                else:
                    e.config(background="white")

        self.status_var.set("New puzzle ready")
        self._update_cell_styles()

    # ------------------------ SOLVE ------------------------
    def solve_current(self):
        board = self.sudoku.board
        if self.use_functional:
            if has_conflict(to_immutable(board)):
                messagebox.showwarning("Sudoku", "Cannot solve: conflicts exist.")
                self.status_var.set("Conflicts detected!")
                return
            solved = functional_solve(copy.deepcopy(board))
        else:
            if has_conflict_imp(board):
                messagebox.showwarning("Sudoku", "Cannot solve: conflicts exist.")
                self.status_var.set("Conflicts detected!")
                return
            solved = imperative_solve(copy.deepcopy(board))

        if solved is None:
            messagebox.showinfo("Sudoku","No solution found.")
            return

        for r in range(9):
            for c in range(9):
                e = self.cells[(r,c)]
                e.config(state="normal")
                e.delete(0, tk.END)
                e.insert(0, str(solved[r][c]))
                e.config(state="readonly", readonlybackground="#DDDDDD")

        self.status_var.set("Solved!")

    # ------------------------ VALIDATE ------------------------
    def validate_current(self):
        board = self.sudoku.board
        if self.use_functional:
            board_immutable = to_immutable(board)
            conflicts = has_conflict(board_immutable)
        else:
            conflicts = has_conflict_imp(board)

        if not conflicts:
            self.status_var.set("Board valid.")
            messagebox.showinfo("Validate", "No conflicts!")
        else:
            for r in range(9):
                for c in range(9):
                    val = board[r][c]
                    if val != 0:
                        row_vals = [board[r][j] for j in range(9) if j != c]
                        col_vals = [board[i][c] for i in range(9) if i != r]
                        br, bc = (r//3)*3, (c//3)*3
                        box_vals = [board[i][j] for i in range(br, br+3) for j in range(bc, bc+3) if (i,j)!=(r,c)]
                        if val in row_vals or val in col_vals or val in box_vals:
                            self.cells[(r,c)].config(background="#FFC3C3")
            self.status_var.set("Conflicts detected.")
            messagebox.showwarning("Validate", "There are conflicts.")

    # ------------------------ CLEAR ------------------------
    def clear_editable(self):
        if not self.original:
            return
        for r in range(9):
            for c in range(9):
                if self.original[r][c] == 0:
                    e = self.cells[(r,c)]
                    e.config(state="normal")
                    e.delete(0, tk.END)
                    e.config(background="white")
                    self.sudoku.board[r][c] = 0
        self.status_var.set("Cleared.")
        self._update_cell_styles()

    # ------------------------ HINT ------------------------
    def give_hint(self):
        if not hasattr(self, "solved_board") or self.solved_board is None:
            messagebox.showinfo("Hint","No solved board available.")
            return

        for r in range(9):
            for c in range(9):
                if self.sudoku.board[r][c] == 0:
                    v = self.solved_board[r][c]
                    e = self.cells[(r,c)]
                    e.delete(0, tk.END)
                    e.insert(0, str(v))
                    e.config(background="#E6FFE6")
                    self.sudoku.board[r][c] = v
                    self.status_var.set(f"Hint: filled ({r+1},{c+1})")
                    return

        messagebox.showinfo("Hint","No empty cells remaining.")

    # ------------------------ STYLE ------------------------
    def _update_cell_styles(self):
        for box_r in range(BOX_SIZE):
            for box_c in range(BOX_SIZE):
                bg = "#F5F5F5" if (box_r+box_c)%2==0 else "white"
                self.box_frames[(box_r,box_c)].config(bg=bg)

        if not self.selected:
            for r in range(9):
                for c in range(9):
                    e = self.cells[(r,c)]
                    if self.original and self.original[r][c]!=0:
                        e.config(readonlybackground="#DDDDDD")
            return

        sr, sc = self.selected
        for r in range(9):
            for c in range(9):
                e = self.cells[(r,c)]
                if (r,c) == (sr,sc):
                    e.config(background="#BFDFFF")
                elif r==sr or c==sc or (r//3, c//3)==(sr//3, sc//3):
                    e.config(background="#F0F8FF")
                else:
                    box = self.box_frames[(r//3,c//3)]
                    e.config(background=box.cget("bg"))


def main():
    root = tk.Tk()
    app = SudokuGUI(root)
    root.mainloop()

if __name__=="__main__":
    main()
