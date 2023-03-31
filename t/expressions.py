# expressions.py
#!/usr/bin/env python3

"""
EXPRESSION HANDLING for SELECT & DERIVE
"""

import ast
from typing import Optional, Any, Type

from .udf import UDF, map_args
from .utils import DELIM_TOKS, tokenize
from .commands import isidentifier


def rewrite_expr(
    tokens: list[str], col_names: list[str], udf: Optional[UDF] = None
) -> tuple[str, list[str]]:
    """Rewrite expression using Pandas dataframe syntax."""

    # Mark the slice operations
    tokens = mark_slices(tokens)

    # Mark UDF references & define wrappers for them
    wrappers: list[str] = []
    if udf:
        tokens, wrappers = mark_udf_calls(tokens, udf)

    # Rewrite the expression using Pandas dataframe syntax
    expr: str = generate_df_syntax(tokens, col_names, udf)

    return expr, wrappers


def isliteral(node_or_string: Any, verbose: bool = False) -> bool:
    """Is the argument a valid Python literal?

    https://docs.python.org/3/library/ast.html -- "The string or node provided may
    only consist of the following Python literal structures: strings, bytes, numbers,
    tuples, lists, dicts, sets, booleans, None and Ellipsis."

    NOTE - Not all literals are supported.
    """

    try:
        l: Any = ast.literal_eval(node_or_string)
        t: Type = type(l)

        print(f"l: {l}, t: {t}")

        return True

    except:
        print(f"Not a valid literal: {node_or_string}")
        return False


def has_valid_col_refs(tokens: list[str], names: list[str]) -> bool:
    """Tokenized expression has valid column references.

    For validating SELECT expressions. Cannot contain single equals signs.
    """

    for tok in tokens:
        if tok in DELIM_TOKS:
            if tok == "=":
                raise Exception("Use '==' for equality comparison.")
            continue
        if isidentifier(tok):
            continue
        if isliteral(tok):
            continue
        if tok not in names:
            raise Exception(f"Invalid reference in SELECT expression: {tok}")

    return True


def has_valid_refs(
    tokens: list[str], col_names: list[str], udf_names: list[str]
) -> bool:
    """Tokenized expression has valid column -or- UDF references.

    For validating the right-hand side of a DERIVE expression.
    Cannot contain single equals signs.
    """

    for tok in tokens:
        if tok in DELIM_TOKS:
            if tok == "=":
                raise Exception("Use '==' for equality comparison.")
            continue
        if isidentifier(tok) and (tok in col_names or tok in udf_names):
            continue
        if isliteral(tok):
            continue

        raise Exception(f"Invalid reference in DERIVE expression: {tok}")

    return True


def generate_df_syntax(
    tokens: list[str], col_names: list[str], udf: Optional[UDF] = None
) -> str:
    """Rewrite the tokens of a (right-hand side) expression into a valid Python Pandas expression.

    - Slices have been rewritten, and
    - UDF calls have been wrapped
    """

    expr: str = ""
    for tok in tokens:
        if tok in DELIM_TOKS:
            expr = expr + tok
        elif tok in col_names:
            expr = expr + col_rewrite_rule(tok)
        elif isslice(tok):
            expr = expr + slice_rewrite_rule(tok)
        elif isudfcall(tok, udf):
            expr = expr + udf_rewrite_rule(tok, udf)
        elif isliteral(tok):
            expr = expr + tok
        else:
            raise Exception(f"Invalid column reference: {tok}")

    return expr


### COLUMN REFERENCES ###


def col_rewrite_rule(tok: str) -> str:
    """Rewrite rule for column references."""

    return f"df['{tok}']"


### SLICES ###


def mark_slices(tokens: list[str]) -> list[str]:
    """Regroup slice operations into single tokens."""

    new_tokens: list[str] = list()
    skip: int = 0

    for i, tok in enumerate(tokens):
        if skip > 0:
            skip = skip - 1
            continue

        if tok == "[":  # Beginning of a slice
            grouped: str
            grouped, skip = get_slice_tokens(tokens[i:])

            if grouped is not None:
                new_tokens.append("slice" + grouped)
                skip -= 1
                continue
            else:
                new_tokens.append(tok)
                continue

        new_tokens.append(tok)

    return new_tokens


