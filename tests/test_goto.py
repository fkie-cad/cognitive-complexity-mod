import textwrap

import pytest

from modified_cognitive_complexity.complexity import Nesting, Scores
from tests.util import assert_toplevel_scores, score


@pytest.mark.parametrize(
    ("code", "expected_scores", "structural_gotos"),
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
            False,
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
            False,
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
            False,
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
            False,
            id="goto overlapping",
        ),
        pytest.param(
            """\
            goto L;
            if (x) {
                goto L;
                if (x) {
                    goto L;
                    L:;
                }
            }
            """,
            [
                score((0, 0), (0, 7), 1, Nesting(value=2, goto=0)),
                score((1, 0), (7, 1), 1, Nesting(value=0, goto=1)),
                score((2, 4), (2, 11), 1, Nesting(value=2, goto=1)),
                score((3, 4), (6, 5), 1, Nesting(value=1, goto=2)),
                score((4, 8), (4, 15), 1, Nesting(value=2, goto=2)),
            ],
            True,
            id="structural goto",
        ),
    ),
)
def test(code: str, expected_scores: Scores, structural_gotos: bool):
    assert_toplevel_scores(textwrap.dedent(code), expected_scores, structural_gotos)
