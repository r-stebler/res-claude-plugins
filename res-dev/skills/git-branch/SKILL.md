---
name: git-branch
description: Create a new feature branch from the default branch. Arguments are ticket key and short description. Use when starting implementation work that belongs on its own branch (every risk tier starts with a branch).
argument-hint: TICKET-123 short description
---

Create a new feature branch.

## Input

Arguments: $ARGUMENTS — first token is the ticket key (e.g. `ABC-123`), the rest is a short
description. If either is missing, ask.

## Steps

1. Branch name: `feature/<TICKET-KEY>-<slugified-description>`
   - Ticket key keeps its original casing: `ABC-123 Add user login` → `feature/ABC-123-add-user-login`
   - Description lowercased, hyphens instead of spaces, no special characters
2. Resolve the default branch `<base>`: `git symbolic-ref --short refs/remotes/origin/HEAD`
   (strip `origin/`); if unset, `gh repo view --json defaultBranchRef -q .defaultBranchRef.name`.
3. Check the current branch with `git branch --show-current`.
4. **Not on `<base>`:** warn that this creates a branch off a branch, show the current branch, ask for
   explicit confirmation. If denied, suggest `git checkout <base> && git pull` first.
5. **On `<base>`:** `git pull`
6. Check `git status` for uncommitted changes. If there are any, ask: stash, commit, or abort.
7. `git checkout -b <branch-name>`
8. `git push -u origin <branch-name>`
9. Confirm the branch exists and tracks remote.

## Sandbox

Steps 7 and 8 need the sandbox disabled:
- `git checkout` fails to stat `.env*` files and can leave the worktree swapped while HEAD stays put.
- `git push` cannot reach the osxkeychain credential helper.
