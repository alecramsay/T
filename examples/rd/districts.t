# scripts/T.py -u user/alec.py -s examples/rd -d data/rd/NC -f districts.t > temp/districts.txt

from(precincts.t, paf=2020_precinct_assignments_NC.csv, census=2020_census_NC.csv, elections=2020_election_NC.csv)

groupby(by=District)

derive(D_pct, vote_share(sum(D_votes), sum(R_votes)))
derive(R_pct, 1 - D_pct)
derive(White_pct, sum(White) / sum(Total_VAP))
derive(Hispanic_pct, sum(Hispanic) / sum(Total_VAP))
derive(Black_pct, sum(Black) / sum(Total_VAP))
derive(Native_pct, sum(Native) / sum(Total_VAP))
derive(Asian_pct, sum(Asian) / sum(Total_VAP))
derive(Pacific_pct, sum(Pacific) / sum(Total_VAP))

keep(District, sum(Total), D_pct, R_pct, sum(Total_VAP), White_pct, Hispanic_pct, Black_pct, Native_pct, Asian_pct, Pacific_pct)

sort(District)

# inspect()
