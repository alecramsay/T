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

    def test_infer_int(self) -> None:
        samples: list[str]
        ti: TypeInferencer

        samples = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
        ti = TypeInferencer()
        for s in samples:
            ti.add(s)
        assert ti.infer() == int

    def test_infer_float(self) -> None:
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

    def test_infer_mixed_numbers(self) -> None:
        samples = ["1", "2", "3", "4", "5", "6.6", "7.7", "8.8", "9.9", "10.10"]
        ti = TypeInferencer()
        for s in samples:
            ti.add(s)
        assert ti.infer() == float

    def test_infer_leading_zeroes(self) -> None:
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

    def test_infer_bool(self) -> None:
        samples = ["True", "true", "TRUE", "tRuE", "False", "false", "FALSE", "fAlSe"]
        ti = TypeInferencer()
        for s in samples:
            ti.add(s)
        assert ti.infer() == bool

    def test_infer_complex(self) -> None:
        samples: list[str]
        ti: TypeInferencer

        samples = [
            "3+5j",
            "3+6j",
            "-2.298223593415307508e-11+2.117954721174255306e-09j",
        ]
        ti = TypeInferencer()
        for s in samples:
            assert is_complex(s)

        # TODO - test integration into inferencer

    def test_infer_bytes(self) -> None:
        samples: list[str]
        ti: TypeInferencer

        samples = [
            b"\x7f\x45\x4c\x46\x01\x01\x01\x00",
            b"\x7fELF\x01\x01\x01\0",
            b"\xe8\x03",
        ]
        ti = TypeInferencer()
        for s in samples:
            assert is_bytes(s)

        # TODO - test integration into inferencer


root: str = "test/formats/"


class TestDelimitedFileReader:
    def test_comma_delimiter(self) -> None:
        sample: str = "sample-01-comma.csv"
        reader: DelimitedFileReader = DelimitedFileReader(root + sample)
        df: pd.DataFrame = reader.read()
        assert df.shape[1] == 12
        assert df.shape[0] == 10

    def test_space_delimiter(self) -> None:
        sample: str = "sample-02-space.csv"
        reader: DelimitedFileReader = DelimitedFileReader(
            root + sample, delimiter="space"
        )
        df: pd.DataFrame = reader.read()
        assert df.shape[1] == 12
        assert df.shape[0] == 10

    def test_tab_delimiter(self) -> None:
        sample: str = "sample-03-tab.tsv"
        reader: DelimitedFileReader = DelimitedFileReader(
            root + sample, delimiter="tab"
        )
        df: pd.DataFrame = reader.read()
        assert df.shape[1] == 12
        assert df.shape[0] == 10

    def test_pipe_delimiter(self) -> None:
        sample: str = "sample-04-pipe.csv"
        reader: DelimitedFileReader = DelimitedFileReader(
            root + sample, delimiter="pipe"
        )
        df: pd.DataFrame = reader.read()
        assert df.shape[1] == 12
        assert df.shape[0] == 10

    def test_noheader(self) -> None:
        sample: str = "sample-05-noheader.csv"
        reader: DelimitedFileReader = DelimitedFileReader(root + sample, header=False)
        df: pd.DataFrame = reader.read()
        assert df.shape[1] == 12
        assert df.shape[0] == 10

    # NOTE - Not currently supporting explicit column types.
    # def test_explicit_types(self) -> None:
    #     sample: str = "sample-01-comma.csv"
    #     col_types: list = [
    #         str,
    #         int,
    #         int,
    #         int,
    #         int,
    #         int,
    #         int,
    #         int,
    #         int,
    #         int,
    #         float,
    #         float,
    #     ]
    #     reader: DelimitedFileReader = DelimitedFileReader(
    #         root + sample, col_types=col_types
    #     )
    #     t: Table = reader.read()
    #     assert t.col_types() == col_types


### END ###
