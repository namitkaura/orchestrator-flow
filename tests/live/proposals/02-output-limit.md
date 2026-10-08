# Proposal: Limit the number of printed lines

## Problem Statement

The accepted line-list CLI and unique-lines feature can preserve unique values, but the user sometimes needs only the first few results. This feature starts from the accepted unique-lines branch tip. Manually editing the input or piping to another program is inconvenient for this small local workflow.

## Proposed Solution

### 1. Add a positive output limit

Add `--limit N`, initially accepting positive integers only. Print at most the first N lines that would otherwise be printed. An omitted limit preserves existing behavior. A limit larger than the available output returns all available lines. Empty input succeeds without output.

Apply the limit after the current empty-line handling and, when requested, exact uniqueness. With input `pear`, `pear`, `Apple`, `apple`, `--unique --limit 2` outputs `pear`, `Apple`. `--limit 2` without uniqueness outputs `pear`, `pear`.

For this initial proposal, zero, negative integers, and nonintegers are invalid and produce a nonzero command-line error. Do not silently clamp, wrap, or reinterpret a value. Any later explicitly communicated change to that boundary becomes part of the approved requirements.

### 2. Preserve existing options and documentation

Keep the input and uniqueness semantics unchanged. Update help and README to explain the limit's position after filtering. Use existing standard-library mechanisms and the current small code organization.

### 3. Verify meaningful boundaries

Cover one result, a limit below/at/above available output, duplicate interaction with and without `--unique`, empty input, invalid values, omitted-option compatibility, and the actual CLI path. Use the existing test command. Do not build a performance harness or prescribe a large-file optimization.

### 4. Non-goals

No pagination, offsets, file rewriting, stdin support, new output format, sorting, or case-insensitive matching.

## Questions

Positive-only limits form the initial planning baseline. Later user decisions may revise that boundary and must be reflected through normal requirements/design/task handling. Newly discovered material ambiguities should be raised rather than resolved through an undocumented behavior change.

## References

Read the consumer repository's current README, project instructions, implementation, tests, and the accepted unique-lines documents and task log under `.docs/specs/unique-lines/`. Follow their references to the accepted initial application, including a versioned initial feature directory where applicable. The source and accepted decisions govern existing behavior; the earlier proposals alone are not approval evidence.
