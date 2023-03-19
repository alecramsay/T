#!/usr/bin/env python3

"""
VERBS - GIVEN ONE OR MORE INPUT TABLES, CREATE A NEW TABLE

NOTE - These verbs don't know anything about the program stack.
"""

from typing import NoReturn

from .constants import *
from .utils import *
from .expressions import *
from .datamodel import *
from .udf import *


AGG_FNS: list[str] = ["count", "min", "max", "std", "sum", "mean", "median"]


def is_agg_fn(fn: str) -> bool:
    if fn in AGG_FNS:
        return True

    raise Exception(f"{fn} is not a valid aggregation function.")


class Verb:
    """Base class for verbs

    Process:
    1. Copy the input table
    2. Make the change to the table's dataframe
    3. Update the table's column metadata to match (to preserve aliases)
    """

    _x_table: Optional[Table]
    _y_table: Optional[Table]
    _col_refs: Optional[list[str]]
    _new_col_refs: list[str]
    _col_specs: list

    _new_table: Optional[Table]

    def __init__(self) -> None:
        self._x_table = None
        self._y_table = None
        self._col_refs = None
        self._new_col_refs = list()
        self._col_specs = list()

        self._new_table = None

    def apply(self) -> NoReturn:
        raise Exception("Not implemented.")

    ### VALIDATION HELPERS ###

    def _validate_col_refs(
        self, col_refs: Optional[list[str]] = None, table: Optional[Table] = None
    ) -> None:
        """Validate existing column references. Raise an exception when one or more are not valid."""

        col_refs = col_refs if col_refs else self._col_refs
        table = table if table else self._x_table
        assert table is not None
        assert col_refs is not None

        table.are_cols(col_refs)

    def _validate_new_col_refs(
        self, new_col_refs: Optional[list[str]] = None, table: Optional[Table] = None
    ) -> None:
        """Validate new column references. Raise an exception when one or more are not valid."""

        new_col_refs = new_col_refs if new_col_refs else self._new_col_refs
        table = table if table else self._x_table
        assert table is not None
        assert new_col_refs is not None

        table.could_be_cols(new_col_refs)

    def _unzip_col_specs(
        self, col_specs: Optional[list] = None
    ) -> tuple[list[str], list[str]]:
        """Unzip a list of column specs into a list existing column refs and a list of new column refs."""

        col_specs = col_specs if col_specs else self._col_specs

        if len(col_specs) < 1:
            raise Exception("No column specs.")

        col_refs: list[str] = list()
        new_col_refs: list[str] = list()
        for pair in col_specs:
            from_col: str
            to_col: str
            from_col, to_col = parse_spec(pair)
            col_refs.append(from_col.strip())
            new_col_refs.append(to_col.strip())

        return col_refs, new_col_refs

    def _unzip_sort_specs(
        self, col_specs: Optional[list] = None
    ) -> tuple[list[str], list[bool]]:
        """Unzip a list of sort specs into a list of column refs and sort order booleans."""

        col_specs = col_specs if col_specs else self._col_specs

        if len(col_specs) < 1:
            raise Exception("No column specs.")

        by_list: list[str] = list()
        ascending_list: list[bool] = list()
        for pair in col_specs:
            by: str
            order: str
            by, order = parse_spec(pair)
            by_list.append(by.strip())

            order = order.strip().upper()
            order = "ASC" if order == by else order
            if order not in ["ASC", "DESC"]:
                raise Exception(f"Invalid sort order: {order}")
            ascending_list.append(True if order == "ASC" else False)

        return by_list, ascending_list


### ROW FILTERS ###


class KeepVerb(Verb):
    """KEEP columns"""

    def __init__(self, x_table: Table, keep_cols: list[str]) -> None:
        super().__init__()

        self._x_table = x_table
        self._col_refs = [x.strip() for x in keep_cols]

        self._validate_col_refs()

    def apply(self) -> Table:
        assert self._x_table is not None
        assert self._col_refs is not None
        self._new_table: Table = self._x_table.copy()
        self._new_table.do_keep_cols(self._col_refs)

        return self._new_table


class DropVerb(Verb):
    """DROP columns"""

    def __init__(self, x_table: Table, drop_cols: list[str]) -> None:
        super().__init__()

        self._x_table = x_table
        self._col_refs = [x.strip() for x in drop_cols]

        self._validate_col_refs()

    def apply(self) -> Table:
        assert self._x_table is not None
        self._new_table: Table = self._x_table.copy()

        assert self._col_refs is not None
        keep_cols: list[str] = [
            name for name in self._x_table.col_names() if name not in self._col_refs
        ]
        self._new_table.do_keep_cols(keep_cols)

        return self._new_table


