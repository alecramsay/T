# T

Tables as a computing model

The purpose of T is to make it easier to work with CSV data.

TODO - Verify all these instructions.

## Installation

On macOS, download the UNIX executable T from the scripts/ directory, and
make sure it is in your PATH. 

## Usage

```bash
T \
    --user file_path \
    --file file_path \
    --source source_dir \
    --data data_dir \
    --output output_dir \
    --log log_file \
    --scriptargs script_args \
    --verbose verbose
```

All parameters are optional. If specified:

- **user** (-u) -- Specifies a relative path to a .py file of user-defined functions. The default is None.
- **file** (-f) -- Specifies a relative path to .t script file.
- **source** (-s) -- Provides a relative directory where T will look for .t script files.
- **data** (-d) -- Provides a relative directory where T will look for .csv data files.
- **output** (-o) -- Provides a relative directory where T will write output .csv or .json files.
- **log** (-l) -- Specifies a relative path to log file where T will log a history of commands. The defaults is "logs/history.log".
- **scriptargs** (-a) -- Provides script arguments used by the script file. Arguments are provides as dictionary represented as a string. For example, '{"paf": "2020_alt_assignments_NC.csv"}'. The default is None.
- **verbose** (-v) -- Toggles verbose mode on.

For command documentation, type:

```
T -h
```

For example:

```
T -u user/alec.py -s examples -d data/rd/NC
```

## Documentation

The language is documented [here](https://alecramsay.github.io/T/).

## Feedback

I welcome your feedback in [Discussions](https://github.com/alecramsay/T/discussions/landing):

- What language features would make T most useful?
- Would a GUI authoring app be useful?

Obviously, I need a Windows executable. 
I would appreciate help with that, as I don't have a Windows PC.
