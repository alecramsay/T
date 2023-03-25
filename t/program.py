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

from .readwrite import fns_from_path
from .datamodel import (
    Table,
    Column,
    table_to_csv,
    table_to_json,
    MergeHow,
    ValidationOptions,
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
    AGG_FNS,
)

# HELPER_FNS = mod_fns(helpers) # TODO


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

    cache: dict

    stats: Optional[dict]
    cols: Optional[list[str]]
    ncols: Optional[int]
    nrows: Optional[int]

    def __init__(
        self,
        user: Optional[str] = None,
        src: Optional[str] = None,
        data: Optional[str] = None,
        output: Optional[str] = None,
        log: Optional[str] = None,
        repl=True,
        silent=False,
    ) -> None:
        self.debug = False
        self.repl = repl
        self.silent = silent

        # TODO - Re-work UDFs
        self.user_functions = dict()
        # self.user_functions = HELPER_FNS
        self.table_stack = Stack()
        self.call_stack = Stack()
        self.call_stack.push(Namespace({}))

        self.user = user if user else None
        if self.user:
            assert user is not None
            self.use(user)
        self.src = os.path.join(src, "") if src else None
        self.data = os.path.join(data, "") if data else None

        self.output = os.path.join("temp", "") if output is None else output
        self.log = "logs/history.log" if log is None else log

        self.cache = dict()
        self._reset_cached_props()

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
            print_execution_exception("read", e)
            return

    @do_pre_op()
    def write(
        self, rel_path: Optional[str] = None, format: Optional[str] = None
    ) -> None:
        """WRITE the top table on the stack to disk as a CSV."""

        try:
            top: Table = self.table_stack.first()

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
    def inspect(self, match: Optional[str] = None) -> None:
        try:
            top: Table = self.table_stack.first()

            cols: list[Column] = (
                [x for x in top.cols() if match in x.name]
                if match
                else copy.deepcopy(top.cols())
            )
            filtered: bool = True if len(cols) < len(top.cols()) else False

            cols = sorted(cols, key=lambda x: x.name)

            name_width: int = max([len(x.name) for x in cols])

            print()
            print("TOP TABLE")
            print("---------")
            print("# rows:", top.n_rows)
            print("# cols:", top.n_cols)
            print()

            if filtered:
                print(
                    "{0} of {1} columns matching '{2}'".format(
                        len(cols), top.n_cols, match
                    )
                )
            else:
                print("All columns")
            print()

            stats_width: int = 15
            stats_headers: list[str] = [x.upper() for x in AGG_FNS]
            stats_headers = [x.center(stats_width) for x in stats_headers]
            stats_header: str = " ".join(stats_headers)
            underlines: str = "-" * stats_width
            stats_underline: str = " ".join([underlines] * 5)

            template: str = (
                "{0:<" + str(name_width) + "} {1:<" + str(name_width) + "} {2:<5} {3:<}"
            )
            print(template.format("NAME", "ALIAS", "TYPE", stats_header))
            print(template.format("----", "----", "----", stats_underline))

            for col in cols:
                alias: str = col.alias if col.alias else "N/A"

                # stats
                # TODO - Re-work stats over Pandas
                # if col.type in [int, float]:
                #     values = []
                #     for fn in AGG_FNS:
                #         v = top.stats[col.name][fn]
                #         if not ismissing(v):
                #             if (col.type == float and fn != "count") or fn == "avg":
                #                 out = "{:,.3f}".format(v)
                #             else:
                #                 out = "{:,d}".format(v)
                #         else:
                #             out = "-"
                #         pad = " " * (stats_width - len(out))
                #         values.append(pad + out)

                #     stats_display = " ".join(values)
                # else:
                #     stats_display = "Examples: " + ", ".join(
                #         [str(x) for x in top.sample_values(col)]
                #     )

                # TODO - Re-work stats over Pandas data types: col.type is a string
                # print(
                #     template.format(col.name, alias, col.type.__name__, stats_display)
                # )

            print()
        except Exception as e:
            print_execution_exception("inspect", e)
            return

    @do_pre_op()
    @do_post_op(pop=0)
    def duplicate(self) -> Table | None:
        """DUPLICATE the table on the top of the stack and push it onto the stack."""

        try:
            top: Table = self.table_stack.first()
            new_table: Table = copy.deepcopy(top)

            return new_table

        except Exception as e:
            print_execution_exception("duplicate", e)
            return

    @do_pre_op()
    @do_post_op()
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

    @do_pre_op(required=2)
    @do_post_op(pop=2)
    def join(
        self,
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

    @do_pre_op()
    @do_post_op()
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
            print_execution_exception("pivot", e)
            return

    @do_pre_op(required=2)
    @do_post_op(pop=2)
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

    @do_pre_op()
    @do_post_op()
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

    @do_pre_op()
    @do_post_op()
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

    @do_pre_op()
    @do_post_op()
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

    @do_pre_op()
    @do_post_op()
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

    @do_pre_op()
    @do_post_op()
    def select(self, expr: str) -> Table | None:
        """SELECT (aka 'where' or 'filter')"""

        try:
            top: Table = self.table_stack.first()

            v: SelectVerb = SelectVerb(top, expr)
            new_table: Table = v.apply()

            return new_table

        except Exception as e:
            print_execution_exception("select", e)
            return

    @do_pre_op()
    @do_post_op()
    def derive(self, name: str, expr: str) -> Table | None:
        """DERIVE (aka 'let' or 'calc')"""

        try:
            top: Table = self.table_stack.first()

            v: DeriveVerb = DeriveVerb(
                top, name, expr
            )  # TODO, udf=self.user_functions)
            new_table: Table = v.apply()

            return new_table

        except Exception as e:
            print_execution_exception("derive", e)
            return

    @do_pre_op()
    @do_post_op()
    def first(self, n: int, pct: Optional[Any] = None) -> Table | None:
        """FIRST (aka 'take' or 'top')"""

        try:
            top: Table = self.table_stack.first()

            v: FirstVerb = FirstVerb(top, n, pct)
            new_table: Table = v.apply()

            return new_table

        except Exception as e:
            print_execution_exception("first", e)
            return

    @do_pre_op()
    @do_post_op()
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

    @do_pre_op()
    @do_post_op()
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

    @do_pre_op()
    @do_post_op()
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

    ### MISCELLANEOUS ###

    def use(self, rel_path: str) -> None:
        """USE - Make user-defined functions available."""

        try:
            self.user_functions.update(fns_from_path(rel_path))

        except Exception as e:
            print("Exception loading user-defined functions: ", e)
            return

    ### HOUSEKEEPING ROUTINES ###

    def _reset_cached_props(self) -> None:
        """Reset cached first (top) table properties for an empty stack"""

        self.stats = None
        self.cols = None
        self.ncols = None
        self.nrows = None

    def _update_stack(self, new_table, pop=1) -> None:
        """Implement stack semantics."""

        for _ in range(pop):
            self.table_stack.pop()

        self.table_stack.push(new_table)

        self._calc_column_stats()
        self._update_table_shortcuts()

    def _update_table_shortcuts(self) -> None:
        """Cache table stats on the program object, so they can be referenced w/o stack ops."""

        top: Table = self.table_stack.first()

        self.cols = top.col_names()
        self.ncols = top.n_cols
        self.nrows = top.n_rows

        self.stats = top.stats

    def _calc_column_stats(self) -> None:
        """Automatically calc column statistics for a table"""

        top: Table = self.table_stack.first()
        agg_cols: list[Column] = [col for col in top.cols() if col.type in [int, float]]

        # TODO - Re-work this over Pandas
        # top.stats = aggregate_cols(None, top, agg_cols)

        pass

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
    repl=False,
    silent=False,
) -> Generator[Program, None, None]:
    T: Program = Program(
        user=user, src=src, data=data, output=output, log=log, repl=repl, silent=silent
    )

    yield T
    del T


def print_execution_exception(verb, e) -> None:
    print("Exception executing '{0}' command: ".format(verb, e))


### END ###
