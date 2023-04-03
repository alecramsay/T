# from

Read a table from a CSV file or read a T script and execute it.
Push the resulting table onto the stack.

## Examples

Read a table from a CSV file:

`>>> from(2020_census_NC.csv)`

Execute a T script with arguments:

`>>> from(precincts.t, paf=2020_precinct_assignments_NC.csv, census=2020_census_NC.csv, elections=2020_election_NC.csv)`

## TODO

These arguments are surfaced yet:

```
delimiter: str = "comma",
header: bool = True,
```

```
StandardDelimiters: dict[str, str] = {
    "tab": "\t",
    "semicolon": ";",
    "comma": ",",
    "space": " ",
    "pipe": "|",
    # user-defined
}
```