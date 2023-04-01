# program.py
#!/usr/bin/env python3

"""
PROGRAM - Apply verbs to the stack & update it
"""

import os
import copy
import pprint
from functools import wraps
from contextlib import contextmanager
from typing import Any, Callable, Optional, Generator

from .utils import value_width
from .udf import UDF
from .readwrite import fns_from_path
from .datamodel import (
    Table,
    Column,
    table_to_csv,
    table_to_json,
    MergeHow,
    ValidationOptions,
    PD_DESCRIBE_TYPES,
)
from .stack import Stack
from .commands import Namespace
from .verbs import (
    KeepVerb,
    DropVerb,
    RenameVerb,
    SortVerb,
    SelectVerb,
    DeriveVerb,
    AliasVerb,
    FirstVerb,
    LastVerb,
    SampleVerb,
    CastVerb,
    SortVerb,
    JoinVerb,
    GroupByVerb,
    UnionVerb,
)


def do_pre_op(required: int = 1) -> Callable[..., Callable[..., Any]]:
    """A decorator to take care of housekeeping tasks *before* each operation."""

    def decorate(func) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(self, *args, **kwargs) -> Any:
            if required == 1 and self.table_stack.len() < required:
                raise Exception("No tables on the stack.")

            if required > 1 and self.table_stack.len() < required:
                raise Exception("Not enough tables on the stack.")

            new_table: Table = func(self, *args, **kwargs)

            return new_table

        return wrapper

    return decorate


def do_post_op(pop: int = 1) -> Callable[..., Callable[..., Any]]:
    """A decorator to take care of housekeeping tasks *after* each operation."""

    def decorate(func) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(self, *args, **kwargs) -> Any:
            new_table: Table = func(self, *args, **kwargs)
            if new_table is None:
                raise Exception("Command failed. No new table created.")
            self._update_stack(new_table, pop)
            self._display_table()

            return new_table

        return wrapper

    return decorate


