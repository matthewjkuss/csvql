# Basic SQL Implementation
"""Implements SQL engine."""

from typing import Dict, Any, List, Optional

import logging


from .database import Table

from . import parse
from . import interpret
from .transactions import Select

log = logging.getLogger(__name__)

def run(query: str, database: Dict[str, Table]) -> Optional[Table]:
    parsed = parse.parse(query)
    if parsed:
        return select(interpret.make_select(parsed), database)
    return None


def sort_order(array: List[Any], order: List[int]) -> List[Any]:
    return [array[x] for x in order]

def select(statement: Optional[Select], database: Dict[str, Table]) -> Optional[Table]:
    """Run select style command on database."""
    if not statement:
        return None
    table = database.get(statement.table)
    if not table:
        log.error(f"Table `{statement.table}` not found")
        return None
    columns = statement.columns if statement.columns != "*" else table.columns
    log.debug("col %s", columns)
    try:
        column_idx = [table.columns.index(column) for column in columns]
    except ValueError as err:
        log.error(f"Column named `{str(err).split()[0][1:-1]}` cannot be found.")
        return None
    rows = [[row[idx] for idx in column_idx] for row in table.rows]
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
    return Table(columns, rows)
