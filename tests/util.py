import tree_sitter_c
from tree_sitter import Language, Parser, Point

from modified_cognitive_complexity import *


def assert_scores(
    code: str,
    expected_toplevel_scores: Scores,
    expected_function_scores: dict[bytes, Scores] = {}
):
    lang = Language(tree_sitter_c.language())
    parser = Parser(lang)
    tree = parser.parse(code.encode())

    toplevel_scores, function_scores = cognitive_complexity(tree.walk())
    assert sorted(toplevel_scores) == sorted(expected_toplevel_scores)
    assert sorted(expected_function_scores) == sorted(expected_function_scores)

def score(
    start: tuple[int, int],
    end: tuple[int, int],
    increment: int,
    nesting: Nesting | None
) -> tuple[Location, Score]:
    return (
        Location(
            start=Point(row=start[0], column=start[1]),
            end=Point(row=end[0], column=end[1])
        ),
        Score(increment = increment, nesting=nesting)
    )
    