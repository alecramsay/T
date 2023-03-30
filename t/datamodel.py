# datamodel.py
#!/usr/bin/env python3

"""
The T data model for 2D tables with rows & columns, implemented over Pandas.
"""

import pandas as pd
from typing import Any, Literal, Optional
from collections import namedtuple
import re
import copy
from csv import DictWriter
import json

from .readwrite import DelimitedFileReader, FileSpec, smart_open

from .expressions import rewrite_expr
from .utils import map_keys
from .udf import UDF

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

# The stats Pandas df.describe() returns for inspect()
PD_DESCRIBE_FNS: list[str] = ["count", "mean", "std", "min", "25%", "50%", "75%", "max"]
PD_DESCRIBE_TYPES: list[str] = ["int64", "float64", "datetime64", "timedelta64"]

# Pandas agg functions for groupby()
PD_AGG_FNS: list[str] = ["count", "mean", "std", "min", "max"]
# AGG_FNS: list[str] = ["count", "min", "max", "std", "sum", "mean", "median"]


class Column:
    """Column definitions are meta data for managing aliases & data types"""

    name: str
    alias: str
    type: str
    default: Optional[Any]
    format: str

    def __init__(self, name: str, dtype: str) -> None:
        """Create a new column definition

        - User-visible column names contain spaces & lowercase letters.
        - Internal column names must be a valid identifiers.
        """

        self.name = Column.canonicalize_name(name)
        self.alias = name if (name != self.name) else ""  # Automatic aliasing
        self.type = dtype
        self.default = None
        self.format = ""

    def copy(self) -> "Column":
        """Return a copy of the column"""

        return copy.deepcopy(self)

    def set_default(self, default: Any) -> None:
        self.default = default

    def set_format(self, format: str) -> None:
        self.format = format

    def set_name(self, new_name: str) -> None:
        self.name: str = Column.canonicalize_name(new_name)

    def set_alias(self, new_name: str) -> None:
        # NOTE - This allows aliased columns to be re-aliased.
        self.alias: str = Column.canonicalize_name(new_name)

    @classmethod
    def canonicalize_name(cls, name: str) -> str:
        if name.isidentifier():
            return name

        # Try to convert the name into a legal Python identifier
        if name.find(" ") > -1:
            name = name.replace(" ", "_")

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

    _cols: list[Column]
    _data: pd.DataFrame
    stats: Optional[dict[Any, dict[Any, Any]]]

    command: str  # for debugging

    ### CONSTRUCTORS ###

    def __init__(self) -> None:
        """Create an empty table to populate by hand or by reading a file"""

        self._cols = []
        self._data = pd.DataFrame({})

        self.stats = None
        self.command = "Unknown"

    def read(
        self,
        rel_path: str,
        *,
        delimiter: str = "comma",
        header: bool = True,
    ) -> None:
        """Read a table from a delimited file (e.g., CSV."""

        self._data = DelimitedFileReader(
            rel_path, header=header, delimiter=delimiter
        ).read()
        self._extract_col_defs()

    def copy(self) -> "Table":
        """Return a copy of the table"""

        return copy.deepcopy(self)

    def test(self, data: dict[str, list]) -> None:
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

    def _calc_stats(self) -> None:
        """Calculate statistics for numeric columns in a table.

        https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.describe.html

                        count         mean          std   min      25%     50%      75%      max
        Tot_2010_tot   2666.0  3576.700300  2176.170775  37.0  2137.25  3204.0  4557.50  33124.0
        Wh_2010_tot    2666.0  2334.581770  1599.392462   5.0  1222.25  2066.5  3133.75  22290.0
        His_2010_tot   2666.0   300.120030   397.547706   0.0    72.00   168.0   363.00   4696.0
        BlC_2010_tot   2666.0   806.997749   957.650283   0.0   142.00   457.5  1113.50   6918.0
        NatC_2010_tot  2666.0    69.048012   254.456423   0.0    17.00    32.0    55.00   5712.0
        AsnC_2010_tot  2666.0    94.743061   189.572929   0.0    12.00    37.0   102.75   4019.0
        PacC_2010_tot  2666.0     5.541635    12.372363   0.0     1.00     2.0     6.00    310.0
        Tot_2010_vap   2666.0  2720.873218  1627.584872  29.0  1658.75  2469.5  3436.75  26768.0
        Wh_2010_vap    2666.0  1862.087397  1247.839395   4.0  1000.50  1669.0  2504.00  18500.0
        His_2010_vap   2666.0   184.669917   249.148990   0.0    44.00   104.0   225.00   3598.0
        ...
        """

        stats_df: pd.DataFrame = self._data.describe().transpose()
        self.stats = stats_df.to_dict(orient="index")

    ### PUBLIC METHODS ###

    @property
    def n_cols(self) -> int:
        if len(self._cols) != self._data.shape[1]:
            raise ValueError("Number of columns doesn't match DataFrame")
        return len(self._cols)

    @property
    def n_rows(self) -> int:
        return self._data.shape[0]

    def cols(self) -> list[Column]:
        return self._cols

    def nth_row(self, n: int) -> list:
        """Return the nth row as a list of values"""

        # When did I need to flatten the row?!?
        # return self._data.loc[n, :].values.flatten().tolist()
        return list(self._data.loc[n, :].values)

    def first_n_rows(self, n: int) -> list:
        """Return the first n rows as a list of lists of values."""

        return self._data.head(n).values.tolist()

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

    def has_column(self, name: str) -> bool:
        """Does the table have a column called <name>? (soft fail)"""

        if name in self.col_names():
            return True
        else:
            return False

    def iscolumn(self, name: str) -> bool:
        """Does the table have a column called <name>? (hard fail)"""

        if self.has_column(name):
            return True
        else:
            raise Exception("Column {0} not in table.".format(name))

    def get_column(self, name: str) -> Column:
        for col in self._cols:
            if col.name == name:
                return col

        raise Exception("Column {0} not in table.".format(name))

    def are_cols(self, names: list[str]) -> bool:
        if len(names) < 1:
            raise Exception("No columns referenced.")

        for i, x in enumerate(names):
            if self.iscolumn(x):
                continue

        return True

    def could_be_column(self, name: str) -> bool:
        """Could <name> be the name of a *new* column?"""

        if not name.isidentifier():
            return False

        if name in self.col_names():
            return False

        return True

    def could_be_cols(self, names: list[str]) -> bool:
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

    def do_keep_cols(self, names: list[str]) -> None:
        """Keep only the specified columns *in the specified order*"""

        # https://stackoverflow.com/questions/53141240/pandas-how-to-swap-or-reorder-columns

        self._data = self._data[names]
        self._data = self._data.reset_index(drop=True)
        self._cols = [self.get_column(name) for name in names]

    def do_rename_cols(self, renames: dict[str, str]) -> None:
        """Rename columns in the table"""

        self._data.rename(columns=renames, inplace=True)
        self._data = self._data.reset_index(drop=True)
        for col in self._cols:
            if col.name in renames:
                col.set_name(renames[col.name])

    def do_alias_cols(self, aliases: dict[str, str]) -> None:
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

    def do_first(self, n: int = 5) -> None:
        """Select the first n rows of the table"""

        self._data = self._data.head(n)
        self._data = self._data.reset_index(drop=True)

    def do_last(self, n: int = 5) -> None:
        """Select the last n rows of the table"""

        self._data = self._data.tail(n)
        self._data = self._data.reset_index(drop=True)

    def do_sample(self, n: int = 5) -> None:
        """Sample n rows of the table"""

        self._data = self._data.sample(n)
        self._data = self._data.reset_index(drop=True)

    def do_cast_cols(self, names: list[str], dtype: str) -> None:
        """Cast the specified columns to the given data type"""

        col_names: list[str] = self.col_names()
        col_types: list[str] = self.col_types()

        cast_types: dict[str, str] = dict(zip(col_names, col_types))
        for col in names:
            cast_types[col] = dtype

        self._data = self._data.astype(cast_types, errors="raise")
        # Update the new column types in the table's column metadata.
        for col in self._cols:
            if col.name in names:
                col.type = dtype

    def do_derive(
        self, name: str, tokens: list[str], udf: Optional[UDF] = None
    ) -> None:
        """Derive a new column from the table

        Pandas:

        derive(Minority_2020_tot, Tot_2020_tot - Wh_2020_tot
        derive(county_fips, GEOID20[2:5]
        derive(D_pct, vote_share(D_2020_pres, R_2020_pres)
        """

        expr: str
        wrappers: list[str]
        expr, wrappers = rewrite_expr(tokens, self.col_names(), udf)

        env: dict = dict()
        if udf:
            for k, v in udf.user_fns.items():
                env[k] = v
            if wrappers:
                for wrapper in wrappers:
                    exec(wrapper, env)

        df: pd.DataFrame = self._data

        # env.update(wrapped)
        env.update({"df": df})

        df[name] = eval(expr, env)

        # Add new column metadata
        dtype: str = df[name].dtype.name
        new_col: Column = Column(name, dtype)
        self._cols.append(new_col)

        # Cross-check the # columns matches the # in the dataframe
        self.n_cols

    def do_sort(self, by_list: list[str], ascending_list: list[bool]) -> None:
        """Sort the table by the specified columns in the specified order"""

        self._data.sort_values(by=by_list, ascending=ascending_list, inplace=True)

    def do_groupby(
        self, by_list: list[str], agg_list: list[str], agg_fns: list
    ) -> None:
        """Group the table by the specified columns"""

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


