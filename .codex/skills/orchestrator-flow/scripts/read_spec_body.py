"""Stream current spec content without loading Revision History into role context."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def markdown_lines(lines):
    """Yield lines and whether they are outside a fenced code block."""
    fence = None
    for line in lines:
        match = re.match(r"^ {0,3}(`{3,}|~{3,})", line)
        if match:
            marker = match.group(1)
            if fence is None:
                fence = marker
            elif marker[0] == fence[0] and len(marker) >= len(fence) and not line[match.end():].strip():
                fence = None
            yield line, False
        else:
            yield line, fence is None


def spec_lines(path, history=False):
    in_history = False
    with Path(path).open(encoding="utf-8-sig") as source:
        for line, outside in markdown_lines(source):
            if outside and line.rstrip() == "## Revision History":
                in_history = True
                if not history:
                    return
            if in_history == history:
                yield line


def check_document(path, expected_version):
    text = Path(path).read_text(encoding="utf-8-sig")
    lines = text.splitlines()
    if not lines or not lines[0].startswith("# ") or len(lines) < 2 or lines[1] != f"Content version: {expected_version}":
        raise ValueError(f"{path}: expected Content version: {expected_version} immediately below title")
    history = "".join(spec_lines(path, history=True))
    if not history:
        raise ValueError(f"{path}: missing final Revision History")
    headings = [line for line, outside in markdown_lines(history.splitlines()) if outside]
    if any(line.startswith("## ") for line in headings[1:]):
        raise ValueError(f"{path}: Revision History must be the final main section")
    versions = [int(v) for v in re.findall(r"^### Version (\d+) — \d{4}-\d{2}-\d{2}$", "\n".join(headings), re.M)]
    if versions != list(range(1, expected_version + 1)):
        raise ValueError(f"{path}: Revision History must preserve versions 1 through {expected_version}")


def check_task_completion(path, progress):
    """Compare completion claims with each actual numbered checkbox, not ordering."""
    tasks = {}
    for line, outside in markdown_lines(spec_lines(path)):
        match = re.match(r"^\s*- \[([ xX])\] ([1-9]\d*)\.\s", line) if outside else None
        if match:
            task_id = match[2]
            if task_id in tasks:
                raise ValueError(f"{path}: duplicate task {task_id}")
            tasks[task_id] = match[1].lower() == "x"
    reported = {task["task_id"]: task for task in progress}
    if not tasks or len(reported) != len(progress) or set(tasks) != set(reported):
        raise ValueError(f"{path}: consolidated progress must account for every numbered task exactly once")
    for task_id, checked in tasks.items():
        if reported[task_id]["status"] == "completed" and not checked:
            raise ValueError(f"{path}: task {task_id} is unchecked; later completion is not evidence for it")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    parser.add_argument("--history", action="store_true", help="Return Revision History instead of current content")
    args = parser.parse_args()
    for line in spec_lines(args.path, args.history):
        sys.stdout.write(line)


if __name__ == "__main__":
    main()
