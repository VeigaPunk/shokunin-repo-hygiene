# Round 97 — verifier spot-check (non-author)

author: hyaku closure (non-author integrator, @m_zfl)

Lane: souji-shokunin. Lane base `210084b24de1dd1f1fd499f49b0c70744f099f5f`,
lane final `ff254387005e35ff442555451374ff079dafc2db`. Date: 2026-11-09.

## 1. Step-1 conformance

- Report `.ufo/reports/round-97/souji.md` committed in the fleet repo by the
  lane identity: `git log --format='%an %H' -1 -- .ufo/reports/round-97/souji.md`
  → `souji-shokunin ad0ff871a674e6c61b451851173edad32d8d83db`. Pass.
- `SHONEN` heading present with one `[~]` line per box (4 boxes). Pass.
- Lane base is an ancestor of the lane final:
  `git -C souji-shokunin merge-base --is-ancestor 210084b2… ff254387…` → yes;
  `ff254387…` is the ancestor of `master` (`merge-base --is-ancestor … master`
  → yes). Every cited lane commit exists (`053287d4`, `677a6cbb`, `5314d01d`,
  `fd0be377`, `ff254387` in the `210084b2..ff254387` log). Pass.
- Lane repo state (`scripts/hyaku/jj-lane.sh state`): `ahead=0 behind=0`,
  `git status --porcelain` empty, HEAD `ff254387…` == remote
  `refs/heads/master`. No uncommitted round work. Pass.
- Prompt `.ufo/prompts/souji-round-97.md` carries the template contract
  (MISSION/AXES binding, 1–3 claims, frontier step, L2 floor, report contract,
  commit/push scope, §6 hyaku addendum). Pass.
- Not a marker report: real committed work is cited throughout. Status `ok`.
- Prefile falsification ledger (re-run after the report exists):
  `python3 scripts/hyaku/prefile-falsification.py --lane souji --round 97` →
  `PREFILE-FALSIFICATION: pass claims=2 rows=16 attack_seats=8 findings=0`,
  exit 0. (The lane's pre-report run showed `SETUP findings=1` with only the
  report-missing finding; the ledger rules themselves passed.)

## 2. Per-claim re-check

### C1 — calibration 7: RERAISE-aware pending-clear latch keeps the 14-shape
### declared-exit table at `mismatched=0`

Lane's own verdict: **harmed (trade)** — the latch regresses `q1q` (caught at
module, then a direct terminating `helper()`) from 70 to 1 and leaves `q1o`
(saved exception re-raised by bare `raise`) at 1. Not admitted; score stays 7.

**Re-measured by the verifier** (plain measurement over committed bytes,
work dirs under `/fast/scratch/hyaku/souji-r97-closure/` — the script refuses
a `/tmp` work dir, `SHAPES-FATAL: --work under /tmp`):

```
mkdir -p /fast/scratch/hyaku/souji-r97-closure/w1 /fast/scratch/hyaku/souji-r97-closure/w2
python3 -B census/round-97/declared-shapes.py --search census/round-97/c1-survivor-search.py --scripts census/round-97/shapes --work /fast/scratch/hyaku/souji-r97-closure/w1 | tail -1
  → SHAPES-SUMMARY shapes=14 mismatched=0            (r97 hook, EXIT 0)
python3 -B census/round-97/declared-shapes.py --search census/round-96/c1-survivor-search.py --scripts census/round-97/shapes --work /fast/scratch/hyaku/souji-r97-closure/w2 | tail -1
  → SHAPES-SUMMARY shapes=14 mismatched=2            (r96 hook, EXIT 1)
```

Matches the reported before→after and the committed
`census/round-97/controls/shapes-r97.txt` / `shapes-r96.txt` (x1/x2 MISMATCH
at 1 under r96, all 14 ok under r97).

