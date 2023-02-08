#!/usr/bin/env python3

"""
TEST UTILTIES
"""

from t.utils import *


class TestUtils:
    def test_parse_spec(self) -> None:
        assert parse_spec("ONLY") == ("ONLY", "ONLY")
        assert parse_spec(["FIRST", "SECOND"]) == ("FIRST", "SECOND")
        assert parse_spec(["COLUMN", "ASC"]) == ("COLUMN", "ASC")


### END ###
