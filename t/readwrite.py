#!/usr/bin/env python3

"""
READ/WRITE
"""

import os
import pandas as pd
from typing import Type

from .constants import *

# from .excel import *
# from .utils import *
# from .datamodel import *


class FileSpec:
    pass  # Declaration


StandardDelimiters: dict[str, str] = {
    "tab": "\t",
    "semicolon": ";",
    "comma": ",",
    "space": " ",
    "pipe": "\|",
    # user-defined
}

TextQualifiers: dict = {
    "doublequote": '"',
    "singlequote": "'",
    "\{none\}": None,
}


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

    A two-pass wrapper over Pandas' read_csv() function. The first pass
    infers the column types. The second pass reads the file using them.

    Args:
        file (str): Absolute file path
        delimiter (str, optional): Delimiter. Defaults to ','.
        header (int, optional): Header row. Defaults to 0.
    """

    df: pd.DataFrame = pd.read_csv(
        file, dtype=str, header=header, sep=delimiter, nrows=PREREAD_LINES
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

    return pd.read_csv(file, header=header, sep=delimiter, dtype=str_cols)


### INFER COLUMN TYPES ###


class TypeInferencer:
    def __init__(self) -> None:
        self.n: int = 0
        self.lengths: set[int] = set()
        self.types: set[Type] = set()

    def add(self, example: str) -> None:
        self.n += 1

        if is_int(example):
            self.types.add(int)
        elif is_float(example):
            self.types.add(float)
        elif is_bool(example):
            self.types.add(bool)
        else:
            self.types.add(str)

        self.lengths.add(len(example))

    def infer(self) -> Type[str] | Type[int] | Type[float] | Type[bool]:
        if self.n == 0:
            return str

        # All the same type
        if len(self.types) == 1:
            inferred_type: Type[str] | Type[int] | Type[float] | Type[
                bool
            ] = self.types.pop()

            # All 'integers' the same multi-digit width, e.g., GEOIDs
            # NOTE - This check assumes a non-trivial number of examples.
            if (
                inferred_type == int
                and len(self.lengths) == 1
                and self.lengths.pop() > 1
            ):
                return str

            return inferred_type

        # All int & float
        if self.types == {int, float}:
            return float

        # No change
        return str


# Type Inference Helpers


def leading_zeroes(s: str) -> bool:
    """
    Like GEODID
    """
    if len(s) > 1 and s[0] == "0":
        return True
    else:
        return False


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


def is_bool(s: str) -> bool:
    """
    Is the string a boolean?
    """
    return s.lower() in ["true", "false"]


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
