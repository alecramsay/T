# scripts/T.py -u user/alec.py -s examples/rd -d data/rd/NC -f census.t > temp/census.txt

from(args.census or 2020_census_NC.csv)

keep(GEOID20, Tot_2020_tot, Tot_2020_vap, Wh_2020_vap, His_2020_vap, BlC_2020_vap, NatC_2020_vap, AsnC_2020_vap, PacC_2020_vap)
rename((Tot_2020_tot, Total), (Tot_2020_vap, Total_VAP), (Wh_2020_vap, White), (His_2020_vap, Hispanic), (BlC_2020_vap, Black), (NatC_2020_vap, Native), (AsnC_2020_vap, Asian), (PacC_2020_vap, Pacific))
