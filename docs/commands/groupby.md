# groupby

Aggregate the rows of a table by the the values of one or more columns.

aka "pivot"

## Examples

`>>> groupby(by=[county_fips])`

`>>> groupby(by=[county_fips], only=[Total], agg=[max])`