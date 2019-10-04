"""Misc tools."""

from typing import Any, List, Generic, Optional, TypeVar
from dataclasses import dataclass

import collections

T = TypeVar('T')  # pylint: disable=invalid-name


def extract_literals(literal: Any) -> List[Any]:
    """Extract values from a `Literal` into a list."""
    result = []
    for elem in literal.__args__:
        if isinstance(elem, str):
            result.append(elem)
        else:
            result += extract_literals(elem)
    return result


@dataclass
class Result(Generic[T]):
    """Hold value and messages from value creation."""
    messages: List[str]
    value: Optional[T] = None


class Smariter(collections.abc.Iterator, Generic[T]):  # type: ignore
    """A smarter iter, which allows for looking ahead, and reading values multiple times."""

    def __init__(self, iter_list: List[T]) -> None:
        self._list = iter_list
        self._i = -1

    def __next__(self) -> T:
        self._i += 1
        value = self.value()
        if not value:
            raise StopIteration
        return value

    def __getitem__(self, offset: int) -> T:
        if not 0 < self._i + offset < len(self._list):
            raise IndexError
        return self._list[self._i + offset]

    def value(self) -> Optional[T]:
        """Retrieve the current buffered value (i.e. the last returned by `next`)."""
        return self._list[self._i] if self._i < len(self._list) else None

    def look_ahead(self, offset: int) -> Optional[T]:
        """Look ahead to some offset."""
        return self._list[self._i + offset] if self._i + offset < len(self._list) else None
