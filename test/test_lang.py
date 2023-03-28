#!/usr/bin/env python3

"""
TEST LANG
"""

from T.run import run_script


class TestLangHelpers:
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

    # TODO - def test_join(self) -> None:

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

    # TODO - def test_grouby(self) -> None:

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

    # TODO - def test_UDF(self) -> None:

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

    # TODO - def test_cast(self) -> None:

    # TODO - def test_scriptargs(self) -> None:

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
