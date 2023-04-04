# The T model

T's power comes from the underlying computing model:

- There is a stack of tables.
- Commands operate the stack, instead of naming tables & passing them around as arguments. 
- They use one or more tables on the stack, create a new table, pop the old one(s) off, and push the new one on.
- Commands appear like functions: they have a name, and they take arguments in parentheses.
- They implicitly iterate over the rows of a table--there is no looping.
- You can use user-defined Python functions to define new columns.

