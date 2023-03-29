# utils.py
#!/usr/bin/env python3

"""
UTILITIES
"""

import re
import builtins
from typing import Any

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


def find_args_string(s: str) -> tuple[int, int]:
    """Find the offsets of the open & close parens bounding the args string in a command."""

    # Args are between mandatory outside delimiting parens
    left: int = s.find("(")
    right: int = s.rfind(")")

    if (left == -1 or right == -1) or (left > right):
        raise Exception(
            "Commands have zero or more arguments w/in matching parentheses."
        )

    if left < 1:
        raise Exception("Commands start with a verb and open parenthesis.")

    return left, right


def split_verb_and_args(s: str) -> tuple[str, str]:
    """Split a command string into a verb and args string."""

    left: int
    right: int
    left, right = find_args_string(s)

    verb = s[:left].strip()
    args_str = s[left + 1 : right].strip()

    return verb, args_str


def split_args_string(s: str) -> list[str]:
    """Split a string into a list of arguments, ignoring commas within parentheses."""

    if s == "":
        return list()

    args: list[str] = re.split(r",\s*(?![^()]*\))", s)  # negative lookahead

    return args


def split_col_spec_string(arg: str) -> tuple[str, str] | str:
    """Split a column spec string into a pair of column names.

    Examples:
        "(foo, bar)" => ("foo", "bar")
        "foobar" => "foobar"
    """

    if len(arg.split(",")) == 1:
        return arg

    pair: list[str] = [x.strip() for x in arg[1:-1].split(",")]
    return pair[0], pair[1]


def parse_spec(spec: str | list[str] | tuple) -> tuple:
    """Parse a spec singleton -or- pair.

    Examples:

    spec = 'GEOID20' => ('GEOID20', 'GEOID20')
    spec = ['GEOID20', 'GEOID'] => ('GEOID', 'GEOID')

    spec = 'GEOID' => ('GEOID', 'GEOID')
    spec = ['Total', 'DESC'] => ('Total', 'DESC')

    parse_spec(spec)
    """

    first: str
    second: str

    if isinstance(spec, list) or isinstance(spec, tuple):
        assert isinstance(spec, list) or isinstance(spec, tuple)
        first = spec[0]
        second = spec[1]
    else:
        first = spec
        second = spec

    return first, second


def isstringifiedlist(s: str) -> bool:
    """Is a string a stringified list?"""

    if s.startswith("[") and s.endswith("]"):
        return True
    else:
        return False


def islistofstr(obj: Any) -> bool:
    """Is obj a stringified list of strings? (but not nested lists))"""

    if not isinstance(obj, list):
        return False

    if not all(isinstance(elem, str) for elem in obj):
        return False

    if any(isstringifiedlist(elem) for elem in obj):
        return False

    return True


def value_width(v: Any, pad: int = 2) -> int:
    if v is None:
        return 10

    if type(v) is str:
        return len(v)

    if type(v) in [int, float]:
        return len(str(v))

    if type(v) is list:
        return sum([value_width(x) + pad for x in v])

    return 10


def map_keys(d: dict, mapping: dict) -> dict:
    """mapping is a dict of {old_key: new_key}"""

    return {mapping[k]: v for k, v in d.items()}


def get_builtin_fn(name: str) -> Any:
    """Get a builtin function by name."""

    return getattr(builtins, name)


# TODO - mod_fns?
# def mod_fns(mod):
#     pairs = inspect.getmembers(mod, inspect.isfunction)
#     fns_dict = {k: v for k, v in pairs}

#     return fns_dict

### MISSING ###


#  TODO - Handle missing?
# def ismissing(v: Any) -> bool:
#     """Return True if v is missing, else False."""

#     return True if (v is None) else False


### END ###
