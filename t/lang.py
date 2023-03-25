# lang.py
#!/usr/bin/env python3

"""
INTERPRETER AND REPL, RUN SCRIPT, & DEBUGGER MODES
"""

import logging
from logging.handlers import RotatingFileHandler
from typing import Callable, Literal, Optional

from .commands import Command, Namespace, validate_nargs, could_be_filename, isidpair
from .program import Program
from .reader import Reader, ReadState, FILE_IN_VERBS, make_input_fn
from .readwrite import FileSpec
from .utils import split_col_spec_string

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
        case "show":
            return _handle_show(cmd, env)
        case "history":
            return _handle_history(cmd, env)
        case "inspect":
            return _handle_inspect(cmd, env)
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
        case _:
            print("Unrecognized command: ", verb)
            print("Note: File names need to be enclosed in quotes.")
            return ERROR


def repl_mode(env: Program) -> None:
    """Interpret T commands in a REPL"""

    count: int = 0
    is_rooted: bool = False  # Has a table been read in in some fashion?

    # Setup 1MB history log

    logFile: str = env.log
    with open(logFile, "a+"):
        pass  # Touch the file to create it if it doesn't exist
    # logFile = "logs/history.log"
    log_formatter = logging.Formatter("%(message)s")
    log_handler = RotatingFileHandler(
        logFile,
        mode="a",
        maxBytes=1 * 1024 * 1024,
        backupCount=2,
        encoding=None,
        delay=False,
    )
    log_handler.setFormatter(log_formatter)
    log_handler.setLevel(logging.INFO)

    app_log: logging.Logger = logging.getLogger("root")
    app_log.setLevel(logging.INFO)

    app_log.addHandler(log_handler)
    app_log.info("000")

    r: Reader = Reader()
    prompt = ">>> "

    while True:
        try:
            current_cols: list[str] = env.cols if env.cols else list()
            input_fn: Callable[..., str] = make_input_fn(is_rooted, current_cols)

            line: str = input_fn(prompt)
            state: Literal[
                ReadState.BLANK, ReadState.COMMANDS, ReadState.CONTINUED
            ] = r.next(line)

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
                result: str = interpret(command, env)

                count += 1
                app_log.info(str(count).zfill(3) + " " + command)

                if result in FILE_IN_VERBS:
                    is_rooted = True

            print()

        except Exception as e:
            print("Exception while processing command: ", e)


def run_mode(rel_path: str, env: Program) -> tuple[bool, str | None]:
    """Run a T script, i.e., interpret a file of T commands"""

    if env.src:
        rel_path = env.src + rel_path

    result: Optional[str] = None
    exit: bool = False
    last_verb: Optional[str] = None

    fs: FileSpec = FileSpec(rel_path)
    abs_path: str = fs.abs_path
    with open(abs_path, "r") as f:
        r: Reader = Reader()
        line: str = f.readline()

        while line:
            state: Literal[
                ReadState.BLANK, ReadState.COMMANDS, ReadState.CONTINUED
            ] = r.next(line)

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

    env: Program
    reader: Reader
    lines: list[str]
    pc: int

    def __init__(self, env: Program, lines: list[str]):
        self.env = env
        self.reader = Reader()
        self.lines = lines
        self.pc = 0
        # TODO - Add breakpoints, etc.

    def add_line(self, line: str):
        self.lines.append(line)

    def insert_line(self, line: str, index: int):
        self.lines.insert(index, line)
        self.reset()

    def reset(self):
        self.reader = Reader()
        self.pc = 0

    def run(self, step: bool = False):
        end: int = self.pc + 1 if step else len(self.lines)

        for line in self.lines[self.pc : end]:
            state: Literal[
                ReadState.BLANK, ReadState.COMMANDS, ReadState.CONTINUED
            ] = self.reader.next(line)
            self.pc += 1

            if state == ReadState.COMMANDS:
                for command in self.reader.commands:
                    result: str = interpret(command, self.env)

                    if result == ERROR:
                        raise Exception("Error in T script.")

        # Check for unclosed block comments or multi-line statements
        if self.reader.continued or self.reader.in_block:
            raise Exception("Unexpected end of script.")


### COMMAND HANDLERS ###


