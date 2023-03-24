#!/usr/bin/env python3

"""
A script harness for debugging.

Use one of these arg sets:

$ scripts/t.py
$ scripts/t.py -u user/alec.py
$ scripts/t.py -u user/alec.py -s examples/rd -d data/rd/NC
$
$ scripts/t.py -u user/alec.py -s examples -d data/rd/NC -f demo.t > temp/demo.txt
$ scripts/t.py -u user/alec.py -s examples -d data/join -f join.t > temp/join.txt
$ scripts/t.py -u user/alec.py -s examples -d data/rd/NC -f aliases.t > temp/aliases.txt
$ scripts/t.py -u user/alec.py -s examples -d data/rd/NC -f top10precincts.t > temp/top10precincts.txt
$
$ scripts/t.py -u user/alec.py -s examples/rd -d data/rd/NC -f census.t > temp/census.txt
$ scripts/t.py -u user/alec.py -s examples/rd -d data/rd/NC -f elections.t > temp/elections.txt
$ scripts/t.py -u user/alec.py -s examples/rd -d data/rd/NC -f precincts.t > temp/precincts.txt
$ scripts/t.py -u user/alec.py -s examples/rd -d data/rd/NC -f districts.t > temp/districts.txt
$ scripts/t.py -u user/alec.py -s examples/rd -d data/rd/NC -f geographic_seats.t > temp/geographic_seats.txt
$ scripts/t.py -u user/alec.py -s examples/rd -d data/rd/NC -f misc.t > temp/misc.txt

>>> from('2020_census_NC.csv')
>>> from('precincts.t')

"""

import json

from src.pytables import *

user: str = "user/alec.py"
file: str = "elections.t"

scriptargs: str = ""
# scriptargs = '{"paf": "2020_alt_assignments_NC.csv"}'
# scriptargs = '{"paf": "\'2020_alt_assignments_NC.csv\'"}' <<< This doesn't work in argparse

# source = "examples"
source: str = "examples/rd"

data: str = "data/rd/NC"
# data = "data/join"

verbose: bool = False

scriptargs = json.loads(scriptargs) if (scriptargs) else {}

run_script(
    user=user, file=file, src=source, data=data, verbose=verbose, scriptargs=scriptargs
)
