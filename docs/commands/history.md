# history

Show the command history.
This command does not alter the table stack.

## Syntax

`history()`

Parameters -- None.

## Examples

`>>> history()`

The log looks like this, so you can easily capture sequences of commands that did what you wanted:

```text
001 from_(precincts.csv)
002 derive(county_fips, GEOID[2:5])
003 keep(county_fips, Total, D_votes, R_votes)
004 from_(NC_counties.csv)
005 join(on=[[county_fips], [FIPS]])
006 rename((NAME, County))
007 keep(County, Total, D_votes, R_votes)
008 groupby(by=[County], agg=[sum])
009 derive(D_pct, vote_share(D_votes_sum, R_votes_sum))
010 derive(D_prob, est_seat_probability(D_pct))
011 keep(County, Total_sum, D_pct, D_prob)
012 rename((Total_sum, Total))
```

The log rolls over when it reaches 1MB.