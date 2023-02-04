#!/usr/bin/env python3

"""
The T data model for 2D tables with rows & columns
"""


from typing import Any, Type
from collections import namedtuple
import re
import pprint

from .constants import *

# from .utils import *

# TODO - HERE

dtypes: dict[str, str] = {
    "object": "object",
    "string": "string",
    "int": "int64",
    "float": "float64",
    "bool": "bool",
    "datetime": "datetime64",
    "timedelta": "timedelta64",
}


class Column:
    """
    Column definition meta data for managing aliases & data types
    - Pandas data types: a numpy.dtype or Python type -or-
    - Pandas extension types

    Pandas data types:
    https://pbpython.com/pandas_dtypes.html
    https://pandas.pydata.org/pandas-docs/stable/user_guide/basics.html#basics-dtypes
    https://pandas.pydata.org/pandas-docs/stable/user_guide/text.html#text-types
    https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.astype.html
    https://numpy.org/doc/stable/reference/arrays.dtypes.html

    object                       <<< "can hold any Python object, including strings"
    string                       <<< text
    int                          <<< integers
    float                        <<< floating point numbers
    bool                         <<< booleans
    datetime                     <<< dates & times
    timedelta                    <<< time durations
    category                     <<< categorical data

    Pandas extension types:
    https://pandas.pydata.org/pandas-docs/stable/development/extending.html#extending-extension-types
    https://pandas.pydata.org/pandas-docs/stable/ecosystem.html#ecosystem-extensions

    Built-in Python data types & their literal representations:
    https://www.w3schools.com/python/python_datatypes.asp

    str                          <<< text
    int, float, complex          <<< numbers
    list, tuple, range           <<< sequences
    dict                         <<< mappings
    set, frozenset               <<< sets
    bool                         <<< booleans
    bytes, bytearray, memoryview <<< binary data

    """

    def __init__(self, name, dtype=None) -> None:
        """
        User-visible column names contain spaces & lowercase letters.
        Internal column names must be a valid identifiers.
        """
        self.name = Column.canonicalize_name(name)
        self.alias = name if (name != self.name) else None  # Automatic aliasing
        self.type = dtype if (dtype) else str
        self.default = None
        self.format: str = None

    def set_default(self, default) -> None:
        self.default: Any = default

    def set_format(self, format) -> None:
        self.format = format

    def rename(self, new_name) -> None:
        self.name: str = Column.canonicalize_name(new_name)

    def set_alias(self, new_name) -> None:
        # NOTE - This allows aliased columns to be re-aliased.
        # if self.alias:
        #     raise Exception("Column already has an alias.")
        self.alias: str = Column.canonicalize_name(new_name)

    @classmethod
    def canonicalize_name(cls, name: str) -> str:
        if name.isidentifier():
            return name

        # Try to convert the name into a legal Python identifier
        if name.find(" ") > -1:
            name: str = name.replace(" ", "_")

        if name.find("-") > -1:
            name = name.replace("-", "_")

        if name.find(".") > -1:
            name = name.replace(".", "_")

        if not re.search("^[A-Za-z_]", name[0]):
            name = "_" + name

        if name.isidentifier():
            return name

        raise ValueError(
            "Column name can't be converted to a legal identifer: '{}'".format(name)
        )

    def output_name(self) -> str:
        return self.alias if (self.alias) else self.name


### END ###
