#!/usr/bin/env python3
#
# TEST PROGRAM
#

from T.program import *


class TestNamespaces:
    def test_bind(self):
        # No arg passed from caller
        script_args = {}
        elections_args = {"elections": "data/rd/NC/2020_election_NC.csv"}
        default = elections_args["elections"]

        ns = Namespace(script_args)
        assert ns.bind("elections") is None

        ns = Namespace(script_args)
        assert ns.bind("elections", default) == "data/rd/NC/2020_election_NC.csv"

        # Arg passed from caller
        caller = "data/rd/AZ/2020_election_AZ.csv"
        script_args = {"elections": caller}
        elections_args = {"elections": "data/rd/NC/2020_election_NC.csv"}
        default = elections_args["elections"]

        ns = Namespace(script_args)
        assert ns.bind("elections") == caller

        ns = Namespace(script_args)
        assert ns.bind("elections", default) == caller


### END ###
