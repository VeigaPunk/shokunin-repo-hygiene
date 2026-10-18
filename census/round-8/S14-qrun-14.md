# S14 (round 8) — differential quarantine-runner fragment

Seat S14, runner. Drove the SAME scenario matrix through all four competing
round-8 quarantine tools — `impl-01`, `impl-02`, `impl-03`, `impl-S12` — on
identical fixture fleets (gate-open: fixture bare remotes, backdated stale
scratch, pushed `.gitignore`), plus live read-only probes. Full evidence:
`results/qrun-14.json`; ~110 invocation transcripts under
`/home/vgpnk/.cache/s14-qrun/evidence/` (drivers outside the repo).

## Baseline

Selftests: impl-01 **63/63**, impl-02 **76/76**, impl-S12 **26/26** (all
rc=0); **impl-03 is RED: 9 FAIL + ABORT, rc=1** against the installed
engines (gate3 no-safe-receipt clusters, an AUTHORIZED-where-refusal-
expected case, sandbox refusal, missing record). Engine shas match the
install records.

## Matrix verdicts (evidence: matrix*.tsv + logs/)

- **Positive flows**: all four complete pushed and stale end-to-end where
  their gate design allows it. impl-02/03 authorize untracked stale scratch
  ONLY when it is ignored (pushed `.gitignore` makes it porcelain-invisible);
  otherwise gate2 refuses every `??` candidate — the SKILL.md plain-mv flow
  is unreachable for them without that precondition.
- **Mid-hold receipt-break** (live-ref injected during hold): caught by 3/4
  — impl-01 ABORTs and retains the copy; impl-02 verify FAILs
  (`stale-not-reverified`) and retire refuses; impl-S12 check FAILs
  (`live-refs=1`, rc=5), refuses release, and `restore` returns the bytes.
  Unreachable for impl-03 by construction (see gate2 point).
- **Origin-path recreation before release**: caught by 3/4 — impl-02
  `gate2-regressed`, impl-03 `original-reappeared`, impl-S12
  `origin-recreated`. **impl-01 misses it**: second check prints
  `pin=ok mtime=ok intro-blob=ok` and DELETES anyway.
- **Dirty tracked file**: impl-01 DRY-RUN-BLOCKED (`r7-gate2 porcelain= M`),
  impl-02/03 gate2 refuse — **impl-S12 STAGED it (rc=0, receipt=pushed)**:
  its gate is engine-verdict-only and the engine pins commits, not the
  worktree. Release would permanently delete uncommitted edits. Highest-
  priority fix for any S12-based install; `restore` works as the abort.
- **Guards**: S12 `LIVE-TREE-LOCKED` fires without the allow-list even when
  `--root` is a fixture; 02/03 refuse retire without `--operator-signoff`;
  impl-03 enforces NO hold duration (instant stage→retire possible);
  **impl-02 refuses every mutating op outside tmpdir**
  (`sandbox-not-under-tmpdir`, impl-02.sh:491-494) — proven blocking on
  /home, and /tmp hit a per-user quota outage during this very round, so a
  tmpdir-sited tool is fragile exactly when /tmp is stressed
  (`TMPDIR=<fixture>` is a proven workaround).

## Selection guidance (parent's call; details in qrun-14.json)

No impl certifiable as-is. S12 skeleton is closest (hold clock + restore +
origin pin + lock) IF it gains a dirty/gate2 pre-flight and ideally a
signoff gate; 02 has the best gate hygiene + signoff + hold-min but must
drop/configure the tmpdir guard; 03 is blocked on its red selftest and a
verify-vs-retire asymmetry (verify HOLDs tracked staging forever, retire
ignores that check); 01 lacks resurrection pin, lock, and signoff.

## Runbook deltas for the gate-opening lane

1. Dirty/gate2 pre-flight is mandatory before any stage (S12 gap proven).
2. Second check must be class-split (confirms qrun-13 F2) AND
   resurrection-pinned; three working pin forms observed.
3. Ignored-file precondition must be stated for the untracked plain-mv flow.
4. Tracked files with scratch names classify PUSHED by the engines (receipt
   priority) — "tracked stale" scenarios exercise the pushed second check.

Live probes (dry-run/check only, both engines + all four impls on
`kotodama-shokunin/.scratch` and `results/.write-probe`): every impl
refused; consistent with r7. Mutation proof: probed files byte-identical
before/after; porcelain movement during the window is sibling-seat traffic
(`r31-check-2.json`, `final-24.json`, `dissent-24.md`) with zero s14
fingerprints. Claims: differential matrix EXERCISED (met); zero live
mutation by this seat (met); live gate-opening stays blocked on operator
sign-off / lane pushes / remote creation (r7 boundary unchanged).
