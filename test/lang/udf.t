# scripts/T.py -u user/alec.py -s test/lang -d test/files -f udf.t 
from('2020_election_AZ(PARTIAL).csv')
keep(D_2020_pres, R_2020_pres)
derive(D_pct, vote_share(D_2020_pres, R_2020_pres))