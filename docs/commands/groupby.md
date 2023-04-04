# groupby

Aggregate the numeric columns of the table on the top of the stack by the the values of one or more columns.
This is similar to creating pivot table in Excel.
Pop the ungrouped table off and push the grouped table onto the stack.

## Syntax

`groupby(*, by=by, only=only, agg=agg)`

Parameters:

- **by**: list of columns to group by
- **only**: list of columns, optional -- By default, all numeric columns are grouped. If 'only' is specified, only those column are grouped.
- **agg**: list of functions, optional -- By default, all aggregate functions are computed: {sum, count, mean, std, min, max, median}. If 'agg' is specified, only those functions are computed.

## Examples

Group all numeric columns by the county_fips column and compute all aggregate functions:

`>>> groupby(by=[county_fips])`

Group only the Total column and only compute the sum aggregate function:

`>>> groupby(by=[county_fips], only=[Total], agg=[sum])`

# TODO

- Should I make 'by' a required positional argument?