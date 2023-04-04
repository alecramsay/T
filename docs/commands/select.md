# select

Select rows from the table on the top of the stack that match a condition. Discard the rest.
Pop that table off and push the new table onto the stack.

## Syntax

`select(condition)`

Parameters:

- **condition**: expression -- An expression that evaluates to a boolean value.

## Examples

`>>> select(county_fips == '191')`

## TODO

- Enable user-defined functions, like in 'derive' formulas
- Enable aggregate function references, like in 'derive' formulas