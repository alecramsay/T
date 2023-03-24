# scripts/T.py -u user/alec.py -s examples -d data/rd/NC -f error.t > temp/error.txt

from(args.elections or '2020_election_NC.csv')

# Invalid commands
D_votes = composite(D_2020_ag, D_2020_gov, D_2016_sen, D_2020_sen, D_2016_pres, D_2020_pres)

# Should be ignored
R_votes = composite(R_2020_ag, R_2020_gov, R_2016_sen, R_2020_sen, R_2016_pres, R_2020_pres)
# Ditto
keep(GEOID20, D_votes, R_votes)