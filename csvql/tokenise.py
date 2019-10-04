"""Defines an SQL tokeniser."""

from typing import NamedTuple, List, Tuple, Match

import re
from functools import reduce

from typing_extensions import Literal

import grammer
from tools import Result

# First we define the possible labels for our tokens (both intermediate and final).

TokenLabel = Literal["operator", "word", "keyword", "number"]  # pylint: disable=invalid-name
RegexLabel = Literal["dquote", "squote", TokenLabel]  # pylint: disable=invalid-name


class Token(NamedTuple):
    """Define a holder for an SQL token."""
    label: TokenLabel
    value: str


# Now we define some functions to help generate our matching regex, and then define the pieces.

def or_regexes(sub_expressions: List[str]) -> str:
    """Take the disjunction of a list of regex expressions."""
    return reduce(lambda x, y: x + "|" + y, sub_expressions)

def group_regexes(regexes: List[Tuple[RegexLabel, str]]) -> str:
    """Generate a regex expression, from a list of labelled sub-expressions."""
    return or_regexes([f"(?P<{label}>{pattern})" for label, pattern in regexes])

reg_list: List[Tuple[RegexLabel, str]] = [
    ("dquote", '(")(""|[^"])*(")'),
    ("squote", "(')(''|[^'])*(')"),
    ("keyword", "(?i:" + or_regexes(grammer.KEYWORDS) + ")"),
    ("operator", or_regexes(["\\" + x for x in grammer.OPERATORS])),
    ("number", r"\d+"),
    ("word", r"\w+|\*"),
]


# Then we extract our tokens from the regex matches, and do some post-processing (such as lower
# casing keywords and removing extra quotation marks).

def extract_token(match: Match[str]) -> Token:
    """Provided with a match, extract a token."""
    for key, value in match.groupdict().items():
        if value:
            print("Debug - Token:", key, value)
            if key == "squote":
                if value[0] == "\'" and value[-1] == "\'":
                    value = value[1:-1]
                return Token("word", value.replace("\'\'", "\'"))
            if key == "dquote":
                if value[0] == "\"" and value[-1] == "\"":
                    value = value[1:-1]
                return Token("word", value.replace("\"\"", "\""))
            if key == "keyword":
                return Token("keyword", value.lower())
            return Token(key, value)  # type: ignore
    raise ValueError


# And finally we bring it all together!

def tokenise(query: str) -> Result[List[Token]]:
    """Generate tokens for a given SQL query."""
    print("Debug - Regex:", group_regexes(reg_list))
    matches = re.finditer(group_regexes(reg_list), query)
    return Result([], [extract_token(token) for token in matches])
