# Aggregate Functions

By default the [groupby command](commands/groupby.md) computes all of these functions for the numeric columns associated with the grouping columns:

- sum
- count
- mean
- std
- min
- max
- median

They are also computed for the numeric columns of a table as it is added to the stack.
These values can be referenced in [derive command](commands/derive.md) formulas, like this:

`>>> derive(w, Total / sum(Total))`

# TODO

- Enable aggregate function references in 'select' conditions