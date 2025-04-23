from pathlib import Path

import tree_sitter_cpp
from tree_sitter import Language, Parser

from modified_cognitive_complexity import cognitive_complexity


def cognitive_complexity_for_file(file: Path) -> dict[bytes | None, int]:
    code = file.read_bytes()
    return cognitive_complexity_for_string(code)


def cognitive_complexity_for_string(code: str | bytes | bytearray | memoryview) -> dict[bytes | None, int]:
    if isinstance(code, str):
        code = code.encode()
    
    lang = Language(tree_sitter_cpp.language())
    parser = Parser(lang)
    tree = parser.parse(code)

    scores_by_function = cognitive_complexity(tree.walk())
    return {
        function_name: sum(cost.total for _, cost in scores)
        for function_name, scores
        in scores_by_function.items()
    }