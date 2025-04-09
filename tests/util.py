import tree_sitter_c
from tree_sitter import Language, Parser, Point

from modified_cognitive_complexity import *


def assert_scores(code: str, expected_scores: list[tuple[Location, Cost]]):
    lang = Language(tree_sitter_c.language())
    parser = Parser(lang)
    tree = parser.parse(code.encode())

    scores = cognitive_complexity(tree)
    assert sorted(scores) == sorted(expected_scores)

def score(
    start: tuple[int, int],
    end: tuple[int, int],
    increment: int,
    nesting: Nesting | None
) -> tuple[Location, Cost]:
    return (
        Location(
            start=Point(row=start[0], column=start[1]),
            end=Point(row=end[0], column=end[1])
        ),
        Cost(increment = increment, nesting=nesting)
    )
    