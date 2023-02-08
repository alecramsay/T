#!/usr/bin/env python3

"""
VERBS - GIVEN ONE OR MORE INPUT TABLES, CREATE A NEW TABLE

NOTE - These verbs don't know anything about the program stack.
"""

from typing import NoReturn

from .constants import *
from .utils import *
from .datamodel import *


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
        self._new_table.keep_cols(self._col_refs)

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
        self._new_table.keep_cols(keep_cols)

        return self._new_table


class RenameVerb(Verb):
    """RENAME specified columns & keep everything else"""

    def __init__(self, x_table, col_specs) -> None:
        super().__init__()

        self._x_table = x_table
        self._col_refs, self._new_col_refs = self._unzip_col_specs(col_specs)

        self._validate_col_refs()
        self._validate_new_col_refs()

    def apply(self) -> Table:
        self._new_table: Table = self._x_table.copy()

        renames: dict() = {
            from_col: to_col
            for from_col, to_col in zip(self._col_refs, self._new_col_refs)
        }
        self._new_table.rename_cols(renames)

        return self._new_table


class AliasVerb(Verb):
    """ALIAS specified columns

    - Aliasing is just like renaming, except it retains the alias so it can be reverted.
    - Use original column names on write.
    """

    def __init__(self, x_table, col_specs) -> None:
        super().__init__()

        self._x_table = x_table
        self._col_refs, self._new_col_refs = self._unzip_col_specs(col_specs)

        self._validate_col_refs()
        self._validate_new_col_refs()

    def apply(self) -> Table:
        self._new_table: Table = self._x_table.copy()

        renames: dict() = {
            from_col: to_col
            for from_col, to_col in zip(self._col_refs, self._new_col_refs)
        }
        self._new_table.rename_cols(renames)

        aliases: dict() = {
            from_col: to_col
            for from_col, to_col in zip(self._new_col_refs, self._col_refs)
        }
        self._new_table.alias_cols(aliases)

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
        self._new_table.first(self._take)

        return self._new_table


class LastVerb(Verb):
    """LAST (complement of 'first')"""

    def __init__(self, x_table, n, pct=None) -> None:
        super().__init__()

        self._x_table = x_table
        self._take: int = n if not pct else max(round(n * (x_table.n_rows() / 100)), 1)

    def apply(self) -> Table:
        self._new_table: Table = self._x_table.copy()
        self._new_table.last(self._take)

        return self._new_table


class SampleVerb(Verb):
    """SAMPLE (like 'first' except it's randomly selected rows)"""

    def __init__(self, x_table, n, pct=None) -> None:
        super().__init__()

        self._x_table = x_table
        self._take: int = n if not pct else max(round(n * (x_table.n_rows() / 100)), 1)

    def apply(self) -> Table:
        self._new_table: Table = self._x_table.copy()
        self._new_table.sample(self._take)

        return self._new_table


class CastVerb(Verb):
    pass  # TODO


class DeriveVerb(Verb):
    pass  # TODO


### TABLE FILTERS ###


class SortVerb(Verb):
    pass  # TODO


class GroupVerb(Verb):
    pass  # TODO


class JoinVerb(Verb):
    pass  # TODO


class UnionVerb(Verb):
    pass  # TODO


### END ###
