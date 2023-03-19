# utils.py
#!/usr/bin/env python3

"""
UTILITIES
"""

import builtins
from typing import Any

# import inspect


def parse_spec(spec: str | list[str] | tuple[str]) -> tuple:
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


def is_list_of_str(obj: Any) -> bool:
    return isinstance(obj, list) and all(isinstance(elem, str) for elem in obj)


def value_width(v: Any, pad: int = 2) -> int:
    if v is None:
        return 10

    if type(v) is str:
        return len(v)

    if type(v) in [int, float]:
        return len(str(v))

    if type(v) is list:
        return sum([value_width(x) + pad for x in v])

    return 10


def map_keys(d: dict, mapping: dict) -> dict:
    """mapping is a dict of {old_key: new_key}"""

    return {mapping[k]: v for k, v in d.items()}


def get_builtin_fn(name: str) -> Any:
    """Get a builtin function by name."""

    return getattr(builtins, name)


# def mod_fns(mod):
#     pairs = inspect.getmembers(mod, inspect.isfunction)
#     fns_dict = {k: v for k, v in pairs}

#     return fns_dict

### MISSING ###


def is_missing(v: Any) -> bool:
    """Return True if v is missing, else False.

    TODO - Handle missing?
    """

    return True if (v is None) else False


### END ###
