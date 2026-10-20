#!/usr/bin/env python3
"""Check that this Claude Code session can run Orchestrator Flow.

Run with the system interpreter, before anything else, as
``python3 <skill-dir>/scripts/check_claude_code.py``. It uses only the standard library and always
exits 0, so a skill's inline command never aborts on it. Orchestrator reads three lines:

    Claude Code: supported | too_old | unknown (...)
    Runtime venv: ok | missing | broken | missing_dependencies
    Per-call overrides: none | NAME=value, ...
"""
from __future__ import annotations

import os
from pathlib import Path
import re
import subprocess
import sys

# The integration's single statement of the minimum supported Claude Code version.
MINIMUM = (2, 1, 296)
TRUE = {"1", "true", "yes", "on"}
VERSION_OUTPUT = re.compile(r"(\d+)\.(\d+)\.(\d+)\s*\(Claude Code\)")


def dotted(version):
    return ".".join(str(part) for part in version)


def running_version(env):
    """Return (version, executable path, problem) for the binary actually running this session."""
    execpath = env.get("CLAUDE_CODE_EXECPATH")
    if not execpath:
        return None, None, "CLAUDE_CODE_EXECPATH is not set"
    try:
        result = subprocess.run([execpath, "--version"], capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError) as exc:
        return None, execpath, f"could not run the session's Claude Code binary: {exc}"
    match = VERSION_OUTPUT.search(result.stdout)
    if result.returncode != 0 or not match:
        return None, execpath, "the session's Claude Code binary did not report a recognizable version"
    return tuple(int(part) for part in match.groups()), execpath, None


def source(execpath, env):
    """Name the app running this session, or None; the binary's path wins over the inheritable entrypoint."""
    path = (execpath or "").replace("\\", "/")
    if "/Application Support/Claude/" in path or "/Claude.app/" in path:
        return "Claude desktop app"
    if "/.local/" in path or "/claude/versions/" in path or "/@anthropic-ai/claude-code/" in path:
        return "Claude Code CLI"
    return {"claude-desktop": "Claude desktop app", "cli": "Claude Code CLI"}.get(env.get("CLAUDE_CODE_ENTRYPOINT", ""))


def version_lines(env):
    version, execpath, problem = running_version(env)
    if version is None:
        return [f"Claude Code: unknown ({problem})"]
    app = source(execpath, env)
    verdict = "supported" if version >= MINIMUM else "too_old"
    origin = f" from the {app}" if app else ""
    lines = [f"Claude Code: {verdict} (running {dotted(version)}{origin}; minimum {dotted(MINIMUM)})"]
    if verdict == "too_old":
        running = f"{dotted(version)} ({app})" if app else dotted(version)
        lines.append(f"Orchestrator Flow requires Claude Code {dotted(MINIMUM)} or newer. This session is running Claude Code "
                     f"{running}. Update Claude Code, then start a new session: in a terminal run `claude update`; "
                     "for the desktop app, update the Claude app.")
    return lines


def venv_lines(skill_dir):
    venv = skill_dir / ".venv"
    python = venv / "bin" / "python"
    setup = [f'  python3 -m venv --clear "{venv}"',
             f'  "{python}" -m pip install -r "{skill_dir / "scripts" / "requirements.txt"}"']
    if not python.exists():
        state = "broken" if venv.exists() or python.is_symlink() else "missing"
    else:
        try:
            result = subprocess.run([str(python), "-c", "import jsonschema, referencing"], capture_output=True, text=True, timeout=60)
            state = "ok" if result.returncode == 0 else "missing_dependencies" if "No module named" in result.stderr else "broken"
        except (OSError, subprocess.SubprocessError):
            state = "broken"
    if state == "ok":
        return ["Runtime venv: ok"]
    return [f"Runtime venv: {state}. Set it up before starting the workflow:", *setup]


def override_lines(env):
    """Report only settings that defeat per-call choices: a true model FORCE (with its model) and an effort level."""
    present = []
    if env.get("CLAUDE_CODE_SUBAGENT_MODEL_FORCE", "").strip().lower() in TRUE:
        present.append(f"CLAUDE_CODE_SUBAGENT_MODEL_FORCE={env['CLAUDE_CODE_SUBAGENT_MODEL_FORCE']}")
        if env.get("CLAUDE_CODE_SUBAGENT_MODEL"):
            present.append(f"CLAUDE_CODE_SUBAGENT_MODEL={env['CLAUDE_CODE_SUBAGENT_MODEL']}")
    if env.get("CLAUDE_CODE_EFFORT_LEVEL"):
        present.append(f"CLAUDE_CODE_EFFORT_LEVEL={env['CLAUDE_CODE_EFFORT_LEVEL']}")
    return [f"Per-call overrides: {', '.join(present) if present else 'none'}"]


def main():
    env = os.environ
    lines = []
    for build in (lambda: version_lines(env), lambda: venv_lines(Path(__file__).resolve().parent.parent), lambda: override_lines(env)):
        try:
            lines += build()
        except Exception as exc:  # The check must never abort the skill invocation.
            lines.append(f"Check error: {exc.__class__.__name__}: {exc}")
    if not any(line.startswith("Claude Code:") for line in lines):
        lines.insert(0, "Claude Code: unknown (the version check failed)")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # pragma: no cover - last-resort guard for the inline command
        print(f"Claude Code: unknown (the check itself failed: {exc})")
        sys.exit(0)
