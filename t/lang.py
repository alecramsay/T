# lang.py
#!/usr/bin/env python3

"""
INTERPRETER AND REPL, RUN SCRIPT, & DEBUGGER MODES
"""

import libcst as cst
import logging
from logging.handlers import RotatingFileHandler

# TODO - Delete this & uninstall PyParsing
# from pyparsing import (
#     ParserElement,
#     ParseResults,
#     Suppress,
#     Word,
#     identchars,
#     identbodychars,
#     nested_expr,
# )

# TODO - Limit these imports to what's needed
from .program import *
from .reader import *
from .expressions import *
from .readwrite import *
from .commands import Namespace, Command

ERROR: str = "_error_"


def interpret(command, env) -> str:
    """Interpret one T command"""

    ### BIND VARIABLES ###

    try:
        command = bind_command_args(command, env.call_stack.first())
    except Exception as e:
        print("Exception binding command args: ", e)
        return ERROR

    ### RE-WRITE AGGREGATE FUNCTION REFERENCES ###

    try:
        if not env.table_stack.isempty():
            names = env.table_stack.first().col_names()
            command = rewrite_agg_refs(command, names)  # TODO - Not implemented
    except Exception as e:
        print("Exception rewriting aggregate function references: ", e)
        return ERROR

    ### PARSE & RUN VERBS ###

    try:
        tree = cst.parse_expression(command)
        # command parses as an expression

        try:
            if isinstance(tree, cst.Call):
                nargs = len(tree.args)
                verb = tree.func.value.lower()

                ### FROM ###

                # HACK - 'from' is a Python keyword; 'from_' substituted on the fly
                if verb == "from_":
                    verb = "from"
                    try:
                        could_be_filename(tree.args[0])

                        fs = FileSpec(tree.args[0].value.value.strip("'"))
                        name = fs.name
                        rel_path = fs.rel_path
                        # REVIEW - Why do I need this? (Why) only for 'read'?
                        rel_path = rel_path.strip("'")

                        if fs.extension == ".t":
                            # Run a T script
                            isNargsOK(verb, nargs, 1)
                            call_args = (
                                parse_call_args(tree.args) if (nargs > 1) else {}
                            )
                            env.call_stack.push(Namespace(call_args))

                            run_mode(rel_path, env)

                            env.call_stack.pop()
                            env._display_table()

                        else:
                            # Read a file
                            isNargsOK(verb, nargs, 1, 2)

                            type_fns = None
                            if nargs == 2:
                                # Second positional arg
                                types = tree.args[1].value
                                if not isinstance(types, cst.List):
                                    raise Exception(
                                        "The 'from' command takes an optional list of types as the second argument."
                                    )

                                types = [x.value.value for x in types.elements]
                                type_fns = [get_builtin_fn(x) for x in types]

                            env.read(rel_path, type_fns)

                            env._display_table()

                        return verb

                    except Exception as e:
                        print_parsing_exception(verb, e)
                        return ERROR

                ### TABLE VERBS ###

                if verb == "write":
                    try:
                        isNargsOK(verb, nargs, 0, 2)
                        positional, keywords = parse_args(tree.args)

                        format = keywords["format"] if ("format" in keywords) else None

                        nkeys = len(list(keywords.keys()))
                        other = (
                            True
                            if (nkeys > 1) or ((nkeys == 1) and (format is None))
                            else False
                        )
                        if other:
                            print(
                                "Unrecognized arguments: the 'write' command takes an optional format= keyword."
                            )
                            return ERROR

                        rel_path = None
                        if len(positional) > 1:
                            could_be_filename(tree.args[0])
                            rel_path = tree.args[0].value.value.strip("'")

                        env.write(rel_path, format)
                        return verb

                    except Exception as e:
                        print_parsing_exception(verb, e)
                        return ERROR

                if verb == "duplicate":
                    isNargsOK(verb, nargs, 0, 0)
                    env.duplicate()
                    return verb

                if verb == "sort":
                    try:
                        isNargsOK(verb, nargs, 1, 1)
                        col_spec = extract_sort_args(tree)
                        env.sort([col_spec])
                        return verb

                    except Exception as e:
                        print_parsing_exception(verb, e)
                        return ERROR

                if verb == "join":
                    try:
                        isNargsOK(verb, nargs, 0, 3)
                        positional, keywords = parse_args(tree.args)

                        from_col = None if len(positional) == 0 else positional[0]
                        to_col = None if len(positional) < 2 else positional[1]

                        prefix = keywords["prefix"] if ("prefix" in keywords) else None

                        env.join(from_col, to_col, prefix=prefix)
                        return verb

                    except Exception as e:
                        print_parsing_exception(verb, e)
                        return ERROR

                if verb == "union":
                    try:
                        isNargsOK(verb, nargs, 0, 0)
                        env.union()
                        return verb

                    except Exception as e:
                        print_parsing_exception(verb, e)
                        return ERROR

                if verb == "pivot":
                    try:
                        isNargsOK(verb, nargs, 0, 2)
                        positional, keywords = parse_args(tree.args)

                        if nargs > 0:
                            are_valid_keywords({"by", "only"}, keywords)

                        by = keywords["by"] if ("by" in keywords) else None
                        only = keywords["only"] if ("only" in keywords) else None

                        env.pivot(by=by, only=only)
                        return verb

                    except Exception as e:
                        print_parsing_exception(verb, e)
                        return ERROR

                ### ROW VERBS ###

                if verb == "keep":
                    try:
                        cols = extract_col_refs(verb, nargs, tree)
                        env.keep(cols)
                        return verb

                    except Exception as e:
                        print_parsing_exception(verb, e)
                        return ERROR

                if verb == "drop":
                    try:
                        cols = extract_col_refs(verb, nargs, tree)
                        env.drop(cols)
                        return verb

                    except Exception as e:
                        print_parsing_exception(verb, e)
                        return ERROR

                if verb == "rename":
                    try:
                        col_specs = extract_col_specs(verb, nargs, tree)
                        env.rename(col_specs)
                        return verb

                    except Exception as e:
                        print_parsing_exception(verb, e)
                        return ERROR

                if verb == "alias":
                    try:
                        col_specs = extract_col_specs(verb, nargs, tree)
                        env.alias(col_specs)
                        return verb

                    except Exception as e:
                        print_parsing_exception(verb, e)
                        return ERROR

                if verb == "derive":
                    try:
                        isNargsOK(verb, nargs, 2, 3)

                        if not isinstance(tree.args[0].value, cst.Name):
                            print(
                                "'{0}' command requires a new column name.".format(verb)
                            )
                            return ERROR

                        name = tree.args[0].value.value

                        formula = (
                            extract_expr(verb, command, ",", ")")
                            if nargs == 2
                            else extract_expr(verb, command, ",", ",")
                        )

                        data_type = (
                            None
                            if nargs == 2
                            else get_builtin_fn(tree.args[2].value.value)
                        )

                        env.derive(name, formula, data_type)
                        return verb

                    except Exception as e:
                        print_parsing_exception(verb, e)
                        return ERROR

                if verb == "select":
                    try:
                        expr = extract_expr(verb, command, "(", ")")
                        env.select(expr)
                        return verb

                    except Exception as e:
                        print_parsing_exception(verb, e)
                        return ERROR

                if verb == "first":
                    try:
                        n, pct = extract_n_and_pct(verb, nargs, tree)
                        env.first(n, pct)
                        return verb

                    except Exception as e:
                        print_parsing_exception(verb, e)
                        return ERROR

                if verb == "last":
                    try:
                        n, pct = extract_n_and_pct(verb, nargs, tree)
                        env.last(n, pct)
                        return verb

                    except Exception as e:
                        print_parsing_exception(verb, e)
                        return ERROR

                if verb == "random":
                    try:
                        n, pct = extract_n_and_pct(verb, nargs, tree)
                        env.random(n, pct)
                        return verb

                    except Exception as e:
                        print_parsing_exception(verb, e)
                        return ERROR

                if verb == "cast":
                    try:
                        isNargsOK(verb, nargs, 2, 2)
                        isvalidname(verb, tree.args[0], 1)
                        isvalidname(verb, tree.args[1], 2)

                        col = tree.args[0].value.value
                        type_str = tree.args[1].value.value
                        type_fn = get_builtin_fn(type_str)

                        env.cast(col, type_fn)
                        return verb

                    except Exception as e:
                        print_parsing_exception(verb, e)
                        return ERROR

                ### MISCELLANEOUS ###

                if verb == "show":
                    try:
                        n = extract_n(verb, nargs, tree)
                        print()
                        env.show(n)
                        return verb

                    except Exception as e:
                        print_parsing_exception(verb, e)
                        return ERROR

                if verb == "history":
                    try:
                        n = extract_n(verb, nargs, tree)
                        print()
                        env.history(n)
                        return verb

                    except Exception as e:
                        print_parsing_exception(verb, e)
                        return ERROR

                if verb == "inspect":
                    try:
                        isNargsOK(verb, nargs, 0, 1)
                        filter = None
                        if nargs == 1:
                            if not isinstance(tree.args[0].value, cst.SimpleString):
                                raise Exception(
                                    "Column name filters must be simple strings."
                                )
                            filter = tree.args[0].value.value.strip("'")
                        env.inspect(filter)
                        return verb

                    except Exception as e:
                        print_parsing_exception(verb, e)
                        return ERROR

                """
                LEGACY
                if verb == "echo":
                    try:
                        isNargsOK(verb, nargs, 1)

                        # Simply pass through what's between the echo parens.
                        prop = extract_expr(verb, command, "(", ")")
                        env.echo(prop)
                        return verb

                    except Exception as e:
                        print_parsing_exception(verb, e)
                        return ERROR
                """

                ### STACK OPERATIONS ###

                if verb == "clear":
                    isNargsOK(verb, nargs, 0, 0)
                    env.clear()
                    return verb

                if verb == "pop":
                    isNargsOK(verb, nargs, 0, 0)
                    env.pop()
                    return verb

                if verb == "swap":
                    isNargsOK(verb, nargs, 0, 0)
                    env.swap()
                    return verb

                if verb == "reverse":
                    isNargsOK(verb, nargs, 0, 0)
                    env.reverse()
                    return verb

                if verb == "rotate":
                    isNargsOK(verb, nargs, 0, 0)
                    env.rotate()
                    return verb

                print("Unrecognized expression.")
                return ERROR

        except Exception as e:
            print("Exception processing expression: ", command)
            print(e)
            return ERROR

    except Exception as e:
        print("Unrecognized command.")
        print("Note: File names need to be enclosed in quotes.")
        return ERROR


