# alias

Alias one or more columns in the table on the top of the stack.
Pop that table off and push the new table onto the stack.

Aliases are soft renames: you use the aliases in subsequent commands, 
but when you write the table to a file, the original column names are used.

## Examples

`>>> alias((Tot_2020_tot, Total))`