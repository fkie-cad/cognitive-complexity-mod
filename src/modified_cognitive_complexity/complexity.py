import dataclasses
from dataclasses import dataclass
from typing import Iterator

from tree_sitter import TreeCursor, Point


@dataclass(frozen=False, slots=True)
class Nesting:
    """Represents the nesting caused by control flow and spanning gotos."""
    value: int = 0
    goto: int = 0


@dataclass(frozen=False, slots=True)
class Score:
    """Represents the score of a node in the sytanx tree, consisting of an increment and a nesting."""
    increment: int
    nesting: Nesting | None
    
    @property
    def total(self):
        return self.increment + (0 if self.nesting is None else (self.nesting.value + self.nesting.goto)) 


@dataclass(frozen=True, slots=True, order=True)
class Location:
    """A location in the syntax tree consisting of a start and end position."""
    start: Point
    end: Point


type _LabelId = str
type Scores = list[tuple[Location, Score]]


def _collect_general(
    cursor: TreeCursor,
    nestings: list[Nesting | None],
    locations: list[Location | None],
    gotos: list[tuple[_LabelId, int]],
    labels: dict[_LabelId, int],
    function_scores: dict[bytes | None, Scores],
    depth: int,
    goto_nesting: bool,
    structural_gotos: bool
):
    """
    Recursively traverse the syntax tree to collect cognitive complexity scores 
    from control flow constructs.

    This function inspects nodes in the syntax tree and records complexity scores 
    based on the type and nesting of control flow statements. It tracks the depth
    of nesting, which increases the cognitive cost.
    
    Additionally, locations of gotos and labels are tracked. 

    :param cursor: The cursor used to navigate the syntax tree.
    :param nestings: The list that accumulates nesting depths for different code locations.
    :param locations: The list that accumulates the locations for different code locations.
        `None` means no score penalty for this code.
    :param gotos: A list of (label name, index) tuples representing `goto` statements
        and their position in the nestings/locations list.
    :param labels: A mapping from label names to their position in the nestings/locations list.
    :param function_scores: A mapping from function names to their collected scores.
    :param depth: The current nesting depth, which increases when entering 
        control structures that affect complexity.
        
    :return None
    """
    
    node_type = cursor.node.type
    node_location = Location(cursor.node.start_point, cursor.node.end_point)

    if node_type == "function_definition":
        function_name: bytes | None = None
        for _ in _childs(cursor):
            if cursor.field_name == "declarator":
                for _ in _childs(cursor):
                    if cursor.field_name == "declarator":
                        function_name = cursor.node.text

        if function_name is not None:
            for _ in _childs(cursor):
                if cursor.field_name == "body":
                    nested_scores = cognitive_complexity(cursor, goto_nesting=goto_nesting, structural_gotos=structural_gotos)
                    function_scores[function_name] = nested_scores.pop(None)
                    function_scores.update(nested_scores)
        else:
            pass  # TODO: Maybe warning or exception?
        
    elif node_type == "goto_statement":
        for _ in _childs(cursor):
            if cursor.field_name == "label":
                label_text = cursor.node.text.decode(encoding="utf-8")
                gotos.append((label_text, len(locations)))
                locations.append(node_location)
                nestings.append(None)

    elif node_type == "labeled_statement":
        for _ in _childs(cursor):
            if cursor.field_name == "label":
                label_text = cursor.node.text.decode(encoding="utf-8")
                labels[label_text] = len(locations)
                locations.append(None)
                nestings.append(Nesting(depth))
        
        for _ in _childs(cursor):
            _collect_general(cursor, nestings, locations, gotos, labels, function_scores, depth, goto_nesting=goto_nesting, structural_gotos=structural_gotos)

    # already handled by else branch
    # elif node_type == "compound_statement":
    #     for _ in childs(cursor):
    #         collect_general(cursor, scores, gotos, labels, depth)

    elif node_type == "if_statement":
        locations.append(node_location)
        nestings.append(Nesting(value=depth))
        for _ in _childs(cursor):
            depth_inc = 1 if cursor.field_name in {"consequence"} else 0
            _collect_general(cursor, nestings, locations, gotos, labels, function_scores, depth + depth_inc, goto_nesting=goto_nesting, structural_gotos=structural_gotos)

    elif node_type == "else_clause":
        locations.append(node_location)
        nestings.append(None)
        for _ in _childs(cursor):
            if cursor.node.type == "if_statement":
                for _ in _childs(cursor):
                    _collect_general(cursor, nestings, locations, gotos, labels, function_scores, depth + 1, goto_nesting=goto_nesting, structural_gotos=structural_gotos)
            else:
                _collect_general(cursor, nestings, locations, gotos, labels, function_scores, depth + 1, goto_nesting=goto_nesting, structural_gotos=structural_gotos)

    elif node_type == "switch_statement":
        locations.append(node_location)
        nestings.append(Nesting(value=depth))
        for _ in _childs(cursor):
            _collect_general(cursor, nestings, locations, gotos, labels, function_scores, depth + 1, goto_nesting=goto_nesting, structural_gotos=structural_gotos)

    elif node_type == "for_statement":
        locations.append(node_location)
        nestings.append(Nesting(value=depth))
        for _ in _childs(cursor):
            depth_inc = 1 if cursor.field_name == "body" else 0
            _collect_general(cursor, nestings, locations, gotos, labels, function_scores, depth + depth_inc, goto_nesting=goto_nesting, structural_gotos=structural_gotos)

    elif node_type in {"while_statement", "do_statement"}:
        locations.append(node_location)
        nestings.append(Nesting(value=depth))
        for _ in _childs(cursor):
            depth_inc = 1 if cursor.field_name == "body" else 0
            _collect_general(cursor, nestings, locations, gotos, labels, function_scores, depth + depth_inc, goto_nesting=goto_nesting, structural_gotos=structural_gotos)
    
    elif node_type == "catch_clause":
        locations.append(node_location)
        nestings.append(Nesting(value=depth))
        for _ in _childs(cursor):
            depth_inc = 1 if cursor.field_name == "body" else 0
            _collect_general(cursor, nestings, locations, gotos, labels, function_scores, depth + depth_inc, goto_nesting=goto_nesting, structural_gotos=structural_gotos)

    elif node_type == "conditional_expression":
        locations.append(node_location)
        nestings.append(Nesting(value=depth))
        for _ in _childs(cursor):
            depth_inc = 1 if cursor.field_name in {"consequence", "alternative"} else 0
            _collect_general(cursor, nestings, locations, gotos, labels, function_scores, depth + depth_inc, goto_nesting=goto_nesting, structural_gotos=structural_gotos)

    elif node_type == "binary_expression":
        _collect_expression(cursor, None, nestings, locations)

    else:
        for _ in _childs(cursor):
            _collect_general(cursor, nestings, locations, gotos, labels, function_scores, depth, goto_nesting=goto_nesting, structural_gotos=structural_gotos)


