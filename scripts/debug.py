#!/usr/bin/env python3

"""
DEBUG sandbox

User-defined functions:

https://stackoverflow.com/questions/26886653/create-new-column-based-on-values-from-other-columns-apply-a-function-of-multi

1. User writes & tests a function that takes column values and constants as arguments.
2. Get the source translate that into a lambda function that takes a row as an argument
   with column values converted to row[column] references.
3. Apply that lambda function to the dataframe.

Example:

def composite(ag, gov, sen1, sen2, pres1, pres2) -> float:
    # NOTE - This could be fleshed out to handle missing elections.
    return ((ag + gov) / 2 + (sen1 + sen2) / 2 + (pres1 + pres2) / 2) / 3

expr: str = "composite(D_2020_ag, D_2020_gov, D_2016_sen, D_2020_sen, D_2016_pres, D_2020_pres))"
tokens: list[str] = tokenize(expr)
re_expr: str = rewrite_expr("df", tokens, self.col_names())

-----

def fn(row):
    ...

df.apply(fn, axis=1)                  <<< This form works

TODO
- Re-write full functions
- UDF only
- Constants, e.g., 1 - df[col]  <<< This works
- UDF w/in a broader expression <<< These need to be re-written in call-specific way to accept a row
"""

import inspect

from t import *

# TODO
# - Map function arguments to call arguments
# - Generate a wrapper function
# - Generate the Pandas expression

# Setup

rel_path: str = "user/alec.py"
user_fns: dict[str, Any] = fns_from_path(rel_path)

call_expr: str = (
    "composite(D_2020_ag, D_2020_gov, D_2016_sen, D_2020_sen, D_2016_pres, D_2020_pres)"
)
udf_name: str = "composite"
source: str = inspect.getsource(user_fns[udf_name])

col_names: list[str] = [
    "D_2020_ag",
    "D_2020_gov",
    "D_2016_sen",
    "D_2020_sen",
    "D_2016_pres",
    "D_2020_pres",
]

#


def parse_args(def_or_call: str) -> list[str]:
    """Find the arguments in a function definition or call.

    Examples:

    def composite(ag, gov, sen1, sen2, pres1, pres2) -> float:
    composite(D_2020_ag, D_2020_gov, D_2016_sen, D_2020_sen, D_2016_pres, D_2020_pres)
    """

    open_i: int = def_or_call.find("(")
    close_i: int = def_or_call.find(")")
    args: list[str] = [x.strip() for x in def_or_call[open_i + 1 : close_i].split(",")]

    return args


def map_args(call_expr: str, source: str) -> dict[str, str]:
    """Map function arguments to call arguments."""

    def_line: str = source.splitlines()[0]
    def_args: list[str] = parse_args(def_line)
    call_args: list[str] = parse_args(call_expr)

    return dict(zip(def_args, call_args))


def wrap_fn_name(fn_name: str) -> str:
    """Create a wrapper function name from the wrapped function name."""

    return f"_re_{fn_name}"


def wrap_fn_def(wrapped_fn: str, wrapper_fn: str, arg_map: dict[str, str]) -> str:
    """Generate source for a wrapper function that converts a UDF to a Pandas-compatible row function."""

    wrapper: str = f"def {wrapper_fn}(row):\n"

    for arg, col in arg_map.items():
        wrapper += f"    {arg} = '{col}'\n"

    args: str = ", ".join([f"row[{arg}]" for arg in arg_map.keys()])
    wrapper += f"    return {wrapped_fn}({args})\n"

    return wrapper


#

arg_map: dict[str, str] = map_args(call_expr, source)
wrapper: str = wrap_fn_def(udf_name, wrap_fn_name(udf_name), arg_map)
exec(wrapper)

pass  # TODO - HERE

#

tokens: list[str] = tokenize(call_expr)

re_source: str = ""
for tok in tokens:
    if tok in user_fns:
        re_source += "lambda row: "
    elif tok in arg_map:
        re_source += f"row['{arg_map[tok]}']"
    else:
        re_source += tok


# re_expr: str = rewrite_expr("df", tokens, col_names)


pass

###


def use(self, rel_path):
    """
    USE - Make user-defined functions available.
    """
    try:
        self.user_functions.update(fns_from_path(rel_path))

    except Exception as e:
        print("Exception loading user-defined functions: ", e)
        return
