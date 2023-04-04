T delivers tables as a computing model.
The purpose is to make it easier to work with CSV data.

## Overview

For example, these T commands: 

```
from(2020_census_NC.csv)
keep(GEOID20, Tot_2020_tot)
rename((Tot_2020_tot, Total))
sort((Total, DESC))
first(10)
```

- Load a CSV file of census data with lots of rows (2,666) and columns (57),
- Keep only the geoid and total population columns,
- Renames the total population to something shorter,
- Sorts the rows by total population in descending order, and
- Creates a new table with the first 10 rows.

## Contents

The following document how T works:

- The [README](https://github.com/alecramsay/T) in GitHub explains how to set up & configure T.
- [Model](model.md) sketches the essential computing model.
- [Commands](commands.md) documents each of the over two dozen commands.
- [User-defined functions](udf.md) describes how to use custom Python functions that you've written.
