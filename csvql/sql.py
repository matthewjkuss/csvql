# Basic SQL Implementation
"""Implements SQL engine."""

from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass

from typing_extensions import Literal

from database import Table
from tools import Result

import parse
from parse import Clause




@dataclass
class Select:
    distinct: bool
    columns: Union[List[str], Literal["*"]]
    order: List[str]
    table: str
    limit: Optional[int]

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

def run(query: str, database: Dict[str, Table]) -> Result[Table]:
    parsed = parse.parse(query)
    if parsed.value:
        res = select(make_select(parsed.value), database)
        res.messages += parsed.messages
        return res
    return Result(parsed.messages)


def sort_order(array: List[Any], order: List[int]) -> List[Any]:
    return [array[x] for x in order]

def select(statement: Select, database: Dict[str, Table]) -> Result[Table]:
    """Run select style command on database."""
    table = database.get(statement.table)
    if not table:
        return Result([f"Error: table `{statement.table}` not found"])
    columns = statement.columns if statement.columns != "*" else table.columns
    print("col", columns)
    try:
        column_idx = [table.columns.index(column) for column in columns]
    except ValueError as err:
        return Result([f"Error: Column named `{str(err).split()[0][1:-1]}` cannot be found."])
    rows = [[row[idx] for idx in column_idx] for row in table.rows]
    # TODO Implement `order by`
    if statement.order:
        rows.sort(key=lambda x: x[statement.order[0]])
    if statement.distinct:
        deduped_rows = []
        last = None
        for cell in rows:
            if not last or cell != last:
                deduped_rows.append(cell)
                last = cell
        rows = deduped_rows
    if statement.limit:
        rows = rows[:statement.limit]
    return Result([], Table(columns, rows))
