# cast

Cast one or more columns in the table on the top of the stack to a new data type.
Pop that table off and push the new table onto the stack.

## Syntax

`cast([columns], new_type)`

Parameters:

- **columns**: list[str] -- The columns to cast.
- **new_type**: str -- The new data type. One of { object, string, int64, float64, bool, datetime64, timedelta64, category }.

## Examples

Cast one column to a string:

`>>> cast([GEOID20], string)`

## TODO

- Should I allow the first argument to be a single column?
