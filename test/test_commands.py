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

        subcommand = "args.foo or something"
        expected = ["args.foo", "or", "something"]
        tokens = tokenize(subcommand)
        actual = unwrap_args(tokens)
        assert all([a == b for a, b in zip(actual, expected)])

        subcommand = "(args.foo)"
        expected = ["args.foo"]
        tokens = tokenize(subcommand)
        actual = unwrap_args(tokens)
        assert all([a == b for a, b in zip(actual, expected)])

        subcommand = "(args.foo or something)"
        expected = ["args.foo", "or", "something"]
        tokens = tokenize(subcommand)
        actual = unwrap_args(tokens)
        assert all([a == b for a, b in zip(actual, expected)])

        subcommand = "(foo + args.bar or something)"
        expected = ["(", "foo", "+", "args.bar", "or", "something", ")"]
        tokens = tokenize(subcommand)
        actual = unwrap_args(tokens)
        assert all([a == b for a, b in zip(actual, expected)])

        subcommand = "mumble * (foo + (args.bar or something) - blah)"
        expected = [
            "mumble",
            "*",
            "(",
            "foo",
            "+",
            "args.bar",
            "or",
            "something",
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
        fragment = "args.bar or 2020_precinct_assignments_NC.csv', args.bas"
        tokens = tokenize(fragment)
        actual = bind_args(tokens, Namespace(scriptargs))
        expected = "'2022_precinct_assignments_AZ.csv',mumble"
        assert actual == expected

        # Arg in read
        scriptargs = {"census": "'2020_census_AZ.csv'"}
        fragment = "args.census or 2020_census_NC.csv'"
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
        fragment = "'census.t', census=args.census or 2020_census_NC.csv'"
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
        scriptargs = {"bar": "2022_precinct_assignments_AZ.csv", "bas": "mumble"}
        command = "read(2020_precinct_assignments_NC.csv)"
        cmd: Command = Command(command, Namespace(scriptargs))
        actual = cmd.bind()
        expected = command
        assert actual == expected

        # Args in the command
        scriptargs = {"bar": "'2022_precinct_assignments_AZ.csv'", "bas": "mumble"}
        command = "read(args.bar or 2020_precinct_assignments_NC.csv', args.bas)"
        cmd: Command = Command(command, Namespace(scriptargs))
        actual = cmd.bind()
        expected = "read('2022_precinct_assignments_AZ.csv',mumble)"
        assert actual == expected

        # Arg in read
        scriptargs = {"census": "2020_census_AZ.csv"}
        command = "read(args.census or 2020_census_NC.csv)"
        cmd: Command = Command(command, Namespace(scriptargs))
        actual = cmd.bind()
        expected = "read(2020_census_AZ.csv)"
        assert actual == expected

        # Arg in filter
        scriptargs = {"county_fips": "'191'"}
        command = "select(county_fips == args.county_fips)"
        cmd: Command = Command(command, Namespace(scriptargs))
        actual = cmd.bind()
        expected = "select(county_fips=='191')"
        assert actual == expected

        # Arg in from (was run)
        scriptargs = {"census": "2020_census_AZ.csv"}
        command = "from(census.t, census=args.census or 2020_census_NC.csv)"
        cmd: Command = Command(command, Namespace(scriptargs))
        actual = cmd.bind()
        expected = "from(census.t,census=2020_census_AZ.csv)"
        assert actual == expected

        # Arg in sort
        scriptargs = {"sorton": "Total"}
        command = "sort((args.sorton, DESC))"
        cmd: Command = Command(command, Namespace(scriptargs))
        actual = cmd.bind()
        expected = "sort((Total,DESC))"
        assert actual == expected

        # NOTE - These tests would be binding the *verb* as an arg
        # Arg for verb
        # scriptargs = {"verb": "foo"}
        # command = "args.verb(bar)"
        # cmd: Command = Command(command, Namespace(scriptargs))
        # actual = cmd.bind()
        # expected = "foo(bar)"
        # assert actual == expected

        # Arg for verb wrapped in parens
        # scriptargs = {"verb": "foo"}
        # command = "(args.verb)(bar)"
        # cmd: Command = Command(command, Namespace(scriptargs))
        # actual = cmd.bind()
        # expected = "foo(bar)"
        # assert actual == expected

        # NOTE - These are the legacy derived column syntax
        # Arg on the right side of a derived column
        # scriptargs = {"vap_total": "cvap_total"}
        # command = "demo_pct = demo_total / args.vap_total"
        # cmd: Command = Command(command, Namespace(scriptargs))
        # actual = cmd.bind()
        # expected = "demo_pct=demo_total/cvap_total"
        # assert actual == expected

        # Arg on the right side of a derived column - NOTE the trick here to replace *part* of a column name!
        # scriptargs = {"demo": "Black"}
        # command = "args.demo _pct = sum_ args.demo / sum_Total_VAP"
        # cmd: Command = Command(command, Namespace(scriptargs))
        # actual = cmd.bind()
        # expected = "Black_pct=sum_Black/sum_Total_VAP"
        # assert actual == expected

        # Arg on the left side of a derived column (not that it's any different than the right side)
        # scriptargs = {"new_col": "foo"}
        # command = "args.new_col = existing * 0.8"
        # cmd: Command = Command(command, Namespace(scriptargs))
        # actual = cmd.bind()
        # expected = "foo=existing*0.8"
        # assert actual == expected

        # Arg *wrapped* on the lhs of a derived column (not that it's any different than the right side)
        # scriptargs = {"new_col": "foo"}
        # command = "(args.new_col) = existing * 0.8"
        # cmd: Command = Command(command, Namespace(scriptargs))
        # actual = cmd.bind()
        # expected = "foo=existing*0.8"
        # assert actual == expected

    def test_isidentifier(self):
        name: str

        # Valid name
        name = "bar"
        assert isidentifier(name)

        # Illegal names
        name = "3"
        assert not isidentifier(name)

        name = "1bar"
        assert not isidentifier(name)

    def test_isidpair(self) -> None:
        args = ["(a, b)", "c, d", "(a b, c)"]
        expected = [True, False, False]

        for i, arg in enumerate(args):
            assert isidpair(arg) == expected[i]

    def test_issortarg(self) -> None:
        # Just a column name
        arg = "bar"
        actual = issortarg(arg)
        expected = True
        assert actual == expected

        # A column name & sort order
        arg = "(bar, DESC)"
        actual = issortarg(arg)
        expected = True
        assert actual == expected

        # Bad
        arg = "(bar, foo)"
        actual = issortarg(arg)
        expected = True
        assert actual != expected

        # Bad
        arg = "bar, bas"
        actual = issortarg(arg)
        expected = True
        assert actual != expected

    def test_isint(self) -> None:
        assert isint("1")
        assert isint("5")
        assert not isint("0")
        assert not isint("-1")
        assert not isint("5%")

    def test_isintorpct(self) -> None:
        assert ispct("%")
        assert not ispct("5")
        assert not ispct("@")

    def test_validate_name(self):
        arg: str
        command: str
        verb: str = "test"

        # Valid name
        arg = "bar"

        try:
            validate_name(verb, arg, 1)
            assert True
        except:
            assert False

        # Illegal name
        arg = "3"

        try:
            validate_name(verb, arg, 1)
            assert False
        except:
            assert True

    def test_parse_command(self) -> None:
        commands: list[str] = [
            "sort((args.sorton, DESC))",
            "from_(args.census or 2020_census_NC.csv)",
            "from_(precincts.t, paf=2020_precinct_assignments_NC.csv, census=2020_census_NC.csv, elections=2020_election_NC.csv)",
            "foo(bar, bas, bat)",
            "foo(bar=bas, bat=mumble)",
            "foo()",
            "keep(GEOID20, Tot_2020_tot, Tot_2020_vap)",
            "rename((Tot_2020_tot, Total), (Tot_2020_vap, Total_VAP))",
            "alias((GEOID20, GEOID), (Tot_2020_tot, Total))",
            "derive(D_pct, vote_share(sum_D_votes, sum_R_votes))",
            "select(county_fips == '191')",
            "first(10%)",
            "join()",
            "groupby(by=District)",
            "sort(District)",
            "union()",
            "show(5)",
            "inspect()",
            "write()",
        ]

        expected: list[tuple[str, list[str]]] = [
            ("sort", ["(Total,DESC)"]),
            ("from_", ["2020_census_NC.csv"]),
            (
                "from_",
                [
                    "precincts.t",
                    "paf=2020_precinct_assignments_NC.csv",
                    "census=2020_census_NC.csv",
                    "elections=2020_election_NC.csv",
                ],
            ),
            ("foo", ["bar", "bas", "bat"]),
            ("foo", ["bar=bas", "bat=mumble"]),
            ("foo", []),
            ("keep", ["GEOID20", "Tot_2020_tot", "Tot_2020_vap"]),
            ("rename", ["(Tot_2020_tot,Total)", "(Tot_2020_vap,Total_VAP)"]),
            ("alias", ["(GEOID20,GEOID)", "(Tot_2020_tot,Total)"]),
            ("derive", ["D_pct", "vote_share(sum_D_votes,sum_R_votes)"]),
            ("select", ["county_fips=='191'"]),
            ("first", ["10%"]),
            ("join", []),
            ("groupby", ["by=District"]),
            ("sort", ["District"]),
            ("union", []),
            ("show", ["5"]),
            ("inspect", []),
            ("write", []),
        ]

        for i, command in enumerate(commands):
            try:
                verb: str
                args: list[str]
                scriptargs: dict[str, str] = {
                    "sorton": "Total"
                }  # Only applies to the sort example
                cmd: Command = Command(command, Namespace(scriptargs))
                cmd.bind()
                cmd.parse()
                # print(f"verb: {cmd.verb}, args: {' | '.join(cmd.args)}")

                verb: str = cmd.verb
                args: list[str] = cmd.args

                assert verb == expected[i][0] and args == expected[i][1]

            except:
                assert False
                # print(f"Invalid command: {command}")

    def test_iskeywordarg(self) -> None:
        assert not iskeywordarg("foo")
        assert iskeywordarg("foo=bar")
        assert not iskeywordarg("=bar")
        assert not iskeywordarg("bar=")

    def test_parse_classify_args(self) -> None:
        commands: list[str] = [
            "foo(bar, bas, bat)",
            "foo(bar=bas, bat=mumble)",
            "foo(bar, bat=mumble)",
            "foo()",
        ]

        expected: list[tuple[int, int]] = [
            (3, 0),
            (0, 2),
            (1, 1),
            (0, 0),
        ]

        for i, command in enumerate(commands):
            try:
                verb: str
                args: list[str]
                scriptargs: dict[str, str] = dict()
                cmd: Command = Command(command, Namespace(scriptargs))
                cmd.bind()
                cmd.parse()

                assert cmd.n_pos == expected[i][0] and cmd.n_kw == expected[i][1]

            except:
                assert False

        # Misordered args

        try:
            command: str = "foo(bar=mumble, bas)"
            scriptargs: dict[str, str] = dict()
            cmd: Command = Command(command, Namespace(scriptargs))
            cmd.bind()
            cmd.parse()
            assert False
        except:
            assert True

    def test_validate_filename(self):
        # Valid
        arg = "test/files/exists.csv"
        try:
            validate_filename(arg)
            assert True
        except:
            assert False

        # Not valid
        arg = "test/files/does_not_exist.csv"
        try:
            validate_filename(arg)
            assert False
        except:
            assert True

    def test_could_be_filename(self) -> None:
        args: list[str] = [
            "precincts.t",
            "2020_census_NC.csv",
            "foo/bar.csv",
            "foo/",
            "foo//bar",
        ]
        expected: list[bool] = [True, True, True, False, False]

        for i, arg in enumerate(args):
            try:
                could_be_filename(arg)
                assert expected[i] == True
            except:
                assert expected[i] == False


### END ###
