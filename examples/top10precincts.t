# scripts/T.py -u user/alec.py -s examples -d data/rd/NC -f top10precincts.t > temp/top10precincts.txt

from('2020_census_NC.csv')
keep(GEOID20, Tot_2020_tot)
rename((Tot_2020_tot, Total))

from('top10.t', sorton=Total)
