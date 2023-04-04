# Make Executable

[PyInstaller](https://pyinstaller.org/en/stable/)

From the scripts/ directory, do the following command:

`pyinstaller T.py -F --distpath . --specpath ./build --clean`

## TODO

Figure out how to exclude:

- test/ directory
- pytest
- user/ directory
- data/ directory
- docs/ directory
- examples/ directory
- logs/ directory
- other scripts

## Links

- https://pyinstaller.org/en/stable/index.html
- https://pyinstaller.org/en/stable/advanced-topics.html#the-toc-and-tree-classes