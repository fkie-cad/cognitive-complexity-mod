import textwrap

import pytest

from modified_cognitive_complexity.complexity import Nesting, Scores
from tests.util import score, assert_scores


@pytest.mark.parametrize(
    ("code", "expected_scores", "goto_nesting", "structural_gotos"),
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
            True,
            False,
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
            True,
            False,
            id="functions empty",
        ),
        pytest.param(
            """\
            function f0() {
                L:;
                if (x) {}
                goto L;
            }
            function f1() {
                goto L;
                if (x) {
                    L:;
                }
            }
            """,
            {
                b'f0': [
                    score((2, 4), (2, 13), 1, Nesting(goto=1)),
                    score((3, 4), (3, 11), 1, None),
                ],
                b'f1': [
                    score((6, 4), (6, 11), 1, None),
                    score((7, 4), (9, 5), 1, Nesting(goto=1)),
                ],
                None: []
            },
            True,
            False,
            id="functions goto",
        ),
        pytest.param(
            """\
            function f0() {
                L:;
                if (x) {}
                goto L;
            }
            function f1() {
                goto L;
                if (x) {
                    L:;
                }
            }
            """,
            {
                b'f0': [
                    score((2, 4), (2, 13), 1, Nesting()),
                    score((3, 4), (3, 11), 1, Nesting()),
                ],
                b'f1': [
                    score((6, 4), (6, 11), 1, Nesting(value=1)),
                    score((7, 4), (9, 5), 1, Nesting()),
                ],
                None: []
            },
            False,
            True,
            id="functions goto",
        ),
    ),
)
def test(
    code: str,
    expected_scores: dict[bytes | None, Scores],
    goto_nesting: bool,
    structural_gotos: bool,
):
    assert_scores(textwrap.dedent(code), expected_scores, goto_nesting=goto_nesting, structural_gotos=structural_gotos)