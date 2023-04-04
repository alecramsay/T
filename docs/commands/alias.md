# alias

Alias one or more columns in the table on the top of the stack.
Pop that table off and push the new table onto the stack.

Aliases are soft renames: you use the more convenient aliases in subsequent commands, 
but when you write the table to a file, the real column names are used.

## Syntax

`alias(col_spec, ...)`

Parameters:

- **col_spec**: list -- Each spec is a (column, alias) tuple. Both are unquoted strings. 

## Examples

Alias one column:

## Examples

`>>> alias((Tot_2020_tot, Total))`