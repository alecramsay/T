#!/usr/bin/env python3

"""
A harness for debugging REPL execution
"""

import json
import argparse as ap

from T import run_repl

user: str = "user/alec.py"

# source: str = "examples"
source: str = "examples/rd"

data: str = "data/rd/NC"
# data: str = "test/join"
# data: str = "test/union"

output: str = ""

log: str = ""

verbose: bool = False

args_str: str = ""
# args_str = '{"paf": "2020_alt_assignments_NC.csv"}'
# args_str = '{"paf": "\'2020_alt_assignments_NC.csv\'"}' <<< This doesn't work in argparse
scriptargs: dict = json.loads(args_str) if args_str else dict()

run_repl(
    user=user,
    src=source,
    data=data,
    output=output,
    log=log,
    verbose=verbose,
    scriptargs=scriptargs,
)
