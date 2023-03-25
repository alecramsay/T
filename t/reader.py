# reader.py
#!/usr/bin/env python3

"""
REPL INPUT WITH AUTOCOMPLETE

Patterned after https://sites.google.com/site/xiangyangsite/home/technical-tips/software-development/python/python-readline-completions
"""

import libcst as cst
import readline
import re
import string  # for string.whitespace
from enum import Enum
from typing import Callable, Literal, Optional

from .constants import BEG, END

TOK_DELIM_SPEC: str = "[\\s\\(\\)=]"

readline.parse_and_bind("tab: complete")  # TODO - This is not working


def make_input_fn(is_session_rooted, cols: list[str]) -> Callable[..., str]:
    """Autocomplete function for the REPL."""

    def complete(text: str, state: int) -> str | None:
        try:
            tokens: list[str] = re.split(TOK_DELIM_SPEC, readline.get_line_buffer())

            results: list[str | None] = FILE_IN_VERBS + [None]
            if is_session_rooted:
                if set(tokens) & set(VERBS):
                    words: list[str] = cols if cols else []
                else:
                    words = VERBS

                results = [x for x in words if x.startswith(text)] + [None]

            return results[state]

        except Exception as e:
            print(e)

    def input_fn(prompt) -> str:
        readline.set_completer(complete)
        line: str = input(prompt)
        return line

    return input_fn


### CATEGORIES OF VERBS


# NOTE - See docs/verbs.md for a description of each verb

FILE_IN_VERBS: list[str] = ["from"]
FILE_OUT_VERBS: list[str] = ["write"]
DISPLAY_VERBS: list[str] = ["write", "show", "inspect"]
STACK_VERBS: list[str] = ["clear", "pop", "swap", "reverse", "rotate"]
COLUMN_REFERENCING_VERBS: list[str] = [
    "sort",
    "join",
    "groupby",
    "keep",
    "drop",
    "rename",
    "alias",
    "select",
    "cast",
    "derive",
]
OTHER_VERBS: list[str] = [
    "duplicate",
    "union",
    "first",
    "last",
    "sample",
    "history",
]

VERBS: list[str] = (
    FILE_IN_VERBS
    + FILE_OUT_VERBS
    + DISPLAY_VERBS
    + STACK_VERBS
    + COLUMN_REFERENCING_VERBS
    + OTHER_VERBS
)

### HELPERS ###


def trim_whitespace(line) -> str:
    """Remove leading and trailing whitespace from a line."""

    return line.strip()


def remove_excess_whitespace(line) -> str:
    return " ".join(line.split())


HASH_COMMENT: str = "#"
BLOCK_COMMENT: str = '"""'


def remove_hash_comments(line: str) -> str:
    """Remove # comments from a line."""

    hash_sign: int = line.find(HASH_COMMENT)

    if hash_sign == 0:
        # Skip the whole line
        return ""
    if hash_sign > 0:
        # Strip off the '#' and everything after it
        return line[0:hash_sign]

    return line


def remove_inline_block_comments(line: str) -> str:
    """Remove a block comment fully contained on one line."""

    n: int = len(BLOCK_COMMENT)

    first: int = line.find(BLOCK_COMMENT)
    last: int = line.rfind(BLOCK_COMMENT)

    if first > -1 and last > -1 and first != last:
        new_line = remove_excess_whitespace(line[0:first] + line[last + n :])

        return new_line

    return line


def opens_block_comment(line: str) -> tuple[Optional[str], str]:
    """Does a line open a multi-line block comment?"""

    # n: int = len(BLOCK_COMMENT)
    i: int = line.find(BLOCK_COMMENT)

    comment_char: Optional[str] = BLOCK_COMMENT if i > -1 else None
    new_line: str = line[:i].strip() if i > -1 else line

    return comment_char, new_line


def closes_block_comment(line: str) -> tuple[Optional[str], str]:
    """Does a line close a multi-line block comment?"""

    n: int = len(BLOCK_COMMENT)
    i: int = line.rfind(BLOCK_COMMENT)

    comment_char: Optional[str] = BLOCK_COMMENT if i > -1 else None
    new_line: str = line[i + n :].strip() if i > -1 else line

    return comment_char, new_line


def isblank(line: str) -> bool:
    """After trimming whitespace, is a line blank?"""

    return True if line == "" else False


def iscompound(line: str) -> bool:
    """Is a line a compound command?"""

    return True if line.find(";") >= 0 else False


def split_compound_commands(line: str) -> list[str]:
    """Split a compound command into a list of commands."""

    commands: list[str] = [trim_whitespace(x) for x in line.split(";")]

    return commands


def opens_continuation(line: str) -> tuple[str, str] | tuple[None, str]:
    """Does a line open a continuation of any kind?"""

    continue_char: Optional[str]
    new_line: str

    continue_char, new_line = has_continuation_char(line)
    if continue_char:
        return continue_char, new_line

    continue_char = has_open_pair(line)
    if continue_char:
        return continue_char, line

    return None, line


