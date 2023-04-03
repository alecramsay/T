# write

Write the table on the top of the stack to a CSV or JSON file.

## Syntax

`write(filepath, *, format=CSV)`

Parameters:

- filepath: str -- path to the file to write to (no quotes)
- format: {CSV, JSON} (no quotes), default is CSV

## Examples

Write a table to a CSV file:

`>>> write(2020_census_NC.csv)`

Write a table to a JSON file:

`write(2020_census_NC.json, format=JSON)`