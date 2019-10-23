"""Parse SQL using regex-like expressions."""

import re
from dataclasses import dataclass
from typing import List, Match, Dict, Any, Optional, Callable

from . import tokenise

TEST_QUERY = "from table select id, name cross join table2; from table2 select count(distinct id);"

TOKEN_LIST = [
    ("w", "Word"),
    ("f", "Aggregate"),
    ("c", "Clause"),
    ("b", "Prefix"),
    ("a", "Postfix"),
    (",", "Comma"),
    (";", "Semicolon"),
    ("(", "Left"),
    (")", "Right"),
    ("*", "Asterisk")
]

DISCARDABLE_TOKENS = ["Left", "Right", "Comma", "Semicolon"]

TOKEN_MAP = {
    **{key: value for (key, value) in TOKEN_LIST},
    **{key: value for (value, key) in TOKEN_LIST}
}

TEST_TOKENS = tokenise.tokenise(TEST_QUERY)

TEST_STR = "".join([TOKEN_MAP[token.label.capitalize()] for token in TEST_TOKENS])

PATTERNS = {
    "ast" : "{statement}*",
    "statement" : "{clause}* Semicolon",
    "clause" : "Prefix* Clause ({column_list}|{list}|{expression}) Postfix*",
    "column_list" : "Prefix? ({aggregate}|{column}) (Comma ({aggregate}|{column}))*",
    "aggregate" : "Aggregate Left Prefix? {column} Right",
    "column" : "Word | Asterisk",
    "list" : "Word (Comma Word)*",
    "expression" : "Word"
}

COMPILED_PATTERNS: Dict[str, str] = {}

@dataclass
class Expr():
    name: str
    pattern: str
    children: List[str]

def get_children(query: str) -> List[str]:
    return list(dict.fromkeys([match[0][1:-1] for match in re.finditer("{.*?}", query)]))

def match_token(match: Match[str]) -> str:
    return re.escape(TOKEN_MAP[match[0]])

def match_pattern(match: Match[str]) -> str:
    name = match[0][1:-1]
    if name in COMPILED_PATTERNS:
        return "(" + COMPILED_PATTERNS[name] +")"
    return "(" + compile_pattern(name, PATTERNS[name]) + ")"

def compile_pattern(name: str, query: str) -> str:
    query = query.replace(" ", "")
    query = re.sub("[A-Z][a-z]+", match_token, query)
    query = re.sub("{.*?}", match_pattern, query)
    COMPILED_PATTERNS[name] = query
    return query

def make_expr(name: str, pattern: str) -> Expr:
    return Expr(name, compile_pattern(name, pattern), get_children(pattern))

EXPRS = {key: make_expr(key, value) for (key, value) in PATTERNS.items()}

def ref(expr: Expr) -> str:
    return f"(?P<{expr.name}>{expr.pattern})"

ENDC = '\033[0m'
GREEN = '\033[92m\033[4m'
RED = '\033[91m'

def str_zip(compare: Callable[[str, str], str], left: str, right: str) -> str:
    assert len(left) == len(right)
    return "".join([compare(left[i], right[i]) for (i, _) in enumerate(left)])

def clear(string: str, x: int, y: int) -> str:
    return string[:x] + (y-x) * '_' + string[y:]

def clear_complement(string: str, x: int, y: int) -> str:
    return x * '_' + string[x:y] + (len(string)-y) * '_'

def union(left: str, right: str) -> str:
    return "_" if left == "_" or right == "_" else left

def mask(candidate: str, matched: str) -> str:
    return "_" if matched != "_" else candidate

@dataclass
class Tree:
    name: str
    match: str
    exclusion: str
    children: List['Tree']

def rere(expr: Expr, query: str, depth: int = 0, start: int = 0, end: int = -1) -> List[Tree]:
    if end == -1:
        end = len(query)
    try:
        results = re.finditer(expr.pattern, query[slice(start, end)])
    except re.error as exception:
        print(exception.__dict__)
        print(exception.pattern[exception.pos:]) # type: ignore
        raise exception
    big_ls: List[Tree] = []
    for match in results:
        if not match[0]:
            continue

        sub_start = start + match.start(0)
        sub_end = start + match.end(0)

        matched = clear_complement(query, sub_start, sub_end)
        candidates = matched

        if not expr.children:
            big_ls.append(Tree(expr.name, candidates, candidates, []))
        little_ls: List[Tree] = []
        exclude: str = matched
        for child_expr in expr.children:
            new = rere(EXPRS[child_expr], candidates, depth+1, sub_start, sub_end)
            for tree in new:
                candidates = str_zip(mask, candidates, tree.match)
                exclude = str_zip(mask, exclude, tree.match)
            little_ls += new
        if little_ls:
            big_ls.append(Tree(expr.name, matched, str_zip(union, matched, exclude), little_ls))
    return big_ls

result = rere(EXPRS['ast'], TEST_STR)

def color(match: str, exclusion: str) -> str:
    if exclusion != '_':
        return RED + exclusion + ENDC
    if match != '_':
        return match
    return '_'

def print_tree(tree_list: List[Tree], depth: int = 0) -> str:
    return (
        "".join([f"{str_zip(color, tree.match, tree.exclusion)} | {depth * '. ' + tree.name:<20} | {[(pos, TOKEN_MAP[key], TEST_TOKENS[pos].value) for (pos, key) in enumerate(tree.exclusion) if key != '_' and TOKEN_MAP[key] not in DISCARDABLE_TOKENS]}\n" + print_tree(tree.children, depth+1) for tree in tree_list])
    )

print(print_tree(result))
