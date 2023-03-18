#!/usr/bin/env python3

"""
TEST UDF
"""

from T.udf import *


class TestUDF:
    def test_map_args(self) -> None:
        rel_path: str = "user/alec.py"
        udf: UDF = UDF(rel_path)

        call_expr: str = "composite(D_2020_ag, D_2020_gov, D_2016_sen, D_2020_sen, D_2016_pres, D_2020_pres)"
        udf_name: str = "composite"
        source: str = udf.source(udf_name)

        actual: dict[str, str] = map_args(call_expr, source)

        def_args: list[str] = ["ag", "gov", "sen1", "sen2", "pres1", "pres2"]
        call_args: list[str] = [
            "D_2020_ag",
            "D_2020_gov",
            "D_2016_sen",
            "D_2020_sen",
            "D_2016_pres",
            "D_2020_pres",
        ]

        assert actual == dict(zip(def_args, call_args))


### END ###
