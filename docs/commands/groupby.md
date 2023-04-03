# groupby

Aggregate the numeric columns of the table on the top of the stack by the the values of one or more columns.
This is similar to creating pivot table in Excel.
Pop the ungrouped table off and push the grouped table onto the stack.

## Syntax

`groupby(* by=by, only=only, agg=agg)`

TODO - HERE

Enumerate aggregate functions

Parameters:

- by
- only
- agg

## Examples

Group all numeric columns by the county_fips column and compute all aggregate functions:

`>>> groupby(by=[county_fips])`

Group only the Total column and only compute the max aggregate function:

`>>> groupby(by=[county_fips], only=[Total], agg=[max])`