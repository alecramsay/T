# The T model

T's power comes from the underlying computing model:

- There is a stack of tables.
- Instead of naming tables & passing them around as arguments, commands operate a stack. 
- A command uses one or more tables on the stack, creates a new table, pops the old ones off, and pushes the new one on.
- Commands are like functions: they have a name, and they take arguments in parentheses.
- Commands implicitly iterate over the rows of a table--there is no need to write a loop.
- You can user-defined Python functions to define new columns.

