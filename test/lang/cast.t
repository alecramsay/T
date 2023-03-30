from(cast.csv)
keep(GEOID20, Tot_2010_tot)
rename((Tot_2010_tot, Total))
cast([Total], int64)