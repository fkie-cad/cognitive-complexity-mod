import textwrap

import pytest

from modified_cognitive_complexity.complexity import Nesting, Scores
from tests.util import assert_toplevel_scores, score


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
        pytest.param(
            """\
            if (x)
                goto L1;
            if (y)
                goto L2;
            if (y) {}
            L1:;
            L2:;
            """,
            [
                score((0, 0), (1, 12), 1, Nesting()),
                score((1, 4), (1, 12), 1, None),
                score((2, 0), (3, 12), 1, Nesting(goto=1)),
                score((3, 4), (3, 12), 1, None),
                score((4, 0), (4, 9), 1, Nesting(goto=2)),
            ],
            id="goto overlapping",
        ),
    ),
)
def test(code: str, expected_scores: Scores):
    assert_toplevel_scores(textwrap.dedent(code), expected_scores)
