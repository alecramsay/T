#!/usr/bin/env python3

"""
A harness for debugging script execution
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
