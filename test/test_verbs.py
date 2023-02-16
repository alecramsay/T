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

    def test_join_verb(self) -> None:
        # Join census data -- infer the join column
        y_table: Table = Table()
        y_table.read("data/rd/NC/2020_precinct_assignments_NC.csv")
        x_table: Table = Table()
        x_table.read("data/rd/NC/2020_census_NC.csv")

        f: JoinVerb = JoinVerb(y_table, x_table)
        f.apply()

        assert isinstance(f._new_table, Table)
        assert f._new_table.n_cols() == (x_table.n_cols() + y_table.n_cols() - 1)

        # Alias duplicate columns

        data: list[dict[str, Any]] = [{"ID": "foo", "a": 1, "b": 2}]
        y_table = Table()
        y_table.test(data)

        data: list[dict[str, Any]] = [{"ID": "foo", "a": 2, "c": 3}]
        x_table = Table()
        x_table.test(data)

        join_key: str = "ID"
        f = JoinVerb(y_table, x_table, on=join_key)
        f.apply()
        assert isinstance(f._new_table, Table)

        expected: set[str] = set(["ID", "a_y", "a_x", "b", "c"])
        actual: set = set(f._new_table.col_names())
        assert actual == expected

    def test_groupby_verb(self) -> None:
        sample: str = "precincts_with_counties.csv"
        x_table: Table = Table()
        x_table.read("test/files/" + sample)

        # One by column
        f: GroupByVerb = GroupByVerb(x_table, ["District"], only=["Total"], agg=["sum"])
        f.apply()

        assert True

        assert f._new_table.n_rows() == 13
        assert f._new_table.n_cols() == 2
        assert f._new_table._data.iloc[0]["Total_sum"] == 1115482

        # Two by columns
        f: GroupByVerb = GroupByVerb(
            x_table, ["District", "COUNTY"], only=["Total"], agg=["sum"]
        )
        f.apply()

        assert True

        assert f._new_table.n_rows() == 101
        assert f._new_table.n_cols() == 3
        assert f._new_table._data.iloc[0]["Total_sum"] == 1115482

        # Bad by column
        try:
            f: GroupByVerb = GroupByVerb(
                x_table, ["Disrict"], only=["Total"], agg=["sum"]
            )
            f.apply()
            assert False
        except:
            assert True

        # Bad only column name
        try:
            f: GroupByVerb = GroupByVerb(
                x_table, ["District"], only=["Totl"], agg=["sum"]
            )
            f.apply()
            assert False
        except:
            assert True

        # Bad only column type
        try:
            f: GroupByVerb = GroupByVerb(
                x_table, ["District"], only=["Total", "COUNTY"], agg=["sum"]
            )
            f.apply()
            assert False
        except:
            assert True

        # Bad agg function
        try:
            f: GroupByVerb = GroupByVerb(
                x_table, ["District"], only=["Total"], agg=["foo"]
            )
            f.apply()
            assert False
        except:
            assert True

        # By column in only list
        try:
            f: GroupByVerb = GroupByVerb(
                x_table, ["District"], only=["District", "Total"], agg=["sum"]
            )
            f.apply()
            assert False
        except:
            assert True

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

        # Matched tables
        y_table: Table = Table()
        y_table.read("test/union/first_part.csv")

        x_table: Table = Table()
        x_table.read("test/union/second_part.csv")

        try:
            f: UnionVerb = UnionVerb(y_table, x_table)
            f.apply()
            assert True
        except:
            assert False


### END ###
