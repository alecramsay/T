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

    for token in tokens:
        if token in DELIM_TOKS:
            if token == "=":
                raise Exception("Use '==' for equality comparison.")
            continue
        if is_literal(token):
            continue
        if token not in names:
            raise Exception(f"Invalid column reference: {token}")

    return True


def rewrite_expr(df: str, tokens: list[str], names: list[str]) -> bool:
    """Rewrite the tokens of a (right-hand side) expression into a valid Python Pandas expression."""

    expr: str = ""
    for token in tokens:
        if token in DELIM_TOKS:
            expr = expr + token
        elif is_literal(token):
            expr = expr + token
        elif token.startswith("slice"):
            expr = expr + rewrite_slice(token)
        elif token in names:
            expr = expr + f"{df}['{token}']"
        else:
            raise Exception(f"Invalid column reference: {token}")

    return expr


def rewrite_slice(tok: str) -> str:
    """Rewrite a grouped slice expression (e.g., 'slice[2:5]') into a valid Python Pandas expression."""

    return tok.replace("slice", ".str")


### END ###