def _handle_from(cmd: Command, env: Program) -> str:
    """Execute a 'from' command

    Examples:

    >>> # Read a table from a CSV file
    >>> from('2020_census_NC.csv')

    >>> # Execute a T script with arguments
    >>> from('precincts.t', paf='2020_precinct_assignments_NC.csv', census='2020_census_NC.csv', elections='2020_election_NC.csv')

    """

    verb: str = "from"  # HACK - cmd.verb has 'from_'

    try:
        validate_nargs(verb, cmd.n_pos, 1, most=1)  # There is one positional arg

        name: str = cmd.positional_args[0].strip("'")
        could_be_filename(name)
        # It could be a filename

        fs = FileSpec(name)
        match fs.extension:
            case ".t":  # Run a T script
                # TODO - Verify this code path
                call_args = cmd.keyword_args if cmd.n_kw > 0 else dict()
                env.call_stack.push(Namespace(call_args))

                run_mode(fs.rel_path, env)

                env.call_stack.pop()
                env._display_table()

            case _:  # Read table from a file
                validate_nargs(
                    verb, cmd.n_kw, 0, most=0, arg_type="keyword"
                )  # There are no keyword args
                env.read(fs.rel_path)
                env._display_table()

    except Exception as e:
        print_parsing_exception(verb, e)
        return ERROR

    return cmd.verb


# Table verbs


def _handle_write(cmd: Command, env: Program) -> str:
    """Execute a 'write' command

    Examples:

    >>> # Write a table to a CSV file
    >>> write('2020_census_NC.csv')

    >>> # Write a table to a JSON file
    >>> write('2020_census_NC.json', format=JSON)
    """

    try:
        # There is one positional args
        validate_nargs(cmd.verb, cmd.n_pos, 1, most=1)
        # And at most one keyword arg
        validate_nargs(cmd.verb, cmd.n_kw, 0, most=1, arg_type="keyword")

        filename: str = cmd.positional_args[0].strip("'")
        format: Optional[str] = None if cmd.n_kw == 0 else cmd.keyword_args["format"]

        env.write(filename, format)

    except Exception as e:
        print_parsing_exception(cmd.verb, e)
        return ERROR

    return cmd.verb


def _handle_duplicate(cmd: Command, env: Program) -> str:
    """Execute a 'duplicate' command

    Example:

    >>> duplicate()
    """

    try:
        # There are no positional args
        validate_nargs(cmd.verb, cmd.n_pos, 0)
        # And no keyword args
        validate_nargs(cmd.verb, cmd.n_kw, 0, most=0, arg_type="keyword")

        env.duplicate()

    except Exception as e:
        print_parsing_exception(cmd.verb, e)
        return ERROR

    return cmd.verb


def _handle_sort(cmd: Command, env: Program) -> str:
    """Execute a 'sort' command

    Examples:

    >>> sort((Total, DESC))
    """

    try:
        # There are one or more positional args
        validate_nargs(cmd.verb, cmd.n_pos, 1)
        # But no keyword args
        validate_nargs(cmd.verb, cmd.n_kw, 0, most=0, arg_type="keyword")

        # All positional args are pairs of valid identifiers
        # HACK - ASC and DESC, if given, are valid identifiers
        for pair in cmd.positional_args:
            if not isidpair(pair):
                raise Exception(f"Invalid sort argument: {pair}")

        col_specs: list = [split_col_spec_string(arg) for arg in cmd.positional_args]
        env.sort(col_specs)

    except Exception as e:
        print_parsing_exception(cmd.verb, e)
        return ERROR

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


# Row verbs


def _handle_keep(cmd: Command, env: Program) -> str:
    """Execute a 'keep' command

    Example:

    >>> keep(GEOID20, Tot_2020_tot)
    """

    try:
        # There are one or more positional args
        validate_nargs(cmd.verb, cmd.n_pos, 1)
        # But no keyword args
        validate_nargs(cmd.verb, cmd.n_kw, 0, most=0, arg_type="keyword")

        env.keep(cmd.positional_args)

    except Exception as e:
        print_parsing_exception(cmd.verb, e)
        return ERROR

    return cmd.verb


def _handle_drop(cmd: Command, env: Program) -> str:
    """Execute a 'drop' command

    Example:

    >>> drop(AsnC_2010_tot)
    """

    try:
        # There are one or more positional args
        validate_nargs(cmd.verb, cmd.n_pos, 1)
        # But no keyword args
        validate_nargs(cmd.verb, cmd.n_kw, 0, most=0, arg_type="keyword")

        env.drop(cmd.positional_args)

    except Exception as e:
        print_parsing_exception(cmd.verb, e)
        return ERROR

    return cmd.verb


def _handle_rename(cmd: Command, env: Program) -> str:
    """Execute a 'rename' command

    Example:

    >>> rename((Tot_2020_tot, Total))
    """

    try:
        # There are one or more positional args
        validate_nargs(cmd.verb, cmd.n_pos, 1)
        # But no keyword args
        validate_nargs(cmd.verb, cmd.n_kw, 0, most=0, arg_type="keyword")

        # All positional args are pairs of valid identifiers
        for pair in cmd.positional_args:
            if not isidpair(pair):
                raise Exception(f"Invalid rename argument: {pair}")

        col_specs: list = [split_col_spec_string(arg) for arg in cmd.positional_args]
        env.rename(col_specs)

    except Exception as e:
        print_parsing_exception(cmd.verb, e)
        return ERROR

    return cmd.verb


