# /// script
# requires-python = ">=3.10"
# ///
"""PreToolUse guard for the `reader` subagent: Bash only runs plain read-only git queries.

Every other agent (the main session, other subagents) passes through untouched.
"""
import json
import re
import sys

SAFE = re.compile(r"git (status|diff|log|show|blame|rev-parse|ls-files)( [^;&|<>`$()\n]*)?")
BAD_FLAGS = ("--output", "--ext-diff", "--textconv")


def read_event() -> dict:
    """The hook input as a dict. Read as bytes and decoded as UTF-8: the console code page
    (cp932, cp936) must not decide how a command with non-ASCII text is read."""
    try:
        raw = sys.stdin.buffer.read().decode("utf-8", errors="replace")
        event = json.loads(raw)
    except Exception:
        return {}
    return event if isinstance(event, dict) else {}


def main() -> int:
    event = read_event()
    agent = str(event.get("agent_type") or "")
    if agent.split(":")[-1] != "reader":
        return 0

    tool_input = event.get("tool_input")
    cmd = str(tool_input.get("command", "") if isinstance(tool_input, dict) else "").strip()
    if SAFE.fullmatch(cmd) and not any(f in cmd for f in BAD_FLAGS):
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "allow"}}))
        return 0

    print(
        "reader: only plain read-only git commands are allowed "
        "(status, diff, log, show, blame, rev-parse, ls-files), with no pipes, redirects or chaining.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