class Program:
    """An environment for running a T program."""

    debug: bool
    repl: bool
    silent: bool
    user_functions: dict
    table_stack: Stack
    call_stack: Stack
    user: Optional[str]
    src: Optional[str]
    data: Optional[str]
    output: Optional[str]
    log: str

    command: str  # current command

    cache: dict

    stats: Optional[dict]
    cols: Optional[list[str]]
    _n_cols: Optional[int]
    _n_rows: Optional[int]

    def __init__(
        self,
        user: Optional[str] = None,
        src: Optional[str] = None,
        data: Optional[str] = None,
        output: Optional[str] = None,
        log: Optional[str] = None,
        repl: bool = True,
        silent: bool = False,
        debug: bool = False,
    ) -> None:
        self.debug = debug
        self.repl = repl
        self.silent = silent

        self.table_stack = Stack()
        self.call_stack = Stack()
        self.call_stack.push(Namespace({}))

        self.user = user if user else None
        self.src = os.path.join(src, "") if src else None
        self.data = os.path.join(data, "") if data else None

        self.output = (
            os.path.join("temp", "") if (output is None) or (output == "") else output
        )
        self.log = "logs/history.log" if (log is None) or (log == "") else log

        self.command = ""
        self.cache = dict()
        self._reset_cached_props()

    @property
    def n_cols(self) -> int:
        """Return the number of columns in the top table on the stack."""

        assert self._n_cols is not None
        return self._n_cols

    @property
    def n_rows(self) -> int:
        """Return the number of rows in the top table on the stack."""

        assert self._n_rows is not None
        return self._n_rows

    ### TABLE OPERATIONS ###

    @do_post_op(pop=0)
    def read(self, rel_path: str, field_types=None) -> Table | None:
        """READ a CSV table from disk and push it onto the stack."""

        try:
            if self.data:
                rel_path = self.data + rel_path

            new_table: Table = Table()
            new_table.read(rel_path)

            if new_table.n_rows == 0:
                raise Exception("No rows in table.")

            return new_table

        except Exception as e:
            print_execution_exception("from", e)
            return

    @do_pre_op()
    def write(
        self, rel_path: Optional[str] = None, format: Optional[str] = None
    ) -> None:
        """WRITE the top table on the stack to disk as a CSV."""

        try:
            top: Table = self.table_stack.first()

            if rel_path and self.output:
                rel_path = self.output + rel_path

            if (format is None) or (format == "CSV"):
                table_to_csv(top, rel_path)
            elif format == "JSON":
                table_to_json(top, rel_path)
            else:
                raise Exception("Unrecognized format.")

        except Exception as e:
            print_execution_exception("write", e)
            return

    @do_pre_op()
    def show(self, nrows: Optional[int] = None) -> None:
        """SHOW the top N rows to STDOUT with a header"""

        try:
            top: Table = self.table_stack.first()

            if top.n_rows > 0:
                header: list[str] = top.col_names()
                sample: list = top.nth_row(0)
                n: int = nrows if (nrows is not None) else top.n_rows

                margin: int = 5
                pad: int = 5
                header_width: int = sum([len(x) + pad for x in header]) + margin
                row_width: int = (
                    sum([value_width(x, pad) + pad for x in sample]) + margin
                )
                width: int = max(header_width, row_width)

                pp: pprint.PrettyPrinter = pprint.PrettyPrinter(
                    width=width, compact=False
                )

                rows: list[list[str]] = top.first_n_rows(n)
                out: list[list[str]] = [header] + rows

                pp.pprint(out)

            else:
                print("This table does not have any rows.")

        except Exception as e:
            print_execution_exception("show", e)
            return

    def history(self, ncommands: Optional[int] = None) -> None:
        """Echo the last N commands entered in the REPL to STDOUT."""

        try:
            with open(self.log, "r") as fh:
                lines: list[str] = fh.readlines()
                nlines: int = len(lines)
                count: int = 0

                for line in lines:
                    count += 1

                    if (not ncommands) or (count >= (nlines - ncommands)):
                        print(line.strip())

        except Exception as e:
            print_execution_exception("history", e)
            return

    @do_pre_op()
    def inspect(self, filter_on: Optional[str] = None) -> None:
        try:
            top: Table = self.table_stack.first()

            print()
            print("TOP TABLE")
            print("---------")
            print("# rows:", top.n_rows)
            print("# cols:", top.n_cols)
            print()

            cols: list[Column] = (
                [x for x in top.cols() if filter_on in x.name]
                if filter_on
                else copy.deepcopy(top.cols())
            )
            cols = [x for x in cols if x.type in PD_DESCRIBE_TYPES]

            filtered: bool = True if filter_on else False

            if len(cols) == 0:
                print("No matching numeric columns to inspect.")
                print()
                return

            if filtered:
                print(
                    f"{len(cols)} of {top.n_cols} numeric column names matching '{filter_on}'"
                )
            else:
                print("All numeric columns")
            print()

            cols = sorted(cols, key=lambda x: x.name)

            assert top.stats is not None
            stats_cols: set[str] = set(top.stats.keys())

            name_width: int = max([len(x.name) for x in cols])
            alias_width: int = max(max([len(x.alias) for x in cols]), 5)

            stats_metrics: list[str] = [
                "count",
                "sum",
                "mean",
                "median",
                "std",
                "min",
                "25%",
                "50%",
                "75%",
                "max",
            ]
            stats_width: int = 15
            stats_headers: list[str] = [x.upper() for x in stats_metrics]
            stats_headers = [x.center(stats_width) for x in stats_headers]
            stats_header: str = " ".join(stats_headers)
            underlines: str = "-" * stats_width
            stats_underline: str = " ".join([underlines] * len(stats_metrics))

            template: str = (
                "{0:<"
                + str(name_width)
                + "} {1:<"
                + str(alias_width)
                + "} {2:<7} {3:<}"
            )

            print(template.format("NAME", "ALIAS", "TYPE", stats_header))
            print(
                template.format(
                    "-" * name_width, "-" * alias_width, "-------", stats_underline
                )
            )

            for col in cols:
                alias: str = col.alias if col.alias else "N/A"

                # stats
                if col.name in stats_cols:
                    values: list = []
                    for fn in stats_metrics:
                        v: int | float = top.stats[col.name][fn]
                        # https://docs.python.org/2/library/string.html#format-specification-mini-language
                        out: str
                        if fn == "count":
                            out = "{:,d}".format(int(v))
                        else:
                            out = "{:,.3f}".format(v)

                        pad: str = " " * (stats_width - len(out))
                        values.append(pad + out)

                    stats_display: str = " ".join(values)

                    print(template.format(col.name, alias, col.type, stats_display))

            print()
        except Exception as e:
            print_execution_exception("inspect", e)
            return

    @do_post_op(pop=0)
    @do_pre_op()
    def duplicate(self) -> Table | None:
        """DUPLICATE the table on the top of the stack and push it onto the stack."""

        try:
            top: Table = self.table_stack.first()
            new_table: Table = copy.deepcopy(top)

            return new_table

        except Exception as e:
            print_execution_exception("duplicate", e)
            return

    @do_post_op()
    @do_pre_op()
    def sort(self, col_specs: list) -> Table | None:
        """SORT the table on the top of the stack."""

        try:
            top: Table = self.table_stack.first()

            v: SortVerb = SortVerb(top, col_specs)
            new_table: Table = v.apply()

            return new_table

        except Exception as e:
            print_execution_exception("sort", e)
            return

    @do_post_op(pop=2)
    @do_pre_op(required=2)
    def join(
        self,
        *,
        how: MergeHow,
        on: Optional[str | list[str] | list[list[str]]] = None,
        suffixes: tuple[str, str]
        | tuple[None, str]
        | tuple[str, None] = (
            "_y",
            "_x",
        ),  # Note: This is reversed from Pandas, to match T stack semantics.
        validate: Optional[ValidationOptions] = None,
    ) -> Table | None:
        """JOIN the top two tables on the stack, pop them, and push the result."""

        try:
            x_table: Table = self.table_stack.first()
            y_table: Table = self.table_stack.second()

            v: JoinVerb = JoinVerb(
                y_table, x_table, how=how, on=on, suffixes=suffixes, validate=validate
            )
            new_table: Table = v.apply()

            return new_table

        except Exception as e:
            print_execution_exception("join", e)
            return

    @do_post_op()
    @do_pre_op()
    def groupby(
        self,
        by: list[str],
        *,
        only: Optional[list[str]] = None,
        agg: Optional[list[str]] = None,
    ) -> Table | None:
        """GROUP BY (aka 'aggregate')

        * All -or- specified numeric columns
        * For the whole table -or- by a specified column
        * Push the new table on the stack; don't pop the old table
        """

        try:
            top: Table = self.table_stack.first()

            v: GroupByVerb = GroupByVerb(top, by=by, only=only, agg=agg)
            new_table: Table = v.apply()

            return new_table

        except Exception as e:
            print_execution_exception("groupby", e)
            return

    @do_post_op(pop=2)
    @do_pre_op(required=2)
    def union(self) -> Table | None:
        """UNION the top two tables on the stack, pop them, and push the result."""

        try:
            x_table: Table = self.table_stack.first()
            y_table: Table = self.table_stack.second()

            v: UnionVerb = UnionVerb(y_table, x_table)
            new_table: Table = v.apply()

            return new_table

        except Exception as e:
            print_execution_exception("union", e)
            return

    ### ROW OPERATIONS ###

    @do_post_op()
    @do_pre_op()
    def keep(self, cols: list[str]) -> Table | None:
        """KEEP (aka 'select')"""

        try:
            top: Table = self.table_stack.first()

            v: KeepVerb = KeepVerb(top, cols)
            new_table: Table = v.apply()

            return new_table

        except Exception as e:
            print_execution_exception("keep", e)
            return

    @do_post_op()
    @do_pre_op()
    def drop(self, cols: list[str]) -> Table | None:
        """DROP (i.e., explicit not-selected/kept)"""

        try:
            top: Table = self.table_stack.first()

            v: DropVerb = DropVerb(top, cols)
            new_table: Table = v.apply()

            return new_table

        except Exception as e:
            print_execution_exception("drop", e)
            return

    @do_post_op()
    @do_pre_op()
    def rename(self, col_specs: list) -> Table | None:
        """RENAME specified columns; keep everything else -- pulled out of SELECT"""

        try:
            top: Table = self.table_stack.first()

            v: RenameVerb = RenameVerb(top, col_specs)
            new_table: Table = v.apply()

            return new_table

        except Exception as e:
            print_execution_exception("rename", e)
            return

    @do_post_op()
    @do_pre_op()
    def alias(self, col_specs: list) -> Table | None:
        """ALIAS specified columns. Use original names on write."""

        try:
            top: Table = self.table_stack.first()

            v: AliasVerb = AliasVerb(top, col_specs)
            new_table: Table = v.apply()

            return new_table

        except Exception as e:
            print_execution_exception("alias", e)
            return

    @do_post_op()
    @do_pre_op()
    def select(self, expr: str) -> Table | None:
        """SELECT (aka 'where' or filter')"""

        try:
            top: Table = self.table_stack.first()

            v: SelectVerb = SelectVerb(top, expr)
            new_table: Table = v.apply()

            return new_table

        except Exception as e:
            print_execution_exception("select", e)
            return

    @do_post_op()
    @do_pre_op()
    def derive(self, name: str, expr: str) -> Table | None:
        """DERIVE (aka 'let' or calc')"""

        try:
            top: Table = self.table_stack.first()
            udf: Optional[UDF] = UDF(self.user) if self.user else None

            v: DeriveVerb = DeriveVerb(top, name, expr, udf=udf)
            new_table: Table = v.apply()

            return new_table

        except Exception as e:
            print_execution_exception("derive", e)
            return

    @do_post_op()
    @do_pre_op()
    def first(self, n: int, pct: Optional[Any] = None) -> Table | None:
        """FIRST (aka 'take' or top')"""

        try:
            top: Table = self.table_stack.first()

            v: FirstVerb = FirstVerb(top, n, pct)
            new_table: Table = v.apply()

            return new_table

        except Exception as e:
            print_execution_exception("first", e)
            return

    @do_post_op()
    @do_pre_op()
    def last(self, n: int, pct: Optional[Any] = None) -> Table | None:
        """LAST"""

        try:
            top: Table = self.table_stack.first()

            v: LastVerb = LastVerb(top, n, pct)
            new_table: Table = v.apply()

            return new_table

        except Exception as e:
            print_execution_exception("last", e)
            return

    @do_post_op()
    @do_pre_op()
    def sample(self, n: int, pct=None) -> Table | None:
        """SAMPLE"""

        try:
            top: Table = self.table_stack.first()

            v: SampleVerb = SampleVerb(top, n, pct)
            new_table: Table = v.apply()

            return new_table

        except Exception as e:
            print_execution_exception("random", e)
            return

    @do_post_op()
    @do_pre_op()
    def cast(self, cast_cols: list[str], type_fn: str) -> Table | None:
        """CAST"""

        try:
            top: Table = self.table_stack.first()

            v: CastVerb = CastVerb(top, cast_cols, type_fn)
            new_table: Table = v.apply()

            return new_table

        except Exception as e:
            print_execution_exception("cast", e)
            return

    ### STACK OPERATIONS ###

    def clear(self) -> None:
        self.table_stack.clear()
        self._reset_cached_props()

    def pop(self) -> None:
        if not self.table_stack.isempty():
            self.table_stack.pop()

            if self.table_stack.isempty():
                self._reset_cached_props()
            else:
                self._update_table_shortcuts()

    @do_pre_op()
    def swap(self) -> None:
        self.table_stack.swap()
        self._update_table_shortcuts()

    @do_pre_op()
    def reverse(self) -> None:
        self.table_stack.reverse()
        self._update_table_shortcuts()

    @do_pre_op()
    def rotate(self) -> None:
        self.table_stack.rotate
        self._update_table_shortcuts()

    ### HOUSEKEEPING ROUTINES ###

    def _reset_cached_props(self) -> None:
        """Reset cached first (top) table properties for an empty stack"""

        self.stats = None
        self.cols = None
        self._n_cols = None
        self._n_rows = None

    def _update_stack(self, new_table, pop=1) -> None:
        """Implement stack semantics."""

        if self.debug:
            if self.table_stack.isempty():
                print("Before - Stack is empty.")
            else:
                print(f"Before - Stack size: {self.table_stack.len()}")
                for i, t in enumerate(self.table_stack._queue_):
                    print(
                        f"Table {i+1} ({id(t)}) - {t.command[:10]} ...: {t.n_rows} rows, {t.n_cols} cols"
                    )

        for _ in range(pop):
            self.table_stack.pop()

        new_table.command = self.command  # for debugging
        self.table_stack.push(new_table)

        self._calc_column_stats()
        self._update_table_shortcuts()

        if self.debug:
            if self.table_stack.isempty():
                print("After - Stack is empty.")
            else:
                print(f"After - Stack size: {self.table_stack.len()}")
                for i, t in enumerate(self.table_stack._queue_):
                    print(
                        f"Table {i+1} ({id(t)}) - {t.command[:10]} ...: {t.n_rows} rows, {t.n_cols} cols"
                    )

            print()

    def _update_table_shortcuts(self) -> None:
        """Cache table stats on the program object, so they can be referenced w/o stack ops."""

        top: Table = self.table_stack.first()

        self.cols = top.col_names()
        self._n_cols = top.n_cols
        self._n_rows = top.n_rows

        self.stats = top.stats

    def _calc_column_stats(self) -> None:
        """Automatically calc column statistics for a table"""

        top: Table = self.table_stack.first()
        top._calc_stats()

    def _display_table(self) -> None:
        if (len(self.call_stack._queue_) == 1) and self.repl and not self.silent:
            self.show(5)


@contextmanager
def Tables(
    *,
    user: Optional[str] = None,
    src: Optional[str] = None,
    data: Optional[str] = None,
    output: Optional[str] = None,
    log: Optional[str] = None,
    repl: bool = False,
    silent: bool = False,
    debug: bool = False,
) -> Generator[Program, None, None]:
    T: Program = Program(
        user=user,
        src=src,
        data=data,
        output=output,
        log=log,
        repl=repl,
        silent=silent,
        debug=debug,
    )

    yield T
    del T


def print_execution_exception(verb, e) -> None:
    print(f"Exception executing '{verb}' command: {e}")


### END ###
