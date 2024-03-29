"""Provides read and write on CSV files."""

from typing import NamedTuple, List, Optional

import csv
import logging

log = logging.getLogger(__name__)

DB_PATH = "../data/categories.csv"

class Table(NamedTuple):
    """Define a SQL table/view."""
    columns: List[str]
    rows: List[List[str]]

def load_table(db_path: str) -> Optional[Table]:
    """Load a CSV file into a `Table`."""
    with open(db_path) as csv_file:
        reader = csv.reader(csv_file)
        columns: Optional[List[str]] = None
        rows: List[List[str]] = []
        for row in reader:
            if not columns:
                columns = row
            else:
                rows.append(row)
        if columns:
            return Table(columns, rows)
    log.warning("Unable to load file at {db_path}.")
    return None
