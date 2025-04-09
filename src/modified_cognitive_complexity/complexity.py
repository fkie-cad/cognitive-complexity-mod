from dataclasses import dataclass
from typing import Iterator

from tree_sitter import Tree, TreeCursor, Point


@dataclass(frozen=False, slots=True)
class Nesting:
    value: int = 0
    goto: int = 0


@dataclass(frozen=False, slots=True)
class Cost:
    increment: int
    nesting: Nesting | None
    
    @property
    def total(self):
        return self.increment + (0 if self.nesting is None else (self.nesting.value + self.nesting.goto)) 


@dataclass(frozen=True, slots=True, order=True)
class Location:
    start: Point
    end: Point


type LabelId = str


def _collect_general(
    cursor: TreeCursor,
    scores: list[tuple[Location, Cost]],
    gotos: list[tuple[LabelId, int]],
    labels: dict[LabelId, int],
    depth: int,
):
    """
    Recursively traverse the syntax tree to collect cognitive complexity scores 
    from control flow constructs.

    This function inspects nodes in the syntax tree and records complexity scores 
    based on the type and nesting of control flow statements. It tracks the depth
    of nesting, which increases the cognitive cost.
    
    Additionally, locations of gotos and labels are tracked. 

    :param cursor: The cursor used to navigate the syntax tree.
    :param scores: The list that accumulates cognitive complexity scores for
        different code locations.
    :param gotos: A list of (label name, index) tuples representing `goto` statements
        and their position in the scores list.
    :param labels: A mapping from label names to their position in the scores list.
    :param depth: The current nesting depth, which increases when entering 
        control structures that affect complexity.
        
    :return None
    """
    
    node_type = cursor.node.type

    if node_type == "goto_statement":
        assert cursor.goto_first_child()
        assert cursor.goto_next_sibling()
        assert cursor.node.type == "statement_identifier"

        label_text = cursor.node.text.decode(encoding="utf-8")
        cursor.goto_parent()

        gotos.append((label_text, len(scores)))

        scores.append((
            Location(cursor.node.start_point, cursor.node.end_point),
            Cost(increment=1, nesting=None)
        ))

    elif node_type == "labeled_statement":
        assert cursor.goto_first_child()
        assert cursor.node.type == "statement_identifier"

        label_text = cursor.node.text.decode(encoding="utf-8")
        cursor.goto_parent()

        labels[label_text] = len(scores)

        for _ in _childs(cursor):
            _collect_general(cursor, scores, gotos, labels, depth)

    # elif node_type == "compound_statement":
    #     for _ in childs(cursor):
    #         collect_general(cursor, scores, gotos, labels, depth)

    elif node_type == "if_statement":
        scores.append((
            Location(cursor.node.start_point, cursor.node.end_point),
            Cost(increment=1, nesting=Nesting(value=depth))
        ))
        for _ in _childs(cursor):
            depth_inc = 1 if cursor.field_name in {"consequence"} else 0
            _collect_general(cursor, scores, gotos, labels, depth + depth_inc)

    elif node_type == "else_clause":
        scores.append((
            Location(cursor.node.start_point, cursor.node.end_point),
            Cost(increment=1, nesting=None)
        ))
        for _ in _childs(cursor):
            if cursor.node.type == "if_statement":
                for _ in _childs(cursor):
                    _collect_general(cursor, scores, gotos, labels, depth + 1)
            else:
                _collect_general(cursor, scores, gotos, labels, depth + 1)

    elif node_type == "switch_statement":
        scores.append((
            Location(cursor.node.start_point, cursor.node.end_point),
            Cost(increment=1, nesting=Nesting(value=depth))
        ))
        for _ in _childs(cursor):
            _collect_general(cursor, scores, gotos, labels, depth + 1)

    elif node_type == "for_statement":
        scores.append((
            Location(cursor.node.start_point, cursor.node.end_point),
            Cost(increment=1, nesting=Nesting(value=depth))
        ))
        for _ in _childs(cursor):
            depth_inc = 1 if cursor.field_name == "body" else 0
            _collect_general(cursor, scores, gotos, labels, depth + depth_inc)

    elif node_type in {"while_statement", "do_statement"}:
        scores.append((
            Location(cursor.node.start_point, cursor.node.end_point),
            Cost(increment=1, nesting=Nesting(value=depth))
        ))
        for _ in _childs(cursor):
            depth_inc = 1 if cursor.field_name == "body" else 0
            _collect_general(cursor, scores, gotos, labels, depth + depth_inc)

    elif node_type == "conditional_expression":
        scores.append((
            Location(cursor.node.start_point, cursor.node.end_point),
            Cost(increment=1, nesting=Nesting(value=depth))
        ))
        for _ in _childs(cursor):
            depth_inc = 1 if cursor.field_name in {"consequence", "alternative"} else 0
            _collect_general(cursor, scores, gotos, labels, depth + depth_inc)

    elif node_type == "binary_expression":
        _collect_expression(cursor, None, scores)

    else:
        for _ in _childs(cursor):
            _collect_general(cursor, scores, gotos, labels, depth)


def _collect_expression(
        cursor: TreeCursor,
        parent_operator: bytes | None,
        scores: list[tuple[Location, Cost]]
):
    """
    Recursively collect cognitive complexity costs from binary expressions.

    :param cursor: A cursor currently positioned at a node, typically an expression node.
    :param parent_operator: The logical operator (e.g., `b'&&'`, `b'||'`) of the 
        parent binary expression, or None if there is no parent operator.
    :param scores: The list to which complexity scores will be added.
        Each score is a tuple containing the expression's location and its associated cost.
    """
    
    operator: bytes | None = None
    if cursor.node.type == "binary_expression":
        for _ in _childs(cursor):
            if cursor.field_name == "operator":
                operator = cursor.node.text

        if operator in {b"&&", b"||"} and parent_operator != operator:
            scores.append((
                Location(cursor.node.start_point, cursor.node.end_point),
                Cost(increment=1, nesting=None)
            ))

    for _ in _childs(cursor):
        _collect_expression(cursor, operator, scores)


def cognitive_complexity(tree: Tree) -> list[tuple[Location, Cost]]:
    """
    Calculate the modified cognitive complexity of control flow structures in a syntax tree.

    This function traverses a syntax tree generated by Tree-sitter and collects metrics 
    related to control flow structures such as if/else statements, loops, switch cases, 
    conditional expressions, and goto statements. The result is a list of location-cost 
    tuples, where each cost reflects the increase in complexity at that location, including 
    nesting depth and any additional complexity introduced by goto statements.

    Parameters:
        tree (Tree): A Tree-sitter syntax tree representing parsed source code.

    Returns:
        list[tuple[Location, Cost]]: A list of tuples where each tuple contains:
            - Location: The start and end point in the source code for the construct.
            - Cost: The cognitive cost associated with that construct, including increment 
              values and nesting penalties.
    """
    
    scores: list[tuple[Location, Cost]] = []
    gotos: list[tuple[LabelId, int]] = []
    labels: dict[LabelId, int] = {}

    _collect_general(tree.walk(), scores, gotos, labels, 0)

    for labelId, index in gotos:
        (start, stop) = sorted((index, labels[labelId]))
        if start == index:  # if goto before label, move start behind goto
            start += 1
        for _, cost in scores[start:stop]:
            if cost.nesting is not None:
                cost.nesting.goto += 1

    return scores


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
