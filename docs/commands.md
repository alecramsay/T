# Commands

T commands are like functions: they have a name, they take arguments in parentheses, and they work on the tables on the stack.
Command names ("verbs") can be in upper or lower case.
Whitespace is ignored.

Commands fall into several categories:

- I/O commands:
    - [from](commands/from.md) -- Read a table from a CSV file or read a T script execute it.
    - [write](commands/write.md) -- Write a table to a CSV or JSON file.
- Column commands:
    - [keep](commands/keep.md) -- Keep the specified columns; drop the rest.
    - [drop](commands/drop.md) -- Drop the specified columns; keep the rest.
    - [rename](commands/rename.md) -- Rename the specified columns.
    - [alias](commands/alias.md) -- Alias the specified columns.
    - [derive](commands/derive.md) -- Derive a new column from existing columns.
    - [cast](commands/cast.md) -- Cast the specified columns to a new data type.
- Row commands:
    - [select](commands/select.md) -- Select rows that match the specified criteria.
    - [first](commands/first.md) -- Select the first N (or N%) rows.
    - [last](commands/last.md) -- Select the last N (or N%) rows.
    - [sample](commands/sample.md) -- Select a random sample of N or N% rows.
- Table commands:
    - [sort](commands/sort.md) -- Sort the table by the specified columns.
    - [groupby](commands/groupby.md) -- Group (or pivot) the table by the specified columns.
    - [join](commands/join.md) -- Join two tables.
    - [union](commands/union.md) -- Union two tables.
    - [duplicate](commands/duplicate.md) -- Duplicate a table.
- Stack commands:
    - [clear](commands/clear.md) -- Clear the stack.
    - [pop](commands/pop.md) -- Pop the top table off the stack.
    - [swap](commands/swap.md) -- Swap the top two tables on the stack.
    - [reverse](commands/reverse.md) -- Reverse the tables on the stack.
    - [rotate](commands/rotate.md) -- Rotate the tables on the stack.
- Informational commands -- These commands don't modify the stack:
    - [show](commands/show.md) -- Show the first N rows of a table.
    - [inspect](commands/inspect.md) -- Show descriptive statistics for a table.
    - [history](commands/history.md) -- Show the function (command) history.

[User-defined commands](udf.md) can be used in 'derive' commands.