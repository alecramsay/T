#!/usr/bin/env python3

"""
READ/WRITE
"""

import os
import sys
import ast
import dateutil.parser
import pandas as pd
from importlib.machinery import SourceFileLoader
import inspect
import contextlib

from types import ModuleType
from typing import Any, Type, Optional, Generator, TextIO

from .constants import *
from .excel import *

PREREAD_LINES: int = 1000


### PATHS ###


class FileSpec:
    def __init__(self, path: str, name=None) -> None:
        file_name: str
        file_extension: str
        file_name, file_extension = os.path.splitext(path)

        self.rel_path: str = path
        self.abs_path: str = os.path.abspath(path)
        self.name: str = name.lower() if (name) else os.path.basename(file_name).lower()
        self.extension: str = file_extension


StandardDelimiters: dict[str, str] = {
    "tab": "\t",
    "semicolon": ";",
    "comma": ",",
    "space": " ",
    "pipe": "|",
    # user-defined
}

TextQualifiers: dict = {"doublequote": '"', "singlequote": "'", "none": None}


class DelimitedFileReader:
    """Read a delimited text file into a Pandas DataFrame

    The user specifies what the delimiter is and whether there is a header.
    The column types are inferred from the data.

    Args:
        rel_path (str): Relative path to the file
        delimiter (str, optional): Delimiter. Defaults to "comma."
        header (bool, optional): Header? Defaults to True.
        col_types (list, optional): List of column types. Defaults to None.
    """

    def __init__(
        self,
        rel_path: str,
        *,
        delimiter="comma",
        header=True,
    ) -> None:
        self.file: str = FileSpec(rel_path).abs_path
        self.delimiter: str = StandardDelimiters[delimiter]
        # Translate to Pandas' header parameter
        self.header: int | None = 0 if header else None

    def read(self) -> pd.DataFrame:
        return read_delimited_file(
            self.file, delimiter=self.delimiter, header=self.header
        )


### READ CSV USING PANDAS ###


def read_delimited_file(
    file: str, *, delimiter=StandardDelimiters["comma"], header: Optional[int] = None
) -> pd.DataFrame:
    """Read a delimited text file, e.g., CSV

    A two-pass wrapper over Pandas' read_csv() function:
    * The first pass adds some extra column type inferencing, e.g.,
      - numeric fields with leading zeros treated as strings
      - all upper/lower case variations of "True" & "False" treated as bools
      - Python collection types treated as objects in Pandas
      - dates & times interpreted as such by Pandas
    * The second pass reads the file using that information

    Args:
        file (str): Absolute file path
        delimiter (str, optional): Delimiter. Defaults to ','.
        header (int, optional): Header row. Defaults to None.
    """

    df: pd.DataFrame = pd.read_csv(
        file,
        dtype=str,
        header=header,
        sep=delimiter,
        nrows=PREREAD_LINES,
        engine="python",
    )

    inferencers: list[TypeInferencer] = [TypeInferencer() for _ in list(df)]
    for _, df_row in df.iterrows():
        for i, value in enumerate(df_row):
            inferencers[i].add(value)

    inferred_types: list = [obj.infer() for obj in inferencers]

    str_cols: dict[Any, Any] = dict()
    dt_cols: list = list()
    for i, col in enumerate(list(df)):
        if inferred_types[i] == str:
            str_cols[str(col)] = "string"
        elif inferred_types[i] == "pd.datetime":
            dt_cols.append(col)

    df = pd.read_csv(
        file,
        header=header,
        sep=delimiter,
        dtype=str_cols,  # Read strings as strings
        parse_dates=dt_cols,  # Read dates as dates
        engine="python",
    )

    # NOTE - If a column's contents contain the delimiter -- e.g., a comma in a
    # lists, tuples, dicts, or sets -- then Pandas will split the column which
    # will results in a multiindex.

    if isinstance(df.index, pd.MultiIndex):
        raise Exception("Make sure the delimiter is not in any column values!")

    # Use Excel names, if there wasn't a header
    if header is None:
        offsets: list = list(df.columns)
        fieldnames: list[str] = first_n_excel_column_names(len(offsets))
        rename_dict: dict = dict(zip(offsets, fieldnames))
        df.rename(columns=rename_dict, inplace=True)

    return df


