# first

Select the first N (or N%) rows from the top table on the stack. Discard the rest.
Pop that table off and push the new table onto the stack.

## Syntax

`first(N)`

Parameters:

- **N**: int or int% -- The number or percent of rows to select.

## Examples

Select the first 10 rows:

`>>> first(10)`

Select the first 10% of rows:

`>>> first(10%)`