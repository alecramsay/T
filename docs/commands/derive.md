# derive

Derive a new column from existing columns in the top table on the stack.
Pop that table off and push the new table onto the stack.

## Examples

`>>> derive(Minority_2020_tot, Tot_2020_tot - Wh_2020_tot`

`>>> derive(county_fips, GEOID20[2:5]`

`>>> derive(D_pct, vote_share(D_2020_pres, R_2020_pres)`

[User-defined functions](../udf.md) can be used to define new columns.