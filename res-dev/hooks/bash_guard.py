#!/usr/bin/env python3
"""PreToolUse guard for the Bash tool.

Blocks (exit 2, reason on stderr — shown to the model):
  1. `git commit` on the default branch (master/main) — work belongs on a feature branch.
  2. `git add -A|--all|.` and `git commit -a` — staging everything breaks in the sandbox
     (it cannot stat `.env*` files and stages them as deleted); stage explicit paths.
  3. AI attribution in commit messages / PR bodies — the user never wants it.

A safety net, not a parser: anything it cannot read is let through (exit 0), never blocked.
One exception: a `git commit` whose target directory (after `cd` / `git -C`, `~` and `$VAR`
expanded) does not exist is blocked — otherwise the branch check silently passes. Note the hook's
environment may differ from the sandboxed shell's (e.g. `$TMPDIR`), so absolute paths are safest.
"""
import json
import os
import re
import shlex
import subprocess
import sys

DEFAULT_BRANCHES = {"master", "main"}
ADD_ALL_ARGS = {"-A", "--all", ".", ":/"}
SEPARATORS = {"&&", "||", ";", "|", "&", "\n"}
ATTRIBUTION = re.compile(
    r"co-authored-by:[^\n]*(claude|anthropic\.com)|generated with \[?claude code", re.IGNORECASE
)
GIT_OPTS_WITH_VALUE = {"-C", "-c", "--git-dir", "--work-tree", "--namespace"}


def block(reason: str) -> None:
    print(reason, file=sys.stderr)
    sys.exit(2)


def segments(command: str) -> list[list[str]]:
    """Split a shell command into simple commands, quotes respected."""
    lexer = shlex.shlex(command, posix=True, punctuation_chars=";&|")
    lexer.whitespace_split = True
    result, current = [], []
    for tok in lexer:
        if tok in SEPARATORS:
            result.append(current)
            current = []
        else:
            current.append(tok)
    result.append(current)
    return [s for s in result if s]


def strip_env(tokens: list[str]) -> list[str]:
    i = 0
    while i < len(tokens) and re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", tokens[i]):
        i += 1
    return tokens[i:]


def file_arg(args: list[str], flags: set[str]) -> str | None:
    for i, a in enumerate(args):
        if a in flags and i + 1 < len(args):
            return args[i + 1]
        for f in flags:
            if f.startswith("--") and a.startswith(f + "="):
                return a.split("=", 1)[1]
    return None


def resolve(base: str, path: str) -> str:
    """Join a shell path onto `base` the way the shell would see it: `~` and `$VAR` expanded."""
    return os.path.join(base, os.path.expandvars(os.path.expanduser(path)))


def read_file(path: str | None, cwd: str) -> str:
    if not path or path == "-":
        return ""
    try:
        with open(resolve(cwd, path), encoding="utf-8") as fh:
            return fh.read()
    except OSError:
        return ""


def current_branch(repo_dir: str) -> str | None:
    try:
        out = subprocess.run(
            ["git", "-C", repo_dir, "branch", "--show-current"],
            capture_output=True, text=True, timeout=5,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    return out.stdout.strip() if out.returncode == 0 else None


def check_attribution(text: str) -> None:
    if ATTRIBUTION.search(text):
        block(
            "Blocked: AI attribution (Co-Authored-By: Claude / 'Generated with Claude Code') "
            "in a commit message or PR body. The user never wants it — remove the line and retry."
        )


def check_git(args: list[str], cwd: str) -> None:
    repo_dir = cwd
    i = 0
    while i < len(args) and args[i].startswith("-"):
        opt = args[i]
        if opt in GIT_OPTS_WITH_VALUE and i + 1 < len(args):
            if opt == "-C":
                repo_dir = resolve(repo_dir, args[i + 1])
            i += 2
        else:
            i += 1
    if i >= len(args):
        return
    sub, rest = args[i], args[i + 1:]

    if sub == "add" and ADD_ALL_ARGS.intersection(rest):
        block(
            "Blocked: `git add -A/--all/.` stages everything — in the sandbox `.env*` files show up "
            "as deleted. Stage explicit paths instead (`git add path/a path/b`)."
        )

    if sub == "commit":
        if any(a == "--all" or re.match(r"^-[a-zA-Z]*a[a-zA-Z]*$", a) for a in rest):
            block("Blocked: `git commit -a` stages every tracked change. Stage explicit paths, then commit.")
        check_attribution(" ".join(rest))
        check_attribution(read_file(file_arg(rest, {"-F", "--file"}), cwd))
        if not os.path.isdir(repo_dir):  # unresolvable target: the branch check below would pass blindly
            block(
                f"Blocked: cannot resolve the commit's directory `{repo_dir}` to check its branch. "
                f"Use an absolute path in `cd` / `git -C`, then retry."
            )
        branch = current_branch(repo_dir)
        if branch in DEFAULT_BRANCHES:
            block(
                f"Blocked: commit on `{branch}`. Create a feature branch first "
                f"(`feature/<TICKET>-<slug>`), then commit there."
            )


def check_gh(args: list[str], cwd: str) -> None:
    if len(args) >= 2 and args[0] == "pr" and args[1] in {"create", "edit", "comment", "review"}:
        check_attribution(" ".join(args[2:]))
        check_attribution(read_file(file_arg(args[2:], {"-F", "--body-file"}), cwd))


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return
    if data.get("tool_name") != "Bash":
        return
    command = (data.get("tool_input") or {}).get("command") or ""
    cwd = data.get("cwd") or os.getcwd()
    try:
        parsed = segments(command)
    except ValueError:  # unbalanced quotes, heredoc oddities: fall back to a raw scan
        if re.search(r"\bgit\b.*\bcommit\b|\bgh\s+pr\b", command):
            check_attribution(command)
        return
    for tokens in parsed:
        tokens = strip_env(tokens)
        if not tokens:
            continue
        if tokens[0] == "cd" and len(tokens) > 1:  # `cd repo && git commit` — the hook's cwd is pre-cd
            cwd = resolve(cwd, tokens[1])
        elif tokens[0] == "git":
            check_git(tokens[1:], cwd)
        elif tokens[0] == "gh":
            check_gh(tokens[1:], cwd)


if __name__ == "__main__":
    main()
