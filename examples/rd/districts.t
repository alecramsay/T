# scripts/T.py -u user/alec.py -s examples/rd -d data/rd/NC -f districts.t > temp/districts.txt

from(precincts.t, paf=2020_precinct_assignments_NC.csv, census=2020_census_NC.csv, elections=2020_election_NC.csv)

groupby(by=[District])

derive(D_pct, vote_share(D_votes_sum, R_votes_sum))
derive(R_pct, 1 - D_pct)
derive(White_pct, White_sum / Total_VAP_sum)
derive(Hispanic_pct, Hispanic_sum / Total_VAP_sum)
derive(Black_pct, Black_sum / Total_VAP_sum)
derive(Native_pct, Native_sum / Total_VAP_sum)
derive(Asian_pct, Asian_sum / Total_VAP_sum)
derive(Pacific_pct, Pacific_sum / Total_VAP_sum)

keep(District, Total_sum, D_pct, R_pct, Total_VAP_sum, White_pct, Hispanic_pct, Black_pct, Native_pct, Asian_pct, Pacific_pct)

sort(District)