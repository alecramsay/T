# scripts/T.py -u user/alec.py -s examples/rd -d data/rd/NC -f geographic_seats.t > temp/geographic_seats.txt

from(precincts.csv)
derive(county_fips, GEOID[2:5])
keep(county_fips, Total, D_votes, R_votes)

from(NC_counties.csv)

join(on=[[county_fips], [FIPS]])

rename((NAME, County))
keep(County, Total, D_votes, R_votes)

groupby(by=[County], agg=[sum])

derive(D_pct, vote_share(D_votes_sum, R_votes_sum))
derive(D_prob, est_seat_probability(D_pct))
keep(County, Total_sum, D_pct, D_prob)
rename((Total_sum, Total))

# TODO - Not reimplemented below here yet

# Weight counties by population
derive(w, Total / sum(Total))

# Compute seats by county (13 seats total).
derive(D_seats, (w * 13) * D_prob)