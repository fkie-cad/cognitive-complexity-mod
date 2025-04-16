import textwrap

import pytest

from modified_cognitive_complexity.complexity import Nesting, Scores
from .util import assert_toplevel_scores, score


@pytest.mark.parametrize(
    ("code", "expected_scores"),
    (
        pytest.param(
            """\
            try {
                if (x) {}
            } catch() {
                if (x) {}            
            } catch() {
                if (x) {}            
            }
            """,
            [
                score((1, 4), (1, 13), 1, Nesting(value=0)),
                score((2, 2), (4, 1), 1, Nesting(value=0)),
                score((3, 4), (3, 13), 1, Nesting(value=1)),
                score((4, 2), (6, 1), 1, Nesting(value=0)),
                score((5, 4), (5, 13), 1, Nesting(value=1)),
            ],
            id="try",
        ),
    ),
)
def test(code: str, expected_scores: Scores):
    assert_toplevel_scores(textwrap.dedent(code), expected_scores)