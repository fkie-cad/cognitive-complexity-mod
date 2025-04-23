import textwrap

import pytest

from modified_cognitive_complexity.complexity import Nesting, Scores
from tests.util import assert_toplevel_scores, score


@pytest.mark.parametrize(
    ("code", "expected_scores"),
    (
        pytest.param(
            """\
            (x 
                ? (y ? a : b))
                : c)
            """,
            [
                score((0, 1), (2, 7), 1, Nesting()),
                score((1, 7), (1, 16), 1, Nesting(value=1)),
            ],
            id="ternary",
        ),
    ),
)
def test(code: str, expected_scores: Scores):
    assert_toplevel_scores(textwrap.dedent(code), expected_scores)