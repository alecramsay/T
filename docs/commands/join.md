# join

Join the top two tables on the stack.
Following HP calculator notation, the 'y' table is the first one that was pushed on the stack, and the 'x' table is the last one, i.e., the top table.
Pop those two tables off and push the joined table onto the stack.

## Syntax

`join(*, how=inner, on=None, suffixes=('_x', '_y'), validate=None)`

Parameters:

- **how**: {left, right, outer, inner, cross}, default is inner
- **on**: str, list[str], list[list[str], list[str]], optional (no default) -- If not specified, the join column is inferred. If one column is given, the join is on that column from both tables. If one list is specified, the join is on those columns from both tables. If two lists are specified, they must be of the same length and the join is those columns from the two tables.
- **suffixes**: a length-2 tuple, default is ('_y', '_x') -- Both elements are optionally a string indicating the suffix to add to overlapping column names in the 'y' and 'x' tables, respectively. Passing a value of None instead of a string indicates that that column name should be left as-is, i.e., with no suffix. At least one of the two values must not be None.
- **validate**: {1:1, 1:m, m:1, m:m}, optional (no default) -- If specified, checks if the join is of the specified type.

## Examples

Join on the shared column:

`>>> join()`

Join on county_fips from the 'y' table and FIPS from the 'x' table:

`>>> join(on=[[county_fips], [FIPS]])`

Do an inner join on county_fips from the 'y' table and FIPS from the 'x' table, using the suffixes '_y' and '_x' and validate that the join is 1:M:

`>>> join(how=inner, on=[[county_fips], [FIPS]], suffixes=('_y', '_x'), validate=1:M)`