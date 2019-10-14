"""Hello"""
# pylint: disable=invalid-name
# reason: Pylint doesn't recognise Literals as types

from typing import NamedTuple, List

from typing_extensions import Literal

from csvql import tools

PrimaryClauses = Literal[
    "select", "update", "insert", "delete"
]

SecondaryClauses = Literal[
    "where", "from", "group by", "order by", "join", "limit"
]

Flags = Literal[
    "distinct", "asc", "desc", "inner"
]

Clauses = Literal[PrimaryClauses, SecondaryClauses]

Keyword = Literal[Clauses, Flags]

Operator = Literal["(", ")", ",", "+", ";"]

ExprType = Literal[
    "condition", "column-list", "table-name", "number", "none"
]


PRIMARY_CLAUSES = tools.extract_literals(PrimaryClauses)  # type: ignore
CLAUSES = tools.extract_literals(Clauses)  # type: ignore
KEYWORDS = tools.extract_literals(Keyword)  # type: ignore
OPERATORS = tools.extract_literals(Operator)  # type: ignore


class Form(NamedTuple):
    """Defines the form for SQL clauses"""
    name: Keyword
    expression: ExprType = "none"
    required_clauses: List[Keyword] = []
    optional_clauses: List[Keyword] = []
    prefix_flags: List[Keyword] = []
    infix_flags: List[Keyword] = []
    postfix_flags: List[Keyword] = []
    primary: bool = False


TYPES: List[Form] = [
    Form(
        "select",
        primary=True,
        infix_flags=["distinct"],
        expression="column-list",
        required_clauses=["from"],
        optional_clauses=["order by", "limit"]
    ),
    Form("limit", expression="number"),
    Form("where"),
    Form("join", expression="none", prefix_flags=["inner"]),
    Form("from", "table-name"),
    Form("order by", "column-list", postfix_flags=["asc", "desc"])
]
