from(2020_census_AZ(PARTIAL).csv)
derive(county_fips, GEOID20[2:5])
select(county_fips == '005')