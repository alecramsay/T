T ...

## Contents

T commands fall into several categories:

- File-in verbs
    - from
- Row verbs
    - keep, drop
    - rename, alias
    - select
    - derive
    - first, last, sample
    - cast

## Table Verbs

- sort(x_table, col_specs)
- groupby(x_table, by_cols, only=None, agg=None) <<< renamed
- join(y_table, x_table, y_key_name, how="inner", on=None, suffixes("_y","_x",), validate=None)
- union(y_table, x_table)

## File-out Verbs

- write()

## Display Verbs

- write()
- show()
- inspect()

## Stack Verbs

- clear()
- pop()
- swap()
- reverse()
- rotate()

## Miscellaneous Verbs

- duplicate() <<< rename 'copy'?
- history()

## Overview

TODO

You can find a library of examples in the examples directory in the test/lang folder of the [T GitHub repository](https://github.com/alecramsay/T).