# Line list

Prints the nonempty lines of a UTF-8 text file, in order and exactly as written.

```sh
python3 line_list.py notes.txt
```

Lines end at LF or CRLF. Empty lines are skipped; every other line, including duplicates, letter case and spaces, is printed unchanged. A missing or unreadable file, or one that is not valid UTF-8, exits with status 1. Wrong arguments print usage and exit with a nonzero status.

## Tests

```sh
python3 -m unittest discover -s tests -v
```
