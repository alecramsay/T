#!/usr/bin/env python3
#
# USER-DEFINED FUNCTIONS
#

from math import erf, sqrt


# REDISTRICTING HELPERS


def composite(ag, gov, sen1, sen2, pres1, pres2):
    # NOTE - This could be fleshed out to handle missing elections.
    return ((ag + gov) / 2 + (sen1 + sen2) / 2 + (pres1 + pres2) / 2) / 3


def vote_share(d_votes, r_votes):
    two_party_votes = d_votes + r_votes
    return d_votes / two_party_votes


def est_seat_probability(vpi):
    return 0.5 * (1 + erf((vpi - 0.50) / (0.02 * sqrt(8))))
