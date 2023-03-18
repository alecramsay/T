#!/usr/bin/env python3

"""
TEST DATA MODEL
"""


from T.datamodel import *


class TestDataModel:
    def test_column(self) -> None:
        s: Column = Column("GEOID", "string")
        assert s.type == "string"

        i: Column = Column("Total", "int64")
        assert i.type == "int64"

        f: Column = Column("D_pct", "float64")
        assert f.type == "float64"

        b: Column = Column("BOOLEAN", "bool")
        assert b.type == "bool"

        l: Column = Column("LIST", "object")
        assert l.type == "object"

        t: Column = Column("DATE", "datetime64")
        assert t.type == "datetime64"

        d: Column = Column("CATEGORY", "category")
        assert d.type == "category"

    def test_canonicalize_name(self) -> None:
        mod: str

        mod = Column.canonicalize_name("Total VAP")
        assert mod == "Total_VAP"

        mod = Column.canonicalize_name("Total-VAP")
        assert mod == "Total_VAP"

        mod = Column.canonicalize_name("Total.VAP")
        assert mod == "Total_VAP"

        mod = Column.canonicalize_name("123")
        assert mod == "_123"

        try:
            mod = Column.canonicalize_name("foo#bar")
            assert False
        except Exception as e:
            assert True

    def test_column_refs(self) -> None:
        sample: str = "sample-01-comma.csv"
        census: Table = Table()
        census.read("test/formats/" + sample)

        actual: bool = census.are_cols(["GEOID", "Total"])
        assert actual

        try:
            actual = census.are_cols(["GEOD", "Total"])
            assert False
        except:
            assert True

        assert not census.could_be_column("GEOID")
        assert not census.could_be_column("123")
        assert census.could_be_column("foo")


### END ###
