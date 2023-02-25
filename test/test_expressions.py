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

    def test_regroup_slices(self) -> None:
        tokens: list[str]
        new_tokens: list[str]

        # Only a slice operator
        tokens = ["[", 2, ":", 5, "]"]
        new_tokens = mark_slices(tokens)
        assert new_tokens == ["slice[2:5]"]

        # Slice operator and more
        tokens = ["[", 2, ":", 5, "]", "+", "foo"]
        new_tokens = mark_slices(tokens)
        assert new_tokens == ["slice[2:5]", "+", "foo"]

    def test_has_valid_refs(self) -> None:
        expr: str = "composite(D_2020_ag, D_2020_gov, D_2016_sen, D_2020_sen, D_2016_pres, D_2020_pres)"
        tokens: list[str] = tokenize(expr)
        col_names: list[str] = [
            "D_2020_ag",
            "D_2020_gov",
            "D_2016_sen",
            "D_2020_sen",
            "D_2016_pres",
            "D_2020_pres",
        ]
        udf_names: list[str] = ["composite", "vote_share", "est_seat_probability"]

        try:
            has_valid_refs(tokens, col_names, udf_names)
            assert True
        except:
            assert False

    def test_collapse_udf_calls(self) -> None:
        rel_path: str = "user/alec.py"
        udf: UDF = UDF(rel_path)

        # Simple UDF call
        call_expr: str = "composite(D_2020_ag, D_2020_gov, D_2016_sen, D_2020_sen, D_2016_pres, D_2020_pres)"
        tokens: list[str] = tokenize(call_expr)

        tokens, wrappers = mark_udf_calls(tokens, udf)
        expected: list[str] = ["composite(1)"]
        assert tokens == expected

        # Unclosed UDF ref
        try:
            tokens: list[str] = tokenize(call_expr[:-1])
            tokens, wrappers = mark_udf_calls(tokens, udf)
            assert False
        except:
            assert True


### END ###