def get_slice_tokens(tokens: list[str]) -> tuple[str, int]:
    """Return a slice expression (as string) and how many tokens it consumes or None, 0 if not a slice."""

    state: str = ""

    expr: str = ""
    skip: int = 0

    for i, tok in enumerate(tokens):
        if i == 0:
            expr = expr + tok  # When called, the first token is an open bracket '['
            state = "open"
            skip = 1
            continue

        if state == "open":
            if isint(tok):
                state = "start"
                expr = expr + str(tok)
                skip = skip + 1
                continue

            if tok == ":":  # Slice with no start #
                state = "colon"
                expr = expr + tok
                skip = skip + 1
                continue

            return "", 0

        if state == "start":
            if tok == ":":  # Slice with start #
                state = "colon"
                expr = expr + tok
                skip = skip + 1
                continue

            return "", 0

        if state == "colon":
            if isint(tok):
                state = "stop"
                expr = expr + str(tok)
                skip = skip + 1
                continue

            if tok == "]":  # Slice with no stop #
                state = "close"
                expr = expr + tok
                skip = skip + 1
                continue

            return "", 0

        if state == "stop":
            if tok == "]":  # Slice with no stop #
                state = "close"
                expr = expr + tok
                skip = skip + 1
                continue

            return "", 0

        if state == "close":
            return expr, skip  # More tokens after slice

    if state == "close":
        return expr, skip  # No more tokens after slice

    # Potential slice not completed
    return "", 0


def isint(tok: str) -> bool:
    """Return True if tok is an integer, else False."""

    try:
        int(tok)
        return True
    except ValueError:
        return False


def isslice(tok: str) -> bool:
    """Return True if tok is a slice expression, else False."""

    return tok.startswith("slice")


def slice_rewrite_rule(tok: str) -> str:
    """Rewrite a grouped slice expression (e.g., 'slice[2:5]') into a valid Python Pandas expression."""

    return tok.replace("slice", ".str")


### UDFs ###


def mark_udf_calls(
    tokens: list[str], udf: Optional[UDF] = None
) -> tuple[list[str], list[str]]:
    """Collapse UDF calls back into single tokens & wrap the UDF."""

    if not udf:
        return tokens, []

    new_tokens: list[str] = list()
    wrappers: list[str] = list()

    in_udf: bool = False
    udf_name: str = ""
    udf_call: str = ""

    for i, tok in enumerate(tokens):
        if not in_udf and not udf.isudf(tok):
            new_tokens.append(tok)
            continue

        if not in_udf and udf.isudf(tok):
            in_udf = True
            udf_call = tok
            udf_name = tok
            continue

        if in_udf:
            udf_call = udf_call + tok
            if tok == ")":
                # Wrap the UDF calls
                source: str = udf.source(udf_name)
                arg_map: dict[str, str] = map_args(udf_call, source)
                ref: int = udf.count(udf_name)
                alias: str = udf.alias(udf_name, ref)
                wrapper: str = udf.wrap(alias, udf_name, arg_map)
                wrappers.append(wrapper)

                # Replace the UDF call with the info to reference the wrapper
                new_tokens.append(f"{udf_name}({ref})")

                udf_name = ""
                in_udf = False

    if in_udf:
        raise Exception(f"UDF call not completed: {udf_call}")

    return new_tokens, wrappers


def isudfcall(tok: str, udf: Optional[UDF]) -> bool:
    """Return True if tok is a UDF call, else False."""

    if not udf:
        return False

    tokens: list[str] = tokenize(tok)

    return all(
        [len(tokens) == 4, tokens[1] == "(", tokens[3] == ")", udf.isudf(tokens[0])]
    )


def udf_rewrite_rule(tok: str, udf: Optional[UDF]) -> str:
    """Rewrite a UDF call into a valid Python Pandas expression."""

    if not udf:
        raise Exception(f"UDF not defined: {tok}")

    tokens: list[str] = tokenize(tok)
    udf_name: str = tokens[0]
    ref: int = int(tokens[2])

    alias: str = udf.alias(udf_name, ref)

    return f"df.apply({alias}, axis=1)"


### END ###
