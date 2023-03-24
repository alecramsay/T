#!/usr/bin/env python3

"""
Start a 'T' REPL.

For example:

$ scripts/repl.py
$ scripts/repl.py -u user/alec.py
$ scripts/repl.py -u user/alec.py -s examples -d data/rd/NC
$ scripts/repl.py -u user/alec.py -s examples/rd -d data/rd/NC

For documentation, type:

$ scripts/T.py -h

"""

import json
import argparse as ap

from T import start_repl


parser = ap.ArgumentParser(description="Start the T language processor")

parser.add_argument(
    "-u", "--user", dest="user", help="Relative path to user-defined functions"
)
parser.add_argument("-s", "--source", dest="source", help="Relative source directory")
parser.add_argument("-d", "--data", dest="data", help="Relative data directory")
parser.add_argument("-a", "--scriptargs", type=str)
parser.add_argument(
    "-v", "--verbose", dest="verbose", action="store_true", help="Verbose mode"
)

args: ap.Namespace = parser.parse_args()
scriptargs: dict = json.loads(args.scriptargs) if (args.scriptargs) else dict()

start_repl(
    user=args.user,
    src=args.source,
    data=args.data,
    verbose=args.verbose,
    scriptargs=scriptargs,
)
