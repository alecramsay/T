# Commands

T commands are like functions: they have a name, and they take arguments in parentheses.
Command names ("verbs") can be in lower or upper case.
Whitespace is ignored.
Commands work on the tables on a stack.

Commands fall into several categories:

- I/O commands read & write tables from/to files:
    - [from](commands/from.md) -- Read a table from a CSV file or read a T script and execute it.
    - [write](commands/write.md) -- Write a table to a CSV or JSON file.
- Column commands change the columns in a table:
    - [keep](commands/keep.md) -- Keep one or more columns. Drop the rest.
    - [drop](commands/drop.md) -- Drop one or more columns. Keep the rest.
    - [rename](commands/rename.md) -- Rename one or more columns.
    - [alias](commands/alias.md) -- Alias one or more columns.
    - [derive](commands/derive.md) -- Derive a new column from existing columns.
    - [cast](commands/cast.md) -- Cast one or more columns to a new data type.
- Row commands change the rows in a table:
    - [select](commands/select.md) -- Select rows that match a condition. Discard the rest.
    - [first](commands/first.md) -- Select the first N (or N%) rows. Discard the rest.
    - [last](commands/last.md) -- Select the last N (or N%) rows. Discard the rest.
    - [sample](commands/sample.md) -- Select a random sample of N (or N%) rows. Discard the rest.
- Table commands change entire tables:
    - [sort](commands/sort.md) -- Sort a table by one or more columns.
    - [groupby](commands/groupby.md) -- Aggregate the rows of a table by the the values of one or more columns.
    - [join](commands/join.md) -- Join two tables.
    - [union](commands/union.md) -- Concatenate two tables.
    - [duplicate](commands/duplicate.md) -- Duplicate a table.
- Stack commands manipulate the table stack:
    - [clear](commands/clear.md) -- Clear the stack.
    - [pop](commands/pop.md) -- Pop the top table off the stack.
    - [swap](commands/swap.md) -- Swap the top two tables on the stack.
    - [reverse](commands/reverse.md) -- Reverse the tables on the stack.
    - [rotate](commands/rotate.md) -- Rotate the tables on the stack.
- Informational commands display information about the environment:
    - [show](commands/show.md) -- Show the first N rows of a table.
    - [inspect](commands/inspect.md) -- Show descriptive statistics for the numeric columns of a table.
    - [history](commands/history.md) -- Show the command history.
