#!/usr/bin/env python3

"""
Start the 'T' repl -or- run a 'T' script.

For example:

$ scripts/T.py -u user/alec.py -s examples/rd -d data/rd/NC
$ scripts/T.py -u user/alec.py -s examples/rd -d data/rd/NC -f census.t

For documentation, type:

$ scripts/T.py -h

"""

import json
import argparse as ap

from T import run_script, run_repl


parser = ap.ArgumentParser(description="Start the T language processor")

parser.add_argument(
    "-u", "--user", dest="user", help="Relative path to user-defined functions"
)
parser.add_argument("-f", "--file", dest="file", help="Relative path to script file")
parser.add_argument("-s", "--source", dest="source", help="Relative source directory")
parser.add_argument("-d", "--data", dest="data", help="Relative data directory")
parser.add_argument("-o", "--output", dest="output", help="Relative output directory")
parser.add_argument("-l", "--log", dest="logfile", help="Path to log file")
parser.add_argument("-a", "--scriptargs", type=str)
parser.add_argument(
    "-v", "--verbose", dest="verbose", action="store_true", help="Verbose mode"
)

args: ap.Namespace = parser.parse_args()
scriptargs: dict = json.loads(args.scriptargs) if (args.scriptargs) else dict()

if args.file:
    run_script(
        user=args.user,
        file=args.file,
        src=args.source,
        data=args.data,
        output=args.output,
        log=args.logfile,
        verbose=args.verbose,
        scriptargs=scriptargs,
    )
else:
    run_repl(
        user=args.user,
        src=args.source,
        data=args.data,
        output=args.output,
        log=args.logfile,
        verbose=args.verbose,
        scriptargs=scriptargs,
    )

### END ###
