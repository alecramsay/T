#!/usr/bin/env python3

"""
TEST VERBS
"""

from t.verbs import *
from t.constants import *


class TestRowVerbs:
    def test_verb(self) -> None:
        sample: str = "sample-01-comma.csv"
        x_table: Table = Table()
        x_table.read("test/formats/" + sample)

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

    def test_keep_verb(self) -> None:
        sample: str = "sample-01-comma.csv"
        x_table: Table = Table()
        x_table.read("test/formats/" + sample)

        keep_refs: list[str] = ["GEOID", "Total"]
        f: KeepVerb = KeepVerb(x_table, keep_refs)
        new_table: Table = f.apply()

        assert x_table.n_cols() == 12
        assert new_table.n_cols() == 2

        # Change column order
        sample: str = "sample-01-comma.csv"
        x_table: Table = Table()
        x_table.read("test/formats/" + sample)

        keep_refs: list[str] = ["Total", "GEOID"]
        f: KeepVerb = KeepVerb(x_table, keep_refs)
        new_table: Table = f.apply()

        assert new_table.col_names() == keep_refs

    def test_drop_verb(self) -> None:
        sample: str = "sample-01-comma.csv"
        x_table: Table = Table()
        x_table.read("test/formats/" + sample)

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
        x_table: Table = Table()
        x_table.read("test/files/" + sample)

        col_specs: list[tuple[str, str]] = [
            ("GEOID20", "GEOID"),
            ("Tot_2020_tot", "Total"),
        ]
        f: RenameVerb = RenameVerb(x_table, col_specs)
        new_table: Table = f.apply()

        assert new_table.is_column("GEOID")
        assert new_table.is_column("Total")

    def test_alias_verb(self) -> None:
        sample: str = "2020_census_AZ(PARTIAL).csv"
        x_table: Table = Table()
        x_table.read("test/files/" + sample)

        # Alias some columns
        alias_cols: list = [
            ("GEOID20", "GEOID"),
            ("Tot_2020_tot", "Total"),
            ("Tot_2020_vap", "Total_VAP"),
            ("Wh_2020_vap", "White"),
            ("His_2020_vap", "Hispanic"),
            ("BlC_2020_vap", "Black"),
            ("NatC_2020_vap", "Native"),
            ("AsnC_2020_vap", "Asian"),
            ("PacC_2020_vap", "Pacific"),
        ]
        f: AliasVerb = AliasVerb(x_table, alias_cols)
        f.apply()

        for col in f._new_table._cols:
            name: str = col.name
            if name in f._col_refs:
                i: int = f._col_refs.index(name)
                expected: str = f._new_col_refs[i].alias
                actual: str = col.alias
                assert actual == expected

        # Re-alias some columns
        re_aliased_cols: list = [
            ("Total", "Total_REALIASED"),
            ("White", "White_REALIASED"),
        ]

        x_table = f._new_table
        g: AliasVerb = AliasVerb(x_table, re_aliased_cols)
        g.apply()

        for col in g._new_table._cols:
            name = col.name
            if name in g._col_refs:
                i = g._col_refs.index(name)
                expected = g.new_cols[i].alias
                actual = col.alias
                assert actual == expected

    def test_first_verb(self) -> None:
        sample: str = "2020_census_AZ(PARTIAL).csv"  # 100 rows
        x_table: Table = Table()
        x_table.read("test/files/" + sample)

        # n = #
        f: FirstVerb = FirstVerb(x_table, 10)
        f.apply()

        actual: int = f._new_table.n_rows()
        expected: int = 10

        assert actual == expected

        # n = pct
        f = FirstVerb(x_table, 20, "%")
        f.apply()

        actual = f._new_table.n_rows()
        expected = 20

        assert actual == expected

    def test_last_verb(self) -> None:
        sample: str = "2020_census_AZ(PARTIAL).csv"  # 100 rows
        x_table: Table = Table()
        x_table.read("test/files/" + sample)

        # n = #
        f: LastVerb = LastVerb(x_table, 10)
        f.apply()

        actual: int = f._new_table.n_rows()
        expected: int = 10

        assert actual == expected

        # n = pct
        f = LastVerb(x_table, 20, "%")
        f.apply()

        actual = f._new_table.n_rows()
        expected = 20

        assert actual == expected

    def test_sample_verb(self) -> None:
        sample: str = "2020_census_AZ(PARTIAL).csv"  # 100 rows
        x_table: Table = Table()
        x_table.read("test/files/" + sample)

        # n = #
        f: SampleVerb = SampleVerb(x_table, 10)
        f.apply()

        actual: int = f._new_table.n_rows()
        expected: int = 10

        assert actual == expected

        # n = pct
        f = SampleVerb(x_table, 20, "%")
        f.apply()

        actual = f._new_table.n_rows()
        expected = 20

        assert actual == expected


class TestTableVerbs:
    def test_sort_verb(self) -> None:
        x_table: Table = Table()
        x_table.test(CITIES_DF)

        actual: int = x_table._data.iloc[0]["population"]
        expected: int = 698660

        assert actual == expected

        f: SortVerb = SortVerb(x_table, [("population", "DESC")])
        f.apply()

        actual: int = f._new_table._data.iloc[0]["population"]
        expected: int = 14043239

        assert actual == expected

    def test_union_verb(self) -> None:
        # Matched tables
        y_table: Table = Table()
        y_table.test(CITIES_DF)

        x_table: Table = Table()
        x_table.test(CITIES_DF)

        f: UnionVerb = UnionVerb(y_table, x_table)
        f.apply()

        actual: int = f._new_table.n_rows()
        expected: int = 6
        assert actual == expected

        # Mismatched tables
        y_table: Table = Table()
        y_table.test(CITIES_DF)

        x_table: Table = Table()
        x_table.test(PRODUCTS_DF)

        try:
            f: UnionVerb = UnionVerb(y_table, x_table)
            f.apply()
            assert False
        except:
            assert True


### END ###
