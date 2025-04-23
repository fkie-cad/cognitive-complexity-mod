# Modified Cognitive Complexity

A Python tool to calculate the Modified Cognitive Complexity of C/C++ source code using Tree-sitter for parsing.

Cognitive Complexity is a code metric introduced by SonarSource to address shortcomings in traditional cyclomatic complexity. It aims to more accurately reflect how difficult code is to understand by tracking control flow structures and their nesting, while ignoring structural elements that do not contribute to cognitive load.
You can read the original proposal here: [Campbell, G. Ann. "Cognitive Complexity-A new way of measuring understandability." SonarSource SA 10 (2018)](https://www.sonarsource.com/docs/CognitiveComplexity.pdf).

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

For example, on Linux you can compute the cognitive complexity of a file like this:
```bash
cat example.c | modified_cc
```

You can also use the `--annotate` flag to additionally print the source code with per-line complexity scores annotated in the output:
```bash
cat example.c | modified_cc --annotate
```

### Using as a library

To use the tool as a Python library import the `modified_cognitive_complexity` module and use one of the `cognitive_complexity_*` functions:

```python
from modified_cognitive_complexity import *
from pathlib import Path

file = Path("example.c")
scores_by_function = cognitive_complexity_for_file(file)

for function_name, score in scores_by_function.items():
    if function_name is None:
        function_name = "Top-Level"
		
    print(f"{function_name}: {score}")
```
```python
from modified_cognitive_complexity import *

code = """
function test() {
    if (true) {
        if (true) {}	
    }
}
"""
scores_by_function = cognitive_complexity_for_string(code)

for function_name, score in scores_by_function.items():
    if function_name is None:
        function_name = "Top-Level"
		
    print(f"{function_name}: {score}")
```

Or if you need the score broken down into the locations that make up the score, use the following:

```python
from modified_cognitive_complexity import *
from tree_sitter import Language, Parser
from pathlib import Path
import tree_sitter_cpp

file = Path("example.c")
code = file.read_bytes()

lang = Language(tree_sitter_cpp.language())
parser = Parser(lang)
tree = parser.parse(code)

scores_by_function = cognitive_complexity(tree.walk())
for function_name, scores in scores_by_function.items():
    if function_name is None:
        function_name = "Top-Level"
		
    print(f"{function_name}: {sum(cost.total for _, cost in scores)}")
```