def has_continuation_char(line: str) -> tuple[Optional[str], str]:
    """Is a line continued?"""

    continue_char: Optional[str] = BACKSLASH if line.endswith(BACKSLASH) else None
    new_line: str = line.rstrip(BACKSLASH) if continue_char else line
    # new_line = trim_whitespace(line.rstrip(BACKSLASH)) if continue_char else line

    return continue_char, new_line


BACKSLASH: str = "\\"
ENCLOSING_PAIRS: list[tuple[str, str]] = [("(", ")"), ("[", "]"), ("{", "}")]
ALL_PAIRS: list[tuple[str, str]] = ENCLOSING_PAIRS + [("\\", "\\")]

DOUBLE_QUOTE: str = '"'
SINGLE_QUOTE: str = "'"


def has_open_pair(line: str) -> Optional[str]:
    """Does a line have an open pair of parentheses ( ), brackets [ ], and braces { }?

    NOTE - Theoretically there could be *multiple* open pairs on a line, e.g.:

      foo (bar (
      -or-
      for (bar {
      etc.

    I'm not handling that scenario. I'm also giving implicit precedence to parens
    over brackets over braces.
    """

    for pair in ENCLOSING_PAIRS:
        last_open: int = line.rfind(pair[0])
        last_close: int = line.rfind(pair[1])

        if last_open >= 0 and (last_close == -1 or last_close <= last_open):
            continue_char: str = pair[0]

            return continue_char

    return None


def closes_continuation(
    line, continue_char: Optional[str] = None
) -> tuple[str | None, str]:
    """Does a line close a continuation of any kind?"""

    new_line: str

    if continue_char == BACKSLASH:
        continue_char, new_line = has_continuation_char(line)
        if not continue_char:
            return BACKSLASH, new_line

    continue_char = has_close_pair(line)
    if continue_char:
        return continue_char, line

    return None, line


def has_close_pair(line: str) -> str | None:
    """Does a line have a close pair of parentheses ( ), brackets [ ], and braces { }?

    NOTE - Theoretically a single line could both close a previously open pair *and*
      open a new one, e.g.:

      ...) foo (bar ...

    I'm not handling that scenario.
    """

    for pair in ENCLOSING_PAIRS:
        last_open: int = line.rfind(pair[0])
        last_close: int = line.rfind(pair[1])

        if last_close >= 0 and (last_open == -1 or last_open >= last_close):
            continue_char: str = pair[1]

            return continue_char

    return None


def continuations_match(open_char: str, close_char: str) -> bool:
    """Do an open and close pair match?"""

    for pair in ALL_PAIRS:
        if open_char == pair[0] and close_char == pair[1]:
            return True

    return False


def concatenate_string_literals(line: str):
    """Concatenate string literals:

    - https://stackoverflow.com/questions/34174539/python-string-literal-concatenation
    - https://docs.python.org/3/reference/lexical_analysis.html#string-literal-concatenation

    NOTE - This implementation assumes matching successive quotes, either double or single.
    """

    # Find quoted substrings

    begin_char: Optional[str] = None
    begin_pos: Optional[int] = None
    quoted_strings: list[tuple[int, int]] = list()

    for i, c in enumerate(line):
        # print("char: ", i, c)
        if not begin_char and c in [DOUBLE_QUOTE, SINGLE_QUOTE]:
            begin_char = c
            begin_pos = i
            continue
        if begin_char and c == begin_char:
            assert begin_pos is not None
            quoted_strings.append((begin_pos, i))
            begin_char = None
            begin_pos = None
            continue

    preamble: Optional[tuple[int, int]] = (
        (0, quoted_strings[0][0] - 1)
        if quoted_strings and quoted_strings[0][0] > 0
        else None
    )
    epilogue: Optional[tuple[int, int]] = (
        (quoted_strings[-1][1] + 1, len(line) - 1)
        if quoted_strings and quoted_strings[-1][1] < len(line) - 1
        else None
    )

    if not quoted_strings:
        return line

    new_line: str = ""

    if preamble:
        new_line += line[0 : preamble[END] + 1]

    for i, qs in enumerate(quoted_strings):
        # Emit the first quoted string but not the trailing quote yet ...
        if i == 0:
            new_line += line[qs[BEG] : qs[END]]

        # Eliminate whitespace & redundant quotes between successive quoted strings
        if i > 0:
            prev: tuple[int, int] = quoted_strings[i - 1]
            if line[prev[END] + 1 : qs[BEG] - 1] in string.whitespace:
                # Drop the redundant quotes
                new_line += line[qs[BEG] + 1 : qs[END]]
            else:
                # Emit the previous trailing quote
                new_line += line[prev[END] : prev[END] + 1]
                # Emit the non-whitespace substring between the quotes
                new_line += line[prev[END] + 1 : qs[BEG]]
                # Emit the quoted string but not the trailing quote yet ...
                new_line += line[qs[BEG] : qs[END]]

        # If it's the last quoted string, emit the trailing quote.
        if i == len(quoted_strings) - 1:
            new_line += line[qs[END] : qs[END] + 1]

    if epilogue:
        new_line += line[epilogue[BEG] : len(line)]

    return new_line