def columns_match(table1: Table, table2: Table, match_names: bool = True) -> bool:
    if table1.n_cols != table2.n_cols:
        return False

    if match_names and not all(
        [a == b for a, b in zip(table1.col_names(), table2.col_names())]
    ):
        return False

    if not all([a == b for a, b in zip(table1.col_types(), table2.col_types())]):
        return False

    return True


PD_JOIN_TYPES: list[str] = ["left", "right", "outer", "inner", "cross"]
PD_VALIDATE_TYPES: list[str] = ["1:1", "1:m", "m:1", "m:m"]
MergeHow = Literal["left", "right", "inner", "outer", "cross"]
ValidationOptions = Literal["1:1", "1:m", "m:1", "m:m"]


def do_join(
    left: Table,
    right: Table,
    how: MergeHow,
    left_on: list[str],
    right_on: list[str],
    # Note: These suffixes are reversed from Pandas, to match T stack semantics.
    suffixes: tuple[str, str] | tuple[None, str] | tuple[str, None],
    validate: Optional[ValidationOptions],
) -> Table:
    """Join two tables

    - Verify the parameters before calling this
    """

    # TYPE HINT
    # Reverse the suffixes, to match Pandas semantics.
    assert suffixes[0] is not None or suffixes[1] is not None
    swapped: tuple[str, str] | tuple[None, str] | tuple[str, None] = suffixes[::-1]  # type: ignore

    join_table: Table = Table()
    if validate:
        join_table._data = pd.merge(
            left._data,
            right._data,
            how=how,
            left_on=left_on,
            right_on=right_on,
            suffixes=suffixes,
            validate=validate,
        )
    else:
        join_table._data = pd.merge(
            left._data,
            right._data,
            how=how,
            left_on=left_on,
            right_on=right_on,
            suffixes=suffixes,
            # validate=validate,  # Can't be None
        )
    join_table._data = join_table._data.reset_index(drop=True)

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
    suffixes: tuple[str, str] | tuple[None, str] | tuple[str, None],
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


