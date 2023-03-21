#!/usr/bin/env python3

"""
TEST COMMANDS
"""

from T.commands import *


class TestCommands:
    def test_unwrap_args(self):
        subcommand = "args.foo"
        expected = ["args.foo"]
        tokens = tokenize(subcommand)
        actual = unwrap_args(tokens)
        assert all([a == b for a, b in zip(actual, expected)])

        subcommand = "args.foo or 'something'"
        expected = ["args.foo", "or", "'something'"]
        tokens = tokenize(subcommand)
        actual = unwrap_args(tokens)
        assert all([a == b for a, b in zip(actual, expected)])

        subcommand = "(args.foo)"
        expected = ["args.foo"]
        tokens = tokenize(subcommand)
        actual = unwrap_args(tokens)
        assert all([a == b for a, b in zip(actual, expected)])

        subcommand = "(args.foo or 'something')"
        expected = ["args.foo", "or", "'something'"]
        tokens = tokenize(subcommand)
        actual = unwrap_args(tokens)
        assert all([a == b for a, b in zip(actual, expected)])

        subcommand = "(foo + args.bar or 'something')"
        expected = ["(", "foo", "+", "args.bar", "or", "'something'", ")"]
        tokens = tokenize(subcommand)
        actual = unwrap_args(tokens)
        assert all([a == b for a, b in zip(actual, expected)])

        subcommand = "mumble * (foo + (args.bar or 'something') - blah)"
        expected = [
            "mumble",
            "*",
            "(",
            "foo",
            "+",
            "args.bar",
            "or",
            "'something'",
            "-",
            "blah",
            ")",
        ]

        tokens = tokenize(subcommand)
        actual = unwrap_args(tokens)
        assert all([a == b for a, b in zip(actual, expected)])

    def test_bind_args(self):
        # No args in command fragment
        scriptargs = {"bar": "'2022_precinct_assignments_AZ.csv'", "bas": "mumble"}
        fragment = "'2020_precinct_assignments_NC.csv'"
        tokens = tokenize(fragment)
        actual = bind_args(tokens, Namespace(scriptargs))
        expected = fragment
        assert actual == expected

        # Args in the command fragment
        scriptargs = {"bar": "'2022_precinct_assignments_AZ.csv'", "bas": "mumble"}
        fragment = "args.bar or '2020_precinct_assignments_NC.csv', args.bas"
        tokens = tokenize(fragment)
        actual = bind_args(tokens, Namespace(scriptargs))
        expected = "'2022_precinct_assignments_AZ.csv',mumble"
        assert actual == expected

        # Arg in read
        scriptargs = {"census": "'2020_census_AZ.csv'"}
        fragment = "args.census or '2020_census_NC.csv'"
        tokens = tokenize(fragment)
        actual = bind_args(tokens, Namespace(scriptargs))
        expected = "'2020_census_AZ.csv'"
        assert actual == expected

        # Arg in filter
        scriptargs = {"county_fips": "'191'"}
        fragment = "county_fips == args.county_fips"
        tokens = tokenize(fragment)
        actual = bind_args(tokens, Namespace(scriptargs))
        expected = "county_fips=='191'"
        assert actual == expected

        # Arg in run
        scriptargs = {"census": "'2020_census_AZ.csv'"}
        fragment = "'census.t', census=args.census or '2020_census_NC.csv'"
        tokens = tokenize(fragment)
        actual = bind_args(tokens, Namespace(scriptargs))
        expected = "'census.t',census='2020_census_AZ.csv'"
        assert actual == expected

        # Arg in sort
        scriptargs = {"sorton": "Total"}
        fragment = "(args.sorton, DESC)"
        tokens = tokenize(fragment)
        actual = bind_args(tokens, Namespace(scriptargs))
        expected = "(Total,DESC)"
        assert actual == expected

        # Arg for verb
        scriptargs = {"verb": "foobar"}
        fragment = "args.verb"
        tokens = tokenize(fragment)
        actual = bind_args(tokens, Namespace(scriptargs))
        expected = "foobar"
        assert actual == expected

        # Arg on the right side of a derived column
        scriptargs = {"vap_total": "cvap_total"}
        fragment = "demo_pct = demo_total / args.vap_total"
        tokens = tokenize(fragment)
        actual = bind_args(tokens, Namespace(scriptargs))
        expected = "demo_pct=demo_total/cvap_total"
        assert actual == expected

        # Arg on the right side of a derived column - NOTE the trick here to replace *part* of a column name!
        scriptargs = {"demo": "Black"}
        fragment = "args.demo _pct = sum_ args.demo / sum_Total_VAP"
        tokens = tokenize(fragment)
        actual = bind_args(tokens, Namespace(scriptargs))
        expected = "Black_pct=sum_Black/sum_Total_VAP"
        assert actual == expected

        # Arg on the left side of a derived column (not that it's any different than the right side)
        scriptargs = {"new_col": "foo"}
        fragment = "args.new_col = existing * 0.8"
        tokens = tokenize(fragment)
        actual = bind_args(tokens, Namespace(scriptargs))
        expected = "foo=existing*0.8"
        assert actual == expected

    def test_bind_command_args(self):
        # No args in the command
        scriptargs = {"bar": "'2022_precinct_assignments_AZ.csv'", "bas": "mumble"}
        command = "read('2020_precinct_assignments_NC.csv')"
        cmd: Command = Command(command, Namespace(scriptargs))
        actual = cmd.bind()
        expected = command
        assert actual == expected

        # Args in the command
        scriptargs = {"bar": "'2022_precinct_assignments_AZ.csv'", "bas": "mumble"}
        command = "read(args.bar or '2020_precinct_assignments_NC.csv', args.bas)"
        cmd: Command = Command(command, Namespace(scriptargs))
        actual = cmd.bind()
        expected = "read('2022_precinct_assignments_AZ.csv',mumble)"
        assert actual == expected

        # # Arg in read
        # scriptargs = {"census": "'2020_census_AZ.csv'"}
        # command = "read(args.census or '2020_census_NC.csv')"
        # actual = bind_command_args(command, Namespace(scriptargs))
        # expected = "read('2020_census_AZ.csv')"
        # assert actual == expected

        # # Arg in filter
        # scriptargs = {"county_fips": "'191'"}
        # command = "select(county_fips == args.county_fips)"
        # actual = bind_command_args(command, Namespace(scriptargs))
        # expected = "select(county_fips=='191')"
        # assert actual == expected

        # # Arg in from (was run)
        # scriptargs = {"census": "'2020_census_AZ.csv'"}
        # command = "from('census.t', census=args.census or '2020_census_NC.csv')"
        # actual = bind_command_args(command, Namespace(scriptargs))
        # expected = "from('census.t',census='2020_census_AZ.csv')"
        # assert actual == expected

        # # Arg in sort
        # scriptargs = {"sorton": "Total"}
        # command = "sort((args.sorton, DESC))"
        # actual = bind_command_args(command, Namespace(scriptargs))
        # expected = "sort((Total,DESC))"
        # assert actual == expected

        # # Arg for verb
        # scriptargs = {"verb": "foo"}
        # command = "args.verb(bar)"
        # actual = bind_command_args(command, Namespace(scriptargs))
        # expected = "foo(bar)"
        # assert actual == expected

        # # Arg for verb wrapped in parens
        # scriptargs = {"verb": "foo"}
        # command = "(args.verb)(bar)"
        # actual = bind_command_args(command, Namespace(scriptargs))
        # expected = "foo(bar)"
        # assert actual == expected

        # # Arg on the right side of a derived column
        # scriptargs = {"vap_total": "cvap_total"}
        # command = "demo_pct = demo_total / args.vap_total"
        # actual = bind_command_args(command, Namespace(scriptargs))
        # expected = "demo_pct=demo_total/cvap_total"
        # assert actual == expected

        # # Arg on the right side of a derived column - NOTE the trick here to replace *part* of a column name!
        # scriptargs = {"demo": "Black"}
        # command = "args.demo _pct = sum_ args.demo / sum_Total_VAP"
        # actual = bind_command_args(command, Namespace(scriptargs))
        # expected = "Black_pct=sum_Black/sum_Total_VAP"
        # assert actual == expected

        # # Arg on the left side of a derived column (not that it's any different than the right side)
        # scriptargs = {"new_col": "foo"}
        # command = "args.new_col = existing * 0.8"
        # actual = bind_command_args(command, Namespace(scriptargs))
        # expected = "foo=existing*0.8"
        # assert actual == expected

        # # Arg *wrapped* on the lhs of a derived column (not that it's any different than the right side)
        # scriptargs = {"new_col": "foo"}
        # command = "(args.new_col) = existing * 0.8"
        # actual = bind_command_args(command, Namespace(scriptargs))
        # expected = "foo=existing*0.8"
        # assert actual == expected


### END ###
