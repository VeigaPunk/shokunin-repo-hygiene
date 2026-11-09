# Round 100 verifier spot-check — non-author closure (hyaku closure, non-author integrator)

`author: hyaku closure (non-author integrator, @m_zfl)`

Lane: souji. Lane base `a662bb0d7e033cc5ceccd70b52eb234404300845` → lane HEAD
`cbe068d03eb5a49fc0736bef89f182679a86ca51`. Report:
`.ufo/reports/round-100/souji.md` (fleet repo). Dispatch digest (`.ufo/watchdog.log`,
mutable — copied from the closure prompt):

> 2026-11-09T12:17:48-03:00 launch souji round=100 pgid=3217270 driver=hyaku-inline attempt=1
> 2026-11-09T12:26:05-03:00 lane-dead-no-report souji round=100; retry same round (hyaku-inline attempt=1: L1 ended without a landed report)
> 2026-11-09T12:26:07-03:00 launch souji round=100 pgid=3345845 driver=hyaku-inline attempt=2
> 2026-11-09T12:38:16-03:00 complete souji round=100; hyaku-inline attempt=2

This file is verifier-written only; lane-authored files (report, SCORECARD, LOG,
lessons, SKILL, PROVINCE) were not edited.

## 1. Conformance (PROTOCOL §Round-robin closure step 1)

