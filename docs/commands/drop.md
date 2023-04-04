# drop

Drop one or more columns from the table on the top of the stack. Keep the rest.
Pop that table off and push the narrower table onto the stack.

## Syntax

`drop(column, ...)`

Parameters:

- **column**: list -- Columns to drop.

## Examples

Drop one column:

`>>> drop(AsnC_2010_tot)`