import textwrap

import pytest

from modified_cognitive_complexity.complexity import Nesting, Scores
from tests.util import assert_toplevel_scores, score


@pytest.mark.parametrize(
    ("code", "expected_scores"),
    (
        pytest.param(
            """\
            L: a = 2 * c;
            b = f(a);
            if (c) {
                goto L; 
            }
            return b;
            """,
            [
                score((2, 0), (4, 1), 1, Nesting(value=0, goto=1)),
                score((3, 4), (3, 11), 1, None)
            ],
            id="1 goto",
        ),
        pytest.param(
            """\
            do {
                a = 2 * c;
                b = f(a);
            } while (c);
            return b;
            """,
            [
                score((0, 0), (3, 12), 1, Nesting(value=0, goto=0))
            ],
            id="1 gotoless",
        ),
        pytest.param(
            """\
            L: a = 2 * c;
            for (int i = 1; i < a; i++) {
                if (i % 2) {
                    b = f(i);
                }
            }
            c = c / 2;
            if (c) {
                goto L;
            }
            return b;
            """,
            [
                score((1, 0), (5, 1), 1, Nesting(value=0, goto=1)),
                score((2, 4), (4, 5), 1, Nesting(value=1, goto=1)),
                score((7, 0), (9, 1), 1, Nesting(value=0, goto=1)),
                score((8, 4), (8, 11), 1, None)
            ],
            id="2 goto",
        ),
        pytest.param(
            """\
            do {
                a = 2 * c;
                for (int i = 1; i < a; i++){
                    if (i % 2) {
                        b = f(i);
                    }
                }
                c = c / 2;
            } while (c);
            return b;
            """,
            [
                score((0, 0), (8, 12), 1, Nesting(value=0, goto=0)),
                score((2, 4), (6, 5), 1, Nesting(value=1, goto=0)),
                score((3, 8), (5, 9), 1, Nesting(value=2, goto=0))
            ],
            id="2 gotoless",
        ),
        pytest.param(
            """\
            //int prime(int low, int up) {
                int num = low;
                check_next_numb:
                if (num > up){
                    goto no_prime;
                }
                int div = 2;
                check_divisor:
                if (div * div > num){
                    goto is_prime;
                }
                if (num % div == 0) {
                    num++;
                    goto check_next_numb;
                }
                div++;
                goto check_divisor;
                is_prime: return num;
                no_prime: return -1;
            //}
            """,
            [
                score((3, 4), (5, 5), 1, Nesting(value=0, goto=1)),
                score((4, 8), (4, 22), 1, None),
                score((8, 4), (10, 5), 1, Nesting(value=0, goto=3)),
                score((9, 8), (9, 22), 1, None),
                score((11, 4), (14, 5), 1, Nesting(value=0, goto=4)),
                score((13, 8), (13, 29), 1, None),
                score((16, 4), (16, 23), 1, None)
            ],
            id="prime goto",
        ),
        pytest.param(
            """\
            //int prime(int low, int up) {
                for (int num = low; num <= up; num++) {
                    bool isPrime = true;
                    for (int div = 2; div * div <= num; div++) {
                        if (num % div == 0) {
                            isPrime = false;
                            break;
                        }
                    }
                    if (isPrime) {
                        return num;
                    }
                }
                return -1;
            //}
            """,
            [
                score((1, 4), (12, 5), 1, Nesting(value=0)),
                score((3, 8), (8, 9), 1, Nesting(value=1)),
                score((4, 12), (7, 13), 1, Nesting(value=2)),
                score((9, 8), (11, 9), 1, Nesting(value=1))
            ],
            id="prime gotoless",
        ),
    ),
)
def test(code: str, expected_scores: Scores):
    assert_toplevel_scores(textwrap.dedent(code), expected_scores)