def repl_mode(env):
    """
    Interpret T commands in a REPL
    """

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


def run_mode(rel_path, env):
    """
    Run a T script, i.e., interpret a file of T commands
    """

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
    """
    Run/debug a 'T' script loaded in memory
    """

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


### PARSER HELPERS ###


def parse_args(args) -> tuple[list[str], dict[str, Any]]:
    positional: list[str] = []
    keywords: dict[str, Any] = {}

    for arg in args:
        if not isinstance(arg.value, cst.Name):
            raise Exception("Unknown argument type")

        v = arg.value.value
        if iskeywordarg_cst(arg):
            k = arg.keyword.value
            keywords[k] = v

        else:
            positional.append(v)

    return positional, keywords


def isNargsOK(verb, n, least, most=None):
    if most == 0 and n > 0:
        raise Exception("'{0}' command doesn't take any arguments.".format(verb))

    if n < least:
        raise Exception("Too few arguments for '{0}' command.".format(verb))

    if most and (n > most):
        raise Exception("Too many arguments for '{0}' command.".format(verb))

    return True


def iskeywordarg_cst(arg):
    return True if arg.keyword else False


def parse_keyword_arg(arg):
    return arg.keyword.value, arg.value.value


def parse_call_args(args):
    d = {}

    for x in args[1 : len(args)]:
        k, v = parse_keyword_arg(x)
        d[k] = v
        # d[k] = v.strip("'")

    return d


