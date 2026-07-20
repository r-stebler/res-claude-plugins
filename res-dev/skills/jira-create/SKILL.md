---
name: jira-create
description: Create a well-structured Jira ticket from free-text input. Transforms rough ideas into proper issues with title, user story, description, and acceptance criteria.
---

# Create Jira Ticket

When the user types `/jira-create`, transform the provided free-text into a structured Jira ticket.

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

## Process

### 1. Analyze the input
Read the user's free-text description and determine:
- **Issue type**: Infer from context:
  - **Story** — new functionality or feature (default if unclear)
  - **Bug** — something is broken or behaves incorrectly
  - **Task** — technical work, setup, maintenance, refactoring
  - **Epic** — only if explicitly requested or clearly a large initiative
- **Priority**: Infer if mentioned, otherwise default to Medium

### 2. Structure the ticket
Generate the following in **English** (code language convention). Keep it tight: short
sentences, bullet points over prose, no filler. A ticket should be scannable in seconds.

**Title**: Concise, imperative, under 80 characters. No ticket prefix.
  - Good: "Add PDF export to invoice summary step"
  - Bad: "PDF export feature" or "<projectKey>-X: User should be able to..."

**Description** in Markdown:

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

For **Bugs**, replace User Story with:
```
## Bug
- **Current:** [what happens now]
- **Expected:** [what should happen]
- **Steps:** [1 → 2 → 3]
```

For **Tasks**, use a simpler format:
```
## Objective
[One line: what and why]

## Tasks
- [ ] [Subtask]
- [ ] [...]

## Done When
- [Definition of done — one line]
```

### 3. Preview for approval
Present the structured ticket to the user in a clear preview:
- Show: Type, Title, Priority, and full Description
- Ask the user to confirm or request changes
- **Do NOT create the ticket until the user explicitly approves**

### 4. Create the ticket
Once approved, create the issue using `mcp__atlassian__createJiraIssue` with:
- `cloudId`: `<cloudId>`
- `projectKey`: `<projectKey>`
- `issueTypeName`: the determined type (Story, Bug, Task, Epic)
- `summary`: the generated title
- `description`: the full structured description in Markdown

After creation, confirm with the ticket key and link:
`<siteUrl>/browse/<projectKey>-X`

## Guidelines
- **Be concise.** Short sentences. Bullets over prose. No filler, no restating the title, no obvious context.
- Cut anything that doesn't help someone act on the ticket. Omit empty/optional sections — don't write "N/A".
- Write ticket content in English; communicate with the user in their language (German or English).
- Acceptance criteria: specific, testable, one line each — avoid vague items like "works correctly". Aim for 3-5, not more.
- If the input is too vague for good acceptance criteria, ask clarifying questions before the preview.
