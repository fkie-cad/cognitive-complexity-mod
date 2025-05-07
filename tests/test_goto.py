import textwrap

import pytest

from modified_cognitive_complexity.complexity import Nesting, Scores
from tests.util import assert_toplevel_scores, score




@pytest.mark.parametrize(
    ("code", "expected_scores", "goto_nesting", "structural_gotos"),
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
            True,
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
            True,
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
            True,
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
            True,
            False,
            id="goto overlapping",
        ),
        pytest.param(
            """\
            L1:;
            goto L2;
            if (x) {
                goto L2;
                if (x) {
                    goto L2;
                    L2:;
                }
            }
            goto L1;
            """,
            [
                score((1, 0), (1, 8), 1, Nesting(value=2, goto=1)),
                score((2, 0), (8, 1), 1, Nesting(value=0, goto=2)),
                score((3, 4), (3, 12), 1, Nesting(value=2, goto=1)),
                score((4, 4), (7, 5), 1, Nesting(value=1, goto=3)),
                score((5, 8), (5, 16), 1, Nesting(value=2, goto=1)),
                score((9, 0), (9, 8), 1, Nesting()),
            ],
            True,
            True,
            id="structural goto",
        ),
        pytest.param(
            """\
            L1:;
            goto L2;
            if (x) {
                goto L2;
                if (x) {
                    goto L2;
                    L2:;
                }
            }
            goto L1;
            """,
            [
                score((1, 0), (1, 8), 1, Nesting(value=2, goto=0)),
                score((2, 0), (8, 1), 1, Nesting(value=0, goto=0)),
                score((3, 4), (3, 12), 1, Nesting(value=2, goto=0)),
                score((4, 4), (7, 5), 1, Nesting(value=1, goto=0)),
                score((5, 8), (5, 16), 1, Nesting(value=2, goto=0)),
                score((9, 0), (9, 8), 1, Nesting()),
            ],
            False,
            True,
            id="no nesting goto",
        ),
    ),
)
def test(code: str, expected_scores: Scores, goto_nesting: bool, structural_gotos: bool):
    assert_toplevel_scores(
        textwrap.dedent(code),
        expected_scores,
        goto_nesting=goto_nesting,
        structural_gotos=structural_gotos
    )
