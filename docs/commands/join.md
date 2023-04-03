# join

Join the top two tables on the stack.
Pop those two tables off and push the joined table onto the stack.

## Examples

`>>> join()`

`>>> join(on=[[county_fips], [FIPS]])`

`>>> join(how=inner, on=[[county_fips], [FIPS]], suffixes=('_y', '_x'), validate=1:M)`