# commands.py
#!/usr/bin/env python3

"""
COMMANDS
"""

from typing import Optional

from .expressions import tokenize


class Command:
    """A class for parsing commands"""

    _command: str
    _verb: Optional[str]
    _args: Optional[list[str]]

    def __init__(self, command: str) -> None:
        """Initialize a command."""

        self._command = command
        self._verb = None
        self._args = None

    def parse(self) -> bool:
        """Parse the command. Return True if successful, False otherwise.

        Valid commands:
        - Have a verb
        - Matching parentheses
        - Zero or more comma-separated arguments
        """

        tokens: list[str] = tokenize(self._command)
        rtokens: list[str] = tokens[::-1]

        open_paren: int = tokens[1:].index("(") + 1 if ("(" in tokens[1:]) else -1
        close_paren: int = (
            abs((rtokens.index(")") - (len(tokens) - 1))) if (")" in tokens) else -1
        )
        if (
            (open_paren != -1)  # Open paren exists
            and (open_paren == 1)  # Open paren is second token
            and (close_paren != -1)  # Close paren exists
            and (close_paren + 1 == len(tokens))  # Close paren is last token
        ):
            self._verb = tokens[0]
            # TODO - Recombine tokens into arguments
            self._args = tokens[2:-1]

            return True

        else:
            return False  # Not a valid command

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


# def iskeywordarg(arg: str) -> bool:
#     """Return True if the argument is a keyword argument."""

#     i: int = arg.find("=")
#     contains_equals: bool = True if (i > -1) and (i > 0 and i < len(arg) - 1) else False

#     return contains_equals


### END ###
