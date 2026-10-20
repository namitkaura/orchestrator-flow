# Line list

A small local Python utility that prints the nonempty lines of a UTF-8 text file. It runs for one user on small files, with no service, network access or credentials.

## Conventions

- Use Python 3 and the standard library only. Do not add dependencies or packaging.
- Keep text processing in small functions that tests can call directly, separate from argument parsing in `main`.
- Read text as UTF-8 and keep each line exactly as written, apart from removing its line terminator.
- Prefer small plain functions over classes, and keep changes easy to read.

## Commands

- Run: `python3 line_list.py <path>`
- Test: `python3 -m unittest discover -s tests -v`

## Documentation

Update `README.md` whenever command-line behavior changes.
