from('2020_census_AZ(PARTIAL).csv')
derive(county_fips, GEOID20[2:5])
# keep(GEOID20, county_fips, Tot_2020_tot)
# rename((Tot_2020_tot, Total))
groupby(by=[county_fips])
# groupby(by=[county_fips], only=[Tot_2020_tot], agg=[sum]) # TODO: this should work
