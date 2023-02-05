#!/usr/bin/env python3

"""
READ/WRITE
"""

import os
import ast
import builtins
import pandas as pd
from typing import Type

from .constants import *
from .excel import *

# from .utils import *
# from .datamodel import *


class FileSpec:
    pass  # Declaration


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
    """Read table from a delimited text file

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
        self.header: int | None = 0 if header else None

    def read(self) -> pd.DataFrame:
        return read_delimited_file(
            self.file, delimiter=self.delimiter, header=self.header
        )


### READ CSV USING PANDAS ###


def read_delimited_file(
    file: str, *, delimiter=StandardDelimiters["comma"], header: int = 0
) -> pd.DataFrame:
    """Read a delimited text file, e.g., CSV

    A two-pass wrapper over Pandas' read_csv() function.
    - The first pass infers string columns (e.g., leading zeros)
    - The second pass reads the file using them

    Args:
        file (str): Absolute file path
        delimiter (str, optional): Delimiter. Defaults to ','.
        header (int, optional): Header row. Defaults to 0.
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

    str_cols: dict[str, str] = dict()
    for i, col in enumerate(list(df)):
        if inferred_types[i] == str:
            str_cols[col] = "string"

    df = pd.read_csv(
        file, header=header, sep=delimiter, dtype=str_cols, engine="python"
    )

    # Use Excel names, if there isn't a header
    if header is None:
        offsets: list = list(df.columns)
        fieldnames: list[str] = first_n_excel_column_names(len(offsets))
        rename_dict: dict = dict(zip(offsets, fieldnames))
        df.rename(columns=rename_dict, inplace=True)

    return df


### INFER COLUMN TYPES ###


class TypeInferencer:
    def __init__(self) -> None:
        self.n: int = 0
        self.lengths: set[int] = set()
        self.types: set[Type] = set()

    def add(self, example: str) -> None:
        self.n += 1

        try:
            if leading_zeroes(example):
                self.types.add(str)
            else:
                dtype: Type
                name: str
                dtype, name = type_from_literal(example)
                # A valid Python literal string
                self.types.add(dtype)
        except:
            # Not a valid Python literal string
            self.types.add(str)

        self.lengths.add(len(example))

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
    """
    Like GEODID
    """
    if len(s) > 1 and s[0] == "0" and s[1] != ".":
        return True
    else:
        return False


# DELETE
def is_int(s: str) -> bool:
    """
    Is the string an integer? (possibly negative)
    """
    try:
        if leading_zeroes(s):
            return False
        int(s)
        return True
    except ValueError:
        return False


# DELETE
def is_float(s: str) -> bool:
    """
    Is the string a float? (possibly negative)
    """
    try:
        if leading_zeroes(s):
            return False
        float(s)
        return True
    except ValueError:
        return False


# DELETE
def is_bool(s: str) -> bool:
    """
    Is the string a boolean?
    """
    return s.lower() in ["true", "false"]


# DELETE
def is_complex(s: str) -> bool:
    """
    Is the string a complex number?
    """
    try:
        complex(s)
        return True
    except ValueError:
        return False


# DELETE
def is_bytes(s: str) -> bool:
    """
    Is the string a bytes object?

    https://stackoverflow.com/questions/47741235/how-to-read-bytes-object-from-csv
    """

    try:
        if isinstance(s, bytes):
            return True
        else:
            return False
    except ValueError:
        return False


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


### END ###
