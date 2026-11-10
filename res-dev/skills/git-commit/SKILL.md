---
name: commit
description: Stages, commits, and pushes git changes with a generated commit message
---

# Git Commit Workflow

When the user types `/commit`:

1. `git status` — review what changed. Stage explicit paths (`git add path/a path/b`); never
   `git add .` / `-A` / `--all` — the `bash_guard` hook blocks it (the sandbox stages `.env*` as deleted).
2. `git diff --staged` to read the staged changes.
3. Compose a conventional-commit message:
   - Summary under 50 characters
   - Body explaining the "why" and the affected components
   - No AI attribution (`Co-Authored-By: Claude`, "Generated with Claude Code") — the hook blocks it
4. Show the message and wait for approval before committing.
5. `git commit -m "<message>"` — on the default branch the hook blocks it; create a feature branch first.
6. Ask before pushing, then `git push`.
7. Confirm.

## Sandbox

`git push` needs the sandbox disabled (osxkeychain credential helper).
