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
| M3 | a handler that NARROWED a pid source opened an orphan window: W2 replaced the base's `local pid=${CLI_PID:-${!:-}}` with `local pid=${CLI_PID:-}`, so a signal between `timeout … &` and `CLI_PID=$!` (4.07 ms on the real tool) ran the handler with an empty pid: it printed `stopped it, no verdict` and exited 143 with the CLI subtree alive. The stated rationale ("`$!` … is never the timeout pid here") was false — `:290` is the tool's only background launch — and the prereg's stated limits excluded only the windows before the traps arm and after `wait`, not this one | A/B on the committed bytes, 150 iterations: base 0 orphans, W2 1 (`.ufo/waves/round-82/w1/S82Sentinel.md` F-1) | the prereg's own reading-based rationale, which was the thing that needed a probe; Q70's pre-freeze leg tested the rows, not the handler's pid source | repair R1 restores the base expression before filing, and the frozen 16 rows + selftest + r17 + probe D re-pass on the repaired bytes (`census/round-82/records/repair-w3/`). New rule: a handler change that narrows where a pid comes from gets an A/B that forces the source empty, before the freeze |
| M4 | a prereg sentence named a branch order the bytes do not implement, and a second new branch was dead code: the frozen text said `_owntree_ok` runs BEFORE the basename test (it runs after, `:349` then `:353`) and attributed PF-1/NF-F/NF-G/NF-H to the census-in-tree full-suffix branch, which never fires on the frozen population (no token under `census/`) | `.ufo/waves/round-82/w1/S82Reviewer.md` LOW; `.ufo/waves/round-82/w1/S82MutCounter.md` LOW M08; `.ufo/waves/round-82/w1/S82CriticClaims.md` MEDIUM; `.ufo/waves/round-82/w1/S82Connector.md` F2 | Q146's grounding rule covers *which rows* a rule keeps, not *which branch* delivers the verdict; the W1 code comment at `:368` restated the wrong order, and one discernment seat then re-asserted it from the comment rather than from the code | amendments A1/A3 in `plans/round-82.md`; Q150 records the corrected order. New rule: a prereg sentence that names a branch order or a rule's identity ships with a one-line truth-table receipt taken from the bytes in the same commit |
| M5 | the round's own-tree rule binds shapes only the harness plants: `CAPTURE` accepts `waves/` or `wave/` or `records/wave-<w>/`, and the lane's real wave trees are `w1` (65), `w2` (19), `w3`, `a2w1` — none named `waves/` — so a genuine own-tree move into a real `wN/` dir is REFUSED while the harness's symmetric `waves/a2w1/` fixture is kept: stricter than r81 for the real shape and looser for the planted one | `.ufo/waves/round-82/w1/S82Connector2.md` F1/F5 (MEDIUM/LOW); L1 truth table in `plans/round-82.md` A2 | Q146 requires real rows for the shapes a rule KEEPS, and the population had no own-tree true row at all — the harness planted both sides | amendment A2; Q151 records the criterion (list the real directory names before naming a shape). Routed: a real own-tree move row (`wN/` and a `decoy/` sibling) is round 83's first C1 item |
| M6 | a seat's MEDIUM was nearly adopted without re-derivation: S82Connector F1 concluded "the mutant that would isolate the round's own new rule is absent" because the K-b variant is the r81 counter, two docstring lines apart — but removing `_owntree_ok` *yields* that counter, so K-b is exactly the isolation it was accused of not providing | `.ufo/waves/round-82/w1/S82Connector.md` F1 vs `plans/round-82.md` A4 and the `judge()` branch list at `census/round-82/c1-pointer-counter.py:340-371` | none in round — the wave was told to attack, and the L1 is the only reader that must re-derive a finding before adopting it | A4 adopts the provenance observation and rejects the conclusion. New rule: a seat finding that would retract a landed control is re-derived by the L1 before it enters the ledger, and the ledger row records the rejection |

## Wave

One v1 wave, 14 seats, policy `scripts/hyaku/ufo-wave-policy.json` (band 8-16): 2 connector, 2 scout, 3 executor,
2 mutation-tester, 1 reviewer, 2 critic, 1 sentinel, 1 scribe. Attack seats 8/14 (57%), over the 25% floor.
13 seats delivered a report; **1 dead seat** (S82ExecC2: 87-byte "Status: in progress" stub, no re-derivation —
C2 was independently re-derived by S82Sentinel, S82MutTool and S82Connector2, so no conjunct lost its check).
Dispatch `w1-dispatch.json`, spec `w1-spec.json`, results `w1-results.json`.

