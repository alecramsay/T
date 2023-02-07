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

    def _validate_new_cols(self, new_col_refs=None, table=None) -> None:
        """Validate new column references. Raise an exception when one or more are not valid."""

        new_col_refs: list[str] = new_col_refs or self._new_col_refs
        table: Table = table or self._x_table

        table.could_be_cols(new_col_refs)

    def _unzip_col_specs(self, col_specs) -> tuple[list[str], list[str]]:
        """Unzip a list of column specs into a list existing column refs and a list of new column refs."""

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

        drop_col_refs: list[str] = [
            name for name in self._x_table.col_names() if name not in self._col_refs
        ]
        self._new_table.drop_cols(drop_col_refs)

        return self._new_table


### END ###
