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


rel_path: str = "user/alec.py"
udf: UDF = UDF(rel_path)

expr: str = (
    "composite(D_2020_ag, D_2020_gov, D_2016_sen, D_2020_sen, D_2016_pres, D_2020_pres)"
)
tokens: list[str] = tokenize(expr)
col_names: list[str] = [
    "D_2020_ag",
    "D_2020_gov",
    "D_2016_sen",
    "D_2020_sen",
    "D_2016_pres",
    "D_2020_pres",
]

re_expr: str
wrappers: list[str]
re_expr, wrappers = rewrite_expr(tokens, col_names, udf)

pass

### END ###
