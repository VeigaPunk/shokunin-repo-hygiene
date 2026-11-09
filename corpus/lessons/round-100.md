# Round 100 — the session-owned escapee reap is structurally unreachable (C1 harmed); the S075/S332 attribution repair clears the bidirectional grep (C2)

Lane base `a662bb0d7e033cc5ceccd70b52eb234404300845` (r99 tip). Plan with frozen predicates: `plans/round-100.md`
(A0.1 frozen predicates). Wave: one v1 wave, 14 seats (`w1`; evidence copied to `census/round-100/wave-evidence/`).
Attack share 7/14 (50 %); connector 1. Attempt 2 `SoujiR100a2` (attempt 1 `SoujiR100` died mid-wave; inherited
`census/round-100/c2-*.py`, the uncommitted C2 worktree edits, and 11 seat dirs — reused what re-verified, discarded
what did not; re-ran the live measurements L1-side with fresh `--work` dirs).

## Claims and verdicts

- **C1 (operability 8; Q177).** The r100 counter reaps the T1 setsid escapee by session ownership (a) spawn pid
  starttime-verified OR (b) candidate's field-6 session id equals the spawn pid's recorded session id with
  starttime >= spawn's. Verdict: **harmed (trade); not admitted** (L1 measurement; the non-author closure decides).
  Measured on committed bytes at the C1 landing commit (below), receipts
  `census/round-100/records/c2-escapee-r100.txt` / `c2-decoy-r100.txt`:
  r100 counter `ESCAPEE-ALIVE alive=1` (live `/proc` argv scan, pid 3418284, ppid 1525, session == own pid) while
  `DECOY-SUMMARY verdict=spared` 83/83 alive; r99 counter (same decoy test, fresh work) alive=1, spared 84/84.
  The session branch never fires on the escapee: the probe is spawned `start_new_session=True` so spawn_sid == spawn
  pid, and the fixture's `os.setsid()` child leads its own new session (sid == escapee pid), so
  `escapee_sid == spawn_sid` is False by construction (ReviewerC1Predicate attack_a, SentinelEscapee dry probe,
  L1 live scan — three independent measurements agree). The frozen `alive=0` leg is structurally unreachable via
  branch (b); it degenerates to the r99 do-nothing (alive=1 both). Do-nothing control r99 alive=1 as frozen.
  The CM8 argv-only mutant kills the decoy (MutC1WideRule wide mutant), so that leg is non-vacuous; the escapee leg
  is the vacuous one. The `m_noppid` mutant is vacuous under this rule (branch (b) never fires on the escapee, so
  removing it cannot change alive) — Q175's vacuity clause catches it, but the experiment cannot run meaningfully.
- **C2 (calibration 7; correction-class).** `corpus/knowledge/deadline-owned-reaping.md` gains an append-only
  correction block citing S332 for the field-4 ppid wording (withdrawing the in-body "S075 field 4" attribution),
  and the S075 row's `used-by` cell gains the entry (append-only cell). Verdict: **improved (verifies under the
  frozen predicate)** (L1 measurement; the non-author closure decides). Measured on committed bytes at the
  C2 landing commit: leg 1 `grep -c 'S332' corpus/knowledge/deadline-owned-reaping.md` = 1 (>= 1); leg 2 the S075
  row names the entry = 1. At base both were 0. No new SOURCES row: 294 rows before and after
  (`grep -cE '^\s*\| S[0-9]' corpus/SOURCES.md`); sources-census exit 0 before and after. Q62 graded gap (not a
  frozen-predicate failure): S332 and S075 are cited in the body, not in front-matter `source:` (ReviewerC2Attribution
  F1/F2); the correction names S332 by row id, file, symbol, tag and capture dir but carries no <=25-word located
  quote from the S332 anchor. Carried for the closure.

## Gate

Source rows re-opened live this round (ScoutSources; URL · access date · located quote, <=25 words · location).
Each live fetch is HTTP 200 and byte-identical to its committed capture; each quote occurs exactly once:

| row | URL | access | located quote | location |
|---|---|---|---|---|
| S075 (re-verified; grounds C1's session key field 6 / starttime field 22) | https://man7.org/linux/man-pages/man5/proc_pid_stat.5.html | 2026-11-09 | "The session ID of the process." (6 words; field 22: "The time the process started after system boot.") | § DESCRIPTION fields (6)/(22); occurrence 1, live sha256 0f04d789 == capture |
| S332 (re-verified; grounds C2's field-4 ppid wording) | https://raw.githubusercontent.com/torvalds/linux/v6.17/fs/proc/array.c | 2026-11-09 | do_task_stat() emission order slot 4 == ppid, slot 6 == sid, slot 22 == start_time | sha256 17f2318d == capture census/round-83/srcs/linux-array.c-v6.17 |
| S368 (re-verified; grounds the setsid new session) | https://man7.org/linux/man-pages/man2/setsid.2.html | 2026-11-09 | "The calling process also becomes the process group leader of a new process group in the session" (17 words) | § DESCRIPTION; occurrence 1, live sha256 52cbc190 == capture |

Sources-census before and after: `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root
/home/vgpnk/Projects/shokunin souji` — 294 rows, EXIT 0 at round start and at round end. Sourced claims: C1
(S075+S368) and C2 (S332), each resting on a row opened this round.

Non-author discernment (LEARNING.md): the Reviewer, Critic, Sentinel, Connector and Scout seats are non-author. They
agreed on the C1 structural failure (ReviewerC1Predicate, CriticC1Scope, SentinelEscapee dry probe, ConnectorOverlap
live scan — four independent measurements of the same session inequality) and disagreed with the frozen predicate, not
the measurements. The C2 admit/reject sample: admit = C2 attribution (bidirectional grep 1/1); reject = C1 session
key (escapee never matches its own key).

Assimilation: none this round (no `merge/souji/` theme taken). considerthese: the lane has no `considerthese/` dir.

## Mistakes

- **M14 — the frozen session key cannot match the escapee it exists to reap (class: key never fires; vacuous
  predicate).** Evidence: ReviewerC1Predicate attack_a (`escapee_session == spawn_session? False`), ConnectorOverlap
  `session-key.txt` (escapee sid == own pid), SentinelEscapee dry probe (`PRED pid=… owned=False`, `DRY-REAP
  owned_count=0`), L1 live runs (r100 alive=1, r99 alive=1, decoys spared both). The probe's `start_new_session=True`
  makes spawn_sid == spawn pid; the fixture's `os.setsid()` makes escapee_sid == escapee pid; the two are equal only
  if the same pid both leads and escapes. Captured-by: none — the pre-freeze gate never evaluated the predicate
  against a live fixture shape before freezing; the r99 spot-check's routed candidate ("fixture session id recorded
  at spawn") named the key without checking which session the escapee leads. Fix (routed r101, not yet shown able
  to fail): the counter-child net (r98 branch (c) + `PR_SET_CHILD_SUBREAPER`) is the only in-lineage mechanism that
  reaches the orphaned escapee; a session key can at most be a persistence note, never the ownership rule. **Shown
  able to fail:** the sentinel dry probe (owned_count=0 on a real live shape) and both live alive=1 runs.
- **M15 — the r100 one() still builds a 2-tuple spawn while _reap_owned unpacks 3 (class: arity / mid-build
  snapshot).** Evidence: CriticC1Scope F-n (`spawn = (p.pid, _proc_starttime(p.pid))` vs
  `spawn_pid, spawn_st, spawn_sid = spawn`). The attempt-1 build was a mid-build snapshot when the seats ran; the
  L1 found the 3-tuple landed in the worktree diff between the critic's read and the live runs (crash path is now
  unreachable — the live r100 runs complete with conform=20). Captured-by: the critic seat (caught it live, in
  the snapshot). Fix: none needed at landing (the 3-tuple is in the landed bytes; `grep -n "spawn = "` at
  `census/round-100/c2-setup-arms.py:349` shows the 3-tuple). **Shown able to fail:** the arity proof
  (`ValueError` on the 2-tuple unpack) plus the successful live runs.

## Wave findings (summary; full verdicts in `census/round-100/wave-evidence/`)

- C1: ExecC1SessionApplier (counter build; 3-tuple + branch (b)), ExecC1SessionNoReap (r99 control, alive=1),
  ReviewerC1Predicate (attacks a/b/c: no / inverted / unsound — all fail), CriticC1Scope (falsifies-wording a1/a2/b1,
  F-n arity), MutC1WideRule (m_wide kills decoy; pristine spares), MutC1SessionKey (dead seat — no evidence
  produced; m_noppid unrun, vacuous under the rule anyway), SentinelEscapee (dry probe: owned_count=0),
  ConnectorOverlap (sibling scan: no lane claims the session reap; live session-key evidence), ScoutSources
  (S075/S332/S368 re-opened, 23 checks pass), LabratField6 (field-6 probe, read-only), RevengerR98Rule (r98/r99
  reconstruction: branch (c) is the only escapee mechanism).
- C2: ExecC2Attribution (two append-only edits, 1/1 legs), ReviewerC2Attribution (F1 quote gap, F2 front-matter gap,
  F3 timing — legs verified on worktree, committed-byte re-measure by L1), ScribeLesson (skeleton, placeholders
  filled by L1).
- No-harm: `census/round-100/c2-decoy-test.py` is byte-identical to r99's (diff empty), so the decoy instrument is
  unchanged; the only new bytes are the counter's branch (b) and the C2 edits.

## Trend verdicts (lane)

- expansion: **unchanged**. No registry row added; S075/S332/S368 re-verified only.
- quality: **harmed** for C1 (the session key is a new rule that cannot fire — worse than no rule, because it
  occupies the claim). C2's attribution repair is a quality gain but does not offset a harmed operability move.
- discernment: **harmed**. The pre-freeze gate froze a structurally unreachable predicate (M14); the wave's attack
  seats caught it, the gate did not.

## Frontier

No `merge/souji/` theme assimilated (Assimilation: none). `considerthese/`: the lane has none. The sourced claims
are C1 (S075+S368) and C2 (S332), each resting on a row re-opened this round. Frontier F5 (process residue, reap
authority) is unchanged: the operator's reap-authority question is still open (`.ufo/l0-questions.md`, round-97/
round-98/round-99 lines; a round-100 line is appended with this round).