def extract_expr(verb, command, l_char, r_char):
    """
    For 'derive' and 'select'
    """
    # HACK: The expression is between these outside delimiting chars.
    left = command.find(l_char)
    right = command.rfind(r_char)

    if left == -1 or right == -1:
        raise Exception("Unable to extract expression from '{0}' command.".format(verb))

    expr = command[left + 1 : right].strip()
    _ = cst.parse_expression(expr)

    # If here, expr parses as a valid Python expression
    return expr


def extract_col_refs(verb, nargs, tree):
    """
    For 'keep' and 'drop'
    """
    if nargs < 1:
        raise Exception("'{0}' command takes one or more columns.".format(verb))

    if not all([isinstance(x.value, cst.Name) for x in tree.args]):
        raise Exception("Columns must be names.")

    cols = [x.value.value for x in tree.args]

    return cols


def extract_col_specs(verb, nargs, tree):
    """
    For 'rename' and 'alias'
    """
    if nargs < 1:
        raise Exception(
            "'{0}' takes one or more tuples of old column name, new column name.".format(
                verb
            )
        )

    if not all([isinstance(x.value, cst.Tuple) for x in tree.args]):
        raise Exception("The arguments to the '{0}' command must be tuples of names.")

    for x in tree.args:
        if not isinstance(x.value.elements[0].value, cst.Name) or not isinstance(
            x.value.elements[1].value, cst.Name
        ):
            raise Exception("The '{0}' command requires tuples of names.".format(verb))

    col_specs = [
        (
            x.value.elements[0].value.value,
            x.value.elements[1].value.value,
        )
        for x in tree.args
    ]

    return col_specs


def extract_n_and_pct(verb, nargs, tree):
    """
    For 'first', 'last', & 'random'
    """

    isNargsOK(verb, nargs, 1, 2)

    if not isinstance(tree.args[0].value, cst.Integer):
        raise Exception("'{0}' command requires a number of rows.".format(verb))

    n = int(tree.args[0].value.value)
    # Interpret *any* second arg as indicating % vs. #
    pct = None if nargs == 1 else "*"

    return n, pct


