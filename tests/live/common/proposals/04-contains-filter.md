# Proposal: Keep only the lines that contain some text

## Problem Statement

`line_list.py <path>` prints every nonempty line of a UTF-8 file. The user keeps notes, reading lists and snippets in such files, and often wants only the lines that mention something: a project code, a word or a piece of markup. Today they pipe the output through `grep`, which treats characters such as `.` and `*` as pattern syntax. The tool should filter on its own and treat the requested text exactly as typed, including non-English text such as `café`, `Straße` or `日本語`.

This feature builds on the initial line-list application. Existing uses of the command without the new option must keep their behavior.

## Proposed Solution

### 1. Add `--contains TEXT`

Add an optional `--contains TEXT` to `line_list.py <path>`. With it, print only the nonempty lines that contain `TEXT` as a literal substring, in their original order and otherwise unchanged. Without it, the command behaves exactly as it does now.

`TEXT` is plain text, not a pattern: characters such as `<`, `>`, `&`, `.`, `*` and `\` match only themselves. For a file with these lines:

```text
<b>R&D</b> budget
R and D
café & croissant
Cafe menu
a.b
axb
```

- `--contains '&'` prints `<b>R&D</b> budget` and `café & croissant`.
- `--contains '<b>'` prints `<b>R&D</b> budget`.
- `--contains 'a.b'` prints `a.b` only.
- `--contains 'café'` prints `café & croissant` only; `Cafe menu` does not match.

An empty `TEXT` is a command-line error with a nonzero exit status. A file without matching lines succeeds with no output.

### 2. Keep the structure small

Put the matching in a small function that tests can call directly, and keep argument parsing separate. Use the standard library only.

### 3. Document and test

Update `README.md` with the option and these examples. Test literal matching of the characters above, non-ASCII text, original order, empty input, no matches, the empty-`TEXT` error, the unchanged default behavior and the command-line wiring.

### 4. Non-goals

This feature includes no regular expressions or wildcards, and no accent folding or Unicode normalization: `cafe` never matches `café`. It also excludes multiple `--contains` values, inverted matching, counts, highlighting and new dependencies.

## Questions

1. Should matching ignore letter case? The user has not decided, so ask before settling the requirements. If it should, `--contains café` also prints `CAFÉ au lait`, and `--contains straße` also prints `STRASSE`. If not, letter case must match exactly.

## References

Read the consumer repository's `AGENTS.md`, `README.md`, `line_list.py` and tests. The examples above are expected behavior, not claims about existing code.
