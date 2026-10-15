# /// script
# requires-python = ">=3.10"
# ///
"""Run: uv run --script tests/test_guard.py"""
import json
import subprocess
import sys
from pathlib import Path

GUARD = Path(__file__).resolve().parent.parent / "hooks" / "reader-git-guard.py"

CASES = [
    # (agent_type, command, expected exit code)
    ("readonly-agents:reader", "git status", 0),
    ("readonly-agents:reader", "git diff", 0),
    ("readonly-agents:reader", "git diff HEAD~1 -- src/a.ts", 0),
    ("readonly-agents:reader", "git log -5 --oneline", 0),
    ("readonly-agents:reader", "git diff; echo x > t.txt", 2),
    ("readonly-agents:reader", "git diff && rm -rf .", 2),
    ("readonly-agents:reader", "git log | head", 2),
    ("readonly-agents:reader", "git diff > out.txt", 2),
    ("readonly-agents:reader", "git diff --output=out.txt", 2),
    ("readonly-agents:reader", "git commit -m x", 2),
    ("readonly-agents:reader", "git -c core.pager=sh diff", 2),
    ("readonly-agents:reader", "ls", 2),
    ("readonly-agents:reader", "git diff $(echo hi)", 2),
    # every other agent, and the main session, is left alone
    ("", "rm -rf x", 0),
    ("readonly-agents:verifier", "rm -rf x", 0),
    ("Explore", "echo x > t.txt", 0),
]


def main() -> int:
    failed = 0
    for agent, cmd, want in CASES:
        payload = json.dumps({"agent_type": agent, "tool_input": {"command": cmd}})
        got = subprocess.run([sys.executable, str(GUARD)], input=payload, text=True, capture_output=True).returncode
        ok = got == want
        failed += not ok
        print(("pass" if ok else "FAIL"), f"agent={agent or '-'!r:26} {cmd!r} -> {got} (want {want})")
    print(f"{len(CASES) - failed} pass, {failed} fail")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
