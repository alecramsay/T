#!/usr/bin/env python3
#
# READER HELPERS
#

from T.reader import *


class TestReader:
    def test_trim_whitespace(self) -> None:
        expected: str = "foo bar bas"

        left: str = "   foo bar bas"
        assert trim_whitespace(left) == expected

        right: str = "foo bar bas   "
        assert trim_whitespace(right) == expected

        both: str = "   foo bar bas  "
        assert trim_whitespace(both) == expected

    def test_remove_hash_comments(self) -> None:
        expected: str = "foo bar bas"

        no_comment: str = "foo bar bas"
        assert remove_hash_comments(no_comment) == expected

        inline_comment: str = "foo bar bas# comment"
        assert remove_hash_comments(inline_comment) == expected

        whole_line_comment: str = "# foo bar bas"
        assert remove_hash_comments(whole_line_comment) == ""

    def test_remove_inline_block_comments(self) -> None:
        expected: str = "foo bar bas"

        no_comment: str = "foo bar bas"
        assert remove_inline_block_comments(no_comment) == expected

        inline_comment: str = 'foo bar """mumble""" bas'
        assert remove_inline_block_comments(inline_comment) == expected

    def test_opens_block_comment(self) -> None:
        no_comment: str = "foo bar bas"
        char: Optional[str]
        line: str
        char, line = opens_block_comment(no_comment)
        assert not char
        assert line == no_comment

        no_comment = 'foo """bar bas'
        char, line = opens_block_comment(no_comment)
        expected = "foo"
        assert char
        assert line == expected

    def test_closes_block_comment(self) -> None:
        no_comment: str = "foo bar bas"
        char: Optional[str]
        line: str
        char, line = closes_block_comment(no_comment)
        assert not char
        assert line == no_comment

        no_comment = 'foo bar""" bas'
        char, line = closes_block_comment(no_comment)
        expected: str = "bas"
        assert char
        assert line == expected

    def test_iscompound(self) -> None:
        line: str = "x = 1; y = 2; z = 3"
        assert iscompound(line)

        line = "x = 1"
        assert not iscompound(line)

    def test_split_compound_commands(self) -> None:
        line: str = "x = 1; y = 2; z = 3"

        actual: list[str] = [trim_whitespace(x) for x in split_compound_commands(line)]
        expected: list[str] = ["x = 1", "y = 2", "z = 3"]

        assert actual == expected

    def test_opens_continuation(self) -> None:
        line: str = "math_result = 1 + 2 + 3 + 4"
        x: Optional[str]
        y: str
        x, y = opens_continuation(line)

        assert not x
        assert y == line

        line = "math_result = 1 + 2 + 3 + 4 + \\"
        x, y = opens_continuation(line)
        assert x and x == "\\"
        assert trim_whitespace(y) == "math_result = 1 + 2 + 3 + 4 +"

        line = 'list_fruits = ["Apple", "Banana",'
        x, y = opens_continuation(line)
        assert x and x == "["
        assert y == line

    def test_opens_block_comment2(self) -> None:
        line: str = '""" ... '
        x: Optional[str]
        y: str
        x, y = opens_block_comment(line)
        assert x and x == '"""'
        assert y == ""

    def test_has_continuation_char(self) -> None:
        line: str = "math_result = 1 + 2 + 3 + 4"
        x: Optional[str]
        y: str
        x, y = has_continuation_char(line)

        assert not x
        assert y == line

        line = "math_result = 1 + 2 + 3 + 4 + \\"

        """
        Full example:

        math_result = 1 + 2 + 3 + 4 + \
              5 + 6 + 7 + 8 + \
              9 + 10
        """

        x, y = has_continuation_char(line)
        assert x and x == "\\"
        assert trim_whitespace(y) == "math_result = 1 + 2 + 3 + 4 +"

    def test_has_open_pair(self) -> None:
        """
        Examples:

        message = ("Hello\n"
                  "Hi\n"
                  "Namaste")

        math_result = (1 + 2 + 3 + 4 +
                      5 + 6 + 7 + 8 +
                      9 + 10)

        prime_numbers_tuple = (2, 3, 5, 7,
                              11, 13, 17)

        list_fruits = ["Apple", "Banana",
                      "Orange", "Mango"]

        dict_countries = {"USA": "United States of America", "IN": "India",
                          "UK": "United Kingdom", "FR": "France"}

        """

        line: str = "foo bar bas"
        x: Optional[str]
        y: str
        x = has_open_pair(line)
        assert not x

        line = "foo (bar) bas"
        x = has_open_pair(line)
        assert not x

        line = 'message = ("Hello\n"'
        x = has_open_pair(line)
        assert x and x == "("

        line = 'message = (foo) ("Hello\n"'
        x = has_open_pair(line)
        assert x and x == "("

        line = "math_result = (1 + 2 + 3 + 4 +"
        x = has_open_pair(line)
        assert x and x == "("

        line = "prime_numbers_tuple = (2, 3, 5, 7,"
        x = has_open_pair(line)
        assert x and x == "("

        line = 'list_fruits = ["Apple", "Banana",'
        x = has_open_pair(line)
        assert x and x == "["

        line = 'dict_countries = {"USA": "United States of America", "IN": "India",'
        x = has_open_pair(line)
        assert x and x == "{"

    def test_closes_continuation(self) -> None:
        line: str = "foo bar bas"
        x: Optional[str]
        y: str
        x, y = closes_continuation(line, BACKSLASH)
        assert x == "\\"
        assert y == line

        line = '"Namaste")'
        x, y = closes_continuation(line)
        assert x and x == ")"
        assert y == line

        line = '"Orange", "Mango"]'
        x, y = closes_continuation(line)
        assert x and x == "]"
        assert y == line

        line = '"UK": "United Kingdom", "FR": "France"}'
        x, y = closes_continuation(line)
        assert x and x == "}"
        assert y == line

    def test_has_close_pair(self) -> None:
        line: str = "foo bar bas"
        x: Optional[str]
        y: str
        x = has_close_pair(line)
        assert not x

        line = "foo (bar) bas"
        x = has_close_pair(line)
        assert not x

        line = '"Namaste")'
        x = has_close_pair(line)
        assert x and x == ")"

        line = "9 + 10)"
        x = has_close_pair(line)
        assert x and x == ")"

        line = "11, 13, 17)"
        x = has_close_pair(line)
        assert x and x == ")"

        line = '"Orange", "Mango"]'
        x = has_close_pair(line)
        assert x and x == "]"

        line = '"UK": "United Kingdom", "FR": "France"}'
        x = has_close_pair(line)
        assert x and x == "}"

    def test_closes_block_comment2(self) -> None:
        line: str = '... """'
        x: Optional[str]
        y: str
        x, y = closes_block_comment(line)
        assert x and x == '"""'
        assert y == ""

    def test_continuations_match(self) -> None:
        assert continuations_match("\\", "\\")
        assert continuations_match("(", ")")
        assert continuations_match("[", "]")
        assert continuations_match("{", "}")
        assert not continuations_match("(", "]")

    def test_isblank(self) -> None:
        line: str = ""
        assert isblank(line)

        line = "foo"
        assert not isblank(line)

    def test_concatenate_string_literals(self) -> None:
        line: str = 'message = "Hello There.\nYou have come to the right place to learn Python Programming.\n" "Follow the tutorials to become expert in Python. " "Don\'t forget to share it with your friends too."'
        line = 'message = ("Hello\n" "Hi\n" "Namaste")'

        # TODO - Write some test cases for this!

        assert True

    def test_rewrite_pct(self) -> None:
        raw: str = "first(5%)"
        actual: str = rewrite_pct(raw)
        expected: str = "first(5, %)"
        assert actual == expected

        raw = "where(foo % bar)"
        actual = rewrite_pct(raw)
        expected = raw
        assert actual == expected


### END ###
