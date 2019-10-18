"""Interpret a SQL AST as command to be run."""

from typing import Optional, Union, List

from typing_extensions import Literal

from .parse import Clause
from .transactions import Select


def make_select(statement: Clause) -> Select:
    distinct: bool = statement.flags and "distinct" in statement.flags
    columns: Union[List[str], Literal["*"]] = statement.expression
    table: str = statement.children['from'].expression
    limit: Optional[int]
    if 'order by' in statement.children:
        order = statement.children['order by'].expression
    else:
        order = None
    if 'limit' in statement.children:
        limit = int(statement.children['limit'].expression)
    else:
        limit = None
    return Select(distinct, columns, order, table, limit)
