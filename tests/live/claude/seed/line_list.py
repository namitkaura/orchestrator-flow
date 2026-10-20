"""Print the nonempty lines of a UTF-8 text file."""

import argparse
import sys


def nonempty_lines(text):
    """Return the lines of text that contain at least one character, in input order.

    Lines end at LF or CRLF. Terminators are removed; everything else is kept exactly.
    """
    lines = (line.removesuffix("\r") for line in text.split("\n"))
    return [line for line in lines if line]


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="line_list.py", description="Print the nonempty lines of a UTF-8 text file."
    )
    parser.add_argument("path", help="UTF-8 text file to read")
    args = parser.parse_args(argv)
    try:
        with open(args.path, encoding="utf-8", newline="") as handle:
            text = handle.read()
    except (OSError, UnicodeDecodeError) as error:
        print(f"line_list.py: {error}", file=sys.stderr)
        return 1
    for line in nonempty_lines(text):
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
