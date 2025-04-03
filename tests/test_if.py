import textwrap

import pytest
from tree_sitter import Point

from modified_cognitive_complexity.complexity import Location, Cost, Nesting
from .util import assert_scores, score


@pytest.mark.parametrize(
    ("code", "expected_scores"),
    (
        pytest.param(
            """\
            if (x) {
                if (y) {}
            }
            """,
            [
                score((0, 0), (2, 1), 1, Nesting()),
                score((1, 4), (1, 13), 1, Nesting(value=1))
            ],
            id="if",
        ),
        pytest.param(
            """\
            if (x) {
                if (y) {}
            } else {
                if (y) {}
            }
            """,
            [
                score((0, 0), (4, 1), 1, Nesting()),
                score((1, 4), (1, 13), 1, Nesting(value=1)),
                score((2, 2), (4, 1), 1, None),
                score((3, 4), (3, 13), 1, Nesting(value=1)),
            ],
            id="if else",
        ),
        pytest.param(
            """\
            if (x) {
                if (y) {
                } else {
                }
            }
            """,
            [
                score((0, 0), (4, 1), 1, Nesting(value=0, goto=0)),
                score((1, 4), (3, 5), 1, Nesting(value=1, goto=0)),
                score((2, 6), (3, 5), 1, None),
            ],
            id="if {if else}",
        ),
        pytest.param(
            """\
            if (x) {
                if (y) {}
            } else if (x) {
                if (y) {}
            }
            """,
            [
                score((0, 0), (4, 1), 1, Nesting()),
                score((1, 4), (1, 13), 1, Nesting(value=1)),
                score((2, 2), (4, 1), 1, None),
                score((3, 4), (3, 13), 1, Nesting(value=1)),
            ],
            id="if else if",
        ),
        pytest.param(
            """\
            if (x) {
                if (y) {}
            } else { if (x) {
                if (y) {}
            } }
            """,
            [
                score((0, 0), (4, 3), 1, Nesting()),
                score((1, 4), (1, 13), 1, Nesting(value=1)),
                score((2, 2), (4, 3), 1, None),
                score((2, 9), (4, 1), 1, Nesting(value=1)),
                score((3, 4), (3, 13), 1, Nesting(value=2)),
            ],
            id="if else { if }",
        ),
    ),
)
def test(code: str, expected_scores: list[tuple[Location, Cost]]):
    assert_scores(textwrap.dedent(code), expected_scores)
