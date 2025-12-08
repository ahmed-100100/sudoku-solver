from functional.functional_solver import solve as solve_fun
from imperative.solver_imperative import solve as solve_imp
# call them as needed
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

sol_imp = solve_imp(puzzle)
sol_fun = solve_fun(puzzle)

print("imperative solved:", sol_imp is not None)
print("functional solved:", sol_fun is not None)
print("solutions match:", sol_imp == sol_fun)
print(sol_imp)