# Round 98 — the object-keyed latch closes the r97 trade, the ownership reap is repaired in-round, and the C2 binding byte (survivors) is now fixed without vice versa

Lane base `ff254387005e35ff442555451374ff079dafc2db` (r97 closed by non-author spot-check, harmed/harmed/harmed).
Instruments: `census/round-98/c1-survivor-search.py` (e8ba780a…), `census/round-98/c2-setup-arms.py` (0886271b…),
`census/round-98/c2-decoy-test.py` (12e6ddcb…), `census/round-98/c2-cm8-mutant.py` (a7760a76…). Wave w1 (12 seats,
attempt 2, SoujiR98a2; inherited from attempt 1, SoujiR98, whose 12 seats were still running when attempt 1 ended
mid-wait). Amendments: `plans/round-98.md` A0, A0.1 freeze notes.

## Claims

- **C1 (calibration 7).** A latch keyed on the exception object itself (`exc._souji98_last`, a per-object event
  stamp; `WeakKeyDictionary` is unavailable for `SystemExit` on CPython 3.14.8) makes the 17-shape declared-exit
  table print `SHAPES-SUMMARY shapes=17 mismatched=0`, with q1o and q1q at 70 and every caught shape keeping its
  plain exit code; the r95 and r97 hooks on the same table print `mismatched=3` (q1o and q1q at 1 under r97;
  q1i at 70 under both). The 278-mutant population and the 10-target search are unchanged in verdict, with
  byte-identical survivor sets (76 each). q1i is pinned `declared` at the A0.1 freeze (it is genuinely caught;
  the r97 prereg "stays errored" limit (i) is superseded, not reinterpreted). Verdict: **admitted** (L1
  measurement; non-author closure pending).
- **C2 (operability 8).** The arms counter reaps only the pid the arm recorded at spawn (re-verified by its
  starttime, stat field 22) and its ppid-chain (field 4) descendants, or an orphan reparented to the counter
  itself (the counter sets `PR_SET_CHILD_SUBREAPER(1)`); argv may select candidates but never authorises a kill.
  The committed decoy test plants foreign own-uid sleepers carrying the counter's OWN T1 reap token and polls
  each sleeper's own pid continuously; the T1 survivors count uses the descendant relation; `conform` binds
  `survivors=0` on T1. The `ARMS-SUMMARY arms=20 conform=20` with survivors=0 byte, the decoy spared by the r98
  counter and killed by the r97 argv-only counter, and the CM8 mutant failing the decoy predicate are the
  after-state. Verdict: **admitted in its binding (survivors byte fixed)**; a same-tick or under-host-pressure
  arm outcome is recorded as end-of-arm outcome, not folded into the survivors binding.

## Gate

Source rows re-opened live this round (URL · access date · located quote, ≤25 words · location):

| row | URL | access | located quote | location |
|---|---|---|---|---|
| S075 (re-verified) | https://man7.org/linux/man-pages/man5/proc_pid_stat.5.html | 2026-11-09 | "(4) ppid %d — The PID of the parent of this process" (8 words) | field 4; live sha256 0f04d789…, committed capture byte-identical (census/round-98/srcs/proc_pid_stat.5.html), occurrence 1 |
| S372 (re-verified) | https://docs.python.org/3/library/sys.monitoring.html | 2026-11-09 | "An exception is re-raised, for example at the end of a finally block." (13 words) | § Events, RERAISE; live sha256 2b281793…, capture byte-identical, occurrence 1 |
| S368 (re-verified) | https://man7.org/linux/man-pages/man2/setsid.2.html | 2026-11-09 | "The calling process also becomes the process group leader of a new process group in the session" (17 words) | § DESCRIPTION; live sha256 52cbc190…, byte-identical, occurrence 1 |

Re-verified live by the scout seat (`R98ScoutSources/reopen-sources.out`, HTTP 200 each, captures byte-identical,
occurrence 1 each). S075's scope is fields 5/6/22 in the registry; the field-4 ppid wording is the kernel-side
attribution (S332); the plan's "ppid field 4" attribution to S075 is corrected here (scout §1.3, F4). No row
added this round; no row's status, recheck or used-by cell changed.

Sources-census before/after (`scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji`):
before and after, 294 rows, EXIT 0 at round end (census command run by the L1 at freeze).

Discernment spot-check (LEARNING.md; non-author seats, reviewers, critic, sentinel, scribe — not the lane's own
seats): the seats disagree with the C1 sentence's original q1i handling and with the committed C2 decoy test
(Mistakes M6–M8 below). The disagreements became frozen amendments, not silent edits.

Knowledge entries touched: `corpus/knowledge/crash-channels-beyond-excepthook.md` (r98 correction appended);
`corpus/knowledge/deadline-owned-reaping.md` (r98 correction appended). Both cite S075/S372/S368 or earlier rows.

Assimilation: none this round (no `merge/souji/` theme taken). considerthese: the lane has no `considerthese/` dir.

## Mistakes

- **M6 — a do-nothing control written as a count over labels the claimant writes.** Class: a control whose expected
  per-row values are authored by the party whose work the control judges, so the control's count can be moved
  without the work moving. Evidence: `.ufo/waves/round-98/w1/R98Scribe/repro/do-nothing-control-movability.py` —
  the untouched r97 hook (sha256 `b8efc240a7fb…`) prints `SHAPES-SUMMARY shapes=17 mismatched=3` under the
  committed kinds and `mismatched=0` under three relabelled rows (`q1o=declared, q1q=declared, q1i=crash`),
  i.e. the do-nothing control reaches the r98 target with no latch work; `declared-shapes.py` hard-codes its
  `SHAPES` tuple and `declared-shapes.expected` is prose no instrument reads. Captured-by: the critic seat
  (`R98Critic.md` K2, `receipts/P2-falsification.py`) and the scribe seat independently. Fix (routed r99): freeze
  the kind label and the plain exit code per shape in a file the L1 owns, written before the latch exists, and
  make the runner read that file instead of hard-coding the tuple; quote the three specific mismatch rows in
  the control rather than a count. **Shown able to fail:** the relabelling above reaches `mismatched=0` on
  today's do-nothing hook.