### INFER COLUMN TYPES ###


class TypeInferencer:
    """Infer the type of a column from a sample of values

    The set of types is a *hybrid* composite of:
    - The Python type literals supported by ast.literal_eval(), and
    - The Pandas datetime types
    """

    def __init__(self) -> None:
        self.n: int = 0
        self.lengths: set[int] = set()
        self.types: set = set()

    def add(self, example: str) -> None:
        self.n += 1
        self.lengths.add(len(example))

        # Treat columns with leading zeroes as strings
        if leading_zeroes(example):
            self.types.add(str)
            return

        # Allow upper/lower case "true" and "false"
        if is_bool(example):
            self.types.add(bool)
            return

        try:
            dtype: Type
            name: str
            dtype, name = type_from_literal(example)
            # A valid Python literal string
            self.types.add(dtype)
        except:
            # Not a valid Python literal string:
            # It's either an unquoted string, in which case quoting will make it a valida string literal; or
            # It's a Python literal not (yet) supported by ast.literal_eval(), in which case treat it as a string; or
            # It's a datetime, in which case *don't* treat it as a string, so Pandas can parse it

            if is_date_time(example):
                self.types.add("pd.datetime")
            else:
                self.types.add(str)

        return

    def infer(self) -> Type:
        if self.n == 0:
            return str

        # All the same type
        if len(self.types) == 1:
            inferred_type: Type = self.types.pop()

            # All 'integers' the same multi-digit width, e.g., GEOIDs
            # NOTE - This check assumes a non-trivial number of examples.
            if (
                inferred_type == int
                and len(self.lengths) == 1
                and self.lengths.pop() > 1
            ):
                return str

            return inferred_type

        # Mixed types

        # All int & float
        if self.types == {int, float}:
            return float

        return str


# Type Inference Helpers


def type_from_literal(s: str) -> tuple[Type, str]:
    """Evaluate the string as a literal and return the type & name

    Built-in Python data types & their literal representations:
    https://www.w3schools.com/python/python_datatypes.asp

    Throws an exception if the string is not a valid literal
    """

    t: Type = type(ast.literal_eval(s))
    name: str = t.__name__

    return t, name


def leading_zeroes(s: str) -> bool:
    """Does the string have leading zeroes, like a GEODID?"""

    if len(s) > 1 and s[0] == "0" and s[1] != ".":
        return True
    else:
        return False


def is_bool(s: str) -> bool:
    """Is the string a boolean?"""

    return s.lower() in ["true", "false"]


def is_date_time(s: str) -> bool:
    """Is the string a date or time?

    https://strftime.org/
    https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior
    https://stackoverflow.com/questions/9507648/datetime-from-string-in-python-best-guessing-string-format
    """

    try:
        dt: Any = dateutil.parser.parse(s)
        return True
    except:
        return False


### SMART OPEN ###


@contextlib.contextmanager
def smart_open(filename=None) -> Generator[TextIO | TextIO, None, None]:
    """Write to a file or stdout.

    Patterned after: https://stackoverflow.com/questions/17602878/how-to-handle-both-with-open-and-sys-stdout-nicely
    """

    if filename and filename != "-":
        fh: TextIO = open(filename, "w")
    else:
        fh = sys.stdout

    try:
        yield fh
    finally:
        if fh is not sys.stdout:
            fh.close()


### IMPORTING FUNCTIONS ###


def fns_from_path(rel_path) -> dict[str, ModuleType]:
    abs_path: str = FileSpec(rel_path).abs_path

    mod: ModuleType = SourceFileLoader("module.name", abs_path).load_module()
    pairs: list[tuple[str, Any]] = inspect.getmembers(mod, inspect.isfunction)
    fns_dict: dict[str, Any] = {k: v for k, v in pairs}

    return fns_dict


### END ###
