# expressions.py
#!/usr/bin/env python3

"""
EXPRESSION HANDLING for SELECT & DERIVE
"""

import ast
from typing import Optional

from .udf import *

### CONSTANTS ###

EXPR_DELIMS: str = " ,|()[]{}<>=+-*/:"  # NOTE - with colon
# EXPR_DELIMS: str = " ,|()[]{}<>=+-*/"
# EXPR_DELIMS: str = " ,'|()[]{}<>=+-*/"  # NOTE - with single quotes
# EXPR_DELIMS: str = " ,'|()[]<>=+-*/"    # NOTE - without {}'s

DELIM_TOKS: list[str] = [d.strip() for d in EXPR_DELIMS if d != " "] + ["=="]


def tokenize(expr: str) -> list[str]:
    tokens: list[str] = list()

    word: str = ""
    for i, c in enumerate(expr):
        if c in EXPR_DELIMS:
            if len(word) > 0:
                tokens.append(word)
                word = ""
            if c != " ":
                tokens.append(c)
        else:
            word = word + c

    if len(word) > 0:
        tokens.append(word)

    # Collapse successive '='s
    for i, tok in enumerate(tokens):
        if tok == "=":
            if i > 0 and tokens[i - 1] == "=":
                tokens[i - 1] = "=="
                tokens[i] = ""

    # Remove empty tokens
    tokens = [tok for tok in tokens if len(tok) > 0]

    return tokens


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


def is_literal(tok: str) -> bool:
    """Return True if tok is a Python literal, else False.

    NOTE - Not all literals are supported.
    """

    try:
        ast.literal_eval(tok)
        return True
    except ValueError:
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
        if is_literal(tok):
            continue
        if tok not in names:
            raise Exception(f"Invalid column reference: {tok}")

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
        if is_literal(tok):
            continue
        if tok in col_names:
            continue
        if tok in udf_names:
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
        elif is_slice(tok):
            expr = expr + slice_rewrite_rule(tok)
        elif is_udf_call(tok, udf):
            expr = expr + udf_rewrite_rule(tok, udf)
        elif is_literal(tok):
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
            if is_int(tok):
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
            if is_int(tok):
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


def is_int(tok: str) -> bool:
    """Return True if tok is an integer, else False."""

    try:
        int(tok)
        return True
    except ValueError:
        return False


def is_slice(tok: str) -> bool:
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
        if not in_udf and not udf.is_udf(tok):
            new_tokens.append(tok)
            continue

        if not in_udf and udf.is_udf(tok):
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


def is_udf_call(tok: str, udf: Optional[UDF]) -> bool:
    """Return True if tok is a UDF call, else False."""

    if not udf:
        return False

    tokens: list[str] = tokenize(tok)

    return all(
        [len(tokens) == 4, tokens[1] == "(", tokens[3] == ")", udf.is_udf(tokens[0])]
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