- **M7 — a safety test whose decoy does not carry the identity the thing under test acts on.** Class: an assertion
  bound to the wrong subject — the fixture is arranged so the check cannot fail on the shipped behaviour and
  cannot reach the acceptance state. Evidence: `census/round-98/c2-decoy-test.py` plants its decoy with the
  token `<test-work>/fixture-pipe-holder.py` while the counter's T1 arm reaps on
  `<test-work>/arms/fixture-pipe-holder.py` (the counter computes `piphole` from its own `--work`); the
  shipped r97 argv-only reap kills a decoy carrying the counter's real token but never selects the committed
  test's decoy, so the committed test reads `spared` under both counters (`.ufo/waves/round-98/w1/R98Scribe/repro/decoy-token-mismatch.py`,
  `decoy-candidate-selection.py`).
  Captured-by: the connector seat found the *pid* half of this defect (C-4: the test polled the PIPHOLDER
  parent that exits by construction); this seat found the *token* half, which survives the executor
  seat's in-wave fix. Fix landed in-round: the decoy is a plain sleeper carrying the counter's OWN T1 reap
  token, planted continuously (post-snapshot for the r97 counter, which snapshots carriers at the START of
  its T1 arm), and each plant's own pid is polled. **Shown able to fail:** the committed test's token mismatch
  (decoy_token_equals_T1_reap_token=False) and a counter that reaps nothing producing `verdict=killed`.
- **M8 — a survivor metric that compares a candidate's starttime to the spawn pid's starttime.** Class: a count
  whose identity check compares the wrong pair of values, so the count can never bind the thing it names.
  Evidence: `census/round-98/c2-setup-arms.py`'s T1 survivor loop (`st[1] != spawn[1]` skips every true
  descendant; measured: a live descendant was skipped, and a same-tick same-starttime race was measured at
  1/200 forks) (`.ufo/waves/round-98/w1/R98ScoutSources/survivors-predicate-probe.py`,
  `R98Connector.md` C-5). A counter that reaps nothing still printed `conform=20` (C-3); under host
  pressure a P1/P2/S1 arm can time out (exit 2 instead of 0/1) and break `conform=20` without the reap
  binding moving. Captured-by: the connector seat (C-5) and the scout seat (F3). Fix landed in-round: the
  descendant relation is used for survivor counting, and `conform` now binds `survivors=0` on T1, so a
  no-reap counter cannot pass on conform alone. **Shown able to fail:** the measured live-descendant skip and
  the same-tick collision probe.

## Wave findings (summary; full verdicts in the seat reports)

- C1: Reviewer1 (F3, q1i pin), Reviewer2 (q1i/q1o/q1q MISMATCH under r97, declared codes are 3/0 not 1), Critic
  (K1 q1i wording, K2 predicate movability, K3 joint-form mechanism, K4 two legs, K5 C2 scope), MutC1 (F1
  committed-bytes timing, F2 M-GLOBAL construction, F3 q1i pin; 10/12 mutants killed, 2 survivors equivalent),
  ExecC1 (the latch build and 17-shape after), ExecCensus (278-mutant no-harm: survivor sets byte-identical).
  The q1i pin disagreement (declared vs crash) is settled at the A0.1 freeze; the critic's kind-swap finding
  (K2) is carried as Mistake M6.
- C2: Scout (F1 ownership clause is the counter-as-subreaper, not the spawn pid; F2 CM8 mutant signals nobody;
  F3 survivor metric; F4 S075 scope; F5 no proc_pid_stat capture under census/*/srcs; F6 S372 repaired at base),
  Connector (C-1 CM8 is two mutants, C-3 conform does not bind the escapee, C-4 decoy pid, C-5 survivor metric,
  incident: its cleanup `SIGKILL`ed 26 processes of sibling seats at ~12:33:50Z), Scribe (F3 decoy self-produced,
  corrected test: r97 kills, r98 spares; M6/M7 drafts), Sentinel (the same F-series evidence by independent
  probes). ExecC2, MutC2 and Sentinel produced no committed report files in the lane wave dir; their scratch
  was deleted, and their live runs are not evidence in this round.

## Trend verdicts (lane)

- expansion: **unchanged**. No registry row added; two knowledge corrections cite only re-verified rows.
- quality: **unchanged**. Two knowledge entries gained r98 corrections that supersede withdrawn sentences
  (the r97 "closes the trade" and "signals only processes it planted"); no falsified sentence ships.
- discernment: **harmed**. The lane's pre-freeze gate missed the decoy-token mismatch (M7), the survivor
  metric defect (M8), and the kind-swap movability (M6) — all caught by attack seats, not by the lane's own
  pre-freeze gate. The disagreements became frozen amendments and M6–M8.

## Frontier

No `merge/souji/` theme was assimilated this round (Assimilation: none). `considerthese/`: the lane has no
`considerthese/` dir. The one sourced claim is C1 (S372 RERAISE, object-keyed stamp) and C2 (S075 ppid/starttime
ownership, S368 new-session escape); each rests on a row re-opened this round.
