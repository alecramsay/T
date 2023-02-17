#!/usr/bin/env python3

"""
EXPRESSION HANDLING for SELECT & DERIVE
"""

import ast

### CONSTANTS ###

EXPR_DELIMS: str = " ,|()[]{}<>=+-*/"
# EXPR_DELIMS = " ,'|()[]{}<>=+-*/"  # NOTE - with single quotes
# EXPR_DELIMS = " ,'|()[]<>=+-*/"    # NOTE - without {}'s

EXPR_TOKS: list[str] = [d.strip() for d in EXPR_DELIMS if d != " "] + ["=="]


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


### END ###
