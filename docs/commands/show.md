# show

Print the first N rows of the top table on the stack.
This command does not alter the table stack.

If there are less than 10 columns, a nice tabluar format is used like this:

```text
GEOID20        Tot_2020_tot    Wh_2020_tot    BlC_2020_tot    His_2020_tot
-----------  --------------  -------------  --------------  --------------
370210001.1           2,982          2,159             578             139
370210053.1           4,491          3,954             118             248
370210068.1           7,502          5,782             379           1,028
370210022.2           2,640          2,414              46              84
370210027.2             953            896              15              11

```

If there are more than 10 columns, a compressed CSV format is used.

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