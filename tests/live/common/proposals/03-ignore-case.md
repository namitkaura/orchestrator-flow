# Proposal: Optional case-insensitive uniqueness

## Problem Statement

The accepted initial application, unique-lines, and output-limit features are prerequisites. Start from the accepted output-limit branch tip. Exact uniqueness intentionally treats `Apple` and `apple` as different values. The user also has personal lists where differences in letter case should count as duplicates, while the original spelling and first-seen order should remain visible.

## Proposed Solution

### 1. Add an explicit comparison mode

Add `--ignore-case` for use together with `--unique`. Compare retained lines using Python's Unicode `str.casefold()` behavior. Keep the text of the first occurrence unchanged and preserve first-seen order. Do not trim spaces or normalize accents. The comparison mode is explicit so existing `--unique` usage stays case-sensitive.

For input `Apple`, `apple`, `PEAR`, `pear`, `--unique --ignore-case` outputs `Apple`, `PEAR`. `Straße` followed by `STRASSE` collapses to `Straße` under the specified comparison. `apple` and ` apple` remain distinct. Empty input still succeeds with no output.

Using `--ignore-case` without `--unique` is a command-line error with a nonzero exit status; do not silently activate uniqueness. Omitted `--ignore-case` preserves all accepted baseline, exact-uniqueness, and output-limit behavior.

Apply the existing empty-line handling, then the requested uniqueness comparison, then the existing output limit. With input `Apple`, `apple`, `PEAR`, `pear`, `plum`, `--unique --ignore-case --limit 2` outputs `Apple`, `PEAR`; `--unique --limit 2` remains `Apple`, `apple`. Preserve all previously accepted limit boundaries.

### 2. Verify the comparison assumption

Confirm the chosen Python runtime's relevant case-folding behavior using source/documentation or a small reproducible experiment. Distinguish the observation from conclusions about broader language-specific matching. Record useful research only if needed to support the design; do not create an unstructured scratchpad.

The existing exact-comparison implementation is source context, not evidence that the new comparison has already been implemented. Identify affected processing and CLI wiring explicitly. Preserve the accepted output-limit option and ordering. A missing prerequisite is a contradiction to raise, not permission to implement an unaccepted predecessor silently.

### 3. Document and test the behavior

Update help/README with the explicit pairing requirement, first-occurrence rule, and filtering order. Cover ASCII case differences, the stated Unicode example, original spelling/order, preserved whitespace distinctions, empty input, default compatibility, invalid option pairing, and the combined uniqueness/case-folding/limit CLI witness above. Keep tests focused on this declared behavior and earlier accepted boundaries.

### 4. Non-goals

No locale-specific collation, accent removal, fuzzy matching, sorting, transliteration, database, or third-party dependency. This is still a small private local utility, regardless of the assurance selected for its delivery.

## Questions

The comparison rule and pairing requirement are settled planning inputs. Raise actual runtime/source contradictions or changes to these product semantics through the normal workflow; do not broaden matching behavior silently.

## References

Read the consumer repository's current `README.md`, `AGENTS.md`, implementation/tests, and accepted documents and task logs under `.docs/specs/output-limit/` and `.docs/specs/unique-lines/`. Follow their recorded references to the initial application, including a versioned initial feature directory where applicable. Verify claims about the runtime's `str.casefold()` behavior during the investigation; this proposal's examples are expected behavior, not a claim that research has already been performed.
