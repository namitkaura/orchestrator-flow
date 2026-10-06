# Proposal: Small local line-list project

## Problem Statement

We need a small, understandable Python project on which to exercise a development workflow. It will run locally for one user, read small text files, and have no service, deployment, credentials, external API, or public users. Its code and tests should be quick to inspect so workflow overhead remains visible.

## Proposed Solution

### 1. Print nonempty lines from one file

Provide `python line_list.py <path>` and a small separately testable function used by the CLI. Read UTF-8 text and print its lines in input order. Remove line terminators, discard lines containing no characters after that removal, and otherwise preserve text exactly, including leading/trailing spaces and whitespace-only lines. Accept LF and CRLF input. Write one output line per retained input line; tests may normalize platform output line endings.

Keep duplicates and letter case. For input `pear`, an empty line, `Apple`, `pear`, and `apple`, in that order, output `pear`, `Apple`, `pear`, `apple`. An empty file succeeds with no output. A final line without a terminating newline is still processed.

Require exactly one input path. Invalid command syntax returns a nonzero exit status and usage information. Unreadable or invalid-UTF-8 input returns nonzero; exact error wording and friendly exception formatting are not promised in this baseline. Successful processing returns zero.

### 2. Keep the baseline easy to extend

Use Python's standard library and `unittest`; no dependency manager or application package installation is required. Keep input processing distinct from argument parsing so later options can be verified at both function and CLI boundaries. Do not preimplement filtering options from the later feature proposals.

Create a short README with invocation and test commands, a minimal `AGENTS.md` describing ordinary project coding conventions, and `.gitignore` entries for Python caches. Keep the product guidance free of test-controller expectations and special workflow-policy overrides. The baseline should be a few small files, not a framework.

### 3. Verify the baseline

Use `python -m unittest discover -s tests -v`. Cover order, retained duplicates/case/whitespace, empty lines/files, line endings, and the CLI's use of the processing function. Include a meaningful nonzero-error check without over-specifying a traceback or diagnostic string.

This baseline is built once as test setup and then distributed as identical Git history to three local repositories. It is not itself evidence that Orchestrator Flow completed a feature.

### 4. Non-goals

No recursion, directory traversal, stdin mode, network access, automatic retries, persistence, GUI, packaging, benchmarks, or large-file streaming guarantee. Optional future convenience improvements must not become requirements merely because they are easy to add.

## Questions

The behavior above is the setup baseline. The setup agent may choose small internal function names and file organization. Raise material contradictions rather than adding user-visible behavior beyond this scope.

## References

This proposal defines a new seed project. `line_list.py`, `tests/`, `README.md`, and `AGENTS.md` are outputs to create, not claims about existing files. Follow-up proposals are independent inputs after this baseline exists.
