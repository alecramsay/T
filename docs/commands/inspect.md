# inspect

Show descriptive statistics for the numeric columns of the table on the top of the stack.

## Syntax

`inspect(match=None)`

Parameters:

- **match**: str, optional -- By default, show all numeric columns. If a string is provided, show only columns with that string in the name.

## Examples

All numeric columns:

`>>> inspect()`

All numeric columns with '2020' in the name:

`>>> inspect(2020)`