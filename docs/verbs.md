# Verbs

Supported verbs fall into two categories:

- Verbs that operate on rows, and
- Verbs that operate on tables

TODO - Document each verb

## File-in Verbs

- from()

## Row Verbs

- keep(x_table, keep_cols)
- drop(x_table, drop_cols)
- rename(x_table, col_specs)
- alias(x_table, col_specs)

- select(x_table, expr)
- derive(x_table, name, expr, **kwargs) <<< rename 'let'?

- first(x_table, n, pct=None)
- last(x_table, n, pct=None)
- sample(x_table, n, pct=None) <<< renamed

- cast(x_table, cast_cols, dtype)

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