| check | command | observed | result |
|---|---|---|---|
| report landed by lane identity | `git -C /home/vgpnk/Projects/shokunin log --format='%an %H' -- .ufo/reports/round-100/souji.md` | `souji-shokunin 17d0d29acabbef0e504485fde4bbf85c6da4e8d0` | PASS — `git log --format='%an %H' -- <report>` matches |
| SHONEN heading + 4 boxes | `grep -c 'SHONEN' report` = 1; `grep -E '^\s*-\s+\[.\]' report \| wc -l` = 4; `wc -c` = 7266 | PASS — heading present, one `[~]` line per box |
| marker vs report | — | Real committed round-work hash cited (`cbe068d0…`), work/evidence/LOG tie-outs present | PASS — report, not marker |
| cited commit ancestry (lane repo, branch ref) | `git merge-base --is-ancestor cbe068d03eb5a49fc0736bef89f182679a86ca51 master` | exit 0 | PASS |
| lane HEAD | `git -C souji-shokunin rev-parse HEAD` | `cbe068d03eb5a49fc0736bef89f182679a86ca51` | PASS |
| pushed | `jj-lane.sh state souji-shokunin` → `ahead=0 behind=0` | PASS | PASS |
| uncommitted round work | `git -C souji-shokunin status --porcelain` | empty | PASS (clean) |
| prompt contract | `grep` MISSION/claims/Sources/SHONEN/commit in `.ufo/prompts/souji-round-100.md` | canonical `templates/round-prompt.md` rendering present (##1 MISSION/AXES, ##2 claims 1–3, ##2b frontier, SHONEN, commit-order) | PASS |

No conformance defect bars admission.

## 2. Per-claim re-check (PROTOCOL §Evidence standard)

### C1 — operability: session-owned escapee reap (Q177) — **harmed**

Frozen predicate: r100 counter `ESCAPEE-ALIVE alive=0` while decoy `verdict=spared` 83/83; r99 counter `alive=1`; CM8 mutant decoy `verdict=killed`; `m_noppid` must FAIL (1).

| leg | command (on committed bytes at `cbe068d0…`) | observed | result |
|---|---|---|---|
| after (escapee) | `git show cbe068d0:census/round-100/records/c2-escapee-r100.txt` | `ESCAPEE-ALIVE run=r100 alive=1` (pid 3418284) | FAIL (predicate wants `alive=0`) |
| after (decoy) | `git show cbe068d0:census/round-100/records/c2-decoy-r100.txt` | `DECOY-SUMMARY verdict=spared`, `DECOY-PLANTED n=83 dead=0 alive=83` | PASS (spared 83/83) |
| before (r99 control) | `git show a662bb0d:census/round-99/records/c2-escapee-r99.txt` | `ESCAPEE-ALIVE run=r99 alive=1` | PASS (do-nothing, alive=1) |
| controls (r99 counter / CM8) | lane receipts `c2-decoy-r100.txt` + `census/round-99/records/c2-decoy-r97.txt` read-only + `c2-decoy-cm8.txt` | r99 alive=1 spared 84/84; CM8 kills decoy | PASS (non-vacuous kill leg) |

Adjudication: the frozen `alive=0` leg is structurally unreachable via branch (b).
The decoy probe is spawned `start_new_session=True` ⇒ `spawn_sid == spawn_pid`; the
fixture `os.setsid()` child leads its own session ⇒ `escapee_sid == escapee_pid`;
`escapee_sid == spawn_sid` is False by construction (ReviewerC1Predicate attack_a,
SentinelEscapee dry probe `owned_count=0`, ConnectorOverlap `session-key.txt`,
all agreeing — recorded in `census/round-100/wave-evidence/`). Four non-author
seats caught the same inequality; the frozen predicate, written before sampling a
live fixture shape, did not. The `m_noppid` mutant is vacuous under this rule
(branch (b) never fires on the escapee). The rule occupies the claim and mislabels
the mechanism.

Re-measured vs evidence-verified: C1 re-measured on committed bytes (receipts read
directly); C2 greps ran on committed bytes (receipts + committed SOURCES/file
bytes). Neither claim's verification depends on executing a lane-owned gate; no
sibling gate was executed.

No owned axis was harmed beyond the claim itself: `git diff a662bb0d cbe068d0 --
SCORECARD.md` shows no score moves (calibration 7, operability 8, coverage 8
unchanged); the harm is axis-verdict harm on operability (a new rule that cannot
fire), not a score decrement.

### C2 — calibration: S075/S332 attribution repair (correction-class) — **improved**

Frozen predicate: leg1 `grep -c 'S332' corpus/knowledge/deadline-owned-reaping.md` ≥ 1;
leg2 S075 row names the entry; 294 registry rows; sources-census exit 0.

| leg | command | observed (base → HEAD) | result |
|---|---|---|---|
| leg1 | `git show a662bb0d:…/deadline-owned-reaping.md \| grep -c 'S332'` → `git show cbe068d0:… \| grep -c 'S332'` | 0 → 1 | Improved |
| leg2 | `git show <rev>:corpus/SOURCES.md \| awk '/^\| S075 /' \| grep -c 'deadline-owned-reaping'` | 0 → 1 | Improved |
| registry | `… \| grep -cE '^\s*\| S[0-9]'` | 294 → 294 | Unchanged, no harm |
| census | `sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` | `ok …corpus/SOURCES.md` EXIT 0 (pre-existing W04 duplicate-URL warnings only) | PASS |

Correction block (`corpus/knowledge/deadline-owned-reaping.md:80`): append-only,
withdraws the in-body "S075 field 4" attribution in favour of S332 (kernel
emission order), keeps S075 for field 22. No other file harmed: the S075 diff is a
one-cell `used-by` append (`corpus/SOURCES.md:110`); S332/S368 rows unchanged.

Graded gaps carried (Q62, not predicate failures): S332/S075 cited in the body,
not front-matter `source:` (ReviewerC2Attribution F1/F2); the correction names S332
by row, file, symbol, tag and capture dir but carries no ≤25-word located quote
from the S332 anchor. The closure independently verified the emission order itself
(see §3: S332 quote verified against the captured `array.c` — ppid is field 4,
sid field 6, start_time field 22 in `do_task_stat()`), so the attribution is
sound even though the body quote is missing. Verdict: **improved** under the
frozen predicate.

Re-mesUREd vs evidence-verified: C1 re-measured on committed bytes (receipts read
directly); C2 greps ran on committed bytes (receipts + committed SOURCES/file bytes).
Neither claim's verification depends on executing a lane-owned gate; no sibling gate
was executed.

### Pre-file falsification ledger (§2b)

`python3 …/prefile-falsification.py --lane souji --round 100` →
`PREFILE-FALSIFICATION: SETUP findings=3`, exit 2, findings:
`claims.json` missing, `w1-results.json` missing, `claim-falsification.tsv`
missing (all under `souji-shokunin/.ufo/waves/round-100/`).

Adjudication: the ledger is **absent** — a conformance defect (named in §5), not
an automatic rejection. The lane's wave evidence lives in
`census/round-100/wave-evidence/` (14 seat dirs + `swarm-registry.json`), which
is where the r99 ledger inputs (`census/round-99/wave-evidence/claims.json`) also
lived; the r100 pre-file runner looks in `.ufo/waves/` instead. The attack-role
surface is verifiable without the runner: `CriticC1Scope.md` contains
`falsifies-wording` verdicts (a1/a2/b1) and `falsifies-number` (F-n). Each:

- **a1** ("in a different session" never measured): real and unreconciled against
  the frozen sentence — the sentence asserts the *reason*; the instrument never
  reads the decoy's session. Narrowing exists only as the claim's honest
  re-wording: the landed report claims C1 `harmed`, not admitted, and names the
  escapee/decoy legs by their bytes (`alive=1` / `verdict=spared`), not as
  "because a different session". Real, reconciled by the honest-stop verdict;
  C1 does not verify and was not admitted on this wording.
- **a2** ("alive=0 counts ppid chain, not session"): real — the survivors scan is
  a descendant (ppid) count; the plan's separate external `ESCAPEE-ALIVE` scan is
  the only session-independent byte. Same reconciliation: the report's C1 leg is
  the external scan (`alive=1`), and the claim is graded harmed.
- **b1** (byte-exact filter, starttime gate, CM8 limb, `conform` binding omitted
  from the sentence): real as a narrowing — the sentence is narrower than the
  instrument. The report's C1 verdict rests on the whole triple (alive / CM8 /
  `m_noppid` vacuity) and is graded harmed; the narrowing is named, never hidden.
