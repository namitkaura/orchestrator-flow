# Proposal: Preserve the first occurrence of each unique line

## Problem Statement

The local line-list CLI currently prints every nonempty input line, including duplicates. For small personal lists, the user wants an optional way to keep each exact value once while retaining the original order. Existing scripts using the command without a new option must retain their behavior.

## Proposed Solution

### 1. Add optional exact uniqueness

Add `--unique` to `python line_list.py <path>`. When present, output only the first occurrence of each retained line. Equality is exact and case-sensitive; do not trim whitespace or sort the values. Empty-line handling is unchanged.

For input `pear`, `Apple`, `pear`, `apple`, `Apple`, output `pear`, `Apple`, `apple` with `--unique`. `A` and `a`, and `apple` and ` apple`, remain different values. Without the flag, all retained input lines including duplicates are printed exactly as before. Empty input succeeds with no output in either mode.

### 2. Preserve the small project structure

Carry the option through the CLI to the separately testable processing behavior. Use the standard library. Keep file-reading and failure behavior within the baseline contract. This remains a personal local utility processing small files; there is no unattended service requirement.

### 3. Document and verify the option

Update README/help examples. Cover order preservation, duplicate removal, exact case/whitespace distinctions, empty input, the unchanged default, and actual CLI-to-processing wiring. Existing applicable baseline tests remain meaningful. Use the project's `unittest` command and plan proportionate test maintenance explicitly.

### 4. Non-goals

No sorting, case-insensitive comparison, output limit, counts, concurrency, retry mechanism, or new dependency. Those are separate product choices.

## Questions

The recorded behavior is the planning baseline. Internal data structure choices remain open to design. Raise any conflict with actual source behavior during planning rather than silently changing the preservation guarantees.

## References

Read the consumer repository's `README.md`, `AGENTS.md`, `line_list.py`, and `tests/`. They establish the current implementation and coding conventions. `.docs/inputs/00-line-list-project.md` records the intended baseline; verify current source instead of treating that input as implementation evidence.
