---
name: jira
description: Quick access to Jira tickets in the current project. Search, view, and list issues without leaving the terminal.
---

# Jira Quick Access

When the user types `/jira`, interpret the arguments to perform one of the following actions.

## Resolve project context

These values are project-specific — never hardcode them. Resolve them before any Jira call:

1. **`.claude/jira.json`** in the current project (if present) provides `projectKey` and, optionally, `cloudId` / `siteUrl`.
2. **Otherwise, infer & discover:**
   - `projectKey`: match `[A-Z][A-Z0-9]+-\d+` in the current git branch (`git branch --show-current`) or recent commits (`git log -20 --oneline`); take the issue-key prefix.
   - `cloudId` + `siteUrl`: call `mcp__atlassian__getAccessibleAtlassianResources` — one accessible site → use its `id` (cloudId) and `url` (siteUrl); multiple → pick the one whose projects include `projectKey`, else ask.
   - Briefly confirm the resolved project key / site with the user.
3. **Otherwise (nothing inferable):** ask the user for the project key (and site if ambiguous).

**If the values did not come from `.claude/jira.json`, offer to create it** (with the resolved
`projectKey`, `cloudId`, `siteUrl`) so future runs are instant — only write the file after the user agrees.

Use the resolved `<projectKey>` / `<cloudId>` / `<siteUrl>` in place of the placeholders below.

## Usage Patterns

### No arguments → Show my open tickets
If no arguments are provided, search for all open issues assigned to the current user:
- JQL: `project = <projectKey> AND assignee = currentUser() AND statusCategory != Done ORDER BY updated DESC`
- Display as a compact table: Key | Type | Summary | Status | Priority

### Ticket key → Show ticket details
If the argument looks like a ticket key (e.g. `<projectKey>-1` or just `1`):
- Fetch the full issue details
- Show: Summary, Status, Priority, Assignee, Description, and recent comments
- If only a number is given, prepend `<projectKey>-`

### Search query → Search issues
If the argument is free text (e.g. `open bugs`, `setup`, `in progress`):
- Use Rovo search or JQL to find matching issues in `<projectKey>`
- Display results as a compact table: Key | Type | Summary | Status | Assignee

## Output Format
- Present results in a clean markdown table
- Keep output concise and scannable
- Always include clickable links to tickets: `<siteUrl>/browse/<projectKey>-X`
- If no results are found, say so clearly
- Communicate in the same language the user is using (German or English)