- **F-n (falsifies-number, arity)**: real on the mid-build snapshot the critic
  read (2-tuple vs 3-tuple unpack); reconciled by the landed 3-tuple at
  `census/round-100/c2-setup-arms.py:349` (lesson M15) and the successful live
  runs (`conform=20`). The critic caught a real state-at-time; the landed bytes no
  longer carry it.

So the `falsifies-wording` rows are **real, each named and narrowed**; none is
spurious; none is hidden by a green counter. C1's verdict (harmed, not admitted)
already reflects them; C2 has no `falsifies-wording` row. The absent `.tsv`
ledger is a conformance defect, not a verification failure.

### Per-axis verdicts

| axis | verdict | evidence |
|---|---|---|
| operability | **harmed** | C1 re-measured `alive=1` vs frozen `alive=0`; new session key structurally unreachable (§2) |
| calibration | **improved** | C2 bidirectional grep 0/0 → 1/1, census 294→294 EXIT 0, correction append-only; Q62 gaps carried openly |
| coverage | **unchanged** | census 294→294; no registry row added/touched beyond S075 `used-by`; no capability row entered the SCORECARD table (`capabilities:` unchanged — correct, the counter reaps nothing new) |

## 3. Discernment spot-check (LEARNING.md)

Re-opened from committed lane captures (public sources; GitHub raw is also
fetchable, and both sides agree — the local capture sha256 matches the SOURCES
row):

| item | lane decision | re-opened source | closure | reason |
|---|---|---|---|---|
| S075 admit (gate) | re-verified (proc_pid_stat(5), field 6 / field 22) | `census/round-98/srcs/proc_pid_stat.txt` | agree | quote verified byte-identical in the capture: "(6) session %d The session ID of the process." (6 words) and "(22) starttime %llu The time the process started after system boot." (8 words); ≤25 words each; fields 5/6/22 descriptions match the row's `teaches` |
| S332 admit (gate) | re-verified (kernel `array.c` `do_task_stat()`, field-4 ppid) | `census/round-83/srcs/linux-array.c-v6.17` | agree | `do_task_stat()` emission order verified in the 23233-byte capture: `seq_put_decimal_ll(m," ",ppid)` is the 4th field after comm/state, `sid` the 6th, `start_time` the 22nd — the C2 correction's field-4 ppid wording follows from the kernel text, not the man page |
| S368 reject-scope (gate) | re-verified (setsid(2) new process-group sentence; scope excludes error cases / setsid(1)) | `census/round-96/srcs/setsid.2.html` | agree | quote verified byte-identical in the tag-stripped capture: "The calling process also becomes the process group leader of a new process group in the session"… (17 words, occurrence 1); the DESCRIPTION context confirms the scope boundary the row states |
| S075 newly written `used-by` row | accept (append `…, corpus/knowledge/deadline-owned-reaping.md`) | `git show cbe068d0:corpus/SOURCES.md:110` | agree | ≤25-word quote behind the row is the field-6 sentence above (6 words); the appended entry is the C2 correction block that actually cites S332/S075 — no stale `used-by` |

`sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` → `ok`,
EXIT 0, with pre-existing W04 duplicate-URL warnings only (no new warnings).
Gitiles base64 warning not applicable (no `…googlesource.com/…?format=TEXT`
source re-opened this round).

Discernment: gate admits (S075/S332/S368 re-verification) agree with the closure;
the gate's C1 **reject** is correct but was not made by the gate — four non-author
wave seats (Reviewer, Critic, Sentinel, Connector) falsified the frozen predicate;
the pre-freeze gate froze it. Lane trend `discernment: harmed` is sustained.

## 4. Trends

| trend | verdict | evidence |
|---|---|---|
| expansion | unchanged | 294→294 rows, no new row, no frontier row advanced; C1/C2 rest on re-verified rows |
| quality | improved (calibration) / harmed (operability) — trade, not netted | C2 bidirectional grep 0/0 → 1/1 with sound, closure-verified S332 attribution (gain); C1 landed a rule that cannot fire (harm). Per the lane's own framing the axes do not cancel; the closure records both |
| discernment | harmed | pre-freeze gate froze a structurally unreachable predicate (M14); the wave's attack seats caught it, the gate did not; gate admits/rejects in the lesson sample agree only because the repair is C2 and the catch was not the gate's |

## 5. Routed defects (lane must fix next round)

1. **r101 blocker — escapee ownership rule.** The session-key rule is structurally
   unreachable for a new-session escapee (spawn leads its own session; `setsid()`
   grandchild leads another). The only in-lineage escapee mechanism is the
   counter-child net (r98 branch (c) + `PR_SET_CHILD_SUBREAPER`, RevengerR98Rule).
   A session key may at most be a persistence note, never the ownership rule.
   Freeze the predicate against a live fixture shape before freezing the sentence.
2. **Q62 carried (C2).** Add a ≤25-word located quote from the S332 anchor to
   the correction block, and move the S332/S075 cites from body-only into
   front-matter `source:` (ReviewerC2Attribution F1/F2). The closure verified the
   kernel emission order directly, so this is documentation debt, not an
   admission blocker.
3. **Pre-file falsification ledger location.** The r100 ledger inputs
   (`claims.json`, `w1-results.json`, `claim-falsification.tsv`) are missing under
   `.ufo/waves/round-100/`; the r99 pair lived in `census/round-99/wave-evidence/`.
   Place the r101 ledger where `prefile-falsification.py` reads it, or name the
   divergence in the plan so the SETUP finding is explained rather than silent.
4. Dead seats (for the record, no action): `MutC1SessionKey` produced no dir;
   `ExecC1SessionApplier`/`ExecC1SessionNoReap` dirs were empty at attempt-1 end;
   the build was verified from the worktree diff. The `m_noppid` mutant remains
   unrun and, under this rule, vacuous — do not re-run it against a session key.
5. Lineage fork / promotion-readiness (operator-owned): four independent
   non-author measurements all read the session inequality — if the operator
   considers the SHONEN boxes fully checkable from this spot-check, the promotion
   call is the operator's, not the closure's.

## Verdict

`admitted=false` overall (C1 harmed ⇒ the round's operability claim does not
verify), with C2 individually verified. Conformance defects (absent ledger,
Q62 carried, dead seats) are status-neutral and recorded above. Axis verdicts
operability harmed / calibration improved / coverage unchanged; trends expansion
unchanged, quality trade, discernment harmed.
