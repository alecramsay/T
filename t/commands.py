# commands.py
#!/usr/bin/env python3

"""
COMMANDS
"""

from typing import Optional

from .expressions import tokenize


class Command:
    """A class for parsing command syntax"""

    _input: str
    _verb: Optional[str]
    _args: Optional[list[str]]

    def __init__(self, command: str) -> None:
        """Initialize a command."""

        self._input = command
        self._verb = None
        self._args = None

    def parse(self) -> bool:
        """Parse the command. Return True if successful, False otherwise.

        Valid commands:
        - Have a verb
        - Matching parentheses
        - Zero or more comma-separated arguments
        """

        # Args are between mandatory outside delimiting parens
        left: int = self._input.find("(")
        right: int = self._input.rfind(")")

        if (left == -1 or right == -1) or (left > right):
            raise Exception("Verbs must have matching parentheses.")

        if left < 1:
            raise Exception(
                "No verb found. Commands must have a verb and zero or more arguments."
            )

        self._verb = self._input[:left].strip()
        self._args = [x.strip() for x in self._input[left + 1 : right].split(",")]

        return True

    @property
    def verb(self) -> str:
        """Return the verb of a successfully parsed command."""

        assert self._verb is not None

        return self._verb

    @property
    def args(self) -> list[str]:
        """Return the args of a successfully parsed command."""

        assert self._args is not None

        return self._args

    ### PRIVATE HELPERS ###


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


### END ###
