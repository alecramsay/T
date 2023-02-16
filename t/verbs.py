#!/usr/bin/env python3

"""
VERBS - GIVEN ONE OR MORE INPUT TABLES, CREATE A NEW TABLE

NOTE - These verbs don't know anything about the program stack.
"""

from typing import NoReturn

from .constants import *
from .utils import *
from .datamodel import *


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

    def __init__(self) -> None:
        self._x_table: Table = None
        self._y_table: Table = None
        self._col_refs: list[str] = list()
        self._new_col_refs: list[str] = list()

        self._new_table: Table = None

    def apply(self) -> NoReturn:
        raise Exception("Not implemented.")

    ### VALIDATION HELPERS ###

    def _validate_col_refs(self, col_refs=None, table=None) -> None:
        """Validate existing column references. Raise an exception when one or more are not valid."""

        col_refs: list[str] = col_refs or self._col_refs
        table: Table = table or self._x_table

        table.are_cols(col_refs)

    def _validate_new_col_refs(self, new_col_refs=None, table=None) -> None:
        """Validate new column references. Raise an exception when one or more are not valid."""

        new_col_refs: list[str] = new_col_refs or self._new_col_refs
        table: Table = table or self._x_table

        table.could_be_cols(new_col_refs)

    def _unzip_col_specs(self, col_specs=None) -> tuple[list[str], list[str]]:
        """Unzip a list of column specs into a list existing column refs and a list of new column refs."""

        col_specs: list[str] = col_specs or self._col_specs

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

    def _unzip_sort_specs(self, col_specs=None) -> tuple[list[str], list[str]]:
        """Unzip a list of sort specs into a list of column refs and sort order booleans."""

        col_specs: list[str] = col_specs or self._col_specs

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
    """KEEP (aka 'select')"""

    def __init__(self, x_table, keep_cols) -> None:
        super().__init__()

        self._x_table = x_table
        self._col_refs = [x.strip() for x in keep_cols]

        self._validate_col_refs()

    def apply(self) -> Table:
        self._new_table: Table = self._x_table.copy()
        self._new_table.do_keep_cols(self._col_refs)

        return self._new_table


class DropVerb(Verb):
    """DROP (i.e., explicit not-selected/kept)"""

    def __init__(self, x_table, drop_cols) -> None:
        super().__init__()

        self._x_table = x_table
        self._col_refs = [x.strip() for x in drop_cols]

        self._validate_col_refs()

    def apply(self) -> Table:
        self._new_table: Table = self._x_table.copy()

        keep_cols: list[str] = [
            name for name in self._x_table.col_names() if name not in self._col_refs
        ]
        self._new_table.do_keep_cols(keep_cols)

        return self._new_table


