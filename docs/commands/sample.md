# sample

Select a random sample of N (or N%) rows from the table on the top of the stack. Discard the rest.
Pop that table off and push the new table onto the stack.

## Syntax

`sample(N)`

Parameters:

- **N**: int or int% -- The number or percent of rows to select.

## Examples

Select 10 sample rows:

`>>> sample(10)`

Select a 10% sample of rows:

`>>> sample(10%)`