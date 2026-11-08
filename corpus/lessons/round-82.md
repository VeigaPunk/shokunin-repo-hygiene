# Round 82 — the pointer counter binds the token's own round tree and the full path suffix (C1 calibration), the vault tool kills the CLI's whole descendant tree (C2 operability)

Attempt 1 (`SoujiR82`). Lane base `488956c45166ed6edc21567e8588a8134413949e` (r81 closed `admitted`; spot-check `corpus/lessons/round-81-verifier-spotcheck.md`). Frozen claims, counters and predicates are in `census/round-82/preregistration.txt` and are not restated here.

## Inherited

The r81 verifier spot-check closed round 81 as `ok`, **admitted**, with five routed defects (`corpus/lessons/round-81-verifier-spotcheck.md` section 5) and the r81 lesson four routes (`## Routed to round 82` (a)–(d)):

- defect 1 (no reject row in the Gate) → this round's Gate carries one reject.
- defect 2 (C2 launch-mode row and descendant-tree kill) → C2 m1/m2 rows and the `cli_kill_tree` change.
- defect 3 (v9/p5/probe-D arms, stale `$!`) → v9/v10 termign rows + probe arms; p5 remains a stated limit (reading-based, needs a second mark; the wave's S81MutTool row was reading-based, not reproduced); the stale `$!` fallback removed (no frozen row held it; the L1 hunt for a deterministic probe in the rule text: the trap arms only while `wait` runs with a live CLI_PID, so dropping the fallback cannot hide a live pid — stated limit).
- defect 4 (C1 NF-F/NF-G/PF-4, M8 killer, PF-1) → NF-F/NF-G/NF-H/NF-I/PF-1 rows and the own-tree check + full-suffix order.
- defect 5 (V1 monitor settle tail; r17 240 s runners) → carried, not rows (instrument work, not claim ground).
- defect 6 (carried: `_regular` pathspec, quarantine intro-blob digest row, fork-tail row, r79 gate re-measurement, check-4 300 s backstop, r76 K03/K04, status-trusting lane tools) → carried unchanged; two of them (`_regular` path framing, intro-blob digest site) receive wave coverage only.
- route (a) C2 missing rows → taken in C2 (termign rows, probe arms, `$!` removed, interrupt-window rows remain stated limits).
- route (b) C1 → taken in C1. route (c) V1 settle tail + r17 runners → carried. route (d) carried list → unchanged.

No inherited lane leftovers (`jj-lane.sh state` at start: `local=remote=488956c4… ahead=0 tracked=0 untracked=0`). No `considerthese/` directory exists in this lane; no shokuknow theme taken (Assimilation: none).

## Gate

- **S330 candidate — procps-ng pgrep(1), process-lookup of the CLI subtree**: opened 2026-11-07 by the L1 (`/usr/share/man/man1/pgrep.1.gz`, owned by procps-ng 4.0.7-1, host roff).
  Rejected as a SOURCES row: the lane already holds S075 (proc pid/stat session/pgrp attribution) for the population of process identities, and pgrep(1)'s parent-lookup semantics (list processes whose parent is X, the mechanism `cli_kill_tree` uses) is the only new proposition. On process identity S075 governs; on the kill mechanism the row's kind/tier would be `docs/A` but the scope is one man page's prose about `-P`, which the tool itself proves by running: the C2 counter's `nonce_pids` census (S075's own ground) is the executable evidence, and the m1/m2 rows are the red-before proof. Per CORPUS rule 1 a row is opened only after its source is opened, and leaned on; this round the source is opened and the claim is leaned on, but a row is rejected because a second row for the same process-identity ground adds no expansion (CORPUS rule 4: expansion is knowledge, not rows). Flip: a future row that teaches pgrep `--oldest`/`-a` argument reporting or signal delivery (`pkill -P` scope) — not this round's mechanism.
- **Pre-freeze drafts vs committed candidates**: the C1 draft measured in `census/round-82/records/prefreeze/` (sha256 `cbfdc07c…`, the committed counter minus the prereg/docstring delta only) and the C2 draft (`d1a43e08…`, byte-equal to the committed successor counter) are the instruments as frozen at P.

## Measured

Staged commits in the order the preregistration binds: P `1cb7c7d11aaac36a1ac757f339d77875ea4b192b` (instruments,
controls, preregistration, lesson skeleton, census-before; freeze-check findings=3 — M1), F corrective `d302b4f330766f9297b8d97ff8968eae84aa1dbe` / F2 `28fd32c031ac0e87efbddb6c26da7827c9873ccd` / F3 `1ec433c6905cff283fdebbc663a5adf575b4a439`
(Control path parse fixes; freeze-check re-run in `records/freeze-check-at-P.txt`), W1 `f5bc4197d426527adc6f5d52f2d7834c0f021f2e` (C1
counter), W2 `73110f6fe56f2a8383baed0ea7dc77f8b7f6ba5e` (C2 tool), A (records), I (integration).

- C1 (frozen harness `census/round-82/c1-false-row-harness.py`, 32 rows): K-a r81 counter mismatches=2 accepted=2
  (NF-F, NF-G), K-b owntree-dropped 2/2, K-c suffix-last-component 2/2 [NF12c, NF-I] → `records/c1-after.txt`
  mismatches=0 accepted=0 refused_true=0 EXIT=0. Regressions at W1: r78 22/22 + 12/12, r77 35/35 + 7/7, r79 harness
  9/9, r80 harness 18/18, r81 harness 25/25.
- C2 (frozen counter `census/round-82/c2-vault-signal-counter.py`, 16 rows, both launches): K-a Base under
  `env SHELLOPTS=monitor` mismatches=4 orphans=4 (v7/v8 + m1/m2 `survivors=1`), K-b trap-only 12/12, K-c no-`<&0` 1
  (p3) → `records/c2-after.txt` (default) and `records/c2-after-monitor.txt` (monitor) both mismatches=0 orphans=0
  EXIT=0. Base under the default launch is 16/16 (`records/prefreeze/c2-base-default.txt`) — the bounded baseline the
  claim is deltas against. Regressions at W2: selftest 57/0, r17 37/0/0, probe D successor 6/6
  (`records/probe-d-successor.txt`).
- V1/Regressions carried: the spot-check section 5 item 6 list (carried items) stays named in the preregistration's
  V1 section; none is a row this round.


## Registry agreement

`tools/souji-registry-agreement.py` (frozen r29 instrument, `--list-rev b8cb4b31…`): at W2 `73110f6f` `k1=1 k2=1`
(`census/round-82/records/registry-agreement-at-W2.txt`). The two left are recorded accepted-red, with the r81
reasons carried: K1 `cited-no-row S146` (provenance prose, not a citation; rewriting would game the instrument) and
K2 `rewrote-not-appended SCORECARD.md` (history; not repairable without rewriting history). Flip: a successor
instrument parsing citations by `S### —` lead position, or an operator ruling on K2. K1/K2 pre-date this round
(`k1=1 k2=1` at r81 I as well).


## Mistakes

| # | class | evidence pointer | captured-by | fix |
|---|---|---|---|---|
| M1 | freeze chronology slip: the P commit (1cb7c7d) carried the preregistration file together with the controls, so the freeze-check's strict-ancestor test reports CONTROL-ADDED-NOT-BEFORE-FREEZE for both controls and FROZEN-EDITED for the prereg after F3 fixes the Control path parse | `census/round-82/records/freeze-check-at-P.txt` (SUMMARY claims=2 findings=3) | the freeze-check itself fired, but only after P landed; Q99's pre-freeze feasibility is not the same check | disclosed here and in the report; the round proceeds with digest-bound counters (every receipt binds its instrument digest), and the closure judges the chronology defect rather than a re-dated freeze; next round P holds controls only and F holds the prereg file alone |
| M2 | C2 control baseline mis-stated: the r82 counter's m1/m2 rows were expected to fail on the Base tool under the default launch, but the Base (R) tool passed them there (`records/prefreeze/c2-base-default.txt` 16/16); the leak reproduces only when the caller's environment carries job control (`SHELLOPTS=monitor` exported into the tool's shell) | `records/prefreeze/c2-base-default.txt` (mismatches=0) vs `controls/c2-K-a-do-nothing.txt` under `env SHELLOPTS=monitor` (mismatches=4) | Q70's feasibility leg (run the do-nothing candidate on the new rows before freeze) — fired | C2's target now requires green under BOTH launches; the default launch is the bounded baseline, monitor is the delta |


## Wave

(to be filled after WAVE-DONE.)

## Repairs after the wave (not the claim's measurement)

(to be filled if any.)

## Routed to round 83

(carried items from the spot-check section 5 and the lesson's own new findings, updated at A.)
