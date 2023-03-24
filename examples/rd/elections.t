# scripts/t.py -u user/alec.py -s examples/rd -d data/rd/NC -f elections.t > temp/elections.txt

from(args.elections or '2020_election_NC.csv')

derive(D_votes, composite(D_2020_ag, D_2020_gov, D_2016_sen, D_2020_sen, D_2016_pres, D_2020_pres))
derive(R_votes, composite(R_2020_ag, R_2020_gov, R_2016_sen, R_2020_sen, R_2016_pres, R_2020_pres))
keep(GEOID20, D_votes, R_votes)
