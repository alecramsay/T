from('2020_census_NC.csv')

keep(GEOID20, Tot_2020_tot, Tot_2020_vap, Wh_2020_vap, His_2020_vap, BlC_2020_vap, NatC_2020_vap, AsnC_2020_vap, PacC_2020_vap)
alias((GEOID20, GEOID), (Tot_2020_tot, Total), (Tot_2020_vap, Total_VAP), (Wh_2020_vap, White), (His_2020_vap, Hispanic), (BlC_2020_vap, Black), (NatC_2020_vap, Native), (AsnC_2020_vap, Asian), (PacC_2020_vap, Pacific))

# GEOID20, Tot_2010_tot, Wh_2010_tot, His_2010_tot, BlC_2010_tot, 
# NatC_2010_tot, AsnC_2010_tot, PacC_2010_tot, Tot_2010_vap, Wh_2010_vap, 
# His_2010_vap, BlC_2010_vap, NatC_2010_vap, AsnC_2010_vap, PacC_2010_vap, 
# Tot_2018_tot, Wh_2018_tot, His_2018_tot, BlC_2018_tot, NatC_2018_tot, 
# AsnC_2018_tot, PacC_2018_tot, Tot_2018_cvap, Wh_2018_cvap, His_2018_cvap, 
# BlC_2018_cvap, NatC_2018_cvap, AsnC_2018_cvap, PacC_2018_cvap, Tot_2019_tot, 
# Wh_2019_tot, His_2019_tot, BlC_2019_tot, NatC_2019_tot, AsnC_2019_tot, 
# PacC_2019_tot, Tot_2019_cvap, Wh_2019_cvap, His_2019_cvap, BlC_2019_cvap, 
# NatC_2019_cvap, AsnC_2019_cvap, PacC_2019_cvap, Tot_2020_tot, Wh_2020_tot, 
# His_2020_tot, BlC_2020_tot, NatC_2020_tot, AsnC_2020_tot, PacC_2020_tot, 
# Tot_2020_vap, Wh_2020_vap, His_2020_vap, BlC_2020_vap, NatC_2020_vap, 
# AsnC_2020_vap, PacC_2020_vap