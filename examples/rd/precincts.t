# scripts/t.py -u user/alec.py -s examples/rd -d data/rd/NC -f precincts.t > temp/precincts.txt

from(args.paf or '2020_precinct_assignments_NC.csv')

from('census.t', census='2020_census_NC.csv')
join()

from('elections.t', elections='2020_election_NC.csv')
join()

rename((GEOID20, GEOID))
