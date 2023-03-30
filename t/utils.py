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


def mask_char(in_str: str, from_char: str, to_char: str) -> str:
    """Replace one character with another in a string, when it is with parentheses, brackets, or braces.

    For example, make all commas w/in ()'s, []'s, or {}'s into hashes so the top-level string can be split on commas.
    """

    out_str: str = ""
    nparens: int = 0
    nbrackets: int = 0
    nbraces: int = 0

    for i, c in enumerate(in_str):
        match c:
            case "(":
                nparens += 1
                out_str += c
            case ")":
                nparens -= 1
                out_str += c
            case "[":
                nbrackets += 1
                out_str += c
            case "]":
                nbrackets -= 1
                out_str += c
            case "{":
                nbraces += 1
                out_str += c
            case "}":
                nbraces -= 1
                out_str += c
            case _:
                if c == from_char and (nparens > 0 or nbrackets > 0 or nbraces > 0):
                    out_str += to_char
                else:
                    out_str += c

    if nparens == 0 or nbrackets == 0 or nbraces == 0:
        return out_str
    else:
        raise Exception("Mismatched parentheses, brackets, or braces.")


def unmask_char(in_str: str, from_char: str, to_char: str) -> str:
    """Reverse a mask_char operation."""

    return mask_char(
        in_str,
        from_char,
        to_char,
    )


def split_args_string(s: str) -> list[str]:
    """Split a string into a list of arguments, ignoring commas within parentheses."""

    if s == "":
        return list()

    # This handles parens but not brackets or braces
    # args: list[str] = re.split(r",\s*(?![^()]*\))", s)  # negative lookahead

    s = mask_char(s, ",", "#")
    args: list[str] = [unmask_char(x.strip(), "#", ",") for x in s.split(",")]

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


#  TODO - Handle missing?
# def ismissing(v: Any) -> bool:
#     """Return True if v is missing, else False."""

#     return True if (v is None) else False


### END ###
