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
    ),
)
def test(
    code: str,
    expected_scores: dict[bytes | None, Scores]
):
    assert_scores(textwrap.dedent(code), expected_scores)