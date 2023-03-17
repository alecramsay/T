# Verbs

Supported verbs fall into two categories:

- Verbs that operate on rows, and
- Verbs that operate on tables

## Row Verbs

- Keep (x_table, keep_cols)
- Drop (x_table, drop_cols)
- Rename (x_table, col_specs)
- Alias (x_table, col_specs)

- Select (x_table, expr)

- First (x_table, n, pct=None)
- Last (x_table, n, pct=None)
- Random (x_table, n, pct=None)

- Cast (x_table, cast_cols, type_fn)

- Derive (x_table, name, expr, **kwargs)

## Table Verbs

- Sort (x_table, col_specs)
- GroupBy (x_table, by_cols, only=None, agg=None)
- Join (y_table, x_table, y_key_name, how="inner", on=None, suffixes("_y","_x",), validate=None)
- Union (y_table, x_table)
