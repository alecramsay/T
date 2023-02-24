#!/usr/bin/env python3
#
# USER-DEFINED FUNCTIONS
#

from math import erf, sqrt
from typing import Any, Callable

# REDISTRICTING HELPERS


def composite(ag, gov, sen1, sen2, pres1, pres2) -> float:
    # NOTE - This could be fleshed out to handle missing elections.
    return ((ag + gov) / 2 + (sen1 + sen2) / 2 + (pres1 + pres2) / 2) / 3


# TODO - DELETE
# composite: Callable[..., Any] = (
#     lambda ag, gov, sen1, sen2, pres1, pres2: (
#         (ag + gov) / 2 + (sen1 + sen2) / 2 + (pres1 + pres2) / 2
#     )
#     / 3
# )


def vote_share(d_votes, r_votes) -> float:
    two_party_votes: int = d_votes + r_votes
    return d_votes / two_party_votes


def est_seat_probability(vpi) -> float:
    return 0.5 * (1 + erf((vpi - 0.50) / (0.02 * sqrt(8))))


### END ###
