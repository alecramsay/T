# commands.py
#!/usr/bin/env python3

"""
COMMANDS
"""

import re
import keyword
from typing import Optional, Iterator, Match

from .utils import tokenize, find_args_string, split_args_string


class Namespace:
    _args: dict[str, str]

    def __init__(self, args_dict: dict[str, str]) -> None:
        self._args = args_dict

    def bind(self, name: str, default: Optional[str] = None) -> str | None:
        if name in self._args:
            return self._args[name]
        else:
            return default if default else None


class Command:
    """A class for parsing command syntax

    1. Instantiate a Command object
    2. Bind args to scriptargs
    3. Rewrite aggregate functions?
    4. Parse the command
    """

    _string: str
    _scriptargs: Namespace

    _verb: Optional[str]
    _args_str: Optional[str]

    _args_list: Optional[list[str]]
    _positional_args: Optional[list[str]]
    _keyword_args: Optional[dict[str, str]]

    def __init__(self, command: str, scriptargs: Namespace) -> None:
        """Initialize a command."""

        self._string = command
        self._scriptargs = scriptargs

        self._split_verb_and_args()
        self._args_list = None
        self._positional_args = None
        self._keyword_args = None

    def bind(self) -> str:
        """Bind "args.<arg> or <default>" and "args.<arg>" (both no quotes)."""

        assert self._args_str is not None
        tokens: list[str] = tokenize(self._args_str)

        args: list[str] = unwrap_args(tokens)
        bound_args: str = bind_args(args, self._scriptargs)

        assert self._verb is not None
        self._string = self._verb + "(" + bound_args + ")"

        self._split_verb_and_args()  # again

        return self._string

    def parse(self) -> tuple:
        """Parse the command. Return True if successful, False otherwise.

        Valid commands have:
        - A verb
        - Matching parentheses, and
        - Zero or more comma-separated arguments

        Validate the verb, arguments, and semantics *in the caller*.
        """

        assert self._verb is not None
        if not isidentifier(self._verb):
            raise Exception(f"Invalid verb: {self._verb}")

        self._split_args_string()
        self._classify_args()

        return self._verb, self._args_list

    @property
    def verb(self) -> str:
        """Return the verb of a successfully parsed command."""

        assert self._verb is not None

        return self._verb

    @property
    def args(self) -> list[str]:
        """Return the args of a successfully parsed command."""

        assert self._args_list is not None

        return self._args_list

    @property
    def n_pos(self) -> int:
        """Return the number of positional args."""

        assert self._positional_args is not None

        return len(self._positional_args)

    @property
    def positional_args(self) -> list[str]:
        """Return the positional args."""

        assert self._positional_args is not None

        return self._positional_args

    @property
    def n_kw(self) -> int:
        """Return the number of keyword args."""

        assert self._keyword_args is not None

        return len(self._keyword_args)

    @property
    def keyword_args(self) -> dict[str, str]:
        """Return the keyword args."""

        assert self._keyword_args is not None

        return self._keyword_args

    ### PRIVATE HELPERS ###

    def _split_verb_and_args(self) -> None:
        """Return the verb & args (as a string) of a command."""

        left: int
        right: int
        left, right = find_args_string(self._string)

        self._verb = self._string[:left].strip()
        self._args_str = self._string[left + 1 : right].strip()

    def _split_args_string(self) -> None:
        """Split the args string into a list of args."""

        assert self._args_str is not None
        self._args_list = split_args_string(self._args_str)
        # self._args_list = [x.strip() for x in self._args_str.split(",")]

    def _classify_args(self) -> None:
        """Classify the args as positional or keyword."""

        assert self._args_list is not None

        positional: list[str] = list()
        keywords: dict[str, str] = dict()
        kw_mode: bool = False

        for arg in self._args_list:
            if iskeywordarg(arg):
                k: str
                v: str
                k, v = split_keyword_arg(arg)
                keywords[k] = v
                kw_mode = True

            else:
                if kw_mode:
                    raise Exception(f"Positional args must precede keyword args.")
                positional.append(arg)

        self._positional_args = positional
        self._keyword_args = keywords


