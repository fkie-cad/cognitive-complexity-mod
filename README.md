# Modified Cognitive Complexity

A Python tool to calculate the Modified Cognitive Complexity of C source code using Tree-sitter for parsing.

Cognitive Complexity is a code metric introduced by SonarSource to address shortcomings in traditional cyclomatic complexity. It aims to more accurately reflect how difficult code is to understand by tracking control flow structures and their nesting, while ignoring structural elements that do not contribute to cognitive load.
You can read the original proposal here [TODO: Link].

This repository implements a modified version of Cognitive Complexity as proposed in [TODO: insert paper link here]. [TODO: Explain difference]

---


## Installation

This project follows the [PEP 517/518](https://www.python.org/dev/peps/pep-0517/) build system standard and uses `pyproject.toml`.

To install the package locally, run:

```bash
pip install .
```

from the root of the project directory.


## Usage

### Command-Line Interface

The CLI tool `modified_cc` reads C source code from standard input (`stdin`).

For example, on Linux, you can compute the cognitive complexity of a file like this:
```bash
cat example.c | modified_cc
```

You can also use the `--annotate` flag to print the source code with per-line complexity scores annotated in the output:
```bash
cat example.c | modified_cc --annotate
```

### Using as a library

To use the tool as a Python library, import the `modified_cognitive_complexity` module and call the `cognitive_complexity` function:

```python
from modified_cognitive_complexity import *
from tree_sitter import Language, Parser
import tree_sitter_c

with open("example.c", "rb") as f:
    code = f.read()

lang = Language(tree_sitter_c.language())
parser = Parser(lang)
tree = parser.parse(code)

toplevel_scores, function_scores = cognitive_complexity(tree.walk())
toplevel_total = sum(cost.total for _, cost in toplevel_scores)
functions_total = sum(sum(cost.total for _, cost in scores) for scores in function_scores.values())
print("Cognitive Complexity:", toplevel_total + functions_total)
```