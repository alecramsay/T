#!/usr/bin/env python3

"""
The T data model for 2D tables with rows & columns
"""

import pandas as pd
from typing import Any, Type
from collections import namedtuple
import re
import copy
import pprint

from .constants import *
from .readwrite import DelimitedFileReader

### PANDAS DATA TYPES ###

# https://pandas.pydata.org/pandas-docs/stable/user_guide/basics.html#dtypes
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

    # TODO - DELETE
    # def rename(self, new_name) -> None:
    #     self.name: str = Column.canonicalize_name(new_name)

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
    """A 2D table: multiple rows with each column having one homogenous data type.

    - Uses a Pandas DataFrame for storage.
    - Tables are either read from a delimited file or copied (and then modified).
      The modifiers are responsible for ensuring that the copied table remains consistent
      across modifications (verbs).
    """

    def __init__(
        self,
        rel_path: str,
        *,
        delimiter="comma",
        header=True,
    ) -> None:
        self._cols: list[Column] = None
        self._data: pd.DataFrame = None

        self.signatures: set = set()

        self._read(rel_path=rel_path, delimiter=delimiter, header=header)
        self._extract_col_defs()

    ### PRIVATE METHODS ###

    def _read(
        self,
        rel_path: str,
        *,
        delimiter,
        header,
    ) -> None:
        """Read a table from a delimited file (e.g., CSV."""

        self._data = DelimitedFileReader(
            rel_path, header=header, delimiter=delimiter
        ).read()

    def _extract_col_defs(self) -> None:
        """Extract column metadata from the DataFrame"""

        names: list[str] = list(self._data.columns)
        dtypes: list[str] = [x.name for x in self._data.dtypes]
        self._cols = [Column(name, dtype) for name, dtype in zip(names, dtypes)]

    ### PUBLIC METHODS ###

    def copy(self) -> "Table":
        """Return a copy of the table"""

        return copy.deepcopy(self)

    def n_cols(self):
        return len(self._cols)

    def n_rows(self):
        return self._data.shape[0]

    def col_names(self) -> list[str]:
        return [c.name for c in self._cols]

    def has_aliases(self) -> bool:
        for c in self._cols:
            if c.alias:
                return True

        return False

    def col_aliases_or_names(self) -> list[str]:
        return [c.alias if c.alias else c.name for c in self._cols]

    def map_names_to_aliases(self) -> dict[str, str]:
        return {c.name: (c.alias if c.alias else c.name) for c in self._cols}

    def col_types(self) -> list[str]:
        return [c.type for c in self._cols]

    def is_column(self, name) -> bool:
        """Does the table have a column called <name>?"""

        if name in self.col_names():
            return True

        raise Exception("Column {0} not in table.".format(name))

    def get_column(self, name) -> Column:
        for col in self._cols:
            if col.name == name:
                return col

        raise Exception("Column {0} not in table.".format(name))

    def are_cols(self, names) -> bool:
        if len(names) < 1:
            raise Exception("No columns referenced.")

        for i, x in enumerate(names):
            if self.is_column(x):
                continue

        return True

    def could_be_column(self, name) -> bool:
        """Could <name> be the name of a *new* column?"""

        if not name.isidentifier():
            return False

        if name in self.col_names():
            return False

        return True

    def could_be_cols(self, names) -> bool:
        if len(names) < 1:
            raise Exception("No columns named.")

        for i, x in enumerate(names):
            if self.could_be_column(x):
                continue

        return True

    ### WRAPPERS ENCAPSULATING PANDAS DATAFRAME METHODS ###
    ### NOTE - Validate column names *before* calling them. ###

    def drop_cols(self, names) -> None:
        """Drop columns from the table"""

        self._data.drop(columns=names, inplace=True)
        self._extract_col_defs()

    def rename_cols(self, renames: dict()) -> None:
        """Rename columns in the table"""

        self._data.rename(columns=renames, inplace=True)
        self._extract_col_defs()

    def alias_cols(self, aliases: dict()) -> None:
        """Alias columns in the table"""

        for col in self._cols:
            if col.name in aliases:
                col.set_alias(aliases[col.name])

    def first(self, n=5) -> None:
        """Select the first n rows of the table"""

        self._data = self._data[:n]


### END ###
