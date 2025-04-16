import textwrap

import pytest

from modified_cognitive_complexity.complexity import Nesting, Scores
from .util import assert_toplevel_scores, score


@pytest.mark.parametrize(
    ("code", "expected_scores"),
    (
        pytest.param(
            "(a && b && c)",
            [
                score((0, 1), (0, 12), 1, None),
            ],
            id="and",
        ),
        pytest.param(
            "(a || b || c)",
            [
                score((0, 1), (0, 12), 1, None),
            ],
            id="or",
        ),
        pytest.param(
            """\
            (a && b && c
                || d || e
                && f)
            """,
            [
                score((0, 1), (0, 12), 1, None),
                score((0, 1), (2, 8), 1, None),
                score((1, 12), (2, 8), 1, None),
            ],
            id="mixed 1",
        ),
        pytest.param(
            """\
            (a && !(b && c))
            """,
            [
                score((0, 1), (0, 15), 1, None),
                score((0, 8), (0, 14), 1, None),
            ],
            id="mixed 2",
        ),
        pytest.param(
            """\
            if (x) {
                (a && b && c);
            }
            """,
            [
                score((0, 0), (2, 1), 1, Nesting()),
                score((1, 5), (1, 16), 1, None),
            ],
            id="nested",
        ),
    ),
)
def test(code: str, expected_scores: Scores):
    assert_toplevel_scores(textwrap.dedent(code), expected_scores)