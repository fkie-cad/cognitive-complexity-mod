import textwrap

import pytest

from modified_cognitive_complexity.complexity import Nesting, Scores
from tests.util import score, assert_scores


@pytest.mark.parametrize(
    ("code", "expected_scores"),
    (
        pytest.param(
            """\
            function f0() {
                if (x) {}
            }
            function f1() {
                if (x) {}
            }
            if (x) {}
            """,
            {
                b"f0": [score((1, 4), (1, 13), 1, Nesting())],
                b"f1": [score((4, 4), (4, 13), 1, Nesting())],
                None: [score((6, 0), (6, 9), 1, Nesting())]
            },
            id="functions",
        ),
        pytest.param(
            """\
            function f0() {
            }
            function f1() {
            }
            """,
            {
                b"f0": [],
                b"f1": [],
                None: []
            },
            id="functions empty",
        ),
        pytest.param(
            """\
            function f0() {
                L:;
                goto L;
                if (x) {}
            }
            function f1() {
                if (x) {}
                goto L;
                L:;
            }
            """,
            {
                b'f0': [
                    score((2, 4), (2, 11), 1, None),
                    score((3, 4), (3, 13), 1, Nesting())
                ],
                b'f1': [
                    score((6, 4), (6, 13), 1, Nesting()),
                    score((7, 4), (7, 11), 1, None)
                ],
                None: []
            },
            id="functions goto",
        ),
    ),
)
def test(
    code: str,
    expected_scores: dict[bytes | None, Scores]
):
    assert_scores(textwrap.dedent(code), expected_scores)