class RenameVerb(Verb):
    """RENAME specific columns"""

    def __init__(self, x_table: Table, col_specs: list) -> None:
        super().__init__()

        self._x_table = x_table
        self._col_specs = col_specs
        self._col_refs, self._new_col_refs = self._unzip_col_specs()

        self._validate_col_refs()
        self._validate_new_col_refs()

    def apply(self) -> Table:
        assert self._x_table is not None
        self._new_table: Table = self._x_table.copy()

        assert self._col_refs is not None
        renames: dict = {
            from_col: to_col
            for from_col, to_col in zip(self._col_refs, self._new_col_refs)
        }
        self._new_table.do_rename_cols(renames)

        return self._new_table


class AliasVerb(Verb):
    """ALIAS specified columns

    - Aliasing is just like renaming, except it retains the alias so it can be reverted.
    - Use original column names on write.
    """

    def __init__(self, x_table: Table, col_specs: list) -> None:
        super().__init__()

        self._x_table = x_table
        self._col_specs = col_specs
        self._col_refs, self._new_col_refs = self._unzip_col_specs()

        self._validate_col_refs()
        self._validate_new_col_refs()

    def apply(self) -> Table:
        assert self._x_table is not None
        self._new_table: Table = self._x_table.copy()

        assert self._col_refs is not None
        renames: dict = {
            from_col: to_col
            for from_col, to_col in zip(self._col_refs, self._new_col_refs)
        }
        self._new_table.do_rename_cols(renames)

        aliases: dict = {
            from_col: to_col
            for from_col, to_col in zip(self._new_col_refs, self._col_refs)
        }
        self._new_table.do_alias_cols(aliases)

        return self._new_table


class SelectVerb(Verb):
    """SELECT rows"""

    def __init__(self, x_table: Table, expr: str) -> None:
        super().__init__()

        self._x_table: Table = x_table
        self._expr: str = expr

        # Check that the expression has valid *syntax* before calling this.
        # Here check that all column references are valid (*semantics*).

        tokens: list[str] = tokenize(expr)
        col_names: list[str] = x_table.col_names()

        has_valid_col_refs(tokens, col_names)

    def apply(self) -> Table:
        self._new_table: Table = self._x_table.copy()
        self._new_table.do_select(self._expr)

        return self._new_table


class FirstVerb(Verb):
    """FIRST n rows"""

    def __init__(self, x_table: Table, n: int, pct: Optional[Any] = None) -> None:
        super().__init__()

        self._x_table = x_table
        self._take: int = n if not pct else max(round(n * (x_table.n_rows / 100)), 1)

    def apply(self) -> Table:
        assert self._x_table is not None
        self._new_table: Table = self._x_table.copy()
        self._new_table.do_first(self._take)

        return self._new_table


class LastVerb(Verb):
    """LAST n rows"""

    def __init__(self, x_table: Table, n: int, pct: Optional[Any] = None) -> None:
        super().__init__()

        self._x_table = x_table
        self._take: int = n if not pct else max(round(n * (x_table.n_rows / 100)), 1)

    def apply(self) -> Table:
        assert self._x_table is not None
        self._new_table: Table = self._x_table.copy()
        self._new_table.do_last(self._take)

        return self._new_table


class SampleVerb(Verb):
    """SAMPLE n rows"""

    def __init__(self, x_table: Table, n: int, pct: Optional[Any] = None) -> None:
        super().__init__()

        self._x_table = x_table
        self._take: int = n if not pct else max(round(n * (x_table.n_rows / 100)), 1)

    def apply(self) -> Table:
        assert self._x_table is not None
        self._new_table: Table = self._x_table.copy()
        self._new_table.do_sample(self._take)

        return self._new_table


class CastVerb(Verb):
    """CAST columns to a new type

    https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.astype.html
    https://www.w3schools.com/python/pandas/ref_df_astype.asp
    https://stackoverflow.com/questions/21197774/assign-pandas-dataframe-column-dtypes
    """

    def __init__(self, x_table: Table, cast_cols: list[str], dtype: str) -> None:
        super().__init__()

        self._x_table = x_table
        self._col_refs = [x.strip() for x in cast_cols]

        self._validate_col_refs()

        if dtype not in PD_TYPES:
            raise ValueError(f"Invalid dtype: {dtype}")
        self._dtype: str = dtype

    def apply(self) -> Table:
        assert self._x_table is not None
        assert self._col_refs is not None
        self._new_table: Table = self._x_table.copy()
        self._new_table.do_cast_cols(self._col_refs, self._dtype)

        return self._new_table


