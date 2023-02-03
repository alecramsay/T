#!/usr/bin/env python3

"""
TEST DATA MODEL
"""


from t.datamodel import *


class TestDataModel:
    def test_column(self) -> None:
        s: Column = Column("GEOID", str)
        assert s.type == str

        i: Column = Column("Total", int)
        assert i.type == int

        f: Column = Column("D_pct", float)
        assert f.type == float

        b: Column = Column("BOOLEAN", bool)
        assert b.type == bool

        l: Column = Column("LIST", list)
        assert l.type == list

        t: Column = Column("TUPLE", tuple)
        assert t.type == tuple

        d: Column = Column("DICT", dict)
        assert d.type == dict

        s = Column("SET", set)
        assert s.type == set

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


### END ###
