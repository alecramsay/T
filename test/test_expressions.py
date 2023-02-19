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

        # Simple expression
        tokens: list[str] = ["Tot_2020_tot", "-", "Wh_2020_tot"]
        actual: str = rewrite_expr(df, tokens, names)
        expected: str = "df['Tot_2020_tot'] - df['Wh_2020_tot']"

        # Expression with a slice operator
        tokens: list[str] = ["GEOID20", "slice[2:5]"]
        actual: str = rewrite_expr(df, tokens, names)
        expected: str = "df['GEOID20'].str[2:5]"

    def test_is_slice(self) -> None:
        tok: str
        skip: int

        # Not a slice
        tok, skip = is_slice(["[", "foo"])
        assert not tok

        # Only a slice operator
        tok, skip = is_slice(["[", 2, ":", 5, "]"])
        assert tok
        assert skip == 5

        # Slice operator and more
        tok, skip = is_slice(["[", 2, ":", 5, "]", "+", "foo"])
        assert tok
        assert skip == 5

        # Not a slice operator
        tok, skip = is_slice(["[", 2, ":", 5])
        assert not tok

        # Not a slice operator
        tok, skip = is_slice(["[", "foo", ":", "bar", "]"])
        assert not tok


### END ###