def _collect_expression(
    cursor: TreeCursor,
    parent_operator: bytes | None,
    nestings: list[Nesting | None],
    locations: list[Location | None],
):
    """
    Recursively collect cognitive complexity costs from binary expressions.

    :param cursor: A cursor currently positioned at a node, typically an expression node.
    :param parent_operator: The logical operator (e.g., `b'&&'`, `b'||'`) of the 
        parent binary expression, or None if there is no parent operator.
    :param nestings: The list that accumulates nesting depths for different code locations.
    :param locations: The list that accumulates the locations for different code locations.
        `None` means no score penalty for this code.
    """
    
    operator: bytes | None = None
    if cursor.node.type == "binary_expression":
        for _ in _childs(cursor):
            if cursor.field_name == "operator":
                operator = cursor.node.text

        if operator in {b"&&", b"||"} and parent_operator != operator:
            locations.append(Location(cursor.node.start_point, cursor.node.end_point))
            nestings.append(None)

    for _ in _childs(cursor):
        _collect_expression(cursor, operator, nestings, locations)

    
def cognitive_complexity(
    cursor: TreeCursor,
    *,
    goto_nesting: bool = True,
    structural_gotos: bool = False
) -> dict[bytes | None, Scores]:
    """
    Calculate the modified cognitive complexity of control flow structures in a syntax tree.

    This function traverses a syntax tree generated by Tree-sitter and collects metrics 
    related to control flow structures such as if/else statements, loops, switch cases, 
    conditional expressions, and goto statements. The result is a dictionary, which maps 
    function names to a list of location-cost tuples, where each cost reflects the increase
    in complexity at that location, including nesting depth and any additional complexity
    introduced by goto statements.
    All top-level costs are mapped to the 'None' key.
    
    :param cursor: A cursor currently positioned at a node, typically an expression node.
    :param goto_nesting: If the additional nesting penalty imposed by gotos should be applied. 
    :param structural_gotos: A flag specifying if goto statements should inherit a nesting penalty
        by their respective label.

    :return: A mapping from each function name to its score. The score of top-level constructs
        is mapped to the 'None' key.
    """
    
    nestings: list[Nesting | None] = []
    locations: list[Location | None] = []
    gotos: list[tuple[_LabelId, int]] = []
    labels: dict[_LabelId, int] = {}
    function_scores: dict[bytes | None, Scores] = {}

    _collect_general(cursor, nestings, locations, gotos, labels, function_scores, 0, goto_nesting, structural_gotos)

    if goto_nesting:
        goto_nesting = [0] * (len(nestings) + 1)
        
        for labelId, goto_index in gotos:
            if labelId not in labels:
                continue
            
            label_index = labels[labelId]
            (start, stop) = sorted((goto_index, label_index))
            start += 1 # shift start behind goto/label
            
            goto_nesting[start] += 1
            goto_nesting[stop] -= 1
        
        current_goto_nesting = 0
        for i, nesting in enumerate(nestings):
            current_goto_nesting += goto_nesting[i]
            if nesting is not None:
                nesting.goto += current_goto_nesting

    if structural_gotos:
        for labelId, goto_index in gotos:
            if labelId not in labels:
                continue

            label_index = labels[labelId]
            nestings[goto_index] = dataclasses.replace(nestings[label_index])
    
    function_scores[None] = [(location, Score(1, nesting)) for nesting, location in zip(nestings, locations) if location is not None]
    return function_scores


def _childs(cursor: TreeCursor) -> Iterator[None]:
    """
    Helper function for traversing all children of the current node in the cursor.
    
    This generator function yields once for each child node of the current node, 
    advancing the cursor to each sibling in turn. After iteration, the cursor is 
    restored to its original parent node.
    Care must be taken to always exhaust the iterator, else the cursor will not 
    return to the original node.
    
    :param cursor: A Tree-sitter cursor positioned at a node whose children will 
        be iterated. 
    """
    if cursor.goto_first_child():
        while True:
            yield None
            if not cursor.goto_next_sibling():
                break
        cursor.goto_parent()
