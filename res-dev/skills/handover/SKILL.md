---
name: handover
description: Hand finished implementation work over to the user — run the tests, auto-review the branch at the depth of its risk tier, sort the findings by the project's ticket threshold, and write the handover note. Use when implementation is done, before the user's manual test (tier M/L) or before the PR (tier S).
argument-hint: "[S|M|L]"
---

Close an implementation with a deterministic gate: green tests, an independent review, a handover
the user can act on. The user triages the findings — this skill sorts and presents, it does not fix.

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
6. **Handover note** — terse, in the user's language:

```
**Tier:** <S|M|L> — <reason>
**Changed:** <1-3 bullets>
**Tests:** <command> → <result>
**Deviations from plan:** <none | list>

**Auto-review (<level>)** — <n> findings
Fix in this branch:  1. <file:line> — <finding> → <fix>
Ticket candidates:   2. <file:line> — <finding> (criterion <n>)
Closed:              3. <one line> · 4. <one line>

**Please test:** <concrete steps: URL / click path / command, expected result>
```

   Number findings globally so the user can answer "1 and 3".
7. **Stop.** Wait for the user's triage. Apply only the fixes they pick, rerun the tests, then record
   the PR line: `<level> · <n> findings · <n> fixed · <n> closed (below threshold)` (git-pr uses it).
   No PR and no ticket until the user says so.
