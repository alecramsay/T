# lang.py
#!/usr/bin/env python3

"""
INTERPRETER AND REPL, RUN SCRIPT, & DEBUGGER MODES
"""

import libcst as cst
import logging
from logging.handlers import RotatingFileHandler

# TODO - Limit these imports to what's needed
from .commands import Namespace, Command
from .program import Program
from .reader import Reader, ReadState, FILE_IN_VERBS, make_input_fn

# from .expressions import *
# from .readwrite import *


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
            print(f"from_ {cmd.args}")

        ### TABLE VERBS ###

        case "write":
            print(f"write {cmd.args}")

        case "duplicate":
            print(f"duplicate {cmd.args}")

        case "sort":
            print(f"sort {cmd.args}")

        case "join":
            print(f"join {cmd.args}")

        case "union":
            print(f"union {cmd.args}")

        case "groupby":
            print(f"groupby {cmd.args}")

        ### ROW VERBS ###

        case "keep":
            print(f"keep {cmd.args}")

        case "drop":
            print(f"drop {cmd.args}")

        case "rename":
            print(f"rename {cmd.args}")

        case "alias":
            print(f"alias {cmd.args}")

        case "derive":
            print(f"derive {cmd.args}")

        case "select":
            print(f"select {cmd.args}")

        case "first":
            print(f"first {cmd.args}")

        case "last":
            print(f"last {cmd.args}")

        case "sample":
            print(f"sample {cmd.args}")

        case "cast":
            print(f"cast {cmd.args}")

        ### MISCELLANEOUS ###

        case "show":
            print(f"show {cmd.args}")

        case "history":
            print(f"history {cmd.args}")

        case "inspect":
            print(f"inspect {cmd.args}")

        ### STACK OPERATIONS ###

        case "clear":
            print(f"clear {cmd.args}")

        case "pop":
            print(f"pop {cmd.args}")

        case "swap":
            print(f"swap {cmd.args}")

        case "reverse":
            print(f"reverse {cmd.args}")

        case "rotate":
            print(f"rotate {cmd.args}")

        # TODO - Else?

    return verb  # TODO


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


def print_parsing_exception(verb, e):
    print("Exception handling '{0}' commmand: {1}".format(verb, e))


### END ###
