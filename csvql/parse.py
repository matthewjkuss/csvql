"""Parser for SQL statements."""

# pylint: disable=invalid-name

from __future__ import annotations

from typing import List, Dict, Any, Union, Optional, Set
from dataclasses import dataclass

from typing_extensions import Literal

import grammer
from grammer import Form, Keyword
from tools import Smariter, Result

import tokenise



@dataclass
class Clause:
    """Constitute component of statement."""
    form: Form
    flags: Set[Keyword]
    expression: Any
    children: Dict[Keyword, 'Clause']


def get_form(value: str) -> Optional[Form]:
    for x in grammer.TYPES:
        if value == x.name:
            return x
    return None


def parse_query(token_iter: Any) -> Result[(Clause)]:
    messages = []
    flags: Set[Keyword] = set()
    form: Form
    expression: Any = None
    children: Dict[Keyword, Clause] = {}
    # ---
    #try:
    #    first_token = next(token_iter)
    #except StopIteration:
    if not token_iter.value():
        return Result(["Error: No tokens to consume."])
    first_token = token_iter.value()
    if not first_token.label == "keyword":
        return Result([f"Error: Expected keyword, but got `{first_token.value}`."])
    first_form = get_form(first_token.value)
    if first_form is None and not token_iter.look_ahead(1):
        return Result([f"Error: Keyword `{first_token.value}` is not a valid clause name."])
    if first_form is None and token_iter.look_ahead(1):
        second_token = next(token_iter)
        second_form = get_form(second_token.value)
        if second_form is None:
            return Result([f"Error: Neither `{first_token.value}` nor `{second_token.value}` are valid clause names."])
        if not first_token.value in second_form.prefix_flags:
            return Result([f"Error: Keyword `{first_token.value}` is not a valid prefix for `{second_token.value}`."])
        flags.add(first_token.value)
        form = second_form
    else:
        form = first_form
    next(token_iter)
    # ---
    if token_iter.value().label == "keyword":
        if token_iter.value().value in form.infix_flags:
            flags.add(token_iter.value().value)
            next(token_iter)
    # ---
    #return Result([f"Form: {form} {token_iter.value()}"])
    if form.expression == "table-name":
        expression = token_iter.value().value
        token = next(token_iter)
    elif form.expression == "number":
        expression = token_iter.value().value
        token = next(token_iter)
    elif form.expression == "column-list":
        # print("bnag", token_iter.value())
        if token_iter.value().value == "*":
            # print("Star found!")
            expression = "*"
            token = next(token_iter)
        else:
            expression = []
            # for token in token_iter:
            while True:
                token = token_iter.value()
                if token_iter.value().label == "keyword":
                    break
                elif token.label == "operator" and token.value != ",":
                    return Result([f"Error: `{token.value} is not a valid operator in column list.`"])
                elif token.value == ",":
                    pass
                else:
                    expression.append(token.value)
                next(token_iter)
    # ---
    for x in form.required_clauses:
        if token_iter.value().value != x:
            return Result([f"Error: `{x}` clause required."])
        result = parse_query(token_iter)
        if result.value is None:
            return Result(["Error: Recursive call failed."] + result.messages)
        children.update({result.value.form.name: result.value})
    # ---
    for x in form.optional_clauses:
        if not token_iter.value() or token_iter.value().value != x:
            messages.append(f"Note: Optional clause `{x}` is absent.")
            continue
        result = parse_query(token_iter)
        if result.value is None:
            return Result(["Error: Recursive call failed."] + result.messages)
        children.update({result.value.form.name: result.value})

    return Result(messages, Clause(form, flags, expression, children))


def parse(query: str) -> Result[Clause]:
    # Tokenise
    tokenise_result = tokenise.tokenise(query)
    tokens = tokenise_result.value
    if tokens is None:
        return Result(["Error: No tokens generated."] + tokenise_result.messages)
    #token_iter = look_ahead(iter(tokens))
    token_iter = Smariter(tokens)
    next(token_iter)
    result = parse_query(token_iter)
    if result.value and not result.value.form.primary:
        return Result(result.messages + [f"Error: Clause `{result.value.form.name}` is not primary."])
    #remainder = list(x[0].value for x in list(token_iter))
    #if remainder:
    #    result.messages.append(f"Warning: Tokens {remainder} still remain.")
    result.messages += [f"Note: {print_clause(result.value)}"]
    result.messages += [f"Note: Tokens are {list(x.value for x in tokens)}."]
    return result


def print_clause(clause: Clause, depth: int = 2) -> str:
    if not clause:
        return ""
    result = ""
    indent = '\t' * depth
    result += f"{indent}- {clause.form.name.upper()}: {clause.flags if clause.flags else {}} - {clause.expression}\n"
    for _, child in clause.children.items():
        result += print_clause(child, depth+1) + "\n"
    return result
