# last

Select the last N (or N%) rows from the table on the top of the stack. Discard the rest.
Pop that table off and push the new table onto the stack.

## Syntax

`last(N)`

Parameters:

- **N**: int or int% -- The number or percent of rows to select.

## Examples

Select the last 10 rows:

`>>> last(10)`

Select the last 10% of rows:

`>>> last(10%)`