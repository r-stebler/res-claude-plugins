---
name: ado-create
description: Use when the user wants to create a new Azure DevOps Boards work item (Product Backlog Item, Bug, Task) from a free-text description in the current project. Azure DevOps (az boards) counterpart of jira-create.
---

# Create Azure DevOps Work Item

When the user types `/ado-create`, transform the provided free-text into a structured Azure DevOps work item, created via the Azure CLI (`az boards`).

## Resolve project context

These values are project-specific — never hardcode them. Resolve them before any `az boards` call:

1. **`.claude/azuredevops.json`** in the current project (if present) provides `org` and `project`, and optionally `areaPath`, `iterationPath`, `workItemType`, `defaultParent`.
2. **Otherwise, infer from the git remote:** run `git remote -v` and parse the Azure DevOps remote.
   - SSH: `git@ssh.dev.azure.com:v3/<org>/<project>/<repo>` · HTTPS: `https://<org>@dev.azure.com/<org>/<project>/_git/<repo>`.
   - **URL-decode** the project (`Web%20Platform` → `Web Platform`).
3. **For the create-only defaults** (`areaPath`, `iterationPath`, `workItemType`, parent) not in `.claude/azuredevops.json`, learn the team convention:
   - **Find a recent item** (you rarely know an id up front): `az boards query --org https://dev.azure.com/<org> --project "<project>" --wiql "SELECT [System.Id] FROM WorkItems WHERE [System.TeamProject]=@project ORDER BY [System.ChangedDate] DESC" -o json`, take a top id, then `az boards work-item show --id <id> --query "{type:fields.\"System.WorkItemType\",area:fields.\"System.AreaPath\",iteration:fields.\"System.IterationPath\",parent:fields.\"System.Parent\"}"`.
   - **List areas** if unsure: `az boards area project list --org https://dev.azure.com/<org> --project "<project>"`.
   - **Iteration:** do **not** copy a past item's sprint — use the team's *current* iteration (or ask the user).
   - **Fallback** (read denied / no items / offline): use the **project root** for area & iteration, leave **parent** unset, and tell the user these are placeholders to confirm — never silently guess a sub-area or sprint.
   - **workItemType** default = `Product Backlog Item` if nothing suggests otherwise.
   - Confirm the resolved area / iteration / type / parent with the user before creating.

**If the values did not come from `.claude/azuredevops.json`, offer to create it** (with the resolved `org`, `project`, and the confirmed `areaPath` / `iterationPath` / `workItemType` / `defaultParent`) so future runs are instant — only write the file after the user agrees.

## Authentication

Relies on the existing `az` session. On an auth error, tell the user to run `az devops login` (PAT with **Work Items: Read/Write**) or `az login`.

## Process

### 1. Analyze the input
- **Work item type**: `Product Backlog Item` / `User Story` (new functionality — default), `Bug` (something broken), `Task` (technical/maintenance work). Match the type used by the team (from step 3 above). **Tie-breaker:** if the work has testable acceptance criteria, prefer PBI/User Story even for technical/infra work; reserve `Task` for simple work without criteria.
- **Parent**: link to the feature/epic in `defaultParent` (or the parent of a sibling item) unless the user says otherwise.

### 2. Structure the work item
Write content in **English** (code-language convention). Keep it tight: short sentences, bullets over prose, scannable in seconds.

**Title**: concise, imperative, under 80 characters. No ID prefix.

**Description** and **Acceptance Criteria** are separate **HTML** fields in Azure DevOps (`System.Description` and `Microsoft.VSTS.Common.AcceptanceCriteria`) — author them as small HTML, not Markdown.

Description (Story/PBI):
```html
<b>User story.</b> As a [role], I want [goal], so [benefit].<br><br>
<b>Context.</b> [Why now / current gap — one or two lines.]<br><br>
<b>Notes.</b> [Optional: constraint, link, edge case. Omit if none.]
```
Acceptance Criteria (Story/PBI and Bug):
```html
<ol><li>[Testable, one line]</li><li>[...]</li></ol>
```
For a **Bug**, replace the description body with:
```html
<b>Current.</b> [what happens now]<br><b>Expected.</b> [what should happen]<br><b>Steps.</b> [1 → 2 → 3]
```
For a **Task**, use a simple objective + checklist in the description and omit Acceptance Criteria.

### 3. Preview for approval
Present Type, Title, Area/Iteration, Parent, Description and Acceptance Criteria. Ask the user to confirm or change. **Do NOT create the work item until the user explicitly approves.**

### 4. Create the work item
**Quoting:** build the HTML Description/AC into shell variables with single-quoted heredocs and reference them (`--description "$DESC"`) instead of inlining — inline HTML with `"`, backticks or `$` breaks the command. Prefer `&quot;` over a literal `"` inside field HTML.
```
DESC=$(cat <<'EOF'
<html description>
EOF
)
AC=$(cat <<'EOF'
<html acceptance criteria>
EOF
)
az boards work-item create \
  --title "<title>" --type "<workItemType>" \
  --org https://dev.azure.com/<org> --project "<project>" \
  --description "$DESC" \
  --fields 'System.AreaPath=<areaPath>' 'System.IterationPath=<iterationPath>' "Microsoft.VSTS.Common.AcceptanceCriteria=$AC" \
  --query id -o tsv
```
- **AreaPath includes the project as its root** (e.g. `Web Platform\Webshop Team`). Quote values with backslashes in single quotes.
- Then link the parent (if any):
```
az boards work-item relation add --id <newId> --relation-type parent --target-id <parent> --org https://dev.azure.com/<org>
```
Confirm with the new ID and link: `https://dev.azure.com/<org>/<project-url-encoded>/_workitems/edit/<newId>`.

## Guidelines
- **Be concise.** Short sentences, bullets over prose, no filler. Cut anything that doesn't help someone act on the item. Omit empty sections — don't write "N/A".
- Author fields as **HTML** (Azure DevOps rich-text), not Markdown.
- Acceptance criteria: specific, testable, one line each; aim for 3–5.
- Write content in English; communicate with the user in their language (German or English).
- If the input is too vague for good acceptance criteria, ask clarifying questions before the preview.
