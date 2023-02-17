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

PD_TYPES: list[str] = [
    "object",
    "string",
    "int64",
    "float64",
    "bool",
    "datetime64",
    "timedelta64",
    "category",
]
PD_GROUP_ABLE_TYPES: list[str] = ["int64", "float64", "datetime64", "timedelta64"]


class Column:
    """Column definitions are meta data for managing aliases & data types"""

    def __init__(self, name, dtype: str) -> None:
        """
        User-visible column names contain spaces & lowercase letters.
        Internal column names must be a valid identifiers.
        """
        self.name = Column.canonicalize_name(name)
        self.alias = name if (name != self.name) else None  # Automatic aliasing
        self.type: str = dtype
        self.default = None
        self.format: str = None

    def copy(self) -> "Column":
        """Return a copy of the column"""

        return copy.deepcopy(self)

    def set_default(self, default) -> None:
        self.default: Any = default

    def set_format(self, format) -> None:
        self.format = format

    def set_name(self, new_name) -> None:
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
    """A 2D table: multiple rows with each column having one homogenous data type.

    - Uses a Pandas DataFrame for storage.
    - Tables are either read from a delimited file or copied (and then modified).
      The modifiers are responsible for ensuring that the copied table remains consistent
      across modifications (verbs).
    """

    ### CONSTRUCTORS ###

    def __init__(self) -> None:
        """Create an empty table to populate by hand or by reading a file"""
        self._cols: list[Column] = None
        self._data: pd.DataFrame = None

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
        self._extract_col_defs()

    def copy(self) -> "Table":
        """Return a copy of the table"""

        return copy.deepcopy(self)

    def test(self, data) -> None:
        """Create a test table

        data is a dict of lists, where each list is a column of data.
        data = {'a': [1., None, 3.], 'b': ['x', None, 'z']}
        """

        self._data = pd.DataFrame(data)
        self._extract_col_defs()

    def _extract_col_defs(self) -> None:
        """Extract column metadata from the DataFrame"""

        names: list[str] = list(self._data.columns)
        dtypes: list[str] = [x.name for x in self._data.dtypes]
        self._cols = [Column(name, dtype) for name, dtype in zip(names, dtypes)]

    ### PUBLIC METHODS ###

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

    def has_column(self, name) -> bool:
        """Does the table have a column called <name>? (soft fail)"""

        if name in self.col_names():
            return True
        else:
            return False

    def is_column(self, name) -> bool:
        """Does the table have a column called <name>? (hard fail)"""

        if self.has_column(name):
            return True
        else:
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

    def group_able_col_names(self) -> list[str]:
        return [c.name for c in self._cols if c.type in PD_GROUP_ABLE_TYPES]

    ### WRAPPERS ENCAPSULATING PANDAS DATAFRAME METHODS ###
    ### Validate column references before calling them. ###

    def do_keep_cols(self, names) -> None:
        """Keep only the specified columns *in the specified order*"""

        # https://stackoverflow.com/questions/53141240/pandas-how-to-swap-or-reorder-columns

        self._data = self._data[names]
        self._cols = [self.get_column(name) for name in names]

    def do_rename_cols(self, renames: dict()) -> None:
        """Rename columns in the table"""

        self._data.rename(columns=renames, inplace=True)
        for col in self._cols:
            if col.name in renames:
                col.set_name(renames[col.name])

    def do_alias_cols(self, aliases: dict()) -> None:
        """Alias columns in the table"""

        for col in self._cols:
            if col.name in aliases:
                col.set_alias(aliases[col.name])

    def do_select(self, expr: str) -> None:
        """Select rows of the table that satisfy the specified expression

        Pandas - https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.query.html
        df.query('name=="Vienna"')
        df.query('population>1e6 and area<1000')

        Validate the expression & columns referenced in it before calling this.
        """

        self._data = self._data.query(expr)

    def do_first(self, n=5) -> None:
        """Select the first n rows of the table"""

        self._data = self._data.head(n)

    def do_last(self, n=5) -> None:
        """Select the last n rows of the table"""

        self._data = self._data.tail(n)

    def do_sample(self, n=5) -> None:
        """Sample n rows of the table"""

        self._data = self._data.sample(n)

    def do_derive(self, name: str, tokens: list[str]) -> None:
        """Derive a new column from the table

        Pandas:

        df["Minority_2020_tot"] = df["Tot_2020_tot"] - df["Wh_2020_tot"]
        df["county_fips"] = df["GEOID20"].str[2:5]
        """

        # TODO - Re-write tokenized expression in df format
        # TODO - Handle substring operations

        pass  # TODO

    def do_sort(self, by_list: list[str], ascending_list: list[bool]) -> None:
        """Sort the table by the specified columns in the specified order"""

        self._data.sort_values(by=by_list, ascending=ascending_list, inplace=True)

    def do_groupby(
        self, by_list: list[str], agg_list: list[str], agg_fns: list[str]
    ) -> None:
        """Group the table by the specified columns"""

        print(f"by_list: {by_list}")
        print(f"for_list: {agg_list}")
        print(f"agg_fns: {agg_fns}")

        # Grab these to preserve aliases
        by_cols: list[Column] = [self.get_column(name) for name in by_list]

        self._data = self._data.groupby(by_list)[agg_list].agg(agg_fns)

        # Flatten the multi-index columns
        # https://towardsdatascience.com/how-to-flatten-multiindex-columns-and-rows-in-pandas-f5406c50e569
        self._data.columns = ["_".join(col) for col in self._data.columns.values]
        self._data = self._data.reset_index()

        # Update the column metadata
        names: list[str] = list(self._data.columns)
        dtypes: list[str] = [x.name for x in self._data.dtypes]
        self._cols = (
            by_cols
            + [Column(name, dtype) for name, dtype in zip(names, dtypes)][
                len(by_cols) :
            ]
        )


