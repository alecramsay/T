#!/usr/bin/env python3

"""
EXPRESSION HANDLING for SELECT & DERIVE
"""


### CONSTANTS ###

EXPR_DELIMS: list[str] = " ,|()[]{}<>=+-*/"
# EXPR_DELIMS = " ,'|()[]{}<>=+-*/"  # NOTE - with single quotes
# EXPR_DELIMS = " ,'|()[]<>=+-*/"    # NOTE - without {}'s


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


### END ###
