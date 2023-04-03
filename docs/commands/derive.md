# derive

Derive a new column from existing columns.

## Examples

`>>> derive(Minority_2020_tot, Tot_2020_tot - Wh_2020_tot`

`>>> derive(county_fips, GEOID20[2:5]`

`>>> derive(D_pct, vote_share(D_2020_pres, R_2020_pres)`

[User-defined functions](../udf.md) can be used to define new columns.