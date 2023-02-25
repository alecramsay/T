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
re_expr: str = generate_df_syntax(tokens, self.col_names())

"""

import inspect

from t import *


# Setup


rel_path: str = "user/alec.py"
udf: UDF = UDF(rel_path)
udf_names: list[str] = udf.names()

call_expr: str = (
    "composite(D_2020_ag, D_2020_gov, D_2016_sen, D_2020_sen, D_2016_pres, D_2020_pres)"
)
# tokens: list[str] = tokenize(call_expr)

# # Collapse UDF calls
# new_tokens: list[str] = mark_udf_calls(tokens, udf)

# pass
# #

# col_names: list[str] = [
#     "D_2020_ag",
#     "D_2020_gov",
#     "D_2016_sen",
#     "D_2020_sen",
#     "D_2016_pres",
#     "D_2020_pres",
# ]

# has_valid_refs(tokens, col_names, udf_names)

# pass
#

udf_name: str = "composite"
source: str = udf.source(udf_name)

arg_map: dict[str, str] = map_args(call_expr, source)
ref: int = udf.count(udf_name)
alias: str = udf.alias(udf_name, ref)
wrapper: str = udf.wrap(alias, udf_name, arg_map)
exec(wrapper)

pass  # TODO - HERE

#

re_source: str = ""
for tok in tokens:
    if tok in user_fns:
        re_source += "lambda row: "
    elif tok in arg_map:
        re_source += f"row['{arg_map[tok]}']"
    else:
        re_source += tok


re_expr: str = generate_df_syntax(tokens, col_names)


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
