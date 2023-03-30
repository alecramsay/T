#!/usr/bin/env python3

"""
A script harness for debugging.

Use one of these arg sets:

$ scripts/T.py
$ scripts/T.py -u user/alec.py
$ scripts/T.py -u user/alec.py -s examples/rd -d data/rd/NC
$
$ scripts/T.py -u user/alec.py -s examples -d data/rd/NC -f demo.t > temp/demo.txt
$ scripts/T.py -u user/alec.py -s examples -d data/join -f join.t > temp/join.txt
$ scripts/T.py -u user/alec.py -s examples -d data/rd/NC -f aliases.t > temp/aliases.txt
$ scripts/T.py -u user/alec.py -s examples -d data/rd/NC -f top10precincts.t > temp/top10precincts.txt
$
$ scripts/T.py -u user/alec.py -s examples/rd -d data/rd/NC -f census.t > temp/census.txt
$ scripts/T.py -u user/alec.py -s examples/rd -d data/rd/NC -f elections.t > temp/elections.txt
$ scripts/T.py -u user/alec.py -s examples/rd -d data/rd/NC -f precincts.t > temp/precincts.txt
$ scripts/T.py -u user/alec.py -s examples/rd -d data/rd/NC -f districts.t > temp/districts.txt
$ scripts/T.py -u user/alec.py -s examples/rd -d data/rd/NC -f geographic_seats.t > temp/geographic_seats.txt
$ scripts/T.py -u user/alec.py -s examples/rd -d data/rd/NC -f misc.t > temp/misc.txt

>>> from(2020_census_NC.csv)
>>> from(precincts.t)

"""

import json
from typing import Optional

from T import run_script

user: str = "user/alec.py"
file: str = "debug.t"

args_str: str = ""
# args_str = '{"paf": "2020_alt_assignments_NC.csv"}'
# args_str = '{"paf": "\'2020_alt_assignments_NC.csv\'"}' <<< This doesn't work in argparse

source: str = "examples"
# source: str = "examples/rd"

data: str = "data/rd/NC"
# data = "data/join"

output: str = ""
log: str = ""


verbose: bool = True

scriptargs: dict = json.loads(args_str) if args_str else dict()

run_script(
    user=user,
    file=file,
    src=source,
    data=data,
    output=output,
    log=log,
    verbose=verbose,
    scriptargs=scriptargs,
)
