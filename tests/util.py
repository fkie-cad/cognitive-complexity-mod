import tree_sitter_cpp
from tree_sitter import Language, Parser, Point

from modified_cognitive_complexity import *


def assert_scores(
    code: str,
    expected_scores: dict[bytes | None, Scores],
    *,
    goto_nesting: bool = True,
    structural_gotos: bool = False
):
    lang = Language(tree_sitter_cpp.language())
    parser = Parser(lang)
    tree = parser.parse(code.encode())

    scores = cognitive_complexity(tree.walk(), goto_nesting=goto_nesting, structural_gotos=structural_gotos)
    _normalize_scores(scores)
    
    expected_scores = expected_scores.copy()
    _normalize_scores(expected_scores)
    
    assert scores == expected_scores


def assert_toplevel_scores(
    code: str,
    expected_scores: Scores,
    *,
    goto_nesting: bool = True,
    structural_gotos: bool = False
):
    lang = Language(tree_sitter_cpp.language())
    parser = Parser(lang)
    tree = parser.parse(code.encode())

    scores = cognitive_complexity(tree.walk(), goto_nesting=goto_nesting, structural_gotos=structural_gotos)
    assert sorted(scores[None]) == sorted(expected_scores)
    assert len(scores) == 1


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


def _normalize_scores(scores: dict[bytes | None, Scores]):
    for key, value in scores.items():
        scores[key] = sorted(value)