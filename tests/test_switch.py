import textwrap

import pytest

from modified_cognitive_complexity.complexity import Location, Score, Nesting
from .util import assert_scores, score


@pytest.mark.parametrize(
    ("code", "expected_scores"),
    (
        pytest.param(
            """\
            switch (x) {
                case 0: break;
                case 1: ;
                    switch (y) {}
                    break;
                default: break;
            }
            """,
            [
                score((0, 0), (6, 1), 1, Nesting()),
                score((3, 8), (3, 21), 1, Nesting(value=1)),
            ],
            id="switch",
        ),
    ),
)
def test(code: str, expected_scores: list[tuple[Location, Score]]):
    assert_scores(textwrap.dedent(code), expected_scores)