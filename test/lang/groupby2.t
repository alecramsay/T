from('2020_census_AZ(PARTIAL).csv')
derive(county_fips, GEOID20[2:5])
groupby(by=[county_fips], only=[Tot_2020_tot], agg=[sum, min, max, mean, median])
