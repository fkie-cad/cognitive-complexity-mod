import sys
from collections import defaultdict
from typing import Annotated

import tree_sitter_c
import typer
from .complexity import cognitive_complexity, Cost
from tree_sitter import Language, Parser

app = typer.Typer()


@app.command()
def main(
        annotate: Annotated[bool, typer.Option()] = False
):
    data = sys.stdin.buffer.read()

    lang = Language(tree_sitter_c.language())
    parser = Parser(lang)
    tree = parser.parse(data)

    scores = cognitive_complexity(tree)

    complexity = sum(cost.total for (_, cost) in scores)
    if not annotate:
        print(complexity)
    else:
        lines = data.decode().splitlines()
        indent = max(len(line) for line in lines)

        cost_by_line: dict[int, list[Cost]] = defaultdict(list)
        for location, cost in scores:
            cost_by_line[location.start.row].append(cost)

        costs_increment = ["+".join(str(cost.increment) for cost in cost_by_line[i]) for i in range(len(lines))]
        costs_nesting = ["+".join(str(0 if cost.nesting is None else cost.nesting.value) for cost in cost_by_line[i]) for i in range(len(lines))]
        costs_goto = ["+".join(str(0 if cost.nesting is None else cost.nesting.goto) for cost in cost_by_line[i]) for i in range(len(lines))]

        max_increment = max(len(s) for s in costs_increment)
        max_nesting = max(len(s) for s in costs_nesting)
        max_goto = max(len(s) for s in costs_goto)

        prefix = " // "
        print(f"{' ' * indent}{' ' * len(prefix)}{'I': ^{max_increment}} {'N': ^{max_nesting}} {'G': ^{max_goto}}")
        for line, c_increment, c_nesting, c_goto in zip(lines, costs_increment, costs_nesting, costs_goto):
            print(f"{line: <{indent}}{prefix}{c_increment: >{max_increment}} {c_nesting: >{max_nesting}} {c_goto: >{max_goto}}")

        print(f"Modified Cognitive Complexity: {complexity}")


if __name__ == "__main__":
    app()
