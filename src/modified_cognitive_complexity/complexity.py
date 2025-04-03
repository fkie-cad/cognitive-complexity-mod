from dataclasses import dataclass
from typing import Iterator

from tree_sitter import Tree, TreeCursor, Point

type LabelId = str


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


def collect_general(
    cursor: TreeCursor,
    scores: list[tuple[Location, Cost]],
    gotos: list[tuple[LabelId, int]],
    labels: dict[LabelId, int],
    depth: int,
):
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

        for _ in childs(cursor):
            collect_general(cursor, scores, gotos, labels, depth)

    # elif node_type == "compound_statement":
    #     for _ in childs(cursor):
    #         collect_general(cursor, scores, gotos, labels, depth)

    elif node_type == "if_statement":
        scores.append((
            Location(cursor.node.start_point, cursor.node.end_point),
            Cost(increment=1, nesting=Nesting(value=depth))
        ))
        for _ in childs(cursor):
            depth_inc = 1 if cursor.field_name in {"consequence"} else 0
            collect_general(cursor, scores, gotos, labels, depth + depth_inc)

    elif node_type == "else_clause":
        scores.append((
            Location(cursor.node.start_point, cursor.node.end_point),
            Cost(increment=1, nesting=None)
        ))
        for _ in childs(cursor):
            if cursor.node.type == "if_statement":
                for _ in childs(cursor):
                    collect_general(cursor, scores, gotos, labels, depth + 1)
            else:
                collect_general(cursor, scores, gotos, labels, depth + 1)

    elif node_type == "switch_statement":
        scores.append((
            Location(cursor.node.start_point, cursor.node.end_point),
            Cost(increment=1, nesting=Nesting(value=depth))
        ))
        for _ in childs(cursor):
            collect_general(cursor, scores, gotos, labels, depth + 1)

    elif node_type == "for_statement":
        scores.append((
            Location(cursor.node.start_point, cursor.node.end_point),
            Cost(increment=1, nesting=Nesting(value=depth))
        ))
        for _ in childs(cursor):
            depth_inc = 1 if cursor.field_name == "body" else 0
            collect_general(cursor, scores, gotos, labels, depth + depth_inc)

    elif node_type in {"while_statement", "do_statement"}:
        scores.append((
            Location(cursor.node.start_point, cursor.node.end_point),
            Cost(increment=1, nesting=Nesting(value=depth))
        ))
        for _ in childs(cursor):
            depth_inc = 1 if cursor.field_name == "body" else 0
            collect_general(cursor, scores, gotos, labels, depth + depth_inc)

    elif node_type == "conditional_expression":
        scores.append((
            Location(cursor.node.start_point, cursor.node.end_point),
            Cost(increment=1, nesting=Nesting(value=depth))
        ))
        for _ in childs(cursor):
            depth_inc = 1 if cursor.field_name in {"consequence", "alternative"} else 0
            collect_general(cursor, scores, gotos, labels, depth + depth_inc)

    elif node_type == "binary_expression":
        collect_expression(cursor, None, scores)

    else:
        for _ in childs(cursor):
            collect_general(cursor, scores, gotos, labels, depth)


def collect_expression(
        cursor: TreeCursor,
        parent_operator: bytes | None,
        scores: list[tuple[Location, Cost]]
):
    operator: bytes | None = None
    if cursor.node.type == "binary_expression":
        for _ in childs(cursor):
            if cursor.field_name == "operator":
                operator = cursor.node.text

        if operator in {b"&&", b"||"} and parent_operator != operator:
            scores.append((
                Location(cursor.node.start_point, cursor.node.end_point),
                Cost(increment=1, nesting=None)
            ))

    for _ in childs(cursor):
        collect_expression(cursor, operator, scores)


def cognitive_complexity(tree: Tree) -> list[tuple[Location, Cost]]:
    scores: list[tuple[Location, Cost]] = []
    gotos: list[tuple[LabelId, int]] = []
    labels: dict[LabelId, int] = {}

    collect_general(tree.walk(), scores, gotos, labels, 0)

    for labelId, index in gotos:
        (start, stop) = sorted((index, labels[labelId]))
        if start == index:  # if goto before label, move start behind goto
            start += 1
        for _, cost in scores[start:stop]:
            if cost.nesting is not None:
                cost.nesting.goto += 1

    return scores


def childs(cursor: TreeCursor) -> Iterator[None]:
    if cursor.goto_first_child():
        while True:
            yield None
            if not cursor.goto_next_sibling():
                break
        cursor.goto_parent()
