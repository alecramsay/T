# Commands

T functions fall into several categories:

- I/O functions:
    - [from](functions/from.md) -- Read a table from a CSV file or read a T script execute it.
    - [write](functions/write.md) -- Write a table to a CSV or JSON file.
- Column functions:
    - [keep](functions/keep.md) -- Keep the specified columns; drop the rest.
    - [drop](functions/drop.md) -- Drop the specified columns; keep the rest.
    - [rename](functions/rename.md) -- Rename the specified columns.
    - [alias](functions/alias.md) -- Alias the specified columns.
    - [derive](functions/derive.md) -- Derive a new column from existing columns.
    - [cast](functions/cast.md) -- Cast the specified columns to a new data type.
- Row functions:
    - [select](functions/select.md) -- Select rows that match the specified criteria.
    - [first](functions/first.md) -- Select the first N or N% rows.
    - [last](functions/last.md) -- Select the last N or N% rows.
    - [sample](functions/sample.md) -- Select a random sample of N or N% rows.
- Table functions:
    - [sort](functions/sort.md) -- Sort the table by the specified columns.
    - [groupby](functions/groupby.md) -- Group (or pivot) the table by the specified columns.
    - [join](functions/join.md) -- Join two tables.
    - [union](functions/union.md) -- Union two tables.
    - [duplicate](functions/duplicate.md) -- Duplicate a table.
- Informational functions -- These functions don't modify the stack:
    - [show](functions/show.md) -- Show the first N rows of a table.
    - [inspect](functions/inspect.md) -- Show descriptive statistics for a table.
    - [history](functions/history.md) -- Show the function (command) history.
- Stack functions:
    - [clear](functions/clear.md) -- Clear the stack.
    - [pop](functions/pop.md)
    - [swap](functions/swap.md)
    - [reverse](functions/reverse.md)
    - [rotate](functions/rotate.md)

Notes:

- Upper & lower case
- Whitespace
