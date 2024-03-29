# udf.py
#!/usr/bin/env python3

"""
USER-DEFINED FUNCTIONS
"""

import inspect
from collections import defaultdict
from typing import Any

from .readwrite import fns_from_path
from .utils import find_args_string, split_args_string


class UDF:
    user_fns: dict[str, Any]
    ref_counts: dict[str, int]

    def __init__(self, rel_path: str) -> None:
        self.user_fns = fns_from_path(rel_path)
        self.ref_counts = defaultdict(int)

    def names(self) -> list[str]:
        """Return a list of user-defined function names."""

        return list(self.user_fns.keys())

    def source(self, fn_name: str) -> str:
        """Return the source code for a user-defined function."""

        return inspect.getsource(self.user_fns[fn_name])

    def count(self, fn_name: str) -> int:
        """Return the number of times a function has been referenced."""

        self.ref_counts[fn_name] += 1

        return self.ref_counts[fn_name]

    def reset(self) -> None:
        """Reset the reference counts for all functions."""

        self.ref_counts = defaultdict(int)

    def alias(self, fn_name: str, ref: int) -> str:
        """Create a wrapper function name from the wrapped function name."""

        return f"_re_{fn_name}_{str(ref)}"

    def wrap(self, alias: str, udf_name: str, arg_map: dict[str, str]) -> str:
        """Generate source for a wrapper function that converts a UDF to a Pandas-compatible row function."""

        wrapper: str = f"def {alias}(row):\n"

        for arg, col in arg_map.items():
            wrapper += f"    {arg} = '{col}'\n"

        args: str = ", ".join([f"row[{arg}]" for arg in arg_map.keys()])
        wrapper += f"    return {udf_name}({args})\n"

        return wrapper

    def isudf(self, fn_name: str) -> bool:
        return fn_name in self.user_fns


### HELPERS ###


def extract_args_list(def_or_call: str) -> list[str]:
    """Find the arguments in a function definition or call.

    Examples:

    def composite(ag, gov, sen1, sen2, pres1, pres2) -> float:
    composite(D_2020_ag, D_2020_gov, D_2016_sen, D_2020_sen, D_2016_pres, D_2020_pres)
    """

    left: int
    right: int
    left, right = find_args_string(def_or_call)

    args: list[str] = split_args_string(def_or_call[left + 1 : right])

    return args


def map_args(call_expr: str, source: str) -> dict[str, str]:
    """Map function arguments to call arguments."""

    def_line: str = source.splitlines()[0]
    def_args: list[str] = extract_args_list(def_line)
    call_args: list[str] = extract_args_list(call_expr)

    return dict(zip(def_args, call_args))


### END ###
