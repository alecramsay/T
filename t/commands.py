# commands.py
#!/usr/bin/env python3

"""
COMMANDS
"""

import re
import keyword
from typing import Optional

from .expressions import tokenize
from .program import Namespace


class Command:
    """A class for parsing command syntax

    1. Instantiate a Command object
    2. Bind args to scriptargs
    3. Parse the command
    """

    _string: str
    _scriptargs: Namespace

    _verb: Optional[str]
    _args_str: Optional[str]
    _args_list: Optional[list[str]]

    def __init__(self, command: str, scriptargs: Namespace) -> None:
        """Initialize a command."""

        self._string = command
        self._scriptargs = scriptargs

        self._split_verb_and_args()
        self._args_list = None

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

        # TODO - Validate positional vs. keyword args

        self._split_args_string()

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

    ### PRIVATE HELPERS ###

    def _split_verb_and_args(self) -> None:
        """Return the verb & args (as a string) of a command."""

        # Args are between mandatory outside delimiting parens
        left: int = self._string.find("(")
        right: int = self._string.rfind(")")

        if (left == -1 or right == -1) or (left > right):
            raise Exception("Verbs must have matching parentheses.")

        if left < 1:
            raise Exception(
                "No verb found. Commands must have a verb and zero or more arguments."
            )

        self._verb = self._string[:left].strip()
        self._args_str = self._string[left + 1 : right].strip()

    def _split_args_string(self) -> None:
        """Split the args string into a list of args."""

        assert self._args_str is not None
        self._args_list = split_args(self._args_str)
        # self._args_list = [x.strip() for x in self._args_str.split(",")]

        pass


### HELPERS ###


def split_args(s: str) -> list[str]:
    """Split a string into a list of arguments, ignoring commas within parentheses."""

    if s == "":
        return list()

    args: list[str] = re.split(r",\s*(?![^()]*\))", s)  # negative lookahead

    return args


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


def is_valid_name(verb, arg, pos) -> None:
    """Language parser helper to validate a name argument & report errors."""

    if not isidentifier(arg):
        raise Exception(
            f"The '{verb}' command requires a valid name for argument {pos}."
        )


### END ###
