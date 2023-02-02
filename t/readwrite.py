#!/usr/bin/env python3

"""
READ/WRITE
"""

import os
from typing import Type


class FileSpec:
    def __init__(self, path: str, name=None) -> None:
        file_name: str
        file_extension: str
        file_name, file_extension = os.path.splitext(path)

        self.rel_path: str = path
        self.abs_path: str = os.path.abspath(path)
        self.name: str = name.lower() if (name) else os.path.basename(file_name).lower()
        self.extension: str = file_extension


### INFER COLUMN TYPES ###


class TypeInferencer:
    def __init__(self) -> None:
        self.n: int = 0
        self.lengths: set[int] = set()
        self.types: set[Type] = set()

    def add(self, example: str) -> None:
        self.n += 1

        if is_int(example):
            self.types.add(int)
        elif is_float(example):
            self.types.add(float)
        elif is_bool(example):
            self.types.add(bool)
        else:
            self.types.add(str)

        self.lengths.add(len(example))

    def infer(self) -> Type[str] | Type[int] | Type[float] | Type[bool]:
        if self.n == 0:
            return str

        # All the same type
        if len(self.types) == 1:
            inferred_type: Type[str] | Type[int] | Type[float] | Type[
                bool
            ] = self.types.pop()

            # All 'integers' the same multi-digit width, e.g., GEOIDs
            # NOTE - This check assumes a non-trivial number of examples.
            if (
                inferred_type == int
                and len(self.lengths) == 1
                and self.lengths.pop() > 1
            ):
                return str

            return inferred_type

        # All int & float
        if self.types == {int, float}:
            return float

        # No change
        return str


# Type Inference Helpers


def leading_zeroes(s: str) -> bool:
    """
    Like GEODID
    """
    if len(s) > 1 and s[0] == "0":
        return True
    else:
        return False


def is_int(s: str) -> bool:
    """
    Is the string an integer? (possibly negative)
    """
    try:
        if leading_zeroes(s):
            return False
        int(s)
        return True
    except ValueError:
        return False


def is_float(s: str) -> bool:
    """
    Is the string a float? (possibly negative)
    """
    try:
        if leading_zeroes(s):
            return False
        float(s)
        return True
    except ValueError:
        return False


def is_bool(s: str) -> bool:
    """
    Is the string a boolean?
    """
    return s.lower() in ["true", "false"]


### END ###
