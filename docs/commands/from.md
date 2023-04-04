# from

Read a table from a CSV file or read a T script and execute it.
Push the resulting table onto the stack.

## Syntax

`from(filepath)`

Parameters:

- **filepath**: str -- path to the CSV file to read or T script to execute (no quotes).

## Examples

Read a table from a CSV file:

`>>> from(2020_census_NC.csv)`

Execute a T script with arguments:

`>>> from(precincts.t, paf=2020_precinct_assignments_NC.csv, census=2020_census_NC.csv, elections=2020_election_NC.csv)`

## TODO

- Surface 'delimiter' and 'header' keyword arguments.