#!/usr/bin/env python3

"""
TEST EXCEL NAMING
"""


from T.excel import *


class TestExcelColumnNames:
    def test_excel_column_to_index(self) -> None:
        assert excel_column_to_index("A") == 1
        assert excel_column_to_index("Z") == 26
        assert excel_column_to_index("AA") == 27
        assert excel_column_to_index("AZ") == 52
        assert excel_column_to_index("ZZ") == 702

    def test_index_to_excel_column_name(self) -> None:
        assert index_to_excel_column_name(1) == "A"
        assert index_to_excel_column_name(26) == "Z"
        assert index_to_excel_column_name(27) == "AA"
        assert index_to_excel_column_name(52) == "AZ"
        assert index_to_excel_column_name(702) == "ZZ"


### END ###
