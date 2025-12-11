from functional.functional_solver import solve as solve_fun
from imperative.solver_imperative import solve as solve_imp


def print_sudoku(board):
    if board is None:
        print("No solution")
        return
    
    print("+" + "-" * 21 + "+")
    for i, row in enumerate(board):
        print("|", end="")
        for j, cell in enumerate(row):
            if j % 3 == 0 and j > 0:
                print(" |", end="")
            print(f" {cell if cell != 0 else '.'}", end="")
        print(" |")
        if (i + 1) % 3 == 0 and i < 8:
            print("|" + "-" * 7 + "+" + "-" * 7 + "+" + "-" * 7 + "|")
    print("+" + "-" * 21 + "+")


puzzle = [
    [5,3,0,0,7,0,0,0,0],
    [6,0,0,1,9,5,0,0,0],
    [0,9,8,0,0,0,0,6,0],
    [8,0,0,0,6,0,0,0,3],
    [4,0,0,8,0,3,0,0,1],
    [7,0,0,0,2,0,0,0,6],
    [0,6,0,0,0,0,2,8,0],
    [0,0,0,4,1,9,0,0,5],
    [0,0,0,0,8,0,0,7,9],
]

hardpuzzle = [
    [8, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 3, 6, 0, 0, 0, 0, 0],
    [0, 7, 0, 0, 9, 0, 2, 0, 0],
    [0, 5, 0, 0, 0, 7, 0, 0, 0],
    [0, 0, 0, 0, 4, 5, 7, 0, 0],
    [0, 0, 0, 1, 0, 0, 0, 3, 0],
    [0, 0, 1, 0, 0, 0, 0, 6, 8],
    [0, 0, 8, 5, 0, 0, 0, 1, 0],
    [0, 9, 0, 0, 0, 0, 4, 0, 0]
]

# sol_imp = solve_imp(puzzle)
# sol_fun = solve_fun(puzzle)
sol_imp_hard = solve_imp(hardpuzzle)
sol_fun_hard = solve_fun(hardpuzzle)

print("imperative solved:", sol_imp_hard is not None)
print("functional solved:", sol_fun_hard is not None)
print("solutions match:", sol_imp_hard == sol_fun_hard)
print("\nFunctional Solution:")
print_sudoku(sol_fun_hard)
print("\nImperative Solution:")
print_sudoku(sol_imp_hard)