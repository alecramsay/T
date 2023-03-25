#!/usr/bin/env python3

"""
TEST UTILTIES
"""

from T.utils import *


class TestUtils:
    def test_tokenize(self) -> None:
        actual: list[str] = tokenize("a = b")
        expected: list[str] = ["a", "=", "b"]
        assert actual == expected

        actual = tokenize("a = b + c")
        expected = ["a", "=", "b", "+", "c"]
        assert actual == expected

        actual: list[str] = tokenize("a == b")
        expected: list[str] = ["a", "==", "b"]
        assert actual == expected

        actual = tokenize("   a=b+c   ")
        expected = ["a", "=", "b", "+", "c"]
        assert actual == expected

    def test_parse_spec(self) -> None:
        assert parse_spec("ONLY") == ("ONLY", "ONLY")
        assert parse_spec(["FIRST", "SECOND"]) == ("FIRST", "SECOND")
        assert parse_spec(["COLUMN", "ASC"]) == ("COLUMN", "ASC")

    def test_split_col_spec_string(self) -> None:
        assert split_col_spec_string("(foo, bar)") == ("foo", "bar")

    def test_islistofstr(self) -> None:
        assert islistofstr(["foo", "bar"])
        assert not islistofstr(["foo", 1])
        assert not islistofstr(["foo", ["bar"]])

    def test_find_args_string(self) -> None:
        examples: list[str] = [
            "def composite(ag, gov, sen1, sen2, pres1, pres2) -> float:",
            "composite(D_2020_ag, D_2020_gov, D_2016_sen, D_2020_sen, D_2016_pres, D_2020_pres)",
        ]
        expected: list[str] = [
            "ag, gov, sen1, sen2, pres1, pres2",
            "D_2020_ag, D_2020_gov, D_2016_sen, D_2020_sen, D_2016_pres, D_2020_pres",
        ]
        for i, example in enumerate(examples):
            left: int
            right: int
            left, right = find_args_string(example)
            args_string: str = example[left + 1 : right]

            assert args_string == expected[i]

    def test_split_args_string(self) -> None:
        examples: list[str] = [
            "def composite(ag, gov, sen1, sen2, pres1, pres2) -> float:",
            "composite(D_2020_ag, D_2020_gov, D_2016_sen, D_2020_sen, D_2016_pres, D_2020_pres)",
        ]
        expected: list[list[str]] = [
            ["ag", "gov", "sen1", "sen2", "pres1", "pres2"],
            [
                "D_2020_ag",
                "D_2020_gov",
                "D_2016_sen",
                "D_2020_sen",
                "D_2016_pres",
                "D_2020_pres",
            ],
        ]
        for i, example in enumerate(examples):
            left: int
            right: int
            left, right = find_args_string(example)
            args_list: list[str] = split_args_string(example[left + 1 : right])

            assert args_list == expected[i]

        pass  # TODO - More ...


### END ###
