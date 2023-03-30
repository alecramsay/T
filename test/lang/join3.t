from(2020_census_NC.csv)
rename((GEOID20, GEOID), (Tot_2020_tot, Total))
derive(county_fips, GEOID[2:5])
keep(GEOID, county_fips, Total)

from(NC_counties.csv)

join(on=[[county_fips], [FIPS]])