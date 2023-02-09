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


class JoinVerb(Verb):
    pass  # TODO


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
