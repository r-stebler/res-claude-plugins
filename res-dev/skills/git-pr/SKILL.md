---
name: git-pr
description: Create a pull request for the current branch. Offers to commit and push uncommitted changes first.
disable-model-invocation: true
argument-hint: []
---

Create a pull request for the current feature branch.

## Steps

1. Check the current branch. If on `main`, inform the user and stop — PRs should be from feature branches
2. Check `git status` for uncommitted changes (staged, unstaged, untracked)
3. **If there are uncommitted changes:**
   - Show the changes to the user
   - Ask if they want to commit and push these changes first before creating the PR
   - If yes, follow the git-commit flow (stage, compose message, confirm, commit, push)
   - If no, proceed with creating the PR from already-pushed commits only
4. Check if the branch has been pushed to remote. If not, push with `git push -u origin <branch>`
5. Check if the branch is up to date with remote (`git status` should show no ahead/behind). If behind, push first
6. Analyze all commits on this branch vs main:
   - `git log main..HEAD --oneline`
   - `git diff main...HEAD`
7. Compose a PR title and body:
   - Title: short, under 70 characters, descriptive
   - If branch name contains a ticket number, include it in the title
   - Body uses this format:

```
## Summary
<1-3 bullet points summarizing the changes>

## Test plan
<checklist of testing steps>
```

8. **Show the proposed PR title and body to the user and ask for confirmation**
9. Create the PR using `gh pr create --title "..." --body "$(cat <<'EOF' ... EOF)"`
10. Return the PR URL to the user
