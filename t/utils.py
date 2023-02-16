#!/usr/bin/env python3

"""
UTILITIES
"""


def parse_spec(spec) -> tuple:
    """Parse a spec singleton -or- pair.

    Examples:

    spec = 'GEOID20' => ('GEOID20', 'GEOID20')
    spec = ['GEOID20', 'GEOID'] => ('GEOID', 'GEOID')

    spec = 'GEOID' => ('GEOID', 'GEOID')
    spec = ['Total', 'DESC'] => ('Total', 'DESC')

    parse_spec(spec)
    """

    first: str = spec[0] if (type(spec) in [list, tuple]) else spec
    second: str = spec[1] if (type(spec) in [list, tuple]) else spec

    return first, second


def is_list_of_str(obj) -> bool:
    return isinstance(obj, list) and all(isinstance(elem, str) for elem in obj)


### END ###
