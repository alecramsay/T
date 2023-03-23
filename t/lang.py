# lang.py
#!/usr/bin/env python3

"""
INTERPRETER AND REPL, RUN SCRIPT, & DEBUGGER MODES
"""

import libcst as cst
import logging
from logging.handlers import RotatingFileHandler

from .commands import Namespace, Command
from .program import Program
from .reader import Reader, ReadState, FILE_IN_VERBS, make_input_fn
from .readwrite import FileSpec

ERROR: str = "_error_"


def interpret(command: str, env: Program) -> str:
    """Interpret one T command"""

    ### BIND VARIABLES & PARSE COMMANDS ###

    try:
        cmd: Command = Command(command, env.call_stack.first())
        cmd.bind()
        cmd.parse()
    except Exception as e:
        print("Exception binding command args: ", e)
        return ERROR

    ### RE-WRITE AGGREGATE FUNCTION REFERENCES ###

    # TODO - Not re-implemented yet
    # try:
    #     if not env.table_stack.isempty():
    #         names = env.table_stack.first().col_names()
    #         command = rewrite_agg_refs(command, names)
    # except Exception as e:
    #     print("Exception rewriting aggregate function references: ", e)
    #     return ERROR

    ### HANDLE VERBS ###

    verb: str = cmd.verb

    match verb:
        case "from_":
            return _handle_from(cmd, env)

        ### TABLE VERBS ###

        case "write":
            return _handle_write(cmd, env)
        case "duplicate":
            return _handle_duplicate(cmd, env)
        case "sort":
            return _handle_sort(cmd, env)
        case "join":
            return _handle_join(cmd, env)
        case "union":
            return _handle_union(cmd, env)
        case "groupby":
            return _handle_groupby(cmd, env)

        ### ROW VERBS ###

        case "keep":
            return _handle_keep(cmd, env)
        case "drop":
            return _handle_drop(cmd, env)
        case "rename":
            return _handle_rename(cmd, env)
        case "alias":
            return _handle_alias(cmd, env)
        case "derive":
            return _handle_derive(cmd, env)
        case "select":
            return _handle_select(cmd, env)
        case "first":
            return _handle_first(cmd, env)
        case "last":
            return _handle_last(cmd, env)
        case "sample":
            return _handle_sample(cmd, env)
        case "cast":
            return _handle_cast(cmd, env)

        ### MISCELLANEOUS ###

        case "show":
            return _handle_show(cmd, env)
        case "history":
            return _handle_history(cmd, env)
        case "inspect":
            return _handle_inspect(cmd, env)

        ### STACK OPERATIONS ###

        case "clear":
            return _handle_clear(cmd, env)
        case "pop":
            return _handle_pop(cmd, env)
        case "swap":
            return _handle_swap(cmd, env)
        case "reverse":
            return _handle_reverse(cmd, env)
        case "rotate":
            return _handle_rotate(cmd, env)

        ### UNRECOGNIZED VERB ###

        case _:
            print("Unrecognized command: ", verb)
            print("Note: File names need to be enclosed in quotes.")
            return ERROR


def repl_mode(env: Program):
    """Interpret T commands in a REPL"""

    count = 0
    is_rooted = False  # Has a table been read in in some fashion?

    # Setup 1MB history log

    logFile = "logs/history.log"
    log_formatter = logging.Formatter("%(message)s")
    log_handler = RotatingFileHandler(
        logFile,
        mode="a",
        maxBytes=1 * 1024 * 1024,
        backupCount=2,
        encoding=None,
        delay=0,
    )
    log_handler.setFormatter(log_formatter)
    log_handler.setLevel(logging.INFO)

    app_log = logging.getLogger("root")
    app_log.setLevel(logging.INFO)

    app_log.addHandler(log_handler)
    app_log.info("000")

    r = Reader()
    prompt = ">>> "

    while True:
        try:
            current_cols = env.cols if env.cols else []
            input_fn = make_input_fn(is_rooted, current_cols)

            line = input_fn(prompt)
            state = r.next(line)

            if state == ReadState.BLANK:
                continue

            if state == ReadState.CONTINUED:
                prompt = "... "
                continue

            if r.commands[0].lower() == "quit()":
                break

            prompt = ">>> "

            print()

            for command in r.commands:
                result = interpret(command, env)

                count += 1
                app_log.info(str(count).zfill(3) + " " + command)

                if result in FILE_IN_VERBS:
                    is_rooted = True

            print()

        except Exception as e:
            print("Exception while processing command: ", e)


def run_mode(rel_path: str, env: Program):
    """Run a T script, i.e., interpret a file of T commands"""

    if env.src:
        rel_path = env.src + rel_path

    result = None
    exit = False
    last_verb = None

    fs = FileSpec(rel_path)
    abs_path = fs.abs_path
    with open(abs_path, "r") as f:
        r = Reader()
        line = f.readline()

        while line:
            state = r.next(line)

            if state == ReadState.COMMANDS:
                for command in r.commands:
                    result = interpret(command, env)

                    if result == ERROR:
                        exit = True
                        break

                    if result != "comment":
                        last_verb = result

            if result and result == ERROR:
                exit = True
                break

            # Read the next line -or- EOF
            line = f.readline()

        # Check for unclosed block comments or multi-line statements
        if r.continued or r.in_block:
            exit = True

    if exit:
        print("Exiting program due to errors.")

    return exit, last_verb


