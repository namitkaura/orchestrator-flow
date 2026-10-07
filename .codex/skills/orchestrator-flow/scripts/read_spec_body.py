"""Stream current spec content without loading Revision History into role context."""
from __future__ import annotations

import argparse
import json
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


def numbered_tasks(text):
    """Return actual numbered checkboxes outside code, preserving execution order."""
    tasks = {}
    for line, outside in markdown_lines(text.splitlines(keepends=True)):
        if outside and line.rstrip() == "## Revision History":
            break
        match = re.match(r"^\s*- \[([ xX])\] ([1-9]\d*)\.\s", line) if outside else None
        if match:
            if match[2] in tasks:
                raise ValueError(f"Duplicate task {match[2]}")
            tasks[match[2]] = match[1].lower() == "x"
    return tasks


def progress_basis(text):
    """Ignore only newline encoding and numbered completion marks outside fences."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    parts, history = [], False
    for line, outside in markdown_lines(text.splitlines(keepends=True)):
        history |= outside and line.rstrip() == "## Revision History"
        parts.append(re.sub(r"^(\s*- \[)[ xX](\] [1-9]\d*\.\s)", r"\1 \2", line) if outside and not history else line)
    return "".join(parts)


def body_chunk(path, offset=0, max_chars=8000, history=False):
    """Scan fence state from the beginning; offsets count normalized characters."""
    if offset < 0 or max_chars < 1:
        raise ValueError("offset must be nonnegative and max-chars positive")
    position, parts, remaining = 0, [], max_chars
    for line in spec_lines(path, history):
        end = position + len(line)
        if end > offset:
            part = line[max(0, offset - position):]
            if len(part) > remaining:
                parts.append(part[:remaining])
                return {"start_offset": offset, "next_offset": offset + max_chars, "eof": False, "text": "".join(parts)}
            parts.append(part)
            remaining -= len(part)
        position = end
    if offset > position:
        raise ValueError("offset exceeds the selected document body")
    return {"start_offset": offset, "next_offset": position, "eof": True, "text": "".join(parts)}


def check_task_completion(path, progress, task_ids=None, *, text=None):
    """Compare completion claims with each actual numbered checkbox, not ordering."""
    tasks = numbered_tasks("".join(spec_lines(path)) if text is None else text)
    if task_ids is not None:
        if not set(task_ids).issubset(tasks):
            raise ValueError(f"{path}: phase refers to absent tasks")
        tasks = {task_id: tasks[task_id] for task_id in task_ids}
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
    parser.add_argument("--offset", type=int)
    parser.add_argument("--max-chars", type=int)
    args = parser.parse_args()
    if args.offset is not None or args.max_chars is not None:
        print(json.dumps(body_chunk(args.path, args.offset or 0, args.max_chars if args.max_chars is not None else 8000, args.history)))
    else:
        for line in spec_lines(args.path, args.history):
            sys.stdout.write(line)


if __name__ == "__main__":
    main()