def extract_n(verb, nargs, tree):
    """
    For 'show' and 'history'
    """

    isNargsOK(verb, nargs, 0, 1)

    if nargs == 0:
        return None

    if not isinstance(tree.args[0].value, cst.Integer):
        units = "rows" if verb == "show" else "commands"
        raise Exception(
            "'{0}' command takes an optional number of {1}.".format(verb, units)
        )

    n = int(tree.args[0].value.value)

    return n


def could_be_filename(arg):
    """
    For 'read' and 'write'
    """

    if not isinstance(arg.value, cst.SimpleString):
        raise Exception("Filenames must be simple strings.")

    return True


def extract_sort_args(tree):
    """
    For 'sort'
    """
    # Just a column name
    if isinstance(tree.args[0].value, cst.Name):
        col_spec = tree.args[0].value.value

        return col_spec

    # A column name and sort order (ASC or DESC)
    if isinstance(tree.args[0].value, cst.Tuple):
        col_spec = (
            tree.args[0].value.elements[0].value.value,
            tree.args[0].value.elements[1].value.value,
        )

        return col_spec

    raise Exception(
        "Unrecognized argument: the 'sort' command takes a single column name or one tuple consisting of a column name & sort order (ASC, DESC)."
    )


def are_valid_keywords(valid, keywords):
    """
    For 'aggregate'
    """

    diff = set(keywords.keys()) - valid
    if diff:
        raise Exception("Invalid keys: ", diff)

    return True


def isvalidname(verb, arg, pos):
    """
    For 'cast'
    """

    if not isinstance(arg.value, cst.Name):
        raise Exception(
            "The '{0}' command requires a valid name for argument {1}.".format(
                verb, pos
            )
        )

    return True


def print_parsing_exception(verb, e):
    print("Exception handling '{0}' commmand: {1}".format(verb, e))


### PREPROCESSING PARSING HELPERS ###

"""
COMMAND-LINE AND SCRIPT ARGUMENTS

* Parse the command
* Unwrap args in the left and right "sides"
* Bind both to scriptargs
* Return the re-written command with bindings

"""


def bind_command_args(command, scriptargs):
    """
    Bind "args.<arg> or <default>" and "args.<arg>" (both no quotes).

    NOTE - This routine has legacy capabilities: It can bind variables on the
    left side of an assignment statement. Assignment statements were used for
    implicit / verb-less derived columns which now use the 'derive' verb.

    """
    left, right, iscall = parse_statement(command)

    left = unwrap_args(left)
    right = unwrap_args(right)

    bound = ""
    left_str = bind_args(left, scriptargs)
    right_str = bind_args(right, scriptargs)

    if iscall:
        bound = left_str + "(" + right_str + ")"
    else:
        bound = left_str + "=" + right_str

    return bound


def bind_args(tokens, scriptargs):
    """
    Bind a call_str or rhs expression with args.<arg> or <default>-style args.
    """

    bound = ""

    in_decl = False
    has_default = False
    name = ""
    has_bound = False

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


def parse_statement(command):
    """
    Tokenize a command and split it into a left-hand side and a right-hand side, and
    identify whether it's a function call (verb) or an assignment statement (derived column).
    """
    tokens = tokenize(command)
    rtokens = tokens[::-1]

    open_paren = tokens[1:].index("(") + 1 if ("(" in tokens[1:]) else -1
    close_paren = (
        abs((rtokens.index(")") - (len(tokens) - 1))) if (")" in tokens) else -1
    )
    equals = tokens.index("=") if ("=" in tokens) else -1

    if equals > 0:
        # Treat as assignment
        left = tokens[:equals]
        right = tokens[equals + 1 :]
        iscall = False

        return left, right, iscall

    if (equals == -1) and (open_paren != -1) and (close_paren + 1 == len(tokens)):
        # Treat as function call
        if tokens[0] == "(":
            # An arg is wrapped in parens instead of a static verb
            left_close = tokens.index(")") if (")" in tokens) else -1
            right_open = (
                tokens[left_close + 1 :].index("(") + (left_close + 1)
                if ("(" in tokens[left_close + 1 :])
                else -1
            )

            left = tokens[: left_close + 1]
            right = tokens[right_open + 1 : close_paren]
        else:
            # The verb is explcit
            left = tokens[:open_paren]
            right = tokens[open_paren + 1 : close_paren]

        iscall = True
        return left, right, iscall

    raise Exception("Unrecognized statement: " + command)


def unwrap_args(tokens):
    """
    Remove extraneous parentheses that simply surround arguments or argument with 'or' defaults.
    """

    out_tokens = []
    pending = []

    in_parens = False

    for token in tokens:
        if in_parens and token == "(":
            out_tokens += pending
            pending = [token]
            continue

        if in_parens and token == ")":
            pending += [token]
            wrapped_decl = False
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
            pending = []
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
