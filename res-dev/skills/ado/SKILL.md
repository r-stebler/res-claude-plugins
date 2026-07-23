---
name: ado
description: Use when the user wants to view, list, or search Azure DevOps Boards work items in the current project — by ID, "my open items", or a text search — without leaving the terminal. Azure DevOps (az boards) counterpart of the jira skill.
---

# Azure DevOps Work Item Quick Access

When the user types `/ado`, interpret the arguments to perform one of the actions below, using the Azure CLI (`az boards`).

## Resolve project context

These values are project-specific — never hardcode them. Resolve them before any `az boards` call:

1. **`.claude/azuredevops.json`** in the current project (if present) provides `org` and `project`, and optionally `areaPath`, `iterationPath`, `workItemType`, `defaultParent`.
2. **Otherwise, infer from the git remote:** run `git remote -v` and parse the Azure DevOps remote.
   - SSH: `git@ssh.dev.azure.com:v3/<org>/<project>/<repo>`
   - HTTPS: `https://<org>@dev.azure.com/<org>/<project>/_git/<repo>`
   - **URL-decode** the project (`Web%20Platform` → `Web Platform`).
   - Briefly confirm the resolved `org` / `project` with the user.
3. **Otherwise (nothing inferable):** ask the user for the organization and project.

**If the values did not come from `.claude/azuredevops.json`, offer to create it** (with the resolved `org`, `project`) so future runs are instant — only write the file after the user agrees.

Use the resolved `<org>` / `<project>` in place of the placeholders below. Pass them on every call as `--org https://dev.azure.com/<org> --project "<project>"` (or once via `az devops configure --defaults`).

## Authentication

Relies on the existing `az` session (`az account show`). If a `az boards` call fails with an auth error ("Before you can run Azure DevOps commands…" or TF400813), tell the user to run `az devops login` (paste a PAT with **Work Items: Read/Write**) or `az login` — do not attempt to store credentials yourself.

## Usage patterns

### No arguments → my open work items
```
az boards query --org https://dev.azure.com/<org> --project "<project>" \
  --wiql "SELECT [System.Id],[System.WorkItemType],[System.Title],[System.State] FROM WorkItems WHERE [System.TeamProject]=@project AND [System.AssignedTo]=@Me AND [System.State] NOT IN ('Done','Closed','Removed','Cut') ORDER BY [System.ChangedDate] DESC"
```
Display as a compact table: ID | Type | Title | State.

### A number → show work-item details
```
az boards work-item show --id <id> --org https://dev.azure.com/<org>
```
Show: Title, Type, State, Assignee, Area, Iteration, Parent, Description, Acceptance Criteria. Fields are **HTML** — strip tags to plain text for the terminal.

### Free text → search by title
Use a WIQL query with `[System.Title] CONTAINS '<text>'` (add `[System.WorkItemType]`, `[System.State]` filters if the text implies them). Display as a compact table: ID | Type | Title | State | Assignee.

## Output format
- Clean markdown table, concise and scannable.
- Always include a clickable link per item: `https://dev.azure.com/<org>/<project-url-encoded>/_workitems/edit/<id>`.
- If no results, say so clearly.
- Communicate in the same language the user is using (German or English).