### HELPERS ###


def unwrap_args(tokens) -> list[str]:
    """Remove extraneous parentheses that simply surround arguments or argument with 'or' defaults."""

    out_tokens: list[str] = list()
    pending: list[str] = list()

    in_parens: bool = False

    for token in tokens:
        if in_parens and token == "(":
            out_tokens += pending
            pending = [token]
            continue

        if in_parens and token == ")":
            pending += [token]
            wrapped_decl: bool = False
            if len(pending) == 3 and pending[1].startswith("args."):
                wrapped_decl = True
            elif (
                len(pending) == 5
                and pending[1].startswith("args.")
                and pending[2] == "or"
            ):
                wrapped_decl = True
            if wrapped_decl:
                out_tokens += pending[1 : len(pending) - 1]
            else:
                out_tokens += pending
            pending = list()
            in_parens = False
            continue

        if in_parens:
            pending += [token]
            continue

        if token == "(":
            in_parens = True
            pending += [token]
            continue

        out_tokens += [token]

    if len(pending) > 0:
        out_tokens += pending

    return out_tokens


def bind_args(tokens: list[str], scriptargs) -> str:
    """Bind a tokenized set if args with args.<arg> or <default>-style syntax."""

    bound: str = ""

    in_decl: bool = False
    has_default: bool = False
    name: str = ""
    has_bound: bool = False

    for token in tokens:
        if token.startswith("args."):
            in_decl = True
            name = token[5:]
            continue

        if in_decl and (token == "or"):
            has_default = True
            continue

        if in_decl and has_default:
            # Bind the default.
            bound += scriptargs.bind(name, token)
            has_bound = True

        if in_decl and (not has_default):
            # Bind the arg w/o default
            bound += scriptargs.bind(name)
            bound += token
            has_bound = True

        if has_bound:
            in_decl = False
            has_default = False
            name = ""
            has_bound = False
            continue

        bound += token

    # Handle a trailing arg
    if in_decl:
        bound += scriptargs.bind(name)

    return bound


def split_keyword_arg(arg: str) -> tuple[str, str]:
    """Split a keyword argument into keyword and value."""

    pos: int = arg.find("=")
    keyword: str = arg[:pos]
    value: str = arg[pos + 1 :]

    return keyword, value


def isidentifier(ident: str) -> bool:
    """Determines if string is valid Python identifier.

    From: https://stackoverflow.com/questions/12700893/how-to-check-if-a-string-is-a-valid-python-identifier-including-keyword-check#29586366
    """

    if not isinstance(ident, str):
        raise TypeError("expected str, but got {!r}".format(type(ident)))

    if not ident.isidentifier():
        return False

    if keyword.iskeyword(ident):
        return False

    return True


def iskeywordarg(arg: str) -> bool:
    """Return True if arg a keyword argument; otherwise False."""

    matches: Iterator[Match[str]] = re.finditer("=", arg)
    one_equals: bool = True if len(list(matches)) == 1 else False
    pos: int = arg.find("=")
    word_before: bool = True if (pos > 0 and pos < len(arg) - 1) else False

    return one_equals and word_before


def validate_name(verb, arg, pos) -> None:
    """Language parser helper to validate a name argument & report errors."""

    if not isidentifier(arg):
        raise Exception(
            f"The '{verb}' command requires a valid name for argument {pos}."
        )


def validate_nargs(verb, n, least, most=None) -> None:
    if most == 0 and n > 0:
        raise Exception(f"The '{verb}' command doesn't take any arguments.")

    if n < least:
        raise Exception(f"Too few arguments for '{verb}' command.")

    if most and (n > most):
        raise Exception(f"Too many arguments for '{verb}' command.")


def validate_filename(arg: str) -> None:
    """For 'read' and 'write'"""

    try:
        open(arg, "r")
    except OSError:
        raise Exception("File not found.")


### END ###