def _handle_alias(cmd: Command, env: Program) -> str:
    """Execute an 'alias' command

    Example:

    >>> alias((Tot_2020_tot, Total))
    """

    try:
        # There are one or more positional args
        validate_nargs(cmd.verb, cmd.n_pos, 1)
        # But no keyword args
        validate_nargs(cmd.verb, cmd.n_kw, 0, most=0, arg_type="keyword")

        # All positional args are pairs of valid identifiers
        for pair in cmd.positional_args:
            if not isidpair(pair):
                raise Exception(f"Invalid alias argument: {pair}")

        col_specs: list = [split_col_spec_string(arg) for arg in cmd.positional_args]
        env.alias(col_specs)

    except Exception as e:
        print_parsing_exception(cmd.verb, e)
        return ERROR

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


# Info verbs


def _handle_show(cmd: Command, env: Program) -> str:
    """Execute a 'show' command

    Example:

    >>> show()
    """

    try:
        # There are zero or one positional args
        validate_nargs(cmd.verb, cmd.n_pos, 0, most=1)
        # And no keyword args
        validate_nargs(cmd.verb, cmd.n_kw, 0, most=0, arg_type="keyword")

        n: Optional[int] = None if cmd.n_pos == 0 else int(cmd.positional_args[0])

        env.show(n)

    except Exception as e:
        print_parsing_exception(cmd.verb, e)
        return ERROR

    return cmd.verb


def _handle_history(cmd: Command, env: Program) -> str:
    """Execute a 'history' command

    Example:

    >>> history()
    """

    try:
        # There are zero or one positional args
        validate_nargs(cmd.verb, cmd.n_pos, 0, most=1)
        # And no keyword args
        validate_nargs(cmd.verb, cmd.n_kw, 0, most=0, arg_type="keyword")

        n: Optional[int] = None if cmd.n_pos == 0 else int(cmd.positional_args[0])

        env.history(n)

    except Exception as e:
        print_parsing_exception(cmd.verb, e)
        return ERROR

    return cmd.verb


def _handle_inspect(cmd: Command, env: Program) -> str:
    print(f"{cmd.verb} {cmd.args}")

    return cmd.verb


# Stack operations


def _handle_clear(cmd: Command, env: Program) -> str:
    """Execute a 'clear' command

    Example:

    >>> clear()
    """

    try:
        # There are no positional args
        validate_nargs(cmd.verb, cmd.n_pos, 0)
        # And no keyword args
        validate_nargs(cmd.verb, cmd.n_kw, 0, most=0, arg_type="keyword")

        env.clear()

    except Exception as e:
        print_parsing_exception(cmd.verb, e)
        return ERROR

    return cmd.verb


def _handle_pop(cmd: Command, env: Program) -> str:
    """Execute a 'pop' command

    Example:

    >>> pop()
    """

    try:
        # There are no positional args
        validate_nargs(cmd.verb, cmd.n_pos, 0)
        # And no keyword args
        validate_nargs(cmd.verb, cmd.n_kw, 0, most=0, arg_type="keyword")

        env.pop()

    except Exception as e:
        print_parsing_exception(cmd.verb, e)
        return ERROR

    return cmd.verb


def _handle_swap(cmd: Command, env: Program) -> str:
    """Execute a 'swap' command

    Example:

    >>> swap()
    """

    try:
        # There are no positional args
        validate_nargs(cmd.verb, cmd.n_pos, 0)
        # And no keyword args
        validate_nargs(cmd.verb, cmd.n_kw, 0, most=0, arg_type="keyword")

        env.swap()

    except Exception as e:
        print_parsing_exception(cmd.verb, e)
        return ERROR

    return cmd.verb


def _handle_reverse(cmd: Command, env: Program) -> str:
    """Execute a 'reverse' command

    Example:

    >>> reverse()
    """

    try:
        # There are no positional args
        validate_nargs(cmd.verb, cmd.n_pos, 0)
        # And no keyword args
        validate_nargs(cmd.verb, cmd.n_kw, 0, most=0, arg_type="keyword")

        env.reverse()

    except Exception as e:
        print_parsing_exception(cmd.verb, e)
        return ERROR

    return cmd.verb


def _handle_rotate(cmd: Command, env: Program) -> str:
    """Execute a 'rotate' command

    Example:

    >>> rotate()
    """

    try:
        # There are no positional args
        validate_nargs(cmd.verb, cmd.n_pos, 0)
        # And no keyword args
        validate_nargs(cmd.verb, cmd.n_kw, 0, most=0, arg_type="keyword")

        env.rotate()

    except Exception as e:
        print_parsing_exception(cmd.verb, e)
        return ERROR

    return cmd.verb


### HELPERS ###


def print_parsing_exception(verb, e):
    print("Exception handling '{0}' commmand: {1}".format(verb, e))


### END ###
