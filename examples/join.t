# scripts/T.py -u user/alec.py -s examples -d data/join -f join.t > temp/join.txt

from('employee.csv', [str, int])
from('department.csv')
join()
