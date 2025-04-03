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
            if (x)
                goto L;
            L:;
            """,
            [
                score((0, 0), (1, 11), 1, Nesting()),
                score((1, 4), (1, 11), 1, None),
            ],
            id="goto forward",
        ),
        pytest.param(
            """\
            L:;
            if (x)
                goto L;
            """,
            [
                score((1, 0), (2, 11), 1, Nesting(goto=1)),
                score((2, 4), (2, 11), 1, None),
            ],
            id="goto backward",
        ),
        pytest.param(
            """\
            if (x)
                goto L;
            if (y) {}
            L:;
            """,
            [
                score((0, 0), (1, 11), 1, Nesting()),
                score((1, 4), (1, 11), 1, None),
                score((2, 0), (2, 9), 1, Nesting(goto=1)),
            ],
            id="goto nesting",
        ),
    ),
)
def test(code: str, expected_scores: list[tuple[Location, Cost]]):
    assert_scores(textwrap.dedent(code), expected_scores)
