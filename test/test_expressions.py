#!/usr/bin/env python3

"""
TEST EXPRESSION HANDLING
"""

from T.expressions import *


class TestExpressions:
    def test_generate_df_syntax(self) -> None:
        names: list[str] = ["GEOID20", "Tot_2020_tot", "Wh_2020_tot"]

        # Simple expression
        tokens: list[str] = ["Tot_2020_tot", "-", "Wh_2020_tot"]
        actual: str = generate_df_syntax(tokens, names)
        expected: str = "df['Tot_2020_tot'] - df['Wh_2020_tot']"

        # Expression with a slice operator
        tokens: list[str] = ["GEOID20", "slice[2:5]"]
        actual: str = generate_df_syntax(tokens, names)
        expected: str = "df['GEOID20'].str[2:5]"

    def test_isslice(self) -> None:
        tok: str
        skip: int

        # Not a slice
        tok, skip = get_slice_tokens(["[", "foo"])
        assert not tok

        # Only a slice operator
        tok, skip = get_slice_tokens(["[", str(2), ":", str(5), "]"])
        assert tok
        assert skip == 5

        # Slice operator and more
        tok, skip = get_slice_tokens(["[", str(2), ":", str(5), "]", "+", "foo"])
        assert tok
        assert skip == 5

        # Not a slice operator
        tok, skip = get_slice_tokens(["[", str(2), ":", str(5)])
        assert not tok

        # Not a slice operator
        tok, skip = get_slice_tokens(["[", "foo", ":", "bar", "]"])
        assert not tok

    def test_mark_slices(self) -> None:
        tokens: list[str]
        new_tokens: list[str]

        # Only a slice operator
        tokens = ["[", str(2), ":", str(5), "]"]
        new_tokens = mark_slices(tokens)
        assert new_tokens == ["slice[2:5]"]

        # Slice operator and more
        tokens = ["[", str(2), ":", str(5), "]", "+", "foo"]
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

    def test_mark_udf_calls(self) -> None:
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
