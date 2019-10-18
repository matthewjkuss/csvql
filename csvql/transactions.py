"""Defines database commands."""

from typing import Union, List, Optional
from dataclasses import dataclass

from typing_extensions import Literal

@dataclass
class Select:
    """A SELECT statement."""
    distinct: bool
    columns: Union[List[str], Literal["*"]]
    order: List[str]
    table: str
    limit: Optional[int]
