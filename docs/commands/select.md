# select

Select rows from the table on the top of the stack that match a condition. Discard the rest.
Pop that table off and push the new table onto the stack.

## Examples

`>>> select(county_fips == '191')`