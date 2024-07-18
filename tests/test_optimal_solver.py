import os

from solve_optimally import get_optimal_plan_length


def test_ipc23lt():
    plan_dir = "tests/plans"
    problem_dir = "tests/problems"

    for f in sorted(os.listdir(plan_dir)):
        plan_f = f"{plan_dir}/{f}"
        problem_f = f"{problem_dir}/{f.replace('plan', 'pddl')}"

        with open(plan_f, "r") as f:
            plan = f.read()
            true_plan_length = plan.split(" = ")[1].split()[0]
            true_plan_length = int(true_plan_length)

        test_plan_length = get_optimal_plan_length(problem_f)

        print(f"{problem_f=} {test_plan_length=} {true_plan_length=}")

        assert test_plan_length == true_plan_length
