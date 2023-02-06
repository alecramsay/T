#!/usr/bin/env python3

"""
The T data model for 2D tables with rows & columns
"""

import pandas as pd
from typing import Any, Type
from collections import namedtuple
import re
import pprint

from .constants import *
from .readwrite import DelimitedFileReader

### PANDAS DATA TYPES ###

# Pandas data types - https://pandas.pydata.org/pandas-docs/stable/user_guide/basics.html#dtypes
PD_FRIENDLY_NAME_TO_TYPE: dict[str, str] = {
    "object": "object",
    "string": "string",
    "int": "int64",
    "float": "float64",
    "bool": "bool",
    "datetime": "datetime64",
    "timedelta": "timedelta64",
    "category": "category",
}
PD_TYPE_FRIENDLY_NAMES: list[str] = list(PD_FRIENDLY_NAME_TO_TYPE.keys())
PD_TYPE_TO_FRIENDLY_NAMES: dict[str, str] = {
    v: k for k, v in PD_FRIENDLY_NAME_TO_TYPE.items()
}


# TODO
# names = list(df.columns)
# dtypes = [x.name for x in df.dtypes]
class Column:
    """Column definitions are meta data for managing aliases & data types"""

    def __init__(self, name, dtype=None) -> None:
        """
        User-visible column names contain spaces & lowercase letters.
        Internal column names must be a valid identifiers.
        """
        self.name = Column.canonicalize_name(name)
        self.alias = name if (name != self.name) else None  # Automatic aliasing
        self.type: str = (
            dtype if dtype and (dtype in PD_TYPE_FRIENDLY_NAMES) else "string"
        )
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


class Table:
    """A 2D table with multiple rows with columns having one data type each.

    Uses a Pandas DataFrame for storage.
    """

    def __init__(self) -> None:
        self._cols: list[Column] = None
        self._data: pd.DataFrame = None

        self.signatures: set = set()
        # self.ncols = len(self.cols)
        # self.indexes = {}
        # self.stats = None

    def read(
        self,
        rel_path: str,
        *,
        delimiter="comma",
        header=True,
    ) -> None:
        """Read a table from a delimited file (e.g., CSV."""

        self._data = DelimitedFileReader(
            rel_path, header=header, delimiter=delimiter
        ).read()

        # TODO - Hook up column definitions to the DataFrame
        # TODO - Wire up n_cols, n_rows, etc.


### END ###