**Trade evidence-verified** (not re-executed — the verifier does not run the
lane's reproducer suite; committed receipts reviewed in
`census/round-97/wave-evidence/w1/R97ReviewerC1.md` Q1): `q1q.py` plain 1,
r97 hooked 1 (no marker), r96 hook 70; `q1o.py` plain 1, r97 hooked 1,
want 70. Both receipts committed alongside the reviewer report. The
shipped knowledge entry `crash-channels-beyond-excepthook.md` carries an
appended r97 correction (A9, A11) withdrawing the falsified closure sentence.

Verdict: the claim as stated (table 2→0) re-verifies, but the claim does not
verify as an axis-move: **harmed** — a real regression on q1q, named by the
lane itself. The lane's honest-stop call is correct.

### C2 — operability 8: r97 probe caps output; r97 counter reaps the T1
### setsid grandchild by argv identity, printing `survivors=0`

Lane's own verdict: **not admitted** — the reap SIGKILLs own-uid processes
the counter did not plant (a PROVINCE refusal-boundary violation), so the
claim cannot verify.

**Evidence-verified** (committed receipts reviewed; the verifier did not
re-execute the arms counter — it signals own-uid processes by argv, and the
finding is precisely that it over-signals):

- `census/round-97/wave-evidence/w1/R97Sentinel/repro_foreign_pid_kill.out`:
  "FOREIGN decoy pid 2790887 state after the counter run: ZOMBIE(SIGKILLed)";
  the T1 line shows `survivors=0` in the same run.
- `census/round-97/wave-evidence/w1/R97Sentinel/continuous_decoy_42_planted.out`:
  "decoys planted: 42 ; NOT alive after the counter run: 30".
- Sentinel Finding 1 (HIGH): "The counter SIGKILLs own-uid processes it did
  not plant."
- Forgery controls (committed `census/round-97/wave-evidence/w1/R97ExecC2.md`
  §1 / `forgery-ctl-out/`): GA/GB/GC refused, GD `refused=no`,
  `C2-FORGERY-CTL-SUMMARY forgeries=4 refused=3` — the GD result falsifies
  the prereg `refused=4` (A14). The hang leg (r95 probe `ARM T1 exit=hung`,
  conform 19 → r97 probe `ARM T1 exit=2`, conform 20, `ARMS-SUMMARY
  arms=20 conform=20`) is present in the same receipts.

The shipped knowledge entry `deadline-owned-reaping.md` carries an appended
r97 correction (A12, A13) withdrawing the "signals only processes it planted"
sentence and routing the r98 repair (ownership by recorded spawn pid and ppid
chain, Q174 decoy test).

Verdict: the hang leg re-verifies from the receipts; the reap leg is a
measured ownership harm. The claim as declared cannot verify: **not
admitted** — and the lane's honest-stop call is correct.

### C1 no-harm leg (not a claim)

278 generated mutants under r97 vs r96 search: `SEARCH-SUMMARY generated=278
ambiguous=9 uncompiled=0 hung=1 scored=268 errored=53 killed=139 survived=76`,
0 verdict differences, byte-identical survivor sets
(`R97ExecCensus.md`; `survivors-r97.json` vs `survivors-r96.json` in the
committed wave evidence). Evidence-verified, not re-run.

### Owned-axis harm check

`git -C souji-shokunin diff 210084b2… ff254387… -- SCORECARD.md`: additive
only — the `### Round 97 measurements` table, `### Planned (r98)`, and the
"no owned axis score changed" note. Scores unchanged: calibration 7,
operability 8, coverage 8. No axis is harmed in the ledger; both harms were
caught by the wave and the claims withdrawn in-round, with the corrections
appended to the shipped knowledge entries.

## 3. Per-axis verdicts

| axis | verdict | evidence |
|---|---|---|
| calibration | harmed | C1 latch 14-shape table 2→0 re-verified, but q1q (caught-then-terminating) regresses 70→1 and q1o is still declared; lane withdrew the claim (A9). Score stays 7. |
| operability | harmed | C2 hang leg measured (conform 19→20) but the reap SIGKILLs foreign own-uid processes (sentinel, HIGH) and forgery GD is not refused; lane withdrew the claim (A12). Score stays 8. |
| coverage | unchanged | no coverage surface moved; registry 293→294; no frontier row moved. Score 8. |

