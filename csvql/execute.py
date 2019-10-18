# Basic SQL Implementation
"""Implements SQL engine."""

from typing import Dict, Any, List


from .database import Table
from .tools import Result

from . import parse
from . import interpret
from .transactions import Select

def run(query: str, database: Dict[str, Table]) -> Result[Table]:
    parsed = parse.parse(query)
    if parsed.value:
        res = select(interpret.make_select(parsed.value), database)
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
