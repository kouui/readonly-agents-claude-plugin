# readonly-agents-claude-plugin

Two subagents for the two cases where a subagent should not be able to change your tree. No settings are touched; the guard only acts on the `reader` agent.

| Agent | Can do | Cannot do |
| --- | --- | --- |
| `readonly-agents:reader` | Read, Grep, Glob, and plain read-only git queries: `status`, `diff`, `log`, `show`, `blame`, `rev-parse`, `ls-files` | write, delete, run anything else, pipe, redirect, chain |
| `readonly-agents:verifier` | write and run anything | touch the main working tree: it runs in its own git worktree (`isolation: worktree`) |

Use `reader` to search, explore and review. Use `verifier` when something must be executed to check a claim.

## Install

```bash
claude plugin marketplace add kouui/magic-claude-code-plugin
claude plugin install readonly-agents@magic-claude-code-plugin -s user
```

Needs `uv` on `PATH` (the guard is a single-file Python script).

## How the guard works

`hooks/hooks.json` registers a `PreToolUse` hook on `Bash`. The hook reads `agent_type` from its input and does nothing unless it is `reader`. For `reader` the command must match `git <read-only subcommand> [args]` with no `; & | < > $ ( )`, backtick or newline, and without `--output`, `--ext-diff` or `--textconv`. A match is allowed without a prompt; anything else exits with code 2 and the model sees the reason.

This is a plain-text allowlist, not a security boundary. A plugin subagent cannot carry its own `hooks` or `permissionMode`, which is why the guard is a plugin-level hook scoped by agent type.

## Limits

- `reader` cannot pipe: use `git log -20`, not `git log | head`.
- `reader` has Bash but no PowerShell tool, so there is no shell back door on Windows.
- `verifier` leaves its worktree under `<project>/.claude/worktrees/` when it changed something; add that path to `.gitignore` and remove old ones with `git worktree remove`.
- Needs a git repository for `verifier`.

## Test

```bash
claude plugin validate .
uv run --script tests/test_guard.py
```

`tests/test_guard.py` runs 16 cases against the guard. It was also checked end to end with `claude -p --plugin-dir .`: `reader` ran `git diff`, and `git diff; echo x > t.txt` and `ls` were refused by the hook; `verifier` created a file only inside its worktree.

## Layout

```text
.claude-plugin/plugin.json
agents/reader.md
agents/verifier.md
hooks/hooks.json
hooks/reader-git-guard.py
tests/test_guard.py
```
