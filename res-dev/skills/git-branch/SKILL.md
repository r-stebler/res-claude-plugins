---
name: git-branch
description: Create a new feature branch from main. Arguments are ticket number and short description.
disable-model-invocation: true
argument-hint: TICKET-123 short description
---

Create a new feature branch.

## Input
Arguments: $ARGUMENTS

Parse the arguments: the first token is the ticket number (e.g. `TICKET-123`), the rest is a short description.

## Steps

1. Parse arguments into ticket number and description
   - If arguments are missing or incomplete, ask the user for ticket number and description
2. Generate the branch name in the format: `feature/<ticket-lower>-<slugified-description>`
   - Example: `TICKET-123 Add user login` → `feature/ticket-123-add-user-login`
   - Lowercase, hyphens instead of spaces, no special characters
3. Check the current branch with `git branch --show-current`
4. **If the current branch is NOT `main`:**
   - Warn the user that a branch-off-branch will be created
   - Show current branch name
   - Ask for explicit confirmation before proceeding
   - If denied, suggest switching to main first: `git checkout main && git pull`
5. **If the current branch IS `main`:**
   - Pull latest changes: `git pull`
6. Check for uncommitted changes (`git status`). If there are changes, ask the user if they want to stash them, commit them, or abort
7. Create and switch to the new branch: `git checkout -b <branch-name>`
8. Push the branch to set upstream: `git push -u origin <branch-name>`
9. Confirm the branch was created and is tracking remote
