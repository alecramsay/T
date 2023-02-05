#!/usr/bin/env python3
#
# TEST READ/WRITE
#

import ast
import random

from t.readwrite import *


class TestIO:
    def test_data_type_predicates(self) -> None:
        # Not valid string literal (no quotes)
        try:
            dtype: Type
            name: str
            dtype, name = type_from_literal("foo")
            assert False
        except:
            assert True

        # Valid string literal
        try:
            dtype: Type
            name: str
            dtype, name = type_from_literal('"foo"')
            assert False
        except:
            assert True

        # Leading zeroes (str)
        for i in range(0, 10):
            assert not leading_zeroes(str(i))

        assert not leading_zeroes("0")

        for s in ["01", "012", "0123"]:
            assert leading_zeroes(s)

        assert not leading_zeroes("0.0")

        # Integer
        dtype: Type
        name: str
        dtype, name = type_from_literal(str(0))
        assert dtype == int

        for i in range(-10, 10 + 1):
            dtype: Type
            name: str
            dtype, name = type_from_literal(str(i))
            assert dtype == int

        try:
            dtype: Type
            name: str
            dtype, name = type_from_literal("04013000006")
            assert False
        except:
            assert True

        # Float
        for i in range(-10, 10 + 1):
            f: float = random.random()
            dtype: Type
            name: str
            dtype, name = type_from_literal(str(i + f))
            assert dtype == float

        # Boolean
        for x in ["True", "False"]:
            dtype: Type
            name: str
            dtype, name = type_from_literal(x)
            assert dtype == bool

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
        samples = ["True", "False"]
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
            ti.add(s)
            assert ti.infer() == complex

    def test_infer_bytes(self) -> None:
        samples: list[str]
        ti: TypeInferencer

        samples = [
            'b"Hello"',
        ]
        ti = TypeInferencer()
        for s in samples:
            ti.add(s)
            assert ti.infer() == bytes

    def test_literal_eval(self) -> None:
        """
        Built-in Python data types & their literal representations:
        https://www.w3schools.com/python/python_datatypes.asp
        """

        # Valid literals
        examples: list[str] = [
            "'Hello world!'",
            "20",
            "20.5",
            "1j",
            '["apple", "banana", "cherry"]',
            '("apple", "banana", "cherry")',
            # "range(6)",
            '{"name" : "John", "age" : 36}',
            '{"apple", "banana", "cherry"}',
            # 'frozenset({"apple", "banana", "cherry"})',
            "True",
            'b"Hello"',
            # "bytearray(5)",
            # "memoryview(bytes(5))",
            "None",
        ]

        types: list[str] = [
            str,
            int,
            float,
            complex,
            list,
            tuple,
            # range, # Not supported by ast.literal_eval
            dict,
            set,
            # frozenset, # Not supported by ast.literal_eval
            bool,
            bytes,
            # bytearray, # Not supported by ast.literal_eval
            # memoryview, # Not supported by ast.literal_eval
            type(None),
        ]

        for q, a in zip(examples, types):
            dtype: Type
            name: str
            dtype, name = type_from_literal(q)
            assert dtype == a

        # Not valid literals
        examples: list[str] = [
            "range(6)",
            'frozenset({"apple", "banana", "cherry"})',
            "bytearray(5)",
            "memoryview(bytes(5))",
        ]

        types: list[str] = [
            range,  # Not supported by ast.literal_eval
            frozenset,  # Not supported by ast.literal_eval
            bytearray,  # Not supported by ast.literal_eval
            memoryview,  # Not supported by ast.literal_eval
        ]

        for q, a in zip(examples, types):
            try:
                dtype: Type
                name: str
                dtype, name = type_from_literal(q)
                assert False
            except:
                assert True


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

    def test_dtypes(self) -> None:
        sample: str = "dtypes.csv"
        reader: DelimitedFileReader = DelimitedFileReader("test/files/" + sample)
        df: pd.DataFrame = reader.read()
        assert df.shape[1] == 7
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

    pass


### END ###