class DebugMode:
    """Run/debug a 'T' script loaded in memory"""

    def __init__(self, env, lines):
        self.env = env
        self.reader = Reader()
        self.lines = lines
        self.pc = 0
        # TODO - Add breakpoints, etc.

    def add_line(self, line):
        self.lines.append(line)

    def insert_line(self, line, index):
        self.lines.insert(index, line)
        self.reset()

    def reset(self):
        self.reader = Reader()
        self.pc = 0

    def run(self, step=False):
        result = None

        end = self.pc + 1 if step else len(self.lines)

        for line in self.lines[self.pc : end]:
            state = self.reader.next(line)
            self.pc += 1

            if state == ReadState.COMMANDS:
                for command in self.reader.commands:
                    result = interpret(command, self.env)

                    if result == ERROR:
                        raise Exception("Error in T script.")

        # Check for unclosed block comments or multi-line statements
        if self.reader.continued or self.reader.in_block:
            raise Exception("Unexpected end of script.")


### COMMAND HANDLERS ###


def _handle_from(cmd: Command, env: Program) -> str:
    print(f"{cmd.verb} {cmd.args}")

    return cmd.verb


def _handle_write(cmd: Command, env: Program) -> str:
    print(f"{cmd.verb} {cmd.args}")

    return cmd.verb


def _handle_duplicate(cmd: Command, env: Program) -> str:
    print(f"{cmd.verb} {cmd.args}")

    return cmd.verb


def _handle_sort(cmd: Command, env: Program) -> str:
    print(f"{cmd.verb} {cmd.args}")

    return cmd.verb


def _handle_join(cmd: Command, env: Program) -> str:
    print(f"{cmd.verb} {cmd.args}")

    return cmd.verb


def _handle_union(cmd: Command, env: Program) -> str:
    print(f"{cmd.verb} {cmd.args}")

    return cmd.verb


def _handle_groupby(cmd: Command, env: Program) -> str:
    print(f"{cmd.verb} {cmd.args}")

    return cmd.verb


def _handle_keep(cmd: Command, env: Program) -> str:
    print(f"{cmd.verb} {cmd.args}")

    return cmd.verb


def _handle_drop(cmd: Command, env: Program) -> str:
    print(f"{cmd.verb} {cmd.args}")

    return cmd.verb


def _handle_rename(cmd: Command, env: Program) -> str:
    print(f"{cmd.verb} {cmd.args}")

    return cmd.verb


def _handle_alias(cmd: Command, env: Program) -> str:
    print(f"{cmd.verb} {cmd.args}")

    return cmd.verb


def _handle_derive(cmd: Command, env: Program) -> str:
    print(f"{cmd.verb} {cmd.args}")

    return cmd.verb


def _handle_select(cmd: Command, env: Program) -> str:
    print(f"{cmd.verb} {cmd.args}")

    return cmd.verb


def _handle_first(cmd: Command, env: Program) -> str:
    print(f"{cmd.verb} {cmd.args}")

    return cmd.verb


def _handle_last(cmd: Command, env: Program) -> str:
    print(f"{cmd.verb} {cmd.args}")

    return cmd.verb


def _handle_sample(cmd: Command, env: Program) -> str:
    print(f"{cmd.verb} {cmd.args}")

    return cmd.verb


def _handle_cast(cmd: Command, env: Program) -> str:
    print(f"{cmd.verb} {cmd.args}")

    return cmd.verb


def _handle_show(cmd: Command, env: Program) -> str:
    print(f"{cmd.verb} {cmd.args}")

    return cmd.verb


def _handle_history(cmd: Command, env: Program) -> str:
    print(f"{cmd.verb} {cmd.args}")

    return cmd.verb


def _handle_inspect(cmd: Command, env: Program) -> str:
    print(f"{cmd.verb} {cmd.args}")

    return cmd.verb


def _handle_clear(cmd: Command, env: Program) -> str:
    print(f"{cmd.verb} {cmd.args}")

    return cmd.verb


def _handle_pop(cmd: Command, env: Program) -> str:
    print(f"{cmd.verb} {cmd.args}")

    return cmd.verb


def _handle_swap(cmd: Command, env: Program) -> str:
    print(f"{cmd.verb} {cmd.args}")

    return cmd.verb


def _handle_reverse(cmd: Command, env: Program) -> str:
    print(f"{cmd.verb} {cmd.args}")

    return cmd.verb


def _handle_rotate(cmd: Command, env: Program) -> str:
    print(f"{cmd.verb} {cmd.args}")

    return cmd.verb


### HELPERS ###


def print_parsing_exception(verb, e):
    print("Exception handling '{0}' commmand: {1}".format(verb, e))


### END ###
