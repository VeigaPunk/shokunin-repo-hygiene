# Round 8 — gate record
Declared: O1 (quarantine flow as a tested tool), C1 (pointer integrity),
K1 (gate-opening runbook). All three verified; round ADMITTED.

## What landed

- tools/souji-quarantine.sh = impl-01 (sha 5780ad75…), 63-check selftest.
  Fail-closed: stage-1 engine authorization with receipt pinning; tracked
  files use git-mv, untracked plain mv; hold window; class-aware second
  check (stale binding on the quarantined copy; pushed/obsidian re-derived
  against original context via intro-blob digest + unpushed-touching +
  quarantine-bytes identity); delete only on PASS, else ABORTED with the
  copy kept. Live-fleet mutations refused (exit 4) without an explicit
  env override.
- The full flow is now EXERCISED on fixtures: DELETED / ABORTED /
  NOT-AUTHORIZED / SKIPPED / DRY-RUN-PASS+BLOCKED all demonstrated —
  the r6/r7 UNEXERCISED flag flips (SKILL.md/AGENTS.md note due next
  content edit).
- 96-row approval list dry-run: all 96 DRY-RUN-PASS, zero mutations —
  the day the operator signs, the command is one line (runbook).

## Findings

- Host /tmp hit DISK QUOTA mid-round; fixture runs corrupted (two seat
  failures traced to it, not to impls). Workaround TMPDIR=/var/tmp.
  The /tmp hygiene queue (2,100+ dirs) is now host-critical — escalated
  in the runbook.
- r7's "gate2 contradiction" dissolved: impl-01's dirty gate is
  tracked-only; untracked stale (.log) flows DRY-RUN-PASS. (.tmp was
  never a scratch class — taxonomy misunderstanding, not a defect.)
- Parent bug caught in verification: awk unquoted variable produced
  empty receipt pins — fixed; lesson: pin lists get schema-validated
  before use (the tool DID refuse the malformed rows — fail-closed
  worked).
- Pointer sweep: 111 tokens, 95 alive; 1 dead pointer confirms the r7
  correction; 1 drift recorded.
