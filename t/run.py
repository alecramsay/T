# run.py
#!/usr/bin/env python3

"""
RUN A SCRIPT OR REPL
"""

from typing import Any

from .program import Tables
from .commands import Namespace
from .lang import run_mode, repl_mode
from .reader import DISPLAY_VERBS


def run_script(
    user, file: str, src: str, data: str, output: str, log: str, verbose: bool, **kwargs
) -> None:
    """Execute a 'T' script file."""

    scriptargs: dict = fixup_quotes(kwargs.get("scriptargs", {}))

    with Tables(user=user, src=src, data=data, output=output, log=log, repl=False) as T:
        try:
            exit: bool
            last_verb: str | None

            # Finish binding args
            if scriptargs:
                T.call_stack.push(Namespace(scriptargs))
            if verbose:
                T.debug = True

            if file:
                last_verb = None
                exit = False

                exit, last_verb = run_mode(file, T)

                if (not exit) and last_verb and (last_verb not in DISPLAY_VERBS):
                    T.write()

                print()
            else:
                raise Exception("No file given")

        except Exception as e:
            print("Exception executing program: ", e)


def run_repl(
    user: str, src: str, data: str, output: str, log: str, verbose: bool, **kwargs
) -> None:
    """Start 'T' REPL"""

    scriptargs: dict = fixup_quotes(kwargs.get("scriptargs", {}))

    with Tables(user=user, src=src, data=data, output=output, log=log, repl=True) as T:
        try:
            # Finish binding args
            if scriptargs:
                T.call_stack.push(Namespace(scriptargs))
            if verbose:
                T.debug = True

            print()
            print("Welcome to T:")
            print()

            repl_mode(T)

            print()
            print("Bye!")
            print()

        except Exception as e:
            print("Exception executing program: ", e)


# Helper for script args


def fixup_quotes(d: dict) -> dict:
    """
    HACK: I haven't figured out how to escape single quotes in argparse string args
    """
    updated: dict = {}
    for k in d:
        v: Any = d[k]
        if type(v) == str:
            updated[k] = "'{}'".format(d[k])
        else:
            updated[k] = v

    return updated


### END ###
