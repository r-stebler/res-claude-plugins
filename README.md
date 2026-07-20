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
    git-branch/  git-commit/  git-pr/  git-pr-review/
    jira/  jira-create/  jira-refine/
```

To add another domain later (e.g. `res-admin`): create a new top-level folder with its own
`.claude-plugin/plugin.json` + `skills/`, then add one entry to `marketplace.json`.

## Install (local dev, this machine)

```
/plugin marketplace add ~/res-claude-plugins
/plugin install res-dev@res
```

Verify with `/plugin` (res-dev enabled) — skills then appear as `res-dev:jira`, `res-dev:git-commit`, …

## Sync to another machine

Preferred end-state: push this repo to a **private git remote**, then on any machine:

```
/plugin marketplace add <git-url-of-this-repo>
/plugin install res-dev@res
```

Pull updates later with `/plugin marketplace update res`.
(Local-path installs work too, but a git URL syncs cleanly across machines.)

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
