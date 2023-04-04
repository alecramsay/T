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

- Load a CSV file of census data with 2666 rows with 57 columns,
- Keep only the geoid and total population columns,
- Renames the total population to something shorter,
- Sorts the rows by total population in descending order, and
- Creates a new table with the first 10 rows.

## Contents

[Installation and usage](https://github.com/alecramsay/T/README.md)

The [model](model.md)

The [commands](commands.md)

[Aggregate functions](aggregates.md)

[User-defined functions](udf.md)

