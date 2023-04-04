# derive

Derive a new column from existing columns in the top table on the stack.
Pop that table off and push the new table onto the stack.

## Syntax

`derive(new_column, formula)`

Parameters:

- **new_column**: str -- The name of the new column (no quotes).
- **formula**: expression -- The formula for calculating the new column's values.

## Examples

Calculate a new column as the difference between two existing ones:

`>>> derive(Minority_2020_tot, Tot_2020_tot - Wh_2020_tot`

Compute a new column as a slice of an existing string column:

`>>> derive(county_fips, GEOID20[2:5]`

Define a new column in terms of an [aggregate function](../aggregates.md):

`>>> derive(w, Total / sum(Total))`

Use a [user-defined functions](../udf.md) to compute a new column:

`>>> derive(D_pct, vote_share(D_2020_pres, R_2020_pres)`
