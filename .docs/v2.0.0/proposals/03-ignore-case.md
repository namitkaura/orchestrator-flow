# Proposal: Optional case-insensitive uniqueness

## Problem Statement

Exact uniqueness intentionally treats `Apple` and `apple` as different values. The user also has personal lists where differences in letter case should count as duplicates, while the original spelling and first-seen order should remain visible.

## Proposed Solution

### 1. Add an explicit comparison mode

Add `--ignore-case` for use together with `--unique`. Compare retained lines using Python's Unicode `str.casefold()` behavior. Keep the text of the first occurrence unchanged and preserve first-seen order. Do not trim spaces or normalize accents. The comparison mode is explicit so existing `--unique` usage stays case-sensitive.

For input `Apple`, `apple`, `PEAR`, `pear`, `--unique --ignore-case` outputs `Apple`, `PEAR`. `Straße` followed by `STRASSE` collapses to `Straße` under the specified comparison. `apple` and ` apple` remain distinct. Empty input still succeeds with no output.

Using `--ignore-case` without `--unique` is a command-line error with a nonzero exit status; do not silently activate uniqueness. Omitted `--ignore-case` preserves all accepted baseline and exact-uniqueness behavior.

### 2. Verify the comparison assumption

Confirm the chosen Python runtime's relevant case-folding behavior using source/documentation or a small reproducible experiment. Distinguish the observation from conclusions about broader language-specific matching. Record useful research only if needed to support the design; do not create an unstructured scratchpad.

The existing exact-comparison implementation is source context, not evidence that the new comparison has already been implemented. Identify affected processing and CLI wiring explicitly. If the chosen starting branch contains other approved options, preserve their documented ordering and behavior; do not add options missing from that branch.

### 3. Document and test the behavior

Update help/README with the explicit pairing requirement and first-occurrence rule. Cover ASCII case differences, the stated Unicode example, original spelling/order, preserved whitespace distinctions, empty input, default compatibility, invalid option pairing, and a real CLI witness. Keep tests focused on this declared behavior.

### 4. Non-goals

No locale-specific collation, accent removal, fuzzy matching, sorting, transliteration, database, or third-party dependency. This is still a small private local utility, regardless of the assurance selected for its delivery.

## Questions

The comparison rule and pairing requirement are settled planning inputs. Raise actual runtime/source contradictions or changes to these product semantics through the normal workflow; do not broaden matching behavior silently.

## References

Read the consumer repository's current `README.md`, `AGENTS.md`, implementation/tests, and accepted `.docs/specs/unique-lines/` documents. Verify claims about the runtime's `str.casefold()` behavior during the investigation; this proposal's examples are expected behavior, not a claim that research has already been performed.
