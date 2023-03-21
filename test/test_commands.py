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


### END ###
