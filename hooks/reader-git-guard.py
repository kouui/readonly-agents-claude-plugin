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


def main() -> int:
    event = json.load(sys.stdin)
    agent = str(event.get("agent_type") or "")
    if agent.split(":")[-1] != "reader":
        return 0

    cmd = str(event.get("tool_input", {}).get("command", "")).strip()
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
