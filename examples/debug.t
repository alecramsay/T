# scripts/T.py -u user/alec.py -s examples -d data/rd/NC -f debug.t

from('2020_census_NC.csv')

# derive(county_fips, GEOID20[2:5])
rename((Tot_2020_tot, Total))
sort((Total, DESC))
first(10%)

# ...
