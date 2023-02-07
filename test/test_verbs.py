#!/usr/bin/env python3

"""
TEST VERBS
"""

from t.verbs import *


class TestRowVerbs:
    def test_verb(self) -> None:
        sample: str = "sample-01-comma.csv"
        x_table: Table = Table("test/formats/" + sample)

        good: list[str] = ["GEOID", "Total"]
        f: Verb = Verb()
        f._validate_col_refs(good, x_table)
        assert True

        try:
            bad: list[str] = ["GEOID20", "foo"]
            f = Verb()
            f._validate_col_refs(bad, x_table)
            assert False
        except:
            assert True

    def test_keep_verb(self):
        sample: str = "sample-01-comma.csv"
        x_table: Table = Table("test/formats/" + sample)

        keep_refs: list[str] = ["GEOID", "Total"]
        f: KeepVerb = KeepVerb(x_table, keep_refs)
        new_table: Table = f.apply()

        assert x_table.n_cols() == 12
        assert new_table.n_cols() == 2

    def test_drop_verb(self):
        sample: str = "sample-01-comma.csv"
        x_table: Table = Table("test/formats/" + sample)

        drop_refs: list[str] = [
            "District",
            "Total",
            "Total_VAP",
            "White",
            "Hispanic",
            "Black",
            "Native",
            "Asian",
            "Pacific",
        ]
        f: DropVerb = DropVerb(x_table, drop_refs)
        new_table: Table = f.apply()

        assert x_table.n_cols() == 12
        assert new_table.n_cols() == 3

    def test_rename_verb(self) -> None:
        sample: str = "2020_census_AZ(PARTIAL).csv"
        x_table: Table = Table("test/files/" + sample)

        col_specs: list[tuple[str, str]] = [
            ("GEOID20", "GEOID"),
            ("Tot_2020_tot", "Total"),
        ]
        f: RenameVerb = RenameVerb(x_table, col_specs)
        new_table: Table = f.apply()

        assert new_table.is_column("GEOID")
        assert new_table.is_column("Total")


### END ###
