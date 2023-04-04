# rename

Rename one or more columns in the table on the top of the stack.
Pop that table off and push the new table onto the stack.

## Syntax

`rename(col_spec, ...)`

Parameters:

- **col_spec**: list -- Each spec is a (column, new_name) tuple. Both are unquoted strings. 

## Examples

Rename one column:

`>>> rename((Tot_2020_tot, Total))`