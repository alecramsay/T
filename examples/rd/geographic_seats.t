# scripts/T.py -u user/alec.py -s examples/rd -d data/rd/NC -f geographic_seats.t > temp/geographic_seats.txt

from('precincts.csv')
derive(county_fips, GEOID[2:5])
keep(county_fips, Total, D_votes, R_votes)

from('NC_counties.csv', [str, str])

join(county_fips, FIPS)

rename((NAME, County))
keep(County, Total, D_votes, R_votes)

groupby(by=County)

derive(D_pct, vote_share(sum_D_votes, sum_R_votes))
derive(D_prob, est_seat_probability(D_pct))
keep(County, sum_Total, D_pct, D_prob)
rename((sum_Total, Total))

# Weight counties by population
derive(w, Total / groupby(sum, Total))
# w = Total / |sum(Total)|

# Compute seats by county (13 seats total).
derive(D_seats, (w * 13) * D_prob)

echo(stats)
# Issue #74 to re-enable this:
# echo(stats['D_seats']['sum'])