| seat | verdict |
|---|---|
| S82ExecC1 | C1 frozen predicates + all 5 regressions + K-a/K-b/K-c reproduced byte-for-byte; 0 findings. Also showed `_owntree_ok` cannot move any of the 14 real MOVED rows (all census targets) |
| S82ExecEvade | interrupt/evade surfaces: windows and refused-configuration limits named, no row can see them |
| S82Reviewer | chronology, freeze-check, C1 and C2 predicates HONOURED; 0 HIGH, 0 MEDIUM, 3 LOW; M1 confirmed by rerun |
| S82CriticClaims | C1 core delta holds; census-in-tree branch vacuous (MEDIUM); C2 holds as a launch-mode delta |
| S82CriticDiscern | S330 reject adjudicated AGREE; 6 routed defects dispositioned; re-asserted the falsified branch order |
| S82MutCounter | 6/8 mutants killed; M07/NR6 MEDIUM (suffix-only rule passes the population); NR1-NR6 new rows |
| S82MutTool | M03/M04/M06 survive the frozen rows; termign-fork and p5-late-term missing rows; m1/m2 monitor label dead |
| S82Sentinel | C2 re-derived 16/0/0/0 both launches; F-1 MEDIUM (empty-CLI_PID orphan window, a W2 regression), F-2/F-3 cost and pid-reuse, F-4/F-5 LOW; verified remediation built |
| S82Connector | cross-claim separation SEPARABLE both ways; 8 sibling `$(timeout …)` rows documented; K-b provenance; PF-1 branch dead code |
| S82Connector2 | own-tree rule UNDER-FITTED (refuses a genuine `wN/` move, MEDIUM); K-a before=4 is modal, not a floor |
| S82ScoutSources | source recon; S330 reject row's ground re-checked |
| S82ScoutPaths | path/shape recon for the carried list |
| S82Scribe | drafts only (capability row, knowledge section, quality rows) — the L1 applied the accepted ones |
| S82ExecC2 | DEAD — stub, no verdict |

## Repairs after the wave (not the claim's measurement)

R1 (W3, `tools/souji-vault-verify.sh`): restore the base's `local pid=${CLI_PID:-${!:-}}`, closing the
empty-`CLI_PID` orphan window S82Sentinel F-1 measured (base 0/150, W2 1/150) whose stated rationale the prereg had
wrong. Re-measured on the repaired bytes (`census/round-82/records/repair-w3/`, tool sha256 `dd6d440e…`): frozen
counter `rows=16 mismatches=0 errors=0 orphans=0` under the default **and** the monitor launch, `selftest: 57
checks, 0 failed`, r17 `total=37 failed=0 skipped=0`, probe D `arms=6 failed=0`. Not landed: F-2/F-3 (per-node
`pgrep -P` cost, snapshot→KILL reuse window) — a full tree-walk rewrite after the freeze would carry no row, so it
is routed with the seat's verified remediation, as are F-4/F-5.

## Routed to round 83

1. **C1 own-tree shape (first item).** Row a real own-tree move into `wN/` (kept) beside a `decoy/` sibling
   (refused) and extend `CAPTURE` to the shapes the lane actually has; Q151 is the criterion.
2. **C1 identity clause.** An own-tree flattened/short-suffix decoy row, so the population can separate the
   identity disjunct from a suffix-only rule (S82MutCounter M07/NR6).
3. **C1 census-in-tree branch.** Ground it with a real token-under-`census` row or delete it (S82CriticClaims,
   S82Connector F2).
4. **C2 tree walk.** One fork-free `/proc` ppid-map pass with kill-as-discovered, closing F-2 and F-3 together;
   the seat's verified remediation is in `S82Sentinel.md` (N=12 → 3.44 s vs 5.74-14.22 s, 16/0/0/0 both launches).
5. **C2 counter.** Fix the dead `m-` prefix test (`c2-vault-signal-counter.py:217`) so the monitor is a row
   property or delete the branch; make the settle robust under `strace` (S82Connector F6); guard `pgrep`
   (S82Connector2 F3).
6. **C2 rows.** `termign-fork` (tree KILL × forked CLI) and the reproduced `p5-late-term` row (S82MutTool).
7. **Carried from r81 section 5 item 6** (unchanged): `_regular` pathspec framing, quarantine intro-blob digest
   row, fork-tail row, r79 gate re-measurement, check-4 300 s backstop, r76 K03/K04, status-trusting lane tools,
   r17 240 s runners. The r82 wave's read-only pointers for four of them are in `S82Connector.md` §3 and are not
   a substitute for a row.
