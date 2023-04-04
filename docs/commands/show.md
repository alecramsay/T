# show

Show the first N rows of the top table on the stack.
This command does not alter the table stack.

After each command in the REPL, `show(5)` is executed to show the result.

## Syntax

`show(N=None)`

Parameters:

- **N**: int, optional -- The number of rows to show. If not provided, all rows are shown.

## Examples

Show all rows:

`>>> show()`

Show the first 10 rows:

`>>> show(10)`