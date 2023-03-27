# scripts/T.py -u user/alec.py -s examples/rd -d data/rd/NC -f misc.t > temp/misc.txt

from('2020_census_NC.csv')

derive(county_fips, GEOID20[2:5])
select(county_fips == '191')
keep(GEOID20, county_fips, Tot_2020_tot)
alias((Tot_2020_tot, Total))
sort((Total, DESC))
first(10%)
