#!/usr/bin/env python3

import argparse
import os
from argparse import RawTextHelpFormatter

template = r"""(define (problem PROBLEM)
    (:domain blocksworld)
    (:objects BLOCKS - object)
    (:init (arm-empty) INIT)
    (:goal (and GOAL))
)
"""


def get_pddl_state(state, n):
    blocks = [f"b{i}" for i in range(1, n + 1)]

    output = []

    something_on_top = set()
    positions = state.split()
    for i, below in enumerate(positions):
        block = f"b{i + 1}"
        below_block = f"b{int(below)}"
        if below == "0":
            output.append(f"(on-table {block})")
        else:
            output.append(f"(on {block} {below_block})")
            something_on_top.add(below_block)

    for block in blocks:
        if block not in something_on_top:
            output.append(f"(clear {block})")

    return " ".join(output)


def main():
    parser = argparse.ArgumentParser(
        description="Generate Blocksworld PDDL problem files and optimal plans",
        formatter_class=RawTextHelpFormatter,
    )
    parser.add_argument("-n", type=int, default=100, help="number of blocks")
    parser.add_argument("-r", type=int, default=2024, help="random seed")
    parser.add_argument(
        "-v",
        type=int,
        default=0,
        choices=[0, 1, 2],
        help="verbosity level\n"
        "0 = PDDL file only\n"
        "1 = optimal plan length in the PDDL file\n"
        "2 = PDDL file and an optimal plan",
    )
    parser.add_argument("-o", type=str, default="output", help="name of output file(s)")
    parser.add_argument("--debug", action="store_true", help="print everything from binary")
    args = parser.parse_args()

    n = args.n
    r = args.r
    v = args.v
    print(f"{n=}")
    print(f"{r=}")
    print(f"{v=}")

    if v == 2:
        raise NotImplementedError("Generating the optimal plan has not been implemented yet.")

    # test binary exists
    file_path = os.path.abspath(__file__)
    dir_path = os.path.dirname(file_path)
    binary = f"{dir_path}/bbwstates_src/bbwstates"
    if not os.path.exists(binary):
        print(f"Binary {binary} not built. Please build it with make. Exiting...")
        return

    # determine binary args
    blocks_args = f"-n {n} -p 1 -r {r} -v 2"
    if v == 0:
        # use the cheapest solver
        blocks_args += " -a 0"
    else:
        # use the optimal solver
        blocks_args += " -a 3"
    output = []
    cmd = f"{binary} {blocks_args}"
    cmd_output = os.popen(cmd).read()
    if args.debug:
        print("-" * 80)
        print(cmd_output)
        print("-" * 80)
    for line in cmd_output.split("\n"):
        line.replace("\n", "")
        line = line.strip()
        output.append(line)

    # parse binary output
    init_state = output[1]
    goal_state = output[3]
    # each action is a pickup/unstack and then putdown/stack
    plan_length = str(int(output[4]) * 2)
    print(f"{init_state=}")
    print(f"{goal_state=}")
    print(f"{plan_length=}")

    # write PDDL file
    problem_file = f"{args.o}.pddl"
    output = template.replace("PROBLEM", f"blocksworld_n{n}_r{r}")
    output = output.replace("BLOCKS", " ".join([f"b{i}" for i in range(1, n + 1)]))
    output = output.replace("INIT", get_pddl_state(init_state, n))
    output = output.replace("GOAL", get_pddl_state(goal_state, n))
    if v > 0:
        output = f";; optimal plan length: {plan_length}\n" + output

    with open(problem_file, "w") as f:
        f.write(output)

    print(f"PDDL file successfully written to {problem_file}")


if __name__ == "__main__":
    main()
