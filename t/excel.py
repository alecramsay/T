#!/usr/bin/env python3

"""
EXCEL - Microsoft Excel column names
"""

from typing import Generator


def excel_column_names() -> Generator[str, None, None]:
    """
    Generate first 702 (= 26 * 27) Excel column names:
    A-Z, AA-AZ, BA-BZ, ..., XA-XZ, YA-YZ, ZA-ZZ
    """

    offset: int = ord("A")

    for n in range(1, 26 * 27 + 1):
        yield index_to_excel_column_name(n)


def first_n_excel_column_names(n: int) -> list[str]:
    """
    Return the first n Excel column names
    """
    default_names: list[str] = list()

    i: int = 1
    for name in excel_column_names():
        default_names.append(name)
        if i >= n:
            break
        i += 1

    return default_names


def excel_column_to_index(name: str) -> int:
    """
    An Excel column name to a one-based index
    """
    if len(name) == 1:
        return ord(name) - ord("A") + 1

    if len(name) == 2:
        return (ord(name[0]) - ord("A") + 1) * 26 + (ord(name[1]) - ord("A") + 1)

    raise Exception(f"Excel column name '{name}' is too long.")


def index_to_excel_column_name(n: int) -> str:
    """
    A one-based indexed to the Excel column name

    for i in range(1, 26 * 27 + 1):
        print(f"{i:3d} {index_to_excel_column_name(i):2s}")
    """
    n -= 1
    i: int = n % 26
    j: int = n // 26

    offset: int = ord("A")

    if j < 1:
        return chr(offset + i)
    else:
        return chr(offset + j - 1) + chr(offset + i)


### END ###
