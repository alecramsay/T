#!/usr/bin/env python3

"""
PROGRAM - Apply verbs to the stack & update it
"""

import copy
import pprint
from functools import wraps
from contextlib import contextmanager

from .constants import *
from .utils import *

from .readwrite import *
from .datamodel import *
from .stack import *
from .verbs import *

# HELPER_FNS = mod_fns(helpers)


def do_pre_op(required=1):
    """
    A decorator to take care of housekeeping tasks *before* each operation.
    """

    def decorate(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if required == 1 and self.table_stack.len() < required:
                raise Exception("No tables on the stack.")

            if required > 1 and self.table_stack.len() < required:
                raise Exception("Not enough tables on the stack.")

            new_table = func(self, *args, **kwargs)

            return new_table

        return wrapper

    return decorate


def do_post_op(pop=1):
    """
    A decorator to take care of housekeeping tasks *after* each operation.
    """

    def decorate(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            new_table = func(self, *args, **kwargs)
            self._update_stack(new_table, pop)
            self._display_table()

            return new_table

        return wrapper

    return decorate


class Program:
    def __init__(
        self,
        user: Optional[str] = None,
        src: Optional[str] = None,
        data: Optional[str] = None,
        repl=True,
        silent=False,
    ) -> None:
        self.debug: bool = False
        self.repl: bool = repl
        self.silent: bool = silent

        self.user_functions: dict = dict()
        # self.user_functions = HELPER_FNS
        self.table_stack: Stack = Stack()
        self.call_stack: Stack = Stack()
        self.call_stack.push(Namespace({}))

        self.user: Optional[str] = user if user else None
        if self.user:
            self.use(user)
        self.src: Optional[str] = os.path.join(src, "") if src else None
        self.data: Optional[str] = os.path.join(data, "") if data else None

        self.cache: dict = dict()
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
            # reader: TableReader
            # if field_types is None:
            #     reader = TableReader(rel_path)
            #     new_table = reader.read()
            # else:
            #     reader = TableReader(rel_path, col_types=field_types)
            #     new_table = reader.read()

            if new_table.n_rows() == 0:
                return  # Exception occurred while reading ...

            return new_table

        except Exception as e:
            print_execution_exception("read", e)
            return

    @do_pre_op()
    def write(self, rel_path=None, format=None) -> None:
        """WRITE the top table on the stack to disk as a CSV."""

        try:
            top = self.table_stack.first()

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
    def show(self, nrows=None):
        """
        SHOW the top N rows to STDOUT with a header
        """
        try:
            top = self.table_stack.first()

            if top.n_rows() > 0:
                header = top.col_names()
                sample = top.rows[0].values()
                # sample = top.rows[0].values()
                n = nrows if (nrows is not None) else top.n_rows()

                margin = 5
                pad = 5
                header_width = sum([len(x) + pad for x in header]) + margin
                row_width = sum([value_width(x, pad) + pad for x in sample]) + margin
                width = max(header_width, row_width)

                pp = pprint.PrettyPrinter(width=width, compact=False)

                rows = [list(row.values()) for row in top.rows[0:n]]
                out = [header] + rows

                pp.pprint(out)

            else:
                print("This table does not have any rows.")

        except Exception as e:
            print_execution_exception("show", e)
            return

    def history(self, ncommands=None):
        """
        Echo the last N commands entered in the REPL to STDOUT.
        """
        try:
            with open("logs/history.log", "r") as fh:
                lines = fh.readlines()
                nlines = len(lines)
                count = 0

                for line in lines:
                    count += 1

                    if (not ncommands) or (count >= (nlines - ncommands)):
                        print(line.strip())

        except Exception as e:
            print_execution_exception("history", e)
            return

    @do_pre_op()
    def inspect(self, match=None):
        try:
            top = self.table_stack.first()

            cols = (
                [x for x in top.cols if match in x.name]
                if match
                else copy.deepcopy(top.cols)
            )
            filtered = True if len(cols) < len(top.cols) else False

            cols = sorted(cols, key=lambda x: x.name)

            name_width = max([len(x.name) for x in cols])

            print()
            print("TOP TABLE")
            print("---------")
            print("# rows:", top.n_rows())
            print("# cols:", top.n_cols())
            print()

            if filtered:
                print(
                    "{0} of {1} columns matching '{2}'".format(
                        len(cols), top.n_cols(), match
                    )
                )
            else:
                print("All columns")
            print()

            stats_width = 15
            stats_headers = [x.upper() for x in AGG_FNS]
            stats_headers = [x.center(stats_width) for x in stats_headers]
            stats_header = " ".join(stats_headers)
            underlines = "-" * stats_width
            stats_underline = " ".join([underlines] * 5)

            template = (
                "{0:<" + str(name_width) + "} {1:<" + str(name_width) + "} {2:<5} {3:<}"
            )
            print(template.format("NAME", "ALIAS", "TYPE", stats_header))
            print(template.format("----", "----", "----", stats_underline))

            for col in cols:
                alias = col.alias if col.alias else "N/A"

                # stats
                if col.type in [int, float]:
                    values = []
                    for fn in AGG_FNS:
                        v = top.stats[col.name][fn]
                        if not is_missing(v):
                            if (col.type == float and fn != "count") or fn == "avg":
                                out = "{:,.3f}".format(v)
                            else:
                                out = "{:,d}".format(v)
                        else:
                            out = "-"
                        pad = " " * (stats_width - len(out))
                        values.append(pad + out)

                    stats_display = " ".join(values)
                else:
                    stats_display = "Examples: " + ", ".join(
                        [str(x) for x in top.sample_values(col)]
                    )

                print(
                    template.format(col.name, alias, col.type.__name__, stats_display)
                )

            print()
        except Exception as e:
            print_execution_exception("inspect", e)
            return

    @do_pre_op()
    @do_post_op(pop=0)
    def duplicate(self):
        """
        DUPLICATE the table on the top of the stack and push it onto the stack.
        """
        try:
            top = self.table_stack.first()
            new_table = copy.deepcopy(top)

            return new_table

        except Exception as e:
            print_execution_exception("duplicate", e)
            return

    @do_pre_op()
    @do_post_op()
    def sort(self, col_specs):
        """
        SORT the table on the top of the stack.
        """
        try:
            top = self.table_stack.first()

            v = SortVerb(top, col_specs)
            new_table = v.apply()

            return new_table

        except Exception as e:
            print_execution_exception("sort", e)
            return

    @do_pre_op(required=2)
    @do_post_op(pop=2)
    def join(self, y_col=None, x_col=None, **kwargs):
        """
        JOIN the top two tables on the stack, pop them, and push the result.
        """
        try:
            prefix = kwargs.get("prefix", None)

            x_table = self.table_stack.first()
            y_table = self.table_stack.second()

            v = JoinVerb(y_table, x_table, y_col, x_col, prefix)
            new_table = v.apply()

            return new_table

        except Exception as e:
            print_execution_exception("join", e)
            return

    @do_pre_op()
    @do_post_op()
    def pivot(self, **kwargs):
        """
        PIVOT (aka 'aggregate')
        * All -or- specified numeric columns
        * For the whole table -or- by a specified column
        * Push the new table on the stack; don't pop the old table
        """
        try:
            by = kwargs.get("by", None)
            only = kwargs.get("only", None)
            top = self.table_stack.first()

            v = GroupByVerb(top, by=by, only=only)
            new_table = v.apply()

            return new_table

        except Exception as e:
            print_execution_exception("pivot", e)
            return

    @do_pre_op(required=2)
    @do_post_op(pop=2)
    def union(self):
        """
        UNION the top two tables on the stack, pop them, and push the result.
        """
        try:
            x_table = self.table_stack.first()
            y_table = self.table_stack.second()

            v = UnionVerb(y_table, x_table)
            new_table = v.apply()

            return new_table

        except Exception as e:
            print_execution_exception("union", e)
            return

    ### ROW OPERATIONS ###

    @do_pre_op()
    @do_post_op()
    def keep(self, cols):
        """
        KEEP (aka 'select')
        """
        try:
            top = self.table_stack.first()

            v = KeepVerb(top, cols)
            new_table = v.apply()

            return new_table

        except Exception as e:
            print_execution_exception("keep", e)
            return

    @do_pre_op()
    @do_post_op()
    def drop(self, cols):
        """
        DROP (i.e., explicit not-selected/kept)
        """
        try:
            top = self.table_stack.first()

            v = DropVerb(top, cols)
            new_table = v.apply()

            return new_table

        except Exception as e:
            print_execution_exception("drop", e)
            return

    @do_pre_op()
    @do_post_op()
    def rename(self, col_specs):
        """
        RENAME specified columns; keep everything else -- pulled out of SELECT
        """
        try:
            top = self.table_stack.first()

            v = RenameVerb(top, col_specs)
            new_table = v.apply()

            return new_table

        except Exception as e:
            print_execution_exception("rename", e)
            return

    @do_pre_op()
    @do_post_op()
    def alias(self, col_specs):
        """
        ALIAS specified columns. Use original names on write.
        """
        try:
            top = self.table_stack.first()

            v = AliasVerb(top, col_specs)
            new_table = v.apply()

            return new_table

        except Exception as e:
            print_execution_exception("alias", e)
            return

    @do_pre_op()
    @do_post_op()
    def select(self, expr):
        """
        SELECT (aka 'where' or 'filter')
        """
        try:
            top = self.table_stack.first()

            v = SelectVerb(top, expr)
            new_table = v.apply()

            return new_table

        except Exception as e:
            print_execution_exception("select", e)
            return

    @do_pre_op()
    @do_post_op()
    def derive(self, name, expr, data_type=None):
        """
        DERIVE (aka 'let' or 'calc')
        """
        try:
            top = self.table_stack.first()

            v = DeriveVerb(top, name, data_type, expr, user=self.user_functions)
            new_table = v.apply()

            return new_table

        except Exception as e:
            print_execution_exception("derive", e)
            return

    @do_pre_op()
    @do_post_op()
    def first(self, n, pct=None):
        """
        FIRST (aka 'take' or 'top')
        """
        try:
            top = self.table_stack.first()

            v = FirstVerb(top, n, pct)
            new_table = v.apply()

            return new_table

        except Exception as e:
            print_execution_exception("first", e)
            return

    @do_pre_op()
    @do_post_op()
    def last(self, n, pct=None):
        """
        LAST
        """
        try:
            top = self.table_stack.first()

            v = LastVerb(top, n, pct)
            new_table = v.apply()

            return new_table

        except Exception as e:
            print_execution_exception("last", e)
            return

    @do_pre_op()
    @do_post_op()
    def random(self, n, pct=None):
        """
        RANDOM
        """
        try:
            top = self.table_stack.first()

            v = RandomVerb(top, n, pct)
            new_table = v.apply()

            return new_table

        except Exception as e:
            print_execution_exception("random", e)
            return

    @do_pre_op()
    @do_post_op()
    def cast(self, cast_col, type_fn):
        """
        CAST
        """
        try:
            top = self.table_stack.first()

            v = CastVerb(top, cast_col, type_fn)
            new_table = v.apply()

            return new_table

        except Exception as e:
            print_execution_exception("cast", e)
            return

    ### STACK OPERATIONS ###

    def clear(self):
        self.table_stack.clear()
        self._reset_cached_props()

    def pop(self):
        if not self.table_stack.isempty():
            self.table_stack.pop()

            if self.table_stack.isempty():
                self._reset_cached_props()
            else:
                self._update_table_shortcuts()

    @do_pre_op()
    def swap(self):
        self.table_stack.swap()
        self._update_table_shortcuts()

    @do_pre_op()
    def reverse(self):
        self.table_stack.reverse()
        self._update_table_shortcuts()

    @do_pre_op()
    def rotate(self):
        self.table_stack.rotate
        self._update_table_shortcuts()

    ### MISCELLANEOUS ###

    def use(self, rel_path):
        """
        USE - Make user-defined functions available.
        """
        try:
            self.user_functions.update(fns_from_path(rel_path))

        except Exception as e:
            print("Exception loading user-defined functions: ", e)
            return

    """
    LEGACY
    def echo(self, var):
        try:
            result = getattr(self, var)
            print(result)

        except Exception as e:
            print_execution_exception("echo", e)
            return
    """

    ### HOUSEKEEPING ROUTINES ###

    def _reset_cached_props(self):
        """
        Reset cached first (top) table properties for an empty stack
        """
        self.stats = None
        # self.rows = None
        self.cols = None
        self.ncols = None
        self.nrows = None

    def _update_stack(self, new_table, pop=1):
        """
        Implement stack semantics.
        """
        for _ in range(pop):
            self.table_stack.pop()

        self.table_stack.push(new_table)

        # REVIEW - Why did I have this condition?
        # if pop > 0:
        self._calc_column_stats()
        self._update_table_shortcuts()

    def _update_table_shortcuts(self):
        """
        Cache table stats on the program object, so they can be referenced w/o stack ops.
        """
        top = self.table_stack.first()

        # self.rows = top.rows
        self.cols = top.col_names()
        self.ncols = top.n_cols()
        self.nrows = top.n_rows()

        self.stats = top.stats

    def _calc_column_stats(self):
        """
        Automatically calc column statistics for a table
        """
        top = self.table_stack.first()
        agg_cols = [col for col in top.cols if col.type in [int, float]]

        top.stats = aggregate_cols(None, top, agg_cols)

    def _display_table(self):
        if (len(self.call_stack._queue_) == 1) and self.repl and not self.silent:
            self.show(5)


class Namespace:
    def __init__(self, args_dict):
        self._args_ = args_dict

    def bind(self, name, default=None):
        if name in self._args_:
            return self._args_[name]
        else:
            return default if default else None


@contextmanager
def Tables(**kwargs):
    user = kwargs.get("user", None)
    src = kwargs.get("src", None)
    data = kwargs.get("data", None)
    repl = kwargs.get("repl", False)

    T = Program(user=user, src=src, data=data, repl=repl)

    yield T
    del T


def print_execution_exception(verb, e):
    print("Exception executing '{0}' command: ".format(verb, e))


### END ###
