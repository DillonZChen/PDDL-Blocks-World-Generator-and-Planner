#!/usr/bin/env python3

import argparse
import os
from argparse import RawTextHelpFormatter

import pymimir


def get_generator_state(state, blocks):
    n = len(blocks)
    output = [0 for _ in range(n)]
    for atom in state:
        if atom.predicate.name == "on":
            block_top = blocks[atom.terms[0].name]
            block_bot = blocks[atom.terms[1].name]
            output[block_top] = block_bot  # backend indexes from 0
        elif atom.predicate.name == "on-table":
            block = blocks[atom.terms[0].name]
            output[block] = -1
    return " ".join(map(str, output))


def get_optimal_plan_length(problem_pddl, debug=False):

    domain = pymimir.DomainParser("domain.pddl").parse()
    problem = pymimir.ProblemParser(problem_pddl).parse(domain)

    blocks = {b.name: i for i, b in enumerate(problem.objects)}
    mmr_init_state = problem.initial
    mmr_goal_state = [literal.atom for literal in problem.goal]
    init_state = get_generator_state(mmr_init_state, blocks)
    goal_state = get_generator_state(mmr_goal_state, blocks)
    n = len(blocks)

    # test binary exists
    file_path = os.path.abspath(__file__)
    dir_path = os.path.dirname(file_path)
    binary = f"{dir_path}/bbwstates_src/bbwstates"
    if not os.path.exists(binary):
        print(f"Binary {binary} not built. Please build it with make. Exiting...")
        return

    binary_input_file = f"{problem_pddl}.tmp"
    input_file_content = f"{n}\n{init_state}\n{goal_state}"
    # print(input_file_content)
    with open(binary_input_file, "w") as f:
        f.write(input_file_content)

    binary_output = os.popen(f"{binary} -i {binary_input_file}").read()
    if debug:
        print("-" * 80)
        print(binary_output)
        print("-" * 80)
    opt_plan_length = int(binary_output)
    os.remove(binary_input_file)
    
    # each action is a pickup/unstack and then putdown/stack
    return opt_plan_length * 2


def main():
    parser = argparse.ArgumentParser(
        description="Generate Blocksworld PDDL problem files and optimal plans",
        formatter_class=RawTextHelpFormatter,
    )
    parser.add_argument("problem_pddl", help="path to problem pddl")
    parser.add_argument(
        "-v",
        type=int,
        default=0,
        choices=[0, 1],
        help="verbosity level\n" "0 = optimal plan length only\n" "1 = output plan\n",
    )
    parser.add_argument("--debug", action="store_true", help="print everything from binary")
    args = parser.parse_args()

    if args.v == 1:
        raise NotImplementedError("Generating the optimal plan has not been implemented yet.")

    problem_pddl = args.problem_pddl
    debug = args.debug
    opt_plan_length = get_optimal_plan_length(problem_pddl, debug)
    print(f"{opt_plan_length=}")


if __name__ == "__main__":
    main()
