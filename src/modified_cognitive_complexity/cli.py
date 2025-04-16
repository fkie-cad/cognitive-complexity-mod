import sys
from collections import defaultdict
from typing import Annotated

import tree_sitter_cpp
import typer
from tree_sitter import Language, Parser

from .complexity import cognitive_complexity, Score

app = typer.Typer()


@app.command()
def main(
    annotate: Annotated[bool, typer.Option(help="Display per-line complexity annotations instead of a single summary value.")] = False
):
    data = sys.stdin.buffer.read()

    lang = Language(tree_sitter_cpp.language())
    parser = Parser(lang)
    tree = parser.parse(data)

    function_scores: dict
    scores_by_function = cognitive_complexity(tree.walk())

    if annotate:
        lines = data.replace(b'\t', b'    ').decode().splitlines()
        indent = max(len(line) for line in lines)

        cost_by_line: dict[int, list[Score]] = defaultdict(list)
        for _, scores in scores_by_function.items():
            for location, cost in scores:
                cost_by_line[location.start.row].append(cost)

        costs_increment = ["+".join(str(cost.increment) for cost in cost_by_line[i]) for i in range(len(lines))]
        costs_nesting = ["+".join(str(0 if cost.nesting is None else cost.nesting.value) for cost in cost_by_line[i]) for i in range(len(lines))]
        costs_goto = ["+".join(str(0 if cost.nesting is None else cost.nesting.goto) for cost in cost_by_line[i]) for i in range(len(lines))]

        max_increment = max(3, max(len(s) for s in costs_increment))
        max_nesting = max(4, max(len(s) for s in costs_nesting))
        max_goto = max(4, max(len(s) for s in costs_goto))

        prefix = " // "
        print(f"{' ' * indent}{' ' * len(prefix)}{'Inc': ^{max_increment}} {'Nest': ^{max_nesting}} {'Goto': ^{max_goto}}")
        for line, c_increment, c_nesting, c_goto in zip(lines, costs_increment, costs_nesting, costs_goto):
            print(f"{line: <{indent}}{prefix}{c_increment: >{max_increment}} {c_nesting: >{max_nesting}} {c_goto: >{max_goto}}")
        
        print("")


    total_cost = sum(
        sum(cost.total for _, cost in scores) for scores in scores_by_function.values()
    )
    print(f"Total Modified Cognitive Complexity: {total_cost}")
    
    if len(scores_by_function) > 1:
        print("")
        print("Complexity by function:")
    
        # Per-function summary
        for func_name, function_scores in scores_by_function.items():
            if func_name is None:
                continue
            
            func_total = sum(cost.total for _, cost in function_scores)
            func_name = func_name.decode(errors="replace")
            print(f"Function '{func_name}': {func_total}")

        print(f"Top-level complexity: {sum(cost.total for _, cost in scores_by_function[None])}")


if __name__ == "__main__":
    app()
