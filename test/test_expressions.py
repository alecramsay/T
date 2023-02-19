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

    def test_rewrite_expr(self) -> None:
        df: str = "df"
        names: list[str] = ["GEOID20", "Tot_2020_tot", "Wh_2020_tot"]
        # tokens = ['GEOID20'].str[2:5]")

        tokens: list[str] = ["Tot_2020_tot", "-", "Wh_2020_tot"]
        actual: str = rewrite_expr(df, tokens, names)
        expected: str = "df['Tot_2020_tot'] - df['Wh_2020_tot']"


### END ###
