#!/usr/bin/env python3

"""
TEST LANG
"""

from T.lang import *


class TestLangHelpers:
    def test_iskeywordarg(self) -> None:
        assert iskeywordarg("a=b")
        assert not iskeywordarg("a=")
        assert not iskeywordarg("=b")
        assert not iskeywordarg("a")

    def test_extract_args(self) -> None:
        pass  # TODO

    # def test_parse_args(self) -> None:
    #     # Positional, no keywords
    #     command: str = "foo(bar, bas, bat)"
    #     tree = cst.parse_expression(command)

    #     positional, keywords = parse_args(tree.args)
    #     assert len(positional) == 3
    #     assert len(keywords) == 0

    #     # No positional, all keywords
    #     command = "foo(bar=bas, bat=mumble)"
    #     tree = cst.parse_expression(command)

    #     positional, keywords = parse_args(tree.args)
    #     assert len(positional) == 0
    #     assert len(keywords) == 2

    #     # No args
    #     command = "foo()"
    #     tree = cst.parse_expression(command)

    #     positional, keywords = parse_args(tree.args)
    #     assert len(positional) == 0
    #     assert len(keywords) == 0

    # def test_parse_statement(self):
    #     try:
    #         command = "= whatever"
    #         _, _, _ = parse_statement(command)
    #         assert False
    #     except:
    #         assert True

    #     try:
    #         command = "read(args.elections or '2020_election_NC.csv'"
    #         _, _, _ = parse_statement(command)
    #         assert False
    #     except:
    #         assert True

    #     try:
    #         command = "foo = bar == baz"
    #         _, _, _ = parse_statement(command)
    #         assert False
    #     except:
    #         assert True

    #     command = "read(args.elections or '2020_election_NC.csv')"
    #     left, right, iscall = parse_statement(command)
    #     actual = [left, right, iscall]
    #     expected = [["read"], ["args.elections", "or", "'2020_election_NC.csv'"], True]
    #     assert all([a == b for a, b in zip(actual, expected)])

    #     command = "D_pct = vote_share(sum_D_votes, sum_R_votes)"
    #     left, right, iscall = parse_statement(command)
    #     actual = [left, right, iscall]
    #     expected = [
    #         ["D_pct"],
    #         ["vote_share", "(", "sum_D_votes", ",", "sum_R_votes", ")"],
    #         False,
    #     ]
    #     assert all([a == b for a, b in zip(actual, expected)])

    #     command = "sort((args.sorton, DESC))"
    #     left, right, iscall = parse_statement(command)
    #     actual = [left, right, iscall]
    #     expected = [["sort"], ["(", "args.sorton", ",", "DESC", ")"], True]
    #     assert all([a == b for a, b in zip(actual, expected)])

    # def test_unwrap_args(self):
    #     subcommand = "args.foo"
    #     expected = ["args.foo"]
    #     tokens = tokenize(subcommand)
    #     actual = unwrap_args(tokens)
    #     assert all([a == b for a, b in zip(actual, expected)])

    #     subcommand = "args.foo or 'something'"
    #     expected = ["args.foo", "or", "'something'"]
    #     tokens = tokenize(subcommand)
    #     actual = unwrap_args(tokens)
    #     assert all([a == b for a, b in zip(actual, expected)])

    #     subcommand = "(args.foo)"
    #     expected = ["args.foo"]
    #     tokens = tokenize(subcommand)
    #     actual = unwrap_args(tokens)
    #     assert all([a == b for a, b in zip(actual, expected)])

    #     subcommand = "(args.foo or 'something')"
    #     expected = ["args.foo", "or", "'something'"]
    #     tokens = tokenize(subcommand)
    #     actual = unwrap_args(tokens)
    #     assert all([a == b for a, b in zip(actual, expected)])

    #     subcommand = "(foo + args.bar or 'something')"
    #     expected = ["(", "foo", "+", "args.bar", "or", "'something'", ")"]
    #     tokens = tokenize(subcommand)
    #     actual = unwrap_args(tokens)
    #     assert all([a == b for a, b in zip(actual, expected)])

    #     subcommand = "mumble * (foo + (args.bar or 'something') - blah)"
    #     expected = [
    #         "mumble",
    #         "*",
    #         "(",
    #         "foo",
    #         "+",
    #         "args.bar",
    #         "or",
    #         "'something'",
    #         "-",
    #         "blah",
    #         ")",
    #     ]

    #     tokens = tokenize(subcommand)
    #     actual = unwrap_args(tokens)
    #     assert all([a == b for a, b in zip(actual, expected)])

    # def test_bind_args(self):
    #     # No args in command fragment
    #     scriptargs = {"bar": "'2022_precinct_assignments_AZ.csv'", "bas": "mumble"}
    #     fragment = "'2020_precinct_assignments_NC.csv'"
    #     tokens = tokenize(fragment)
    #     actual = bind_args(tokens, Namespace(scriptargs))
    #     expected = fragment
    #     assert actual == expected

    #     # Args in the command fragment
    #     scriptargs = {"bar": "'2022_precinct_assignments_AZ.csv'", "bas": "mumble"}
    #     fragment = "args.bar or '2020_precinct_assignments_NC.csv', args.bas"
    #     tokens = tokenize(fragment)
    #     actual = bind_args(tokens, Namespace(scriptargs))
    #     expected = "'2022_precinct_assignments_AZ.csv',mumble"
    #     assert actual == expected

    #     # Arg in read
    #     scriptargs = {"census": "'2020_census_AZ.csv'"}
    #     fragment = "args.census or '2020_census_NC.csv'"
    #     tokens = tokenize(fragment)
    #     actual = bind_args(tokens, Namespace(scriptargs))
    #     expected = "'2020_census_AZ.csv'"
    #     assert actual == expected

    #     # Arg in filter
    #     scriptargs = {"county_fips": "'191'"}
    #     fragment = "county_fips == args.county_fips"
    #     tokens = tokenize(fragment)
    #     actual = bind_args(tokens, Namespace(scriptargs))
    #     expected = "county_fips=='191'"
    #     assert actual == expected

    #     # Arg in run
    #     scriptargs = {"census": "'2020_census_AZ.csv'"}
    #     fragment = "'census.t', census=args.census or '2020_census_NC.csv'"
    #     tokens = tokenize(fragment)
    #     actual = bind_args(tokens, Namespace(scriptargs))
    #     expected = "'census.t',census='2020_census_AZ.csv'"
    #     assert actual == expected

    #     # Arg in sort
    #     scriptargs = {"sorton": "Total"}
    #     fragment = "(args.sorton, DESC)"
    #     tokens = tokenize(fragment)
    #     actual = bind_args(tokens, Namespace(scriptargs))
    #     expected = "(Total,DESC)"
    #     assert actual == expected

    #     # Arg for verb
    #     scriptargs = {"verb": "foobar"}
    #     fragment = "args.verb"
    #     tokens = tokenize(fragment)
    #     actual = bind_args(tokens, Namespace(scriptargs))
    #     expected = "foobar"
    #     assert actual == expected

    #     # Arg on the right side of a derived column
    #     scriptargs = {"vap_total": "cvap_total"}
    #     fragment = "demo_pct = demo_total / args.vap_total"
    #     tokens = tokenize(fragment)
    #     actual = bind_args(tokens, Namespace(scriptargs))
    #     expected = "demo_pct=demo_total/cvap_total"
    #     assert actual == expected

    #     # Arg on the right side of a derived column - NOTE the trick here to replace *part* of a column name!
    #     scriptargs = {"demo": "Black"}
    #     fragment = "args.demo _pct = sum_ args.demo / sum_Total_VAP"
    #     tokens = tokenize(fragment)
    #     actual = bind_args(tokens, Namespace(scriptargs))
    #     expected = "Black_pct=sum_Black/sum_Total_VAP"
    #     assert actual == expected

    #     # Arg on the left side of a derived column (not that it's any different than the right side)
    #     scriptargs = {"new_col": "foo"}
    #     fragment = "args.new_col = existing * 0.8"
    #     tokens = tokenize(fragment)
    #     actual = bind_args(tokens, Namespace(scriptargs))
    #     expected = "foo=existing*0.8"
    #     assert actual == expected

    # def test_bind_command_args(self):
    #     # No args in the command
    #     scriptargs = {"bar": "'2022_precinct_assignments_AZ.csv'", "bas": "mumble"}
    #     command = "read('2020_precinct_assignments_NC.csv')"
    #     actual = bind_command_args(command, Namespace(scriptargs))
    #     expected = command
    #     assert actual == expected

    #     # Args in the command
    #     scriptargs = {"bar": "'2022_precinct_assignments_AZ.csv'", "bas": "mumble"}
    #     command = "read(args.bar or '2020_precinct_assignments_NC.csv', args.bas)"
    #     actual = bind_command_args(command, Namespace(scriptargs))
    #     expected = "read('2022_precinct_assignments_AZ.csv',mumble)"
    #     assert actual == expected

    #     # Arg in read
    #     scriptargs = {"census": "'2020_census_AZ.csv'"}
    #     command = "read(args.census or '2020_census_NC.csv')"
    #     actual = bind_command_args(command, Namespace(scriptargs))
    #     expected = "read('2020_census_AZ.csv')"
    #     assert actual == expected

    #     # Arg in filter
    #     scriptargs = {"county_fips": "'191'"}
    #     command = "select(county_fips == args.county_fips)"
    #     actual = bind_command_args(command, Namespace(scriptargs))
    #     expected = "select(county_fips=='191')"
    #     assert actual == expected

    #     # Arg in from (was run)
    #     scriptargs = {"census": "'2020_census_AZ.csv'"}
    #     command = "from('census.t', census=args.census or '2020_census_NC.csv')"
    #     actual = bind_command_args(command, Namespace(scriptargs))
    #     expected = "from('census.t',census='2020_census_AZ.csv')"
    #     assert actual == expected

    #     # Arg in sort
    #     scriptargs = {"sorton": "Total"}
    #     command = "sort((args.sorton, DESC))"
    #     actual = bind_command_args(command, Namespace(scriptargs))
    #     expected = "sort((Total,DESC))"
    #     assert actual == expected

    #     # Arg for verb
    #     scriptargs = {"verb": "foo"}
    #     command = "args.verb(bar)"
    #     actual = bind_command_args(command, Namespace(scriptargs))
    #     expected = "foo(bar)"
    #     assert actual == expected

    #     # Arg for verb wrapped in parens
    #     scriptargs = {"verb": "foo"}
    #     command = "(args.verb)(bar)"
    #     actual = bind_command_args(command, Namespace(scriptargs))
    #     expected = "foo(bar)"
    #     assert actual == expected

    #     # Arg on the right side of a derived column
    #     scriptargs = {"vap_total": "cvap_total"}
    #     command = "demo_pct = demo_total / args.vap_total"
    #     actual = bind_command_args(command, Namespace(scriptargs))
    #     expected = "demo_pct=demo_total/cvap_total"
    #     assert actual == expected

    #     # Arg on the right side of a derived column - NOTE the trick here to replace *part* of a column name!
    #     scriptargs = {"demo": "Black"}
    #     command = "args.demo _pct = sum_ args.demo / sum_Total_VAP"
    #     actual = bind_command_args(command, Namespace(scriptargs))
    #     expected = "Black_pct=sum_Black/sum_Total_VAP"
    #     assert actual == expected

    #     # Arg on the left side of a derived column (not that it's any different than the right side)
    #     scriptargs = {"new_col": "foo"}
    #     command = "args.new_col = existing * 0.8"
    #     actual = bind_command_args(command, Namespace(scriptargs))
    #     expected = "foo=existing*0.8"
    #     assert actual == expected

    #     # Arg *wrapped* on the lhs of a derived column (not that it's any different than the right side)
    #     scriptargs = {"new_col": "foo"}
    #     command = "(args.new_col) = existing * 0.8"
    #     actual = bind_command_args(command, Namespace(scriptargs))
    #     expected = "foo=existing*0.8"
    #     assert actual == expected

    # def test_extract_expr(self):
    #     command = "foo(bar > bas)"
    #     actual = extract_expr("test", command, "(", ")")
    #     expected = "bar > bas"

    #     assert actual == expected

    #     command = "foo(bar, bas + bat, int)"
    #     actual = extract_expr("test", command, ",", ",")
    #     expected = "bas + bat"

    #     assert actual == expected

    #     command = "foo(bar, (bas + bat))"
    #     actual = extract_expr("test", command, ",", ")")
    #     expected = "(bas + bat)"

    #     assert actual == expected

    #     command = "foo bar, bas + bat, int)"
    #     try:
    #         actual = extract_expr("test", command, "(", ",")
    #         assert False
    #     except:
    #         assert True

    # def test_extract_col_refs(self):
    #     verb = "test"

    #     # Valid identifiers
    #     command = "foo(bar, bas, bat)"
    #     tree = cst.parse_expression(command)
    #     nargs = len(tree.args)

    #     actual = extract_col_refs(verb, nargs, tree)
    #     expected = ["bar", "bas", "bat"]

    #     assert actual == expected

    #     # No args
    #     command = "foo()"
    #     tree = cst.parse_expression(command)
    #     nargs = len(tree.args)
    #     try:
    #         actual = extract_col_refs(verb, nargs, tree)
    #         assert False
    #     except:
    #         assert True

    #     # Illegal identifiers
    #     command = "foo(bar, 3, bat)"
    #     tree = cst.parse_expression(command)
    #     nargs = len(tree.args)
    #     try:
    #         actual = extract_col_refs(verb, nargs, tree)
    #         assert False
    #     except:
    #         assert True

    # def test_extract_col_specs(self):
    #     verb = "test"

    #     # Valid column specs
    #     command = "foo((bar, bas), (bat, mumble))"
    #     tree = cst.parse_expression(command)
    #     nargs = len(tree.args)

    #     actual = extract_col_specs(verb, nargs, tree)
    #     expected = [("bar", "bas"), ("bat", "mumble")]

    #     assert actual == expected

    #     # Invalid column specs
    #     command = "foo((bar, 1), (bat, 2))"
    #     tree = cst.parse_expression(command)
    #     nargs = len(tree.args)

    #     try:
    #         extract_col_specs(verb, nargs, tree)
    #         assert False
    #     except:
    #         assert True

    #     # Column names, not column specs
    #     command = "foo(bar, bas, bat)"
    #     tree = cst.parse_expression(command)
    #     nargs = len(tree.args)

    #     try:
    #         extract_col_specs(verb, nargs, tree)
    #         assert False
    #     except:
    #         assert True

    #     # No args
    #     command = "foo()"
    #     try:
    #         tree = cst.parse_expression(command)
    #         nargs = len(tree.args)

    #         extract_col_specs(verb, nargs, tree)
    #         assert False
    #     except:
    #         assert True

    # def test_extract_n_and_pct(self):
    #     verb = "test"

    #     # An integer
    #     command = "foo(5)"
    #     tree = cst.parse_expression(command)
    #     nargs = len(tree.args)
    #     n, pct = extract_n_and_pct(verb, nargs, tree)
    #     assert n == 5 and pct is None

    #     # An integer
    #     command = "foo(5, '*')"
    #     tree = cst.parse_expression(command)
    #     nargs = len(tree.args)
    #     n, pct = extract_n_and_pct(verb, nargs, tree)
    #     assert n == 5 and pct

    #     # No args
    #     command = "foo()"
    #     tree = cst.parse_expression(command)
    #     nargs = len(tree.args)
    #     try:
    #         extract_n_and_pct(verb, nargs, tree)
    #         assert False
    #     except:
    #         assert True

    #     # Not an integer
    #     command = "foo(bar)"
    #     tree = cst.parse_expression(command)
    #     nargs = len(tree.args)
    #     try:
    #         extract_n_and_pct(verb, nargs, tree)
    #         assert False
    #     except:
    #         assert True

    # def test_extract_n(self):
    #     verb = "test"

    #     # An integer
    #     command = "foo(5)"
    #     tree = cst.parse_expression(command)
    #     nargs = len(tree.args)
    #     actual = extract_n(verb, nargs, tree)
    #     expected = 5

    #     assert actual == expected

    #     # Something else
    #     command = "foo(bar)"
    #     tree = cst.parse_expression(command)
    #     nargs = len(tree.args)
    #     try:
    #         extract_n(verb, nargs, tree)
    #         assert False
    #     except:
    #         assert True

    # def test_could_be_filename(self):
    #     # Valid
    #     command = "foo('bar')"
    #     tree = cst.parse_expression(command)
    #     try:
    #         could_be_filename(tree.args[0])
    #         assert True
    #     except:
    #         assert False

    #     # Not valid
    #     command = "foo('5')"
    #     tree = cst.parse_expression(command)
    #     try:
    #         could_be_filename(tree.args[0])
    #         assert False
    #     except:
    #         assert True

    # def test_extract_sort_args(self):
    #     # Just a column name
    #     command = "foo(bar)"
    #     tree = cst.parse_expression(command)

    #     actual = extract_sort_args(tree)
    #     expected = "bar"
    #     assert actual == expected

    #     # A column name & sort order
    #     command = "foo((bar, DESC))"
    #     tree = cst.parse_expression(command)

    #     actual = extract_sort_args(tree)
    #     expected = ("bar", "DESC")
    #     assert actual == expected

    #     # Something else
    #     command = "foo(bar, bas)"
    #     tree = cst.parse_expression(command)

    #     try:
    #         actual = extract_sort_args(tree)
    #         assert False
    #     except:
    #         assert True

    # def test_are_valid_keywords(self):
    #     """
    #     d = {"by": "foo", "only": "bar", "mumble": "bat"}
    #     d = {"by": "foo", "only": "bar"}
    #     d = {"by": "foo"}
    #     d = {}
    #     """

    #     # Valid
    #     valid = {"by", "only"}
    #     d = {"by": "foo", "only": "bar"}
    #     try:
    #         are_valid_keywords(valid, d)
    #         assert True
    #     except:
    #         assert False

    #     # None
    #     valid = {"by", "only"}
    #     d = {}
    #     try:
    #         are_valid_keywords(valid, d)
    #         assert True
    #     except:
    #         assert False

    #     # Not valid
    #     valid = {"by", "only"}
    #     d = {"by": "foo", "only": "bar", "mumble": "bat"}
    #     try:
    #         are_valid_keywords(valid, d)
    #         assert False
    #     except:
    #         assert True

    # def test_is_valid_name(self):
    #     verb = "test"

    #     # Valid name
    #     command = "foo(bar)"
    #     tree = cst.parse_expression(command)

    #     try:
    #         is_valid_name(verb, tree.args[0], 1)
    #         assert True
    #     except:
    #         assert False

    #     # Illegal name
    #     command = "foo(3)"
    #     tree = cst.parse_expression(command)

    #     try:
    #         is_valid_name(verb, tree.args[0], 1)
    #         assert False
    #     except:
    #         assert True


### END ###
