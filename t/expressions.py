#!/usr/bin/env python3

"""
EXPRESSION HANDLING for SELECT & DERIVE
"""

import ast

### CONSTANTS ###

EXPR_DELIMS: str = " ,|()[]{}<>=+-*/"
# EXPR_DELIMS = " ,'|()[]{}<>=+-*/"  # NOTE - with single quotes
# EXPR_DELIMS = " ,'|()[]<>=+-*/"    # NOTE - without {}'s

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

    Either a SELECT expression or the right-hand side of a DERIVE expression,
    i.e., cannot contain single equals signs.
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


def rewrite_expr(df: str, tokens: list[str], names: list[str]) -> bool:
    """Rewrite the tokens of a (right-hand side) expression into a valid Python Pandas expression."""

    expr: str = ""
    for tok in tokens:
        if tok in DELIM_TOKS:
            expr = expr + tok
        elif is_literal(tok):
            expr = expr + tok
        elif tok.startswith("slice"):
            expr = expr + rewrite_slice(tok)
        elif tok in names:
            expr = expr + f"{df}['{tok}']"
        else:
            raise Exception(f"Invalid column reference: {tok}")

    return expr


def regroup_slices(tokens: list[str]) -> list[str]:
    """Regroup slice operations into single tokens."""

    new_tokens: list[str] = list()

    for i, tok in enumerate(tokens):
        if tok == "[":  # Beginning of a slice
            pass
        else:
            new_tokens.append(tok)

    return new_tokens


def is_int(tok: str) -> bool:
    """Return True if tok is an integer, else False."""

    try:
        int(tok)
        return True
    except ValueError:
        return False


def is_slice(tokens: list[str]) -> tuple[str, int]:
    """Return a slice expression (as string) and how many tokens it consumes or None, 0 if not a slice."""

    state: str = None

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

            return None, 0

        if state == "start":
            if tok == ":":  # Slice with start #
                state = "colon"
                expr = expr + tok
                skip = skip + 1
                continue

            return None, 0

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

            return None, 0

        if state == "stop":
            if tok == "]":  # Slice with no stop #
                state = "close"
                expr = expr + tok
                skip = skip + 1
                continue

            return None, 0

        if state == "close":
            return expr, skip  # More tokens after slice

    if state == "close":
        return expr, skip  # No more tokens after slice

    # Potential slice not completed
    return None, 0


def rewrite_slice(tok: str) -> str:
    """Rewrite a grouped slice expression (e.g., 'slice[2:5]') into a valid Python Pandas expression."""

    return tok.replace("slice", ".str")


### END ###