Both claims were honest stops: scored as `harmed` on their axes (as the lane
did), not `unprovable`, because the harms are measured. No claim is admitted.

## 4. Discernment spot-check (LEARNING.md)

| item | decision | re-opened source | agree/disagree | reason |
|---|---|---|---|---|
| S372 sys.monitoring RERAISE row (tier A) | admit | `gordon — https://docs.python.org/3/library/sys.monitoring.html`, capture `census/round-97/srcs/monitoring.html` sha256 `2b281793…`, re-fetched live 2026-11-09 | agree | The 13-word quote ("An exception is re-raised, for example at the end of a finally block.") is in the committed capture and the byte-identical live page (both 74653 bytes, identical `diff -q`, single occurrence of the RERAISE passage). The row's scope note correctly limits the tier to the entry's one-sentence definition. |
| write(2) EAGAIN errno candidate | reject (by the lane; scout had admitted tier A for the errno clause only) | `R97ScoutSources.md` §6–7; lesson §Gate and §Frontier notes | agree | The candidate was opened this round and recorded as a lead rather than silently appended; the deferral to r98 is a curation-honesty signal (the lane did not take what it could not yet ground). |
| Census / row counts | — | `grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md` → 294 at tip, 293 at lane base (`git show 210084b2…:corpus/SOURCES.md`); `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` → `souji ok`, exit 0 | agree | 293 → 294 with S372 added, no other row touched. W04 duplicate-URL warnings pre-date the round (including S365/S372 sharing the docs page across scopes — allowed: tier is scope-scoped). |

## 5. Trend verdicts

- **expansion: unchanged** — one tier-A row (S372) and two knowledge
  sections; no admitted entry on uncovered coverage-map ground. Registry
  293 → 294. Agrees with the lane.
- **quality: harmed** — two knowledge entries shipped sentences the wave
  falsified (the "closes the trade" sentence in
  `crash-channels-beyond-excepthook.md`, the "signals only processes it
  planted" sentence in `deadline-owned-reaping.md`); both are corrected by
  appended notes this round, but the shipped text was wrong. Agrees with the
  lane.
- **discernment: harmed** — the pre-freeze gate missed three overclaims
  (C1 closure, C2 ownership, the GD forgery number) that the wave's
  reviewer, critic, sentinel and scribe found; the disagreements became
  Mistakes M1–M5 and QUALITY criteria Q173/Q174. The disagreements were
  absorbed into the lane's own quality bar rather than silenced. Agrees with
  the lane.

## 6. Routed defects for the lane (fix next round)

1. **r98 C1 successor (calibration).** Replace the pending-clear latch with a
   latch keyed on the exception object's own state (no global pending flag);
   add q1i, q1o, q1q and the no-free-tool-id fallback to the shape table;
   restore a traceback print after the marker write. Predicate and ownership
   are already in the lane's `### Planned (r98)`; Q173 is the gate. (Plans
   A9, A11.)
2. **r98 C2 successor (operability).** Ownership by recorded spawn pid and
   ppid chain, never argv-only; add the committed decoy test (Q174) that
   plants a foreign token-carrier after the arm starts and asserts it
   survives; a counter-mutant test for CM8 (a broken counter must not give
   the r96 probe 20/20). Until then the reap stays disabled or
   operator-approved. (Plans A12–A15.)
3. **L0 question, operator decision.** "souji | round-97 | C2 counter reap
   kills own-uid processes it did not plant…" is open. The lane routes around
   it; the operator owns the decision whether the reap may keep any form
   before r98 lands. Not an admission input for this round.
4. No routed cross-lane defect: the connector seat found no sibling owns the
   crash-sentinel or probe-timeout surface.
