#!/usr/bin/env python3

"""
TEST LANG
"""

from typing import Optional

from T.lang import *
from T.run import run_script


class TestLangHandlers:
    def test_from(self) -> None:
        try:
            run_script(
                user="user/alec.py",
                file="from.t",
                src="test/lang",
                data="test/files",
                output="",
                log="",
                verbose=False,
                scriptargs=dict(),
            )
            assert True
        except:
            assert False

    def test_duplicate(self) -> None:
        try:
            run_script(
                user="user/alec.py",
                file="duplicate.t",
                src="test/lang",
                data="test/files",
                output="",
                log="",
                verbose=False,
                scriptargs=dict(),
            )
            assert True
        except:
            assert False

    def test_sort(self) -> None:
        try:
            run_script(
                user="user/alec.py",
                file="sort.t",
                src="test/lang",
                data="test/files",
                output="",
                log="",
                verbose=False,
                scriptargs=dict(),
            )
            assert True
        except:
            assert False

    def test_join(self) -> None:
        try:
            run_script(
                user="user/alec.py",
                file="join.t",
                src="test/lang",
                data="test/join",
                output="",
                log="",
                verbose=False,
                scriptargs=dict(),
            )
            assert True
        except:
            assert False

        try:
            run_script(
                user="user/alec.py",
                file="join3.t",
                src="test/lang",
                data="data/rd/NC",
                output="",
                log="",
                verbose=False,
                scriptargs=dict(),
            )
            assert True
        except:
            assert False

    def test_parse_join_on(self) -> None:
        cases: list[dict] = [
            {},  # Case 1
            {"on": "foo"},  # Case 2
            {"on": "[foo, bar]"},  # Case 3
            {"on": "[[county_fips], [FIPS]]"},  # Case 4
        ]
        expected: list = [
            None,
            "foo",
            ["foo", "bar"],
            [["county_fips"], ["FIPS"]],
        ]

        for i, case in enumerate(cases):
            actual: Optional[str | list[str] | list[list[str]]] = parse_join_on(case)
            assert actual == expected[i]

    def test_union(self) -> None:
        try:
            run_script(
                user="user/alec.py",
                file="union.t",
                src="test/lang",
                data="test/union",
                output="",
                log="",
                verbose=False,
                scriptargs=dict(),
            )
            assert True
        except:
            assert False

    def test_groupby(self) -> None:
        try:
            run_script(
                user="user/alec.py",
                file="groupby.t",
                src="test/lang",
                data="test/files",
                output="",
                log="",
                verbose=False,
                scriptargs=dict(),
            )
            assert True
        except:
            assert False

        try:
            run_script(
                user="user/alec.py",
                file="groupby2.t",
                src="test/lang",
                data="test/files",
                output="",
                log="",
                verbose=False,
                scriptargs=dict(),
            )
            assert True
        except:
            assert False

    def test_keep(self) -> None:
        try:
            run_script(
                user="user/alec.py",
                file="keep.t",
                src="test/lang",
                data="test/files",
                output="",
                log="",
                verbose=False,
                scriptargs=dict(),
            )
            assert True
        except:
            assert False

    def test_drop(self) -> None:
        try:
            run_script(
                user="user/alec.py",
                file="drop.t",
                src="test/lang",
                data="test/files",
                output="",
                log="",
                verbose=False,
                scriptargs=dict(),
            )
            assert True
        except:
            assert False

    def test_rename(self) -> None:
        try:
            run_script(
                user="user/alec.py",
                file="rename.t",
                src="test/lang",
                data="test/files",
                output="",
                log="",
                verbose=False,
                scriptargs=dict(),
            )
            assert True
        except:
            assert False

    def test_alias(self) -> None:
        try:
            run_script(
                user="user/alec.py",
                file="alias.t",
                src="test/lang",
                data="test/files",
                output="",
                log="",
                verbose=False,
                scriptargs=dict(),
            )
            assert True
        except:
            assert False

    def test_derive(self) -> None:
        try:
            run_script(
                user="user/alec.py",
                file="derive.t",
                src="test/lang",
                data="test/files",
                output="",
                log="",
                verbose=False,
                scriptargs=dict(),
            )
            assert True
        except:
            assert False

    def test_UDF(self) -> None:
        try:
            run_script(
                user="user/alec.py",
                file="udf.t",
                src="test/lang",
                data="test/files",
                output="",
                log="",
                verbose=False,
                scriptargs=dict(),
            )
            assert True
        except:
            assert False

    def test_select(self) -> None:
        try:
            run_script(
                user="user/alec.py",
                file="select.t",
                src="test/lang",
                data="test/files",
                output="",
                log="",
                verbose=False,
                scriptargs=dict(),
            )
            assert True
        except:
            assert False

    def test_first(self) -> None:
        try:
            run_script(
                user="user/alec.py",
                file="first.t",
                src="test/lang",
                data="test/files",
                output="",
                log="",
                verbose=False,
                scriptargs=dict(),
            )
            assert True
        except:
            assert False

    def test_last(self) -> None:
        try:
            run_script(
                user="user/alec.py",
                file="last.t",
                src="test/lang",
                data="test/files",
                output="",
                log="",
                verbose=False,
                scriptargs=dict(),
            )
            assert True
        except:
            assert False

    def test_sample(self) -> None:
        try:
            run_script(
                user="user/alec.py",
                file="sample.t",
                src="test/lang",
                data="test/files",
                output="",
                log="",
                verbose=False,
                scriptargs=dict(),
            )
            assert True
        except:
            assert False

    def test_cast(self) -> None:
        try:
            run_script(
                user="user/alec.py",
                file="cast.t",
                src="test/lang",
                data="test/files",
                output="",
                log="",
                verbose=False,
                scriptargs=dict(),
            )
            assert True
        except:
            assert False

    def test_scriptargs(self) -> None:
        try:
            scriptargs = {"census": "2020_census_AZ.csv"}
            run_script(
                user="user/alec.py",
                file="scriptargs.t",
                src="test/lang",
                data="test/files",
                output="",
                log="",
                verbose=False,
                scriptargs=dict(),
            )
            assert True
        except:
            assert False

    def test_show(self) -> None:
        try:
            run_script(
                user="user/alec.py",
                file="show.t",
                src="test/lang",
                data="test/files",
                output="",
                log="",
                verbose=False,
                scriptargs=dict(),
            )
            assert True
        except:
            assert False

    def test_inspect(self) -> None:
        try:
            run_script(
                user="user/alec.py",
                file="inspect.t",
                src="test/lang",
                data="test/files",
                output="",
                log="",
                verbose=False,
                scriptargs=dict(),
            )
            assert True
        except:
            assert False

    def test_stack(self) -> None:
        try:
            run_script(
                user="user/alec.py",
                file="stack.t",
                src="test/lang",
                data="test/files",
                output="",
                log="",
                verbose=False,
                scriptargs=dict(),
            )
            assert True
        except:
            assert False


### END ###
