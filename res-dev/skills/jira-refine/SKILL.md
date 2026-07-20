---
name: jira-refine
description: Refine an existing Jira ticket by fetching its current content and restructuring it according to the standard ticket format, guided by optional user instructions.
---

# Refine Jira Ticket

When the user types `/jira-refine`, fetch an existing ticket and refine its content into the standard structure.

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

## Arguments

`/jira-refine <ticket-id> [instructions]`

- **ticket-id** (required): A ticket key like `<projectKey>-42` or just `42` (auto-prepends `<projectKey>-`)
- **instructions** (optional): Free-text guidance on what to change, add, or focus on

Examples:
- `/jira-refine 42` — refine ticket `<projectKey>-42` using the standard structure
- `/jira-refine <projectKey>-42 add acceptance criteria for error handling`
- `/jira-refine 15 rewrite as a bug report, the current description is vague`

## Process

### 1. Fetch the current ticket
Use `mcp__atlassian__getJiraIssue` to retrieve the full issue details:
- Summary, Description, Issue Type, Priority, Status, Comments

If only a number is given, prepend `<projectKey>-`.

### 2. Analyze and plan refinement
Compare the current ticket content against the standard structure for its issue type.
Refine toward brevity: short sentences, bullets over prose, no filler — scannable in seconds.

**Stories** should have:
```
## User Story
As a [role], I want [goal], so [benefit].

## Context
- [Why now / current gap — one line]
- [Add a line only if it adds information]

## Acceptance Criteria
- [ ] [Testable, one line]
- [ ] [...]

## Notes
- [Optional: constraint, link, edge case. Omit the section if none.]
```

**Bugs** should have:
```
## Bug
- **Current:** [what happens now]
- **Expected:** [what should happen]
- **Steps:** [1 → 2 → 3]

## Acceptance Criteria
- [ ] [Testable, one line]
- [ ] [...]
```

**Tasks** should have:
```
## Objective
[One line: what and why]

## Tasks
- [ ] [Subtask]
- [ ] [...]

## Done When
- [Definition of done — one line]
```

Identify what's missing, vague, or bloated. Tighten wordy prose into bullets. If the user provided instructions, prioritize those.

### 3. Preview the refinement
Show a clear before/after comparison:
- **Current title** → **Proposed title** (only if changed)
- **Proposed description**: the full refined description
- Highlight what was changed and why
- If the user's instructions conflict with the current issue type, suggest a type change

Ask the user to confirm or request further changes.
**Do NOT update the ticket until the user explicitly approves.**

### 4. Update the ticket
Once approved, update the issue using `mcp__atlassian__editJiraIssue` with:
- `cloudId`: `<cloudId>`
- `issueKey`: the full ticket key
- `summary`: the refined title (if changed)
- `description`: the full refined description in Markdown

After updating, confirm with the ticket key and link:
`<siteUrl>/browse/<projectKey>-X`

## Guidelines
- **Be concise.** Short sentences. Bullets over prose. No filler, no restating the title, no obvious context.
- Trim wordiness: keep the substance, drop the chatter. Omit empty/optional sections — don't write "N/A".
- Preserve real information — refine and restructure, don't discard. Useful details that don't fit go in Notes (kept short).
- Write ticket content in English; communicate with the user in their language (German or English).
- Acceptance criteria: specific, testable, one line each — avoid vague items like "works correctly". Aim for 3-5, not more.
- If the ticket is too vague to refine well and no instructions help, ask clarifying questions before the preview.
