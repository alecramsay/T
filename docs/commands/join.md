# join

Join two tables.

## Examples

`>>> join()`

`>>> join(on=[[county_fips], [FIPS]])`

`>>> join(how=inner, on=[[county_fips], [FIPS]], suffixes=('_y', '_x'), validate=1:M)`