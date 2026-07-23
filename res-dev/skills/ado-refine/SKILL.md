---
name: ado-refine
description: Use when the user wants to restructure or refine an existing Azure DevOps Boards work item into the standard format (title, description, acceptance criteria), optionally guided by instructions. Azure DevOps (az boards) counterpart of jira-refine.
---

# Refine Azure DevOps Work Item

When the user types `/ado-refine`, fetch an existing work item and refine its content into the standard structure, updating it via the Azure CLI (`az boards`).

## Resolve project context

Never hardcode project-specific values. Resolve `org` / `project` before any call:

1. **`.claude/azuredevops.json`** (if present) provides `org`, `project` (and optional defaults).
2. **Otherwise, infer from the git remote** (`git remote -v` → `dev.azure.com`): SSH `git@ssh.dev.azure.com:v3/<org>/<project>/<repo>` or HTTPS `https://<org>@dev.azure.com/<org>/<project>/_git/<repo>`; **URL-decode** the project. Confirm with the user.
3. **Otherwise:** ask for org and project.

Relies on the existing `az` session; on an auth error tell the user to run `az devops login` (PAT) or `az login`.

## Arguments

`/ado-refine <id> [instructions]`

- **id** (required): the numeric work-item ID.
- **instructions** (optional): free-text guidance on what to change, add, or focus on.

Examples: `/ado-refine 698011` · `/ado-refine 698011 add acceptance criteria for the failure path` · `/ado-refine 512 rewrite as a bug, the description is vague`.

## Process

### 1. Fetch the current work item
```
az boards work-item show --id <id> --org https://dev.azure.com/<org> -o json
```
Read Title, Work Item Type, State, `System.Description`, `Microsoft.VSTS.Common.AcceptanceCriteria`. Fields are **HTML**.

### 2. Analyze and plan the refinement
Compare against the standard structure for the type. Refine toward brevity: short sentences, bullets over prose, no filler.

- **Story / PBI** → Description: `User story` + `Context` (+ optional `Notes`); Acceptance Criteria as an ordered list.
- **Bug** → Description: `Current` / `Expected` / `Steps`; Acceptance Criteria as an ordered list.
- **Task** → Description: objective + checklist.

Identify what's missing, vague, or bloated; tighten wordy prose into bullets. Preserve real information — restructure, don't discard. If the user gave instructions, prioritize them.

### 3. Preview the refinement
Show a before/after: current title → proposed title (only if changed), and the full proposed Description + Acceptance Criteria (rendered readable). Highlight what changed and why. Ask the user to confirm. **Do NOT update until the user explicitly approves.**

### 4. Update the work item
**Quoting:** build the HTML into shell variables with single-quoted heredocs and reference them (`--description "$DESC"`), rather than inlining — inline HTML with `"`, backticks or `$` breaks the command.
```
az boards work-item update --id <id> --org https://dev.azure.com/<org> \
  --title "<new title, if changed>" \
  --description "$DESC" \
  --fields "Microsoft.VSTS.Common.AcceptanceCriteria=$AC"
```
Author fields as **HTML**. Confirm with the ID and link: `https://dev.azure.com/<org>/<project-url-encoded>/_workitems/edit/<id>`.

## Guidelines
- **Be concise.** Short sentences, bullets over prose, no filler. Omit empty sections — don't write "N/A".
- Preserve substance — refine and restructure, don't drop useful detail (park it in Notes, kept short).
- Author fields as **HTML** (Azure DevOps rich-text), not Markdown.
- Write content in English; communicate with the user in their language (German or English).
- If the item is too vague to refine well and no instructions help, ask clarifying questions before the preview.
