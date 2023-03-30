# scripts/T.py -u user/alec.py -s examples/rd -d data/rd/NC -f read_all.t

from(args.paf or 2020_precinct_assignments_NC.csv)
from(args.census or 2020_census_NC.csv)
from(args.elections or 2020_election_NC.csv)

