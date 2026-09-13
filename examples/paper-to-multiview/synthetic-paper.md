# A budget-limited iterative search: synthetic teaching note

This is original synthetic teaching material, not a published study and not the user's research.

## P1 — Question and inputs
We describe how to retain a best-so-far feasible solution under a fixed update budget. Inputs are problem data and algorithm parameters, including a nonnegative integer T_max. This note does not specify a particular search heuristic or objective function.

## P2 — Assumptions
Initialization and candidate generation return feasible candidates in finite time. Evaluation and best-so-far updates also finish in finite time. The first evaluation initializes the incumbent; later evaluations compare using the problem's objective.

## P3 — Exact algorithm
Start; read problem data and parameters; initialize a feasible candidate and t=0; evaluate the current candidate and update the best-so-far solution; check t >= T_max.
If Yes, output the best-so-far solution and end.
If No, generate the next feasible candidate, increment t by one, and return to evaluation, not to initialization.

## P4 — What this example does not establish
This note reports no empirical benchmark, no numeric performance improvement and no global-optimality theorem. It demonstrates control logic only. Infeasible-candidate repair is outside the assumed procedure; it must not be invented as a documented step.

## P5 — A structural consequence
Under P2 and P3, there are T_max updates and T_max+1 evaluations, including the initial evaluation. Even when T_max=0 there is one evaluation. This is not a claim about search quality.
