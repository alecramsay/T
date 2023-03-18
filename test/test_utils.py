#!/usr/bin/env python3

"""
TEST UTILTIES
"""

from T.utils import *


class TestUtils:
    def test_parse_spec(self) -> None:
        assert parse_spec("ONLY") == ("ONLY", "ONLY")
        assert parse_spec(["FIRST", "SECOND"]) == ("FIRST", "SECOND")
        assert parse_spec(["COLUMN", "ASC"]) == ("COLUMN", "ASC")

    def test_is_list_of_str(self) -> None:
        assert is_list_of_str(["foo", "bar"])
        assert not is_list_of_str(["foo", 1])
        assert not is_list_of_str(["foo", ["bar"]])


### END ###