class DeriveVerb(Verb):
    """DERIVE new column from existing columns

    Pandas:
    df['new_col'] = df['col1'] + df['col2']
    """

    def __init__(
        self, x_table: Table, name: str, expr: str, udf: Optional[UDF] = None
    ) -> None:
        super().__init__()

        self._name: str = name
        self._x_table: Table = x_table
        self._expr: str = expr
        self._udf: Optional[UDF] = udf

        # Validate new column name
        self._new_col_refs: list[str] = [name.strip()]
        self._validate_new_col_refs()

        # Before calling this, check that the forumla has the right left-hand side,
        # '=', and right-hand side format and that the rhs expression has valid *syntax*.
        # Here check that all column references are valid (*semantics*).

        tokens: list[str] = tokenize(expr)
        col_names: list[str] = x_table.col_names()

        # Validate column & UDF references
        udf_names: list[str] = self._udf.names() if self._udf else []
        has_valid_refs(tokens, col_names, udf_names)
        self._tokens: list[str] = tokenize(expr)

    def apply(self) -> Table:
        self._new_table: Table = self._x_table.copy()
        self._new_table.do_derive(self._name, self._tokens, self._udf)

        return self._new_table


### TABLE FILTERS ###


class SortVerb(Verb):
    """SORT rows'"""

    def __init__(self, x_table: Table, col_specs: list) -> None:
        super().__init__()

        self._x_table = x_table
        self._col_specs = col_specs
        self._ascending_list: list[bool]
        self._col_refs, self._ascending_list = self._unzip_sort_specs()

        self._validate_col_refs()

    def apply(self) -> Table:
        assert self._x_table is not None
        self._new_table: Table = self._x_table.copy()

        assert self._col_refs is not None
        self._new_table.do_sort(self._col_refs, self._ascending_list)

        return self._new_table


class GroupByVerb(Verb):
    """GROUP BY

    * Aggregate numeric columns by one or more grouping columns. Skip non-numeric ones.
    * Compute one or more statistics for each group: count, min, max, std, sum, mean, median.
    * By default, aggregate all numeric columns. Optionally take an explicit list of cols to aggregate.
    * By default, compute all statistics. Optionally take an explicit list of stats to compute.

    * For each aggregated column 'x', the resulting rows contain columns of the form x_min, x_max, etc.
    * TODO - They can also be referenced as min(X), max(X), sum(X), count(X), and avg(X). <<< Is this true?
    """

    def __init__(
        self,
        x_table: Table,
        by: list[str],
        *,
        only: Optional[list[str]] = None,
        agg: Optional[list[str]] = None,
    ) -> None:
        super().__init__()

        self._x_table = x_table

        # Group by columns
        self._group_cols: list = [x.strip() for x in by]
        self._validate_col_refs(self._group_cols, self._x_table)

        # Columns to aggregate
        self._agg_cols: list[str]
        if only:
            self._agg_cols = [x.strip() for x in only]
            self._validate_col_refs(self._agg_cols, self._x_table)

            for name in self._group_cols:
                if name in self._agg_cols:
                    raise ValueError(
                        f"Column '{name}' cannot be in both 'by' and 'only' lists."
                    )

            for name in self._agg_cols:
                if name not in self._x_table.group_able_col_names():
                    raise ValueError(
                        f"Column '{name}' is not numeric or a datetime and cannot be aggregated."
                    )
        else:
            self._agg_cols = self._x_table.group_able_col_names()
            for name in self._group_cols:
                if name in self._agg_cols:
                    self._agg_cols.remove(name)

        # Aggregation functions
        self._agg_fns: list[str]
        if agg:
            self._agg_fns = [x.strip() for x in agg]
            for fn in self._agg_fns:
                is_agg_fn(fn)
        else:
            self._agg_fns = AGG_FNS

    def apply(self) -> Table:
        assert self._x_table is not None
        self._new_table: Table = self._x_table.copy()

        self._new_table.do_groupby(self._group_cols, self._agg_cols, self._agg_fns)

        return self._new_table


