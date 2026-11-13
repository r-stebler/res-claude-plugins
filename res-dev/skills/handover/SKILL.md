---
name: handover
description: Hand finished implementation work over to the user — run the tests, auto-review the branch at the depth of its risk tier, sort the findings by the project's ticket threshold, apply the in-branch fixes, and write the handover note. Use when implementation is done, before the user's manual test (tier M/L) or before the PR (tier S).
argument-hint: "[S|M|L]"
---

Close an implementation with a deterministic gate: green tests, an independent review, a handover
the user can act on. Defects in the changed code are fixed right away, one commit each; everything
that needs a decision (ticket candidates, closed findings, fixes that outgrow the guardrails) stays
with the user.

## Steps

1. **Tier.** From `$ARGUMENTS`; otherwise the tier stated at the start of this task; otherwise ask.
   Review level: S → `low`, M → `medium`, L → `high`.
2. **Scope.** Resolve the default branch `<base>` (`git symbolic-ref --short refs/remotes/origin/HEAD`,
   strip `origin/`). Look at `git status` and `git diff --stat <base>...HEAD`. Nothing changed → stop.
3. **Tests.** Run the project's test command for the touched area (CLAUDE.md / Makefile /
   package.json). Red → stop and report the failure with output. No review on red tests.
4. **Auto-review.** Invoke the `code-review` skill with the level first, then the target: the current
   branch when the work is committed, no target when it is only in the working tree.
   Pass nothing else — no summary, no hypothesis, no "focus on". The review must not be anchored on
   the implementer's view.
5. **Sort the findings** — each one into exactly one bucket:
   - **Fix in this branch** — a defect in the changed code: wrong result, broken contract, missing
     test for new logic. Name the fix in one line.
   - **Ticket candidate** — outside this change's scope and meets the project's ticket threshold
     (e.g. "When a finding earns a ticket" in the project CLAUDE.md). Name the criterion it meets.
   - **Closed** — everything else, one line of rationale each. No "someday" bucket.
   Verify each finding against the code before sorting; a finding that does not hold is Closed with
   "does not hold: <why>".
6. **Apply the in-branch fixes** — each *Fix in this branch* finding, one at a time:
   - Implement the fix, with a test when the finding is "missing test" or the fix adds logic.
   - Run the tests of the touched area. Green → commit this fix alone (message names the finding),
     so the user can revert a single fix with `git revert <sha>`. Work still uncommitted (review ran
     on the working tree) → leave the fix uncommitted too and list it without a sha.
   - **Guardrails — do not fix, move the finding to "Needs decision" instead** when the fix
     - touches a file outside `git diff --stat <base>...HEAD`,
     - grows beyond ~30 changed lines,
     - needs a choice between approaches rather than a correction, or
     - leaves the tests red (undo the attempt first: `git checkout -- <files>`).
   After the last fix, run the full test command once. Red → stop and report with output.
7. **Handover note** — terse, in the user's language:

```
**Tier:** <S|M|L> — <reason>
**Changed:** <1-3 bullets>
**Tests:** <command> → <result>
**Deviations from plan:** <none | list>

**Auto-review (<level>)** — <n> findings
Fixed:               1. <file:line> — <finding> → <fix> (`<sha>`)
Needs decision:      2. <file:line> — <finding> → <proposed fix> (<guardrail that stopped it>)
Ticket candidates:   3. <file:line> — <finding> (criterion <n>)
Closed:              4. <one line> · 5. <one line>

**Please test:** <concrete steps: URL / click path / command, expected result>
```

   Number findings globally so the user can answer "revert 1, do 2".
8. **Stop.** Wait for the user. They may revert an applied fix (`git revert <sha>`), pick findings from
   *Needs decision* (apply, rerun the tests), or reopen a closed one. Then record the PR line:
   `<level> · <n> findings · <n> fixed · <n> closed (below threshold)` (git-pr uses it).
   No PR and no ticket until the user says so.