### MULTI-TABLE WRAPPERS ###


def do_union(y_table: Table, x_table: Table) -> Table:
    """Union two matching tables

    - Verify that the tables match, before calling this
    - Preserve the y_table's column metadata (e.g., aliases)
    """

    union_table: Table = Table()
    union_table._cols = list(y_table._cols)
    union_table._data = pd.concat([x_table._data, y_table._data], ignore_index=True)

    return union_table


def columns_match(table1, table2, match_names=True) -> bool:
    if table1.n_cols() != table2.n_cols():
        return False

    if match_names and not all(
        [a == b for a, b in zip(table1.col_names(), table2.col_names())]
    ):
        return False

    if not all([a == b for a, b in zip(table1.col_types(), table2.col_types())]):
        return False

    return True


def do_join(
    left: Table,
    right: Table,
    how: str,
    left_on: str,
    right_on: str,
    suffixes,
    validate: str = None,
) -> Table:
    """Join two tables

    - Verify the parameters before calling this
    """

    join_table: Table = Table()
    join_table._data = pd.merge(
        left._data,
        right._data,
        how=how,
        left_on=left_on,
        right_on=right_on,
        suffixes=suffixes,
        validate=validate,
    )

    # Preserve aliases with this:
    join_table._cols = joined_columns(
        join_table, left, right, left_on, right_on, suffixes
    )
    # Instead of blasting them with this:
    # join_table._extract_col_defs()

    return join_table


def joined_columns(
    joined: Table,
    left: Table,
    right: Table,
    left_on: list[str],
    right_on: list[str],
    suffixes: tuple[str, str],
) -> list[Column]:
    """Return the column (objects, not names) resulting from a join:

    - The union of the columns from the left (y) and right (x) tables
    - Except for the join keys *with the same name* which are not duplicated
    - Matching non-join keys are duplicated with suffixes

    NOTE - This routine assumes all column references are valid.
    """

    keys_match: bool = left_on == right_on
    joined_columns: list[Column] = list()

    for col in left._cols:
        if col.name in left_on:
            joined_columns.append(col.copy())
        elif not right.has_column(col.name):
            joined_columns.append(col.copy())
        else:
            new_col: Column = col.copy()
            if suffixes[0]:
                new_col.set_name(col.name + suffixes[0])
            joined_columns.append(new_col)

    for col in right._cols:
        if col.name in right_on:
            if not keys_match:
                joined_columns.append(col.copy())
        elif not left.has_column(col.name):
            joined_columns.append(col.copy())
        else:
            new_col: Column = col.copy()
            if suffixes[1]:
                new_col.set_name(col.name + suffixes[1])
            joined_columns.append(new_col)

    # Match the order of the columns in the joined table to the order

    join_order: list[str] = list(joined._data.columns)
    if len(join_order) != len(joined_columns):
        raise ValueError("Mismatched column counts!")

    ordered_columns: list[Column] = list()
    for col_ref in join_order:
        for col in joined_columns:
            if col.name == col_ref:
                ordered_columns.append(col)
                break
        else:
            raise ValueError(f"Joined column {col_ref} not found!")

    return ordered_columns


### END ###
