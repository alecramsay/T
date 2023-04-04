# keep

Keep one or more columns from the table on the top of the stack. Drop the rest.
Pop that table off and push the narrower table onto the stack.

## Syntax

`>>> keep(column, ...)`

Parameters:

- **column**: list -- Columns to keep *in the order to keep them*.

## Examples

Keep two columns:

`>>> keep(GEOID20, Tot_2020_tot)`