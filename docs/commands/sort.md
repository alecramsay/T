# sort

Sort the table on the top of the stack by one or more columns.
Pop the unsorted table and push the sorted table onto the stack.

## Syntax

`sort(sort_spec, ...)`

Parameters:

- **sort_spec**: list -- Each spec is either a column name or a (column name, order) tuple. Column names are unquoted strings. Order is either ASC or DESC (no quotes) for ascending and descending, respectively. If a spec doesn't have an explicit sort order, the default order is ASC.

## Examples

Sort by one column in ascending order:

`>>> sort(Total)`

Sort by one column in descending order:

`>>> sort((Total, DESC))`

Sort by two columns in mixed orders:

`>>> sort(State, (County_Population, DESC))`

