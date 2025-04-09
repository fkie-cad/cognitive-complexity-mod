# Modified Cognitive Complexity

A Python tool to calculate the **Modified Cognitive Complexity** of C source code using [Tree-sitter](https://tree-sitter.github.io/tree-sitter/) for parsing.

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
````bash
cat example.c | modified_cc
````


### Using as a library

To use the tool as a Python library, import the modified_cognitive_complexity module and call the cognitive_complexity function:

````python
from modified_cognitive_complexity import *
from tree_sitter import Language, Parser
import tree_sitter_c

with open("example.c", "rb") as f:
    code = f.read()

lang = Language(tree_sitter_c.language())
parser = Parser(lang)
tree = parser.parse(code)

scores = cognitive_complexity(tree)
total = sum(cost.total for _, cost in scores)
print("Cognitive Complexity:", total)
````