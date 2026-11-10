# res-claude-plugins

Personal, private Claude Code plugins — available across all my projects, not imposed on teammates.

This repo is a **plugin marketplace**. Claude Code loads plugins by registering this repo
as a marketplace (local path or git URL); it does not load anything by mere folder location.

## Structure

```
.claude-plugin/marketplace.json   # marketplace manifest, lists the plugins below
res-dev/                          # plugin: personal development skills
  .claude-plugin/plugin.json      # plugin manifest (name "res-dev" → skill namespace res-dev:*)
  skills/
    git-branch/  git-commit/  git-pr/  git-pr-review/  handover/
    jira/  jira-create/  jira-refine/  ado/  ado-create/  ado-refine/
  hooks/
    hooks.json                    # registers bash_guard.py as PreToolUse hook on Bash
    bash_guard.py                 # blocks commits on master/main, `git add -A/.`, AI attribution
    test_bash_guard.py            # python3 -m unittest discover -s res-dev/hooks
```

## Hooks

Hooks are active as soon as the plugin is enabled — in every project. `bash_guard.py` blocks
(exit 2, reason shown to Claude):

- `git commit` on `master`/`main` — follows `git -C` and a preceding `cd`
- `git add -A|--all|.` and `git commit -a` — the sandbox stages `.env*` as deleted
- AI attribution (`Co-Authored-By: Claude`, "Generated with Claude Code") in commit messages and
  PR bodies, including `-F`/`--body-file`

It is a safety net, not a shell parser: anything it cannot read passes. Python 3 stdlib only.

To add another domain later (e.g. `res-admin`): create a new top-level folder with its own
`.claude-plugin/plugin.json` + `skills/`, then add one entry to `marketplace.json`.

## Delivery workflow

`handover` closes an implementation: tests → `/code-review` at the depth of the risk tier
(S low · M medium · L high, tiers defined in the global CLAUDE.md) → findings sorted into
*fix in this branch* / *ticket candidate* / *closed* by the project's ticket threshold → handover
note. `git-pr` carries tier and auto-review result into the PR body; `git-pr-review` is the extra
review for tier L and for other people's PRs.

## Install

The marketplace is installed from the git remote, not from a local checkout:

```
/plugin marketplace add https://github.com/r-stebler/res-claude-plugins.git
/plugin install res-dev@res
```

Pull updates after a merge with `/plugin marketplace update res`. Verify with `/plugin` — skills
appear as `res-dev:jira`, `res-dev:git-commit`, …

Test unmerged changes from the working copy (`~/Projects/PRIV/res-claude-plugins`):
`claude --plugin-dir ~/Projects/PRIV/res-claude-plugins/res-dev`.

## Jira skills — per-project config

`res-dev:jira`, `res-dev:jira-create`, `res-dev:jira-refine` are project-agnostic. They resolve the
target Jira context in this order:

1. `.claude/jira.json` in the current project, e.g.
   ```json
   { "projectKey": "ABC", "cloudId": "…", "siteUrl": "https://your-org.atlassian.net" }
   ```
2. Otherwise: infer `projectKey` from the git branch / recent commits (`[A-Z][A-Z0-9]+-\d+`)
   and discover `cloudId` / `siteUrl` via the Atlassian MCP; confirm with the user.
3. Otherwise: ask the user — and offer to write `.claude/jira.json` so it is remembered next time.
