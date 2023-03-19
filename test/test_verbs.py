#!/usr/bin/env python3

"""
TEST VERBS
"""

from T.verbs import *
from T.constants import *


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
        # Same column order
        sample: str = "sample-01-comma.csv"
        x_table: Table = Table()
        x_table.read("test/formats/" + sample)

        keep_refs: list[str] = ["GEOID", "Total"]
        f: KeepVerb = KeepVerb(x_table, keep_refs)
        new_table: Table = f.apply()

        assert x_table.n_cols == 12
        assert new_table.n_cols == 2

        # Change column order
        sample: str = "sample-01-comma.csv"
        x_table: Table = Table()
        x_table.read("test/formats/" + sample)

        keep_refs: list[str] = ["Total", "GEOID"]
        f: KeepVerb = KeepVerb(x_table, keep_refs)
        new_table: Table = f.apply()

        assert new_table.col_names() == keep_refs
        assert new_table.n_cols == 2

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

        assert x_table.n_cols == 12
        assert new_table.n_cols == 3

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
            assert f._col_refs is not None
            if name in f._col_refs:
                i: int = f._col_refs.index(name)
                expected: str = f._new_col_refs[i]
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
            assert g._col_refs is not None
            if name in g._col_refs:
                i = g._col_refs.index(name)
                expected: str = g._new_col_refs[i]
                actual = col.alias
                assert actual == expected

    def test_select_verb(self) -> None:
        expr: str = "county_fips == '019'"

        # No match
        data: dict[str, list] = {
            "GEOID20": ["370210001.1"],
            "Tot_2010_tot": [2310],
            "county_fips": ["021"],
        }
        x_table: Table = Table()
        x_table.test(data)

        f: SelectVerb = SelectVerb(x_table, expr)
        f.apply()

        actual: int = f._new_table.n_rows
        expected: int = 0

        assert actual == expected

        # Match
        data: dict[str, list] = {
            "GEOID20": ["370210001.1"],
            "Tot_2010_tot": [2310],
            "county_fips": ["019"],
        }
        x_table: Table = Table()
        x_table.test(data)

        f = SelectVerb(x_table, expr)
        f.apply()

        actual = f._new_table.n_rows
        expected = 1

        assert actual == expected

        # Bad column name
        try:
            expr: str = "county == '019'"
            x_table: Table = Table()
            x_table.test(data)

            f = SelectVerb(x_table, expr)
            f.apply()
            assert False
        except:
            assert True

        # Equal sign
        try:
            expr: str = "county_fips = '019'"
            x_table: Table = Table()
            x_table.test(data)

            f = SelectVerb(x_table, expr)
            f.apply()
            assert False
        except:
            assert True

    def test_first_verb(self) -> None:
        sample: str = "2020_census_AZ(PARTIAL).csv"  # 100 rows
        x_table: Table = Table()
        x_table.read("test/files/" + sample)

        # n = #
        f: FirstVerb = FirstVerb(x_table, 10)
        f.apply()

        actual: int = f._new_table.n_rows
        expected: int = 10

        assert actual == expected

        # n = pct
        f = FirstVerb(x_table, 20, "%")
        f.apply()

        actual = f._new_table.n_rows
        expected = 20

        assert actual == expected

    def test_last_verb(self) -> None:
        sample: str = "2020_census_AZ(PARTIAL).csv"  # 100 rows
        x_table: Table = Table()
        x_table.read("test/files/" + sample)

        # n = #
        f: LastVerb = LastVerb(x_table, 10)
        f.apply()

        actual: int = f._new_table.n_rows
        expected: int = 10

        assert actual == expected

        # n = pct
        f = LastVerb(x_table, 20, "%")
        f.apply()

        actual = f._new_table.n_rows
        expected = 20

        assert actual == expected

    def test_sample_verb(self) -> None:
        sample: str = "2020_census_AZ(PARTIAL).csv"  # 100 rows
        x_table: Table = Table()
        x_table.read("test/files/" + sample)

        # n = #
        f: SampleVerb = SampleVerb(x_table, 10)
        f.apply()

        actual: int = f._new_table.n_rows
        expected: int = 10

        assert actual == expected

        # n = pct
        f = SampleVerb(x_table, 20, "%")
        f.apply()

        actual = f._new_table.n_rows
        expected = 20

        assert actual == expected

    def test_cast_verb(self) -> None:
        sample: str = "sample-01-comma.csv"
        x_table: Table = Table()
        x_table.read("test/formats/" + sample)
        col_names: list[str] = x_table.col_names()

        cast_cols: list[str] = ["District", "Total", "Total_VAP", "White", "Hispanic"]
        new_type: str = "int64"
        f: CastVerb = CastVerb(x_table, cast_cols, new_type)
        new_table: Table = f.apply()

        actual: list[str] = [new_table._data[col].dtype.name for col in col_names]
        expected: list[str] = [
            "string",
            "int64",
            "int64",
            "int64",
            "int64",
            "int64",
            "int64",
            "int64",
            "int64",
            "int64",
            "float64",
            "float64",
        ]

        assert actual == expected

        actual = new_table.col_types()
        assert actual == expected

    def test_derive_verb(self) -> None:
        # Simple expression
        data: dict[str, list] = {
            "GEOID20": ["370210001.1"],
            "Tot_2020_tot": [2310],
            "Wh_2020_tot": [987],
        }
        x_table: Table = Table()
        x_table.test(data)

        name: str = "Minority_2020_tot"
        expr: str = "Tot_2020_tot - Wh_2020_tot"
        f: DeriveVerb = DeriveVerb(x_table, name, expr)
        new_table: Table = f.apply()

        actual: int = new_table.n_cols
        expected: int = 4

        assert actual == expected

        # Expression with slice operator
        data: dict[str, list] = {
            "GEOID20": ["370210001.1"],
            "Tot_2020_tot": [2310],
            "Wh_2020_tot": [987],
        }
        x_table: Table = Table()
        x_table.test(data)

        name: str = "county_fips"
        expr: str = "GEOID20[2:5]"
        f: DeriveVerb = DeriveVerb(x_table, name, expr)
        new_table: Table = f.apply()

        actual: int = new_table.n_cols
        expected: int = 4

        assert actual == expected

        # Expression with UDF

        x_table: Table = Table()
        x_table.read("data/rd/NC/2020_election_NC.csv")
        expected = len(x_table._data.columns) + 1

        rel_path: str = "user/alec.py"
        udf: UDF = UDF(rel_path)

        name: str = "D_pct"
        expr: str = "vote_share(D_2020_pres, R_2020_pres)"
        f: DeriveVerb = DeriveVerb(x_table, name, expr, udf)
        new_table: Table = f.apply()
        actual = len(new_table._data.columns)

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
        assert f._new_table.n_cols == (x_table.n_cols + y_table.n_cols - 1)

        ## Explicit join type
        join_type: str = "inner"
        f: JoinVerb = JoinVerb(y_table, x_table, how=join_type)
        f.apply()

        assert isinstance(f._new_table, Table)

        ## Explicit validation
        try:
            validation: str = "1:1"
            f: JoinVerb = JoinVerb(y_table, x_table, validate=validation)
            f.apply()
            assert True
        except:
            assert False

        data: dict[str, list]

        # Alias duplicate columns
        data = {
            "ID": ["foo"],
            "a": [1],
            "b": [2],
        }
        # data: list[dict[str, Any]] = [{"ID": "foo", "a": 1, "b": 2}]
        y_table = Table()
        y_table.test(data)

        data = {
            "ID": ["foo"],
            "a": [2],
            "c": [3],
        }
        # data: list[dict[str, Any]] = [{"ID": "foo", "a": 2, "c": 3}]
        x_table = Table()
        x_table.test(data)

        join_key: Any
        join_key = "ID"
        f = JoinVerb(y_table, x_table, on=join_key)
        f.apply()
        assert isinstance(f._new_table, Table)

        expected: set[str] = set(["ID", "a_y", "a_x", "b", "c"])
        actual: set = set(f._new_table.col_names())
        assert actual == expected

        ## Explicit suffixes
        join_key = "ID"
        suffixes = (None, "_mumble")
        f = JoinVerb(y_table, x_table, on=join_key, suffixes=suffixes)
        f.apply()
        assert isinstance(f._new_table, Table)

        expected: set[str] = set(["ID", "a", "a_mumble", "b", "c"])
        actual: set = set(f._new_table.col_names())
        assert actual == expected

        # No shared columns
        data = {
            "a": [1],
            "b": [2],
            "c": [3],
        }
        # data4: list[dict[str, Any]] = [{"a": 1, "b": 2, "c": 3}]
        y_table = Table()
        y_table.test(data)

        data = {
            "d": ["foo"],
            "e": ["bas"],
            "f": ["bat"],
        }
        # data4 = [{"d": "foo", "e": "bas", "f": "bat"}]
        x_table = Table()
        x_table.test(data)

        try:
            f = JoinVerb(y_table, x_table)
            f.apply()
            assert False
        except:
            assert True

        # Matching join keys but no shared columns
        data = {
            "a": [1],
            "b": [2],
            "c": [3],
        }
        # data3: list[dict[str, Any]] = [{"a": 1, "b": 2, "c": 3}]
        y_table = Table()
        y_table.test(data)

        data = {
            "d": [1],
            "e": ["bas"],
            "f": ["bat"],
        }
        # data3 = [{"d": 1, "e": "bas", "f": "bat"}]
        x_table = Table()
        x_table.test(data)

        try:
            on: Optional[str | list[str] | list[list[str]]] = [["a"], ["d"]]
            f = JoinVerb(y_table, x_table, on=on)
            f.apply()
            assert True
        except:
            assert False

        # Mismatched join keys
        data = {
            "a": [1],
            "b": [2],
            "c": [3],
        }
        # data2: list[dict[str, Any]] = [{"a": 1, "b": 2, "c": 3}]
        y_table = Table()
        y_table.test(data)

        data = {
            "a": ["foo"],
            "e": ["bas"],
            "f": ["bat"],
        }
        # data2 = [{"a": "foo", "e": "bas", "f": "bat"}]
        x_table = Table()
        x_table.test(data)

        try:
            f = JoinVerb(y_table, x_table)
            f.apply()
            assert False
        except:
            assert True

        # Invalid parameters

        data = {
            "ID": ["foo"],
            "a": [1],
            "b": [2],
        }
        # data1: list[dict[str, Any]] = [{"ID": "foo", "a": 1, "b": 2}]
        y_table = Table()
        y_table.test(data)

        data = {
            "ID": ["foo"],
            "c": [2],
            "d": [3],
        }
        # data1 = [{"ID": "foo", "c": 2, "d": 3}]
        x_table = Table()
        x_table.test(data)

        ## Bad join key
        try:
            join_key = ["ID", ["ID", "c"]]
            f = JoinVerb(y_table, x_table, on=join_key)
            f.apply()
            assert False
        except:
            assert True

        ## Bad join type
        try:
            join_key = "ID"
            join_type: str = "mumble"
            f = JoinVerb(y_table, x_table, on=join_key, how=join_type)
            f.apply()
            assert False
        except:
            assert True

        ## Bad suffixes
        try:
            join_key = "ID"
            suffixes: tuple[Optional[str], Optional[str]] = (None, None)
            f = JoinVerb(y_table, x_table, on=join_key, suffixes=suffixes)
            f.apply()
            assert False
        except:
            assert True

        ## Bad validate
        try:
            join_key = "ID"
            validate: ValidationOptions = "mumble"
            f = JoinVerb(y_table, x_table, on=join_key, validate=validate)
            f.apply()
            assert False
        except:
            assert True

    def test_groupby_verb(self) -> None:
        sample: str = "precincts_with_counties.csv"
        x_table: Table = Table()
        x_table.read("test/files/" + sample)

        # One by column
        f: GroupByVerb = GroupByVerb(x_table, ["District"], only=["Total"], agg=["sum"])
        f.apply()

        assert True

        assert f._new_table.n_rows == 13
        assert f._new_table.n_cols == 2
        assert f._new_table._data.iloc[0]["Total_sum"] == 1115482

        # Two by columns
        f: GroupByVerb = GroupByVerb(
            x_table, ["District", "COUNTY"], only=["Total"], agg=["sum"]
        )
        f.apply()

        assert True

        assert f._new_table.n_rows == 101
        assert f._new_table.n_cols == 3
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

        assert f._new_table is not None
        actual: int = f._new_table.n_rows
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
