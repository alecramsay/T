#!/usr/bin/env python3

"""
Run a 'T' script from the command line.

For example:

$ scripts/t.py -u user/alec.py -s examples/rd -d data/rd/NC -f census.t > temp/census.txt
$ scripts/t.py -u user/alec.py -s examples/rd -d data/rd/NC -f elections.t > temp/elections.txt
$ scripts/t.py -u user/alec.py -s examples/rd -d data/rd/NC -f precincts.t > temp/precincts.txt
$ scripts/t.py -u user/alec.py -s examples/rd -d data/rd/NC -f districts.t > temp/districts.txt
$
$ scripts/t.py -u user/alec.py -s examples/rd -d data/rd/NC -f precincts.t -a '{"paf": "2020_alt_assignments_NC.csv"}'
$ scripts/t.py -u user/alec.py -s examples/rd -d data/rd/NC -f precincts.t -a '{"paf": "\'2020_alt_assignments_NC.csv\'"}' <<< This doesn't work in argparse

For documentation, type:

$ scripts/t.py -h

"""

import json
import argparse as ap

from T import run_script


parser = ap.ArgumentParser(description="Start the T language processor")

parser.add_argument(
    "-u", "--user", dest="user", help="Relative path to user-defined functions"
)
parser.add_argument("-f", "--file", dest="file", help="Relative path to script file")
parser.add_argument("-s", "--source", dest="source", help="Relative source directory")
parser.add_argument("-d", "--data", dest="data", help="Relative data directory")
parser.add_argument("-a", "--scriptargs", type=str)
parser.add_argument(
    "-v", "--verbose", dest="verbose", action="store_true", help="Verbose mode"
)

args: ap.Namespace = parser.parse_args()
scriptargs: dict = json.loads(args.scriptargs) if (args.scriptargs) else dict()

run_script(
    user=args.user,
    file=args.file,
    src=args.source,
    data=args.data,
    verbose=args.verbose,
    scriptargs=scriptargs,
)
