import textwrap

import pytest

from modified_cognitive_complexity.complexity import Location, Score, Nesting
from .util import assert_scores, score


@pytest.mark.parametrize(
    ("code", "expected_scores"),
    (
        pytest.param(
            """\
            for (int i = 0; i < 10; i++) {
                for (int j = 0; j < 10; j++) {
                    
                }
            }
            """,
            [
                score((0, 0), (4, 1), 1, Nesting()),
                score((1, 4), (3, 5), 1, Nesting(value=1)),
            ],
            id="for",
        ),
    ),
)
def test(code: str, expected_scores: list[tuple[Location, Score]]):
    assert_scores(textwrap.dedent(code), expected_scores)