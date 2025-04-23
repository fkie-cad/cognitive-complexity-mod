import textwrap

import pytest

from modified_cognitive_complexity.complexity import Nesting, Scores
from tests.util import assert_toplevel_scores, score


@pytest.mark.parametrize(
    ("code", "expected_scores"),
    (
        pytest.param(
            """\
            while(x) {
                while (y) {
                    
                }
            }
            """,
            [
                score((0, 0), (4, 1), 1, Nesting(value=0)),
                score((1, 4), (3, 5), 1, Nesting(value=1)),
            ],
            id="while",
        ),
        pytest.param(
            """\
            do {
                do {
                    
                } while (y);
            } while (x);
            """,
            [
                score((0, 0), (4, 12), 1, Nesting(value=0)),
                score((1, 4), (3, 16), 1, Nesting(value=1)),
            ],
            id="do while",
        ),
    ),
)
def test(code: str, expected_scores: Scores):
    assert_toplevel_scores(textwrap.dedent(code), expected_scores)