class RenameVerb(Verb):
    """RENAME specified columns & keep everything else"""

    def __init__(self, x_table, col_specs) -> None:
        super().__init__()

        self._x_table = x_table
        self._col_specs = col_specs
        self._col_refs, self._new_col_refs = self._unzip_col_specs()

        self._validate_col_refs()
        self._validate_new_col_refs()

    def apply(self) -> Table:
        self._new_table: Table = self._x_table.copy()

        renames: dict() = {
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

    def __init__(self, x_table, col_specs) -> None:
        super().__init__()

        self._x_table = x_table
        self._col_specs = col_specs
        self._col_refs, self._new_col_refs = self._unzip_col_specs()

        self._validate_col_refs()
        self._validate_new_col_refs()

    def apply(self) -> Table:
        self._new_table: Table = self._x_table.copy()

        renames: dict() = {
            from_col: to_col
            for from_col, to_col in zip(self._col_refs, self._new_col_refs)
        }
        self._new_table.do_rename_cols(renames)

        aliases: dict() = {
            from_col: to_col
            for from_col, to_col in zip(self._new_col_refs, self._col_refs)
        }
        self._new_table.do_alias_cols(aliases)

        return self._new_table


class SelectVerb(Verb):
    pass  # TODO


class FirstVerb(Verb):
    """FIRST (aka 'take')"""

    def __init__(self, x_table, n, pct=None) -> None:
        super().__init__()

        self._x_table = x_table
        self._take: int = n if not pct else max(round(n * (x_table.n_rows() / 100)), 1)

    def apply(self) -> Table:
        self._new_table: Table = self._x_table.copy()
        self._new_table.do_first(self._take)

        return self._new_table


class LastVerb(Verb):
    """LAST (complement of 'first')"""

    def __init__(self, x_table, n, pct=None) -> None:
        super().__init__()

        self._x_table = x_table
        self._take: int = n if not pct else max(round(n * (x_table.n_rows() / 100)), 1)

    def apply(self) -> Table:
        self._new_table: Table = self._x_table.copy()
        self._new_table.do_last(self._take)

        return self._new_table


class SampleVerb(Verb):
    """SAMPLE (like 'first' except it's randomly selected rows)"""

    def __init__(self, x_table, n, pct=None) -> None:
        super().__init__()

        self._x_table = x_table
        self._take: int = n if not pct else max(round(n * (x_table.n_rows() / 100)), 1)

    def apply(self) -> Table:
        self._new_table: Table = self._x_table.copy()
        self._new_table.do_sample(self._take)

        return self._new_table


class CastVerb(Verb):
    pass  # TODO


class DeriveVerb(Verb):
    pass  # TODO


### TABLE FILTERS ###


class SortVerb(Verb):
    """SORT -- sort rows in place. <<< 'ORDER_BY'"""

    def __init__(self, x_table, col_specs) -> None:
        super().__init__()

        self._x_table = x_table
        self._col_specs = col_specs
        self._ascending_list: list[bool]
        self._col_refs, self._ascending_list = self._unzip_sort_specs()

        self._validate_col_refs()

    def apply(self) -> Table:
        self._new_table: Table = self._x_table.copy()

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
        self, x_table, by: list[str], *, only: list[str] = None, agg: list[str] = None
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
        self._new_table: Table = self._x_table.copy()

        self._new_table.do_groupby(self._group_cols, self._agg_cols, self._agg_fns)

        return self._new_table


PD_JOIN_TYPES: list[str] = ["left", "right", "outer", "inner", "cross"]
PD_VALIDATE_TYPES: list[str] = ["1:1", "1:m", "m:1", "m:m"]


class JoinVerb(Verb):
    """JOIN the two tables on the top of the stack & return a new table.

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

    def __init__(
        self,
        y_table: Table,
        x_table: Table,
        *,
        how: str = "inner",
        on=None,
        suffixes=(
            "_y",
            "_x",
        ),  # Note: This is reversed from Pandas, to match T stack semantics.
        validate: str = None,
    ) -> None:
        super().__init__()

        self._y_table = y_table
        self._x_table = x_table

        # how
        self._how: str = how
        if how not in PD_JOIN_TYPES:
            raise ValueError(f"Invalid join type '{how}'.")

        # on (columns)
        self._y_col: str | list[str]
        self._x_col: str | list[str]

        if on is None:
            # No columns are specified -- infer them
            shared: list[str] = infer_join_cols(y_table, x_table)
            if len(shared) == 1:
                self._y_col: str = shared[0]
                self._x_col: str = shared[0]
            else:
                self._y_col: str = shared
                self._x_col: str = shared

        elif isinstance(on, str):
            # One column is specified -- make sure it exists in both tables with matching types
            cols_match(y_table, x_table, [on], [on])
            self._y_col: str = on
            self._x_col: str = on

        elif is_list_of_str(on):
            # One list of columns
            cols_match(y_table, x_table, on, on)
            self._y_col: str = on
            self._x_col: str = on

        elif (
            isinstance(on, list)
            and len(on) == 2
            and is_list_of_str(on[0])
            and is_list_of_str(on[1])
        ):
            # Two lists of columns
            cols_match(y_table, x_table, on[0], on[1])
            self._y_col: str = on[0]
            self._x_col: str = on[1]

        else:
            raise ValueError(f"on is not a specification of JOIN columns: {on}")

        # suffixes
        self._suffixes: tuple = suffixes
        if suffixes:
            if not isinstance(suffixes, tuple) or len(suffixes) != 2:
                raise ValueError("Suffix must be a tuple of length 2.")
            if (suffixes[0] is None) and (suffixes[1] is None):
                raise ValueError("One suffix must not be None.")

        # validate
        if validate:
            if validate not in PD_VALIDATE_TYPES:
                raise ValueError(f"Invalid validate value '{validate}'.")
        self._validate: str = validate

    def apply(self) -> Table:
        self._new_table = do_join(
            self._y_table,
            self._x_table,
            self._how,
            self._y_col,
            self._x_col,
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

    def __init__(self, y_table, x_table) -> None:
        super().__init__()

        self._y_table = y_table
        self._x_table = x_table

        if not columns_match(y_table, x_table):
            raise ValueError("Tables must have identical columns")

    def apply(self) -> Table:
        self._new_table = do_union(self._y_table, self._x_table)

        return self._new_table


### END ###
