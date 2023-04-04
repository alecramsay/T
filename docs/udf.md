# User-Defined Functions

When you start the T language processor, you can specify the path to a file containing user-defined functions. 
See the `--user` parameter described in the [README](https://github.com/alecramsay/T) in the GitHub repository.
The functions in that file will be available to T commands.
The arguments to the functions are columns in the table on the top of the stack.
These functions are dynamically re-written so the *values* of the columns are passed to the function at runtime.

For example, these are the redistricting-related functions that I've defined in mine:

```python
from math import erf, sqrt
from typing import Any, Callable

def composite(ag, gov, sen1, sen2, pres1, pres2) -> float:
    return ((ag + gov) / 2 + (sen1 + sen2) / 2 + (pres1 + pres2) / 2) / 3


def vote_share(d_votes, r_votes) -> float:
    two_party_votes: int = d_votes + r_votes
    return d_votes / two_party_votes


def est_seat_probability(vpi) -> float:
    return 0.5 * (1 + erf((vpi - 0.50) / (0.02 * sqrt(8))))
```

This lets me [derive](commands/derive.md) a new column like this:

`>>> derive(D_pct, vote_share(D_2020_pres, R_2020_pres)`