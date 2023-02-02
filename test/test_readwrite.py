#!/usr/bin/env python3
#
# TEST DATA MODEL
#

import random

from t.readwrite import *


class TestIO:
    def test_data_type_predicates(self) -> None:
        for i in range(0, 10):
            assert not leading_zeroes(str(i))

        assert not leading_zeroes("0")
        for s in ["01", "012", "0123"]:
            assert leading_zeroes(s)
        assert is_int(str(0))

        for i in range(-10, 10 + 1):
            assert is_int(str(i))

        assert not is_int("04013000006")

        for i in range(-10, 10 + 1):
            f: float = random.random()
            assert is_float(str(i))

        for x in ["True", "true", "TRUE", "tRuE", "False", "false", "FALSE", "fAlSe"]:
            assert is_bool(x)

    def test_infer_data_types(self) -> None:
        samples: list[str]
        ti: TypeInferencer

        samples = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
        ti = TypeInferencer()
        for s in samples:
            ti.add(s)
        assert ti.infer() == int

        samples = [
            "1.1",
            "2.2",
            "3.3",
            "4.4",
            "5.5",
            "6.6",
            "7.7",
            "8.8",
            "9.9",
            "10.10",
        ]
        ti = TypeInferencer()
        for s in samples:
            ti.add(s)
        assert ti.infer() == float

        samples = ["1", "2", "3", "4", "5", "6.6", "7.7", "8.8", "9.9", "10.10"]
        ti = TypeInferencer()
        for s in samples:
            ti.add(s)
        assert ti.infer() == float

        # Leading zeroes
        samples = [
            "04013000006",
            "04013000423",
            "04013000216",
            "04013000728",
            "04013000007",
            "04013000271",
            "04013000082",
            "04013000086",
            "04013000060",
            "04013000709",
        ]
        ti = TypeInferencer()
        for s in samples:
            ti.add(s)
        assert ti.infer() == str

        # Fixed width
        samples = [
            "24013000006",
            "24013000423",
            "24013000216",
            "24013000728",
            "24013000007",
            "24013000271",
            "24013000082",
            "24013000086",
            "24013000060",
            "24013000709",
        ]
        ti = TypeInferencer()
        for s in samples:
            ti.add(s)
        assert ti.infer() == str

        samples = ["True", "true", "TRUE", "tRuE", "False", "false", "FALSE", "fAlSe"]
        ti = TypeInferencer()
        for s in samples:
            ti.add(s)
        assert ti.infer() == bool


### END ###
