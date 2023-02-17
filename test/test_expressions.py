#!/usr/bin/env python3

"""
TEST EXPRESSION HANDLING
"""

from t.expressions import *


class TestExpressions:
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


### END ###