def rewrite_pct(command: str) -> str:
    """For 'first', 'last', & 'random', rewrite '%' in non-select, non-derive commands to fake out the Python parser."""

    alt: str = command.replace("%", ", '%'")
    try:
        tree: cst.BaseExpression = cst.parse_expression(alt)
        # TYPE HINT
        verb = tree.func.value.lower()
        if verb in ["first", "last", "random"]:
            return alt
        else:
            return command
    except:
        return command


class ReadState(Enum):
    BLANK = 1
    CONTINUED = 2
    COMMANDS = 3


class Reader:
    """Convert input lines into T commands"""

    continued: bool
    continuation_char: Optional[str]
    in_block: bool
    multi_line: list[str]
    commands: list[str]

    def __init__(self) -> None:
        self.continued = False
        self.continuation_char = None
        self.in_block = False
        self.multi_line = list()

        self.commands = list()

    def next(
        self, line: str
    ) -> Literal[ReadState.BLANK, ReadState.COMMANDS, ReadState.CONTINUED]:
        if self.commands:
            self.commands = list()

        line = rewrite_input_line(line)
        if isblank(line):
            return ReadState.BLANK

        # Analyze potentially m:n relationship between lines & commands

        # Analyze the non-blank line
        open_char: Optional[str]
        open_line: str
        close_char: Optional[str]
        close_line: str
        beg_block: Optional[str]
        beg_line: str
        end_block: Optional[str]
        end_line: str

        compound: bool = iscompound(line)
        open_char, open_line = opens_continuation(line)
        close_char, close_line = (
            closes_continuation(line, self.continuation_char)
            if self.continued
            else (None, line)
        )
        beg_block, beg_line = (
            opens_block_comment(line) if not self.in_block else (None, line)
        )
        end_block, end_line = (
            closes_block_comment(line) if self.in_block else (None, line)
        )

        # Regular line
        if (
            (not self.continued and not open_char)
            and (not self.in_block and not beg_block)
            and not compound
        ):
            command: str = line
            self.commands.append(command)

            return ReadState.COMMANDS

        # Compound line
        if (
            (not self.continued and not open_char)
            and (not self.in_block and not beg_block)
            and compound
        ):
            commands: list[str] = split_compound_commands(line)
            for command in commands:
                self.commands.append(command)

            return ReadState.COMMANDS

        # Continuation started
        if not self.continued and open_char:
            self.continued = True
            self.continuation_char = open_char
            self.multi_line.append(open_line)

            return ReadState.CONTINUED

        # Block comment started
        if not self.in_block and beg_block:
            self.in_block = True
            self.multi_line.append(beg_line)

            return ReadState.CONTINUED

        # Continuation continued
        if self.continued and (
            not close_char
            or (
                close_char
                and close_char == BACKSLASH
                and self.continuation_char is not None
                and not continuations_match(self.continuation_char, close_char)
            )
        ):
            _: Optional[str]
            continued_line: str

            _, continued_line = has_continuation_char(line)
            self.multi_line.append(continued_line)

            return ReadState.CONTINUED

        # Block comment continued
        if self.in_block and not end_block:
            # Ignore the lines between the block comment delimiters

            return ReadState.CONTINUED

        # Continuation ended
        if self.continued and close_char:
            assert self.continuation_char is not None
            if not continuations_match(self.continuation_char, close_char):
                raise Exception(
                    "Continuation mismatch: "
                    + self.continuation_char
                    + " "
                    + close_char
                )
            self.multi_line.append(close_line)
            command = concatenate_string_literals(" ".join(self.multi_line))
            self.commands.append(command)

            self.continued = False
            self.continuation_char = None
            self.multi_line = []

            return ReadState.COMMANDS

        # Block comment ended
        if self.in_block and end_block:
            self.multi_line.append(end_line)
            command = " ".join(self.multi_line)
            self.commands.append(command)

            self.in_block = False
            self.multi_line = []

            return ReadState.COMMANDS

        raise Exception("Unexpected continuation state")


def rewrite_input_line(line: str) -> str:
    """Rewrite input lines, so you can use the Python parser to parse commands.

    I don't use libcst anymore, but I'm leaving in this in, in case we want to in the future.
    """

    line = remove_hash_comments(line)
    line = remove_inline_block_comments(line)
    line = trim_whitespace(line)

    if isblank(line):
        return line

    # HACK - 'from' is a Python keyword
    if line.find("from(") > -1:
        line = line.replace("from(", "from_(")

    # HACK - '%' is a reserved Python symbol
    line = rewrite_pct(line)

    return line


"""
def reader_sample(rel_path):
    # A test harness for reader helper functions.

    fs = FileSpec(rel_path)
    abs_path = fs.abs_path

    with open(abs_path, "r") as f:
        r = Reader()

        line = f.readline()

        while line:
            read_state = r.next(line)
            if read_state == ReadState.COMMANDS:
                for command in r.commands:
                    ### INTERPRET COMMAND ###
                    print(command)

            # Read the next line -or- EOF
            line = f.readline()

    return
"""

### END ###