class JoinVerb(Verb):
    """JOIN two tables

    https://en.wikipedia.org/wiki/Join_(SQL)

    Map stack nomenclature to Pandas merge terminology:
    https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.merge.html

    y_table : left
    x_table : right

    how (optional) : {'left', 'right', 'outer', 'inner', 'cross'}, default 'inner'
    - left: use only keys from left frame, similar to a SQL left outer join; preserve key order.
    - right: use only keys from right frame, similar to a SQL right outer join; preserve key order.
    - outer: use union of keys from both frames, similar to a SQL full outer join; sort keys lexicographically.
    - inner: use intersection of keys from both frames, similar to a SQL inner join; preserve the order of the left keys.
    - cross: creates the cartesian product from both frames, preserves the order of the left keys.

    on (optional)
    - If no columns are specified, join on the shared columns (matching names + types).
    - If one set of columns are specified, join on those -- make sure they exist in both and data types match.
    - If two sets of columns are specified -- make sure they exist and data types match.

    suffixes (optional) : ("_y", "_x") is default -- Note: This is reversed.

    validate (optional) : {"1:1", "1:m", "m:1", "m:m", None}, default None

    """

    _y_table: Table
    _x_table: Table
    _how: MergeHow
    _y_cols: list[str]
    _x_cols: list[str]
    _suffixes: tuple[str, str] | tuple[None, str] | tuple[str, None]
    _validate: Optional[ValidationOptions]

    def __init__(
        self,
        y_table: Table,
        x_table: Table,
        *,
        how: MergeHow = "inner",
        on: Optional[str | list[str] | list[list[str]]] = None,
        suffixes: tuple[str, str]
        | tuple[None, str]
        | tuple[str, None] = (
            "_y",
            "_x",
        ),  # Note: This is reversed from Pandas, to match T stack semantics.
        validate: Optional[ValidationOptions] = None,
    ) -> None:
        super().__init__()

        self._y_table = y_table
        self._x_table = x_table

        # how
        self._how: MergeHow = how
        if how not in PD_JOIN_TYPES:
            raise ValueError(f"Invalid join type '{how}'.")

        # on (columns)
        self._y_cols: list[str]
        self._x_cols: list[str]

        if on is None:
            # No columns are specified -- infer them
            shared: list[str] = infer_join_cols(y_table, x_table)
            if len(shared) == 1:
                self._y_cols = shared
                self._x_cols = shared
            else:
                self._y_cols = shared
                self._x_cols = shared

        elif isinstance(on, str):
            # One column is specified -- make sure it exists in both tables with matching types
            cols_match(y_table, x_table, [on], [on])
            self._y_cols = [on]
            self._x_cols = [on]

        elif is_list_of_str(on):
            # One list of columns
            # TYPE HINT
            assert isinstance(on, list) and all(isinstance(elem, str) for elem in on)
            cols_match(y_table, x_table, on, on)
            self._y_cols = on
            self._x_cols = on

        elif (
            isinstance(on, list)
            and len(on) == 2
            and is_list_of_str(on[0])
            and is_list_of_str(on[1])
        ):
            # Two lists of columns
            assert isinstance(on[0], list)
            assert isinstance(on[1], list)
            cols_match(y_table, x_table, on[0], on[1])
            self._y_cols = on[0]
            self._x_cols = on[1]

        else:
            raise ValueError(f"on is not a specification of JOIN columns: {on}")

        # suffixes
        self._suffixes = suffixes
        if suffixes:
            if not isinstance(suffixes, tuple) or len(suffixes) != 2:
                raise ValueError("Suffix must be a tuple of length 2.")
            if (suffixes[0] is None) and (suffixes[1] is None):
                raise ValueError("One suffix must not be None.")

        # validate
        if validate:
            if validate not in PD_VALIDATE_TYPES:
                raise ValueError(f"Invalid validate value '{validate}'.")
        self._validate = validate

    def apply(self) -> Table:
        assert self._x_table is not None
        assert self._y_table is not None
        self._new_table = do_join(
            self._y_table,
            self._x_table,
            self._how,
            self._y_cols,
            self._x_cols,
            self._suffixes,
            self._validate,
        )

        return self._new_table


### JOIN HELPERS ###


def infer_join_cols(y_table: Table, x_table: Table) -> list[str]:
    """Given two tables and zero or more join keys, infer the join keys."""

    y_col_names: list[str] = y_table.col_names()
    x_col_names: list[str] = x_table.col_names()
    shared: list[str] = list(set(x_col_names) & set(y_col_names))
    if len(shared) == 0:
        raise ValueError(
            "There are no shared columns to JOIN on. Specify the JOIN columns to use."
        )

    y_col_types: list[str] = [y_table.get_column(x).type for x in shared]
    x_col_types: list[str] = [x_table.get_column(x).type for x in shared]

    if y_col_types != x_col_types:
        raise ValueError(
            "Types don't match for shared columns: "
            + str(shared)
            + "."
            + " Specify matching columns to JOIN on."
        )

    return shared


def cols_match(
    y_table: Table, x_table: Table, y_cols: list[str], x_cols: list[str]
) -> bool:
    """Check that the columns in two tables match."""

    for col in y_cols:
        y_table.is_column(col)
    for col in x_cols:
        x_table.is_column(col)
    for y_col, x_col in zip(y_cols, x_cols):
        if y_table.get_column(y_col).type != x_table.get_column(x_col).type:
            raise ValueError(
                f"JOIN columns ({y_col}, {x_col}) have different types in the two tables."
            )

    return True


class UnionVerb(Verb):
    """UNION"""

    def __init__(self, y_table: Table, x_table: Table) -> None:
        super().__init__()

        self._y_table = y_table
        self._x_table = x_table

        if not columns_match(y_table, x_table):
            raise ValueError("Tables must have identical columns")

    def apply(self) -> Table:
        assert self._x_table is not None
        assert self._y_table is not None
        self._new_table = do_union(self._y_table, self._x_table)

        return self._new_table


### END ###