### WRITE HELPERS ###


def table_to_csv(table: Table, rel_path: Optional[str]) -> None:
    """Write a table to a CSV file"""

    try:
        cf: Optional[str] = (
            FileSpec(rel_path).abs_path if (rel_path is not None) else None
        )

        col_names: list[str] = table.col_names()
        header: str = ",".join(table.col_aliases_or_names()) + "\n"

        with smart_open(cf) as handle:
            writer: DictWriter[str] = DictWriter(handle, fieldnames=col_names)

            # Write the header row with aliases (faking out 'writer')
            handle.write(header)

            for _, row in table._data.iterrows():
                mod: dict = dict(zip(col_names, row))
                # TODO - Handle missing values?
                # mod = {k: missing_to_str(v) for (k, v) in row.dict().items()}
                writer.writerow(mod)

    except:
        raise Exception("Exception writing CSV.")


def table_to_json(table: Table, rel_path: Optional[str]) -> None:
    """Write a table to a JSON file

    https://stackoverflow.com/questions/21525328/python-converting-a-list-of-dictionaries-to-json#21525380
    https://stackoverflow.com/questions/12309269/how-do-i-write-json-data-to-a-file#12309296
    """
    try:
        cf: Optional[str] = (
            FileSpec(rel_path).abs_path if (rel_path is not None) else None
        )

        rows: list[dict] = list()
        col_names: list[str] = table.col_names()
        mapping: Optional[dict[str, str]] = (
            table.map_names_to_aliases() if table.has_aliases() else None
        )

        for _, row in table._data.iterrows():
            d: dict = dict(zip(col_names, row))
            if mapping:
                d = map_keys(d, mapping)
            rows.append(d)

        with smart_open(cf) as handle:
            json.dump(rows, handle)

    except:
        raise Exception("Exception writing JSON.")


### END ###
