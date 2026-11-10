---
name: git-pr
description: Create a pull request for the current branch. Offers to commit and push uncommitted changes first.
disable-model-invocation: true
argument-hint: []
---

Create a pull request for the current feature branch.

## Steps

1. Resolve the default branch `<base>`: `git symbolic-ref --short refs/remotes/origin/HEAD`
   (strip `origin/`); if unset, `gh repo view --json defaultBranchRef -q .defaultBranchRef.name`.
2. Check the current branch. If on `<base>`, stop — PRs come from feature branches.
3. Check `git status` for uncommitted changes (staged, unstaged, untracked).
4. **If there are uncommitted changes:** show them and ask whether to commit and push first.
   - Yes → follow the git-commit flow (stage explicit paths, compose message, confirm, commit, push)
   - No → create the PR from the already-pushed commits only
5. If the branch is not pushed, `git push -u origin <branch>`. If it is behind/ahead, push first.
6. Analyse the branch: `git log <base>..HEAD --oneline` and `git diff <base>...HEAD`.
7. Compose title and body:
   - Title: under 70 characters, descriptive; include the ticket key if the branch name carries one
   - Body:

```
## Summary
<1-3 bullet points summarizing the changes>

## Risk tier
<S|M|L> — <one-line reason>

## Auto-review
<level> · <n> findings · <n> fixed · <n> closed (below threshold)

## Test plan
<checklist of testing steps>
```

   - **Risk tier** and **Auto-review** are mandatory (see "Risk tiers" in the global CLAUDE.md).
     Take both from the `handover` run on this branch. If there was none — no tier stated, no
     auto-review — ask the user instead of guessing or omitting the section.

8. **Show the proposed title and body and ask for confirmation.**
9. `gh pr create --title "..." --body "$(cat <<'EOF' ... EOF)"`
10. Return the PR URL.

## Sandbox

`git push` and `gh` need the sandbox disabled (osxkeychain); otherwise `gh auth status` reports
"invalid" even though the login is fine. A `--body-file` written under `$TMPDIR` in a sandboxed run
is invisible to a non-sandboxed `gh` — pass the body via heredoc, or write it outside `$TMPDIR`.
