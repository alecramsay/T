# groupby

Aggregate the rows of the table on the top of the stack by the the values of one or more columns.
This is similar to creating pivot table in Excel.
Pop the ungrouped table off and push the grouped table onto the stack.

## Examples

`>>> groupby(by=[county_fips])`

`>>> groupby(by=[county_fips], only=[Total], agg=[max])`