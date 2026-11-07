# Round 79 — the pre-report gate answers a caller's signal (C1 operability), the pointer counter refuses the r78 wave's false ledger rows (C2 calibration)

Attempt 1 (`SoujiR79`). Lane base `e65538e73c7f1a8f7570bc24a2215da8a90043f3` (r78 admitted, spot-check committed).
Staged commits in the order the preregistration binds: P `d7f40f764e6b25e32662384761d82d3032714eb1` (counters,
populations, control variants, every control receipt, S325/S326 captures, census-before, pre-freeze
feasibility); F `e98cd0c55b1d8aaec8af8ff3402a5856263923ed` (preregistration; freeze-check `--substance
--chronology` `SUMMARY claims=2 findings=0`, `census/round-79/records/freeze-check-at-F.txt`); W1
`c8c3fbca5ac44184feac3a01ee964139f86c02a4` (C1 candidate gate); W2 `17009fa1f9d335a1bdde1e22ff3894c5d571c250` (C2
candidate counter); A `b8d094299e06bc66352f5232cd7a75d1f503c0fa` (after-arms); R1
`4a9bbb303db7f1508e24f60d4b9feff80bcbc079` (a misdiagnosed repair, M2); R2 `feebf2ba6f120903e45d31cf322751c052f2feb9`
(R1 reverted, gate bytes = W1, R1 receipts kept); D `92cab9c782457c4256acc6f099375caf4056fca3` (diagnosis receipts,
foreground re-measurement, wave spec). Frozen claims, counters and predicates are in
`census/round-79/preregistration.txt` and are not restated here.

## Inherited

The r78 spot-check routed six defects (`corpus/lessons/round-78-verifier-spotcheck.md` section 5) and the r78
lesson four items (`## Routed to round 79`):

- defect 1 (the L commit message `a0f3b91f` miscounts ledger classes) → LOG.md `## Round 79` carries the pointer:
  the class counts are those of `corpus/lessons/round-78.md` M3 and the ledger, never the commit message.
- defect 2 (r78 preregistration Surface attributes the HEAD read to S324) → not amended (frozen); the knowledge
  entry `corpus/knowledge/git-discovery-sources.md` already says the HEAD open (setup.c:373) is read by a seat and
  quoted in no row. No new row this round (no claim rests on HEAD).
- defect 3 (C2 counter: four mutants survive, five false rows pass) → C2 of this round: the five false rows
  NF1-NF5 and the four detector rows are the frozen population; the C1 instrument items (duration bound m13,
  timeout's own group) are carried.
- defect 4 (the domain trial graded a report prefix) → this round's domain trial binds the final report bytes
  (report sha256 printed after the last edit; see the report).
- defect 5 (SIGTERM path, check-4 backstop row) → SIGTERM taken as C1; the backstop row is carried.
- defect 6 (pointer check missing=19 by design) → unchanged; the ledger stays the authority.
- routed (a) C1 instrument successor, (c) C2 instrument successor rows beyond NF1-NF5, (d) r76 K03/K04 and the
  status-trusting tools → carried to round 80.

No inherited lane leftovers (`jj-lane.sh state` at start: `local=remote=e65538e7… ahead=0 tracked=0
untracked=0`; the watchdog log has no `lane-dead-no-report souji round=79`). No `considerthese/` directory
exists in this lane; no shokuknow theme taken (Assimilation: none).

## Measured

- C1 (frozen counter `census/round-79/c1-signal-counter.py`, 11 rows): K-a at the base 10 mismatches / 10
  orphans (`controls/c1-K-a-do-nothing.txt`; foreground repeat `records/foreground/c1-K-a-fg.txt` identical);
  K-b trap-only 10/10, K-c no-kill 10/10. **At A (`records/c1-after.txt`, W1 gate) mismatches=1 orphans=1
  EXIT=1**: row s4 (INT) — the gate was still running 5 s after the signal and no trap ran. By its frozen kill rule
  ("any mismatch") C1 FAILS at A. Cause (M2): the A run, like every receipt run of this round, was
  launched with `&` from a script, so the counter and every gate it started inherited SIGINT ignored, which bash
  cannot trap (`records/foreground/sigint-inherit.txt`). The same frozen counter run in the foreground at W1:
  `SUMMARY rows=11 mismatches=0 errors=0 orphans=0` in 3 of 3 runs (`records/foreground/c1-at-W1-fg-run1..3.txt`).
  R1 (a repair for a race that was not the cause) fails s4 identically in 3 of 3 background runs
  (`records/repair/c1-at-R1-run1..3.txt`) and was reverted.
- C1 regressions at W1: r78 17/17, r77 16/16, r76 30/30, r36 21/21, r27 4/4 (`records/c1-regress-*.txt`).
- C2 (frozen harness `census/round-79/c2-false-row-harness.py`, 9 rows): K-a r78 counter mismatches=5
  accepted=5 → `records/c2-after.txt` (W2 counter) mismatches=0 accepted=0 EXIT=0; K-b refuse-all 9/9 on the
  harness but 3/22 on the r78 regression (`controls/c2-K-b-refuse-all-regress-r78.txt`); ablations range 2,
  nextline 1, moved 1, quarantine 1 (`controls/c2-K-c-without-*.txt`); regressions at W2 r78 22/22 + 12/12, r77
  35/35 + 7/7 (`records/c2-regress-*.txt`).

## Mistakes

| # | class | evidence pointer | captured-by | fix |
|---|---|---|---|---|
| M1 | instrument: the C1 shim matches its argv pattern anywhere in argv, and the row directory names contain the pattern (`s3-term-ls-remote`, `s4-int-ls-remote`), so s3/s4 block at the first `git config --file <rowdir>/clone/.git/config` read of check 0, not at `ls-remote` as labelled; base runs show s3/s4 with no `check-gitsource` line while s2 has one (`controls/c1-K-a-do-nothing.txt`) | `census/round-79/c1-signal-counter.py` SHIM and ROUTES; `controls/c1-K-a-do-nothing.txt` brief lines | none (no selftest prints where each row blocks); found by the L1 reading the K-a brief lines and confirmed by S79ExecC1, S79Sentinel I1, S79CriticClaims MEDIUM-4, S79MutGate (`.ufo/waves/round-79/w1/S79MutGate/probes/argv-s3.txt`) | r80 successor counter: the shim writes its argv at the mark and the row asserts the subcommand (argv[1]) and the check line printed before the mark. Not yet shown able to fail: the r79 marks hold a pid only (S79CriticDiscern F1), so the demonstration is the r80 counter's own red row on an s3-style directory name |
| M2 | diagnosis before evidence: the A s4 failure was taken for a pending-signal race and a repair (R1, ticker + `wait -n`) was committed before any probe of the cause; the cause was SIGINT ignored on entry, inherited from the `&` launch | R1 `4a9bbb30`; `records/repair/c1-at-R1-run1..3.txt` (s4 red 3/3 with the repair); `records/foreground/sigint-inherit.txt` | none at the time (the probe was written after R1; it is now the capturer for this class) | QUALITY Q143 (probe the inherited disposition before a repair); `census/round-79/probes/sigint-inherit.sh` exits 0 only when the background arm shows the ignore, and exits 1 when run under `trap '' INT` (`records/foreground/sigint-inherit-under-ignored-int.txt`, EXIT=1) — the fix can fail; R1 reverted at R2 |
| M3 | measurement environment: every control and after-arm receipt was launched with `&` from a script (parallel receipts), so each INT row ran with an untrappable INT; the controls' s4 verdicts say nothing about the gates | `census/round-79/controls/c1-K-*.txt` s4 rows; A `records/c1-after.txt` | none (the counter does not reset or record dispositions); now `census/round-79/probes/sigint-inherit.sh` | Q143; the r80 C1 counter resets SIGINT/SIGQUIT to default in each gate child (`preexec_fn`) and prints the disposition it ran with; SKILL row r79 says to run the r79 counter in the foreground |
| M4 | wrong reasoning shape for a flake: a single red row under load was read as a timing race; the deterministic 3/3 repeat at R1 refuted it the first time it was looked at | `records/repair/` (3/3) vs every L1 scratch probe of the same rows, all launched in the foreground, which passed (24 rows unloaded, 84 under load; scratch only, not receipts) | none | before calling a failure flaky, repeat it under the SAME launch path as the failing receipt (here `rec.sh … &`), not under a convenient one; bound to the committed probe: `census/round-79/probes/sigint-inherit.sh` prints the disposition each launch path hands down and fails (EXIT=1) when the foreground arm is also ignored (`records/foreground/sigint-inherit-under-ignored-int.txt`) |

## Gate

- **S325 admit (A, mined)** — GNU Bash 5.3 Reference Manual node "Signals" as installed: `/usr/share/info/bash.info.gz`
  owned by bash 5.3.20-1 (`pacman -Qo`), sha256 `cde1a3366897684b0a86fe553687e31d070b7839b19ca98186ffc6e0e105588f`,
  opened 2026-11-07 by the L1 (capture `census/round-79/srcs/bash.info.gz-5.3`, node text
  `census/round-79/srcs/bash.info-5.3-Signals.txt`). Decompressed lines 3281-3283: "it will not execute the trap
  until the command completes. If Bash is waiting for an asynchronous command via the ‘wait’ builtin" (22 words).
  Line 3262 (second proposition used by M2/M3): "When job control is not in effect, asynchronous commands ignore
  ‘SIGINT’ and ‘SIGQUIT’". Cited by `corpus/knowledge/gate-signal-handling.md` and Q142/Q143; grounds the sourced
  claim C1.
- **S326 admit (A, mined)** — https://raw.githubusercontent.com/coreutils/coreutils/v9.12/src/timeout.c, sha256
  `bf1f0d998729f12ddd2323d69db34648763d807d9c4d769eb1414a8738652cc9`, 21183 bytes, HTTP 200, accessed 2026-11-07
  by the L1 (capture `census/round-79/srcs/coreutils-timeout.c-v9.12`; the host's /usr/bin/timeout is coreutils
  9.12-2). Lines 567-572: "Ensure we're in our own group so all subprocesses can be killed." (12 words) and
  `if (!foreground) setpgid (0, 0);`; cleanup() at line 204 forwards a received signal to the child and to group 0.
  Cited by the knowledge entry and Q142.
- **Rejected (L1): https://www.gnu.org/software/bash/manual/html_node/Signals.html and
  …/coreutils/manual/html_node/timeout-invocation.html** — curl exit 28 (no connection after ~135 s) on
  2026-11-07 ~02:00 -03; not opened, nothing to admit. Flip: reachable and identical in substance → may replace
  the installed-info locator.
- **Rejected (L1): https://raw.githubusercontent.com/bminor/bash/{master,devel,bash-5.3}/doc/bashref.texi** —
  HTTP 404 (14 bytes) each; a mirror path guess, not a source. Flip: a verified mirror path.
- **Rejected (L1): coreutils timeout.c at master** (fetched first, sha256 `ea8fa3ef…01bb`) — replaced by the v9.12
  tag, the version installed on this host; the master copy was deleted before P. Flip: a claim about a later
  release.
- No other row's status, recheck or used-by cell changed. Within-scope duplicates: `git show
  e65538e7:corpus/SOURCES.md | grep -cF 'timeout.c'` = 0 and `… | grep -cF 'bash.info'` = 0 before append (the
  first draft wrote the unescaped regex `grep -c 'timeout.c'`, which counts 1 on S094's "timeout current-version";
  S79CriticDiscern F7); the
  same-family bash rows (S043, S065, S072, S233) and timeout manual rows (S034, S038, S094, S098) are other
  scopes, declared in the SOURCES `Round-79 provenance` line.
- Census: before `census/round-79/records/census-before.txt` (souji ok, EXIT=0); after in
  `census/round-79/records/census-after.txt`.

## Wave

One v1 wave `w1`, 12 seats (connector 1, scout 1, executor 3, mutation-tester 2, reviewer 1, critic 2, sentinel 1,
scribe 1; attack seats reviewer + critics + mutation-testers = 5 of 12, 42 %), validated under
`scripts/hyaku/ufo-wave-policy.json` (band 8-16, spawn 12) and dispatched through the inline handoff. The
dispatcher held the wave 02:28-03:20 (orchestrator incident: a kama seat's leaked load probes kept the host load
above the spawn gate; Main's message, not this lane's fault). 0 dead seats. Seat files are mirrored under
`census/round-79/records/wave-w1/`.

| seat | verdict | disposition |
|---|---|---|
| S79Connector | C1/C2 SEPARABLE; lane `tools/souji-quarantine.sh` (7 foreground `timeout` calls, no trap) and `souji-vault-verify.sh`; siblings chousa research-gate, mado-verify, mori-census run foreground `$(timeout)` with no trap | routed r80 (lane tools); sibling rows documented only |
| S79ScoutSources | S325/S326 sha256 match; both bash sentences HOLD; no pending-signal race exists (bash 5.3.20 `wait.def:193` reads `first_pending_trap()` before blocking) — R1's premise false; SIGINT-ignored-on-entry HOLDS (`trap.c:851-854`); F2 the "cannot trap" rule sits in node Bourne Shell Builtins, not Signals | F2 applied (S325 teaches cell gains lines 3942-3943; knowledge entry); F3 timeout's SIG_IGN carve-out added to the knowledge entry; F1/F4/F5 already disclosed (M1, M2) |
| S79ExecC1 | W1 foreground 13/13 runs 11/11; `&` launch 13/13 runs fail only s4 with the A signature; K-b/K-c reproduce; regressions reproduce | agrees with M2/M3; report names the foreground receipts as the 0/0 carrier and `c1-after.txt` as the red frozen measurement |
| S79ExecEvade | 171 timing probes, 0 kill-rule violations; MEDIUM-1 a grandchild of an earlier, finished child survives (setsid, double fork); LOW ulimit, 100 MB output, unwritable TMPDIR exit 2 | MEDIUM-1 recorded as a limit (knowledge entry) and routed r80; LOWs routed |
| S79MutGate | frozen counter kills 7/12; M01 (no group kill) and M02 (no pid kill) survive (timeout's PR_SET_PDEATHSIG covers the direct child); HIGH M09 (no `<&0`: byte-truth block vacuous) survives C1, r78, r36 | M09: the round's own r76 regression conjunct kills it (`census/round-79/records/wave-responses/m09-vs-r76.txt`, 13 mismatches) — the seat ran only r78/r36; M01/M02: qualification "group kill untested", knowledge entry corrected, grandchild row routed r80 |
| S79ExecC2 | C2 reproduces; ITEM lines of r77/r78 populations identical under r78 and r79 counters (no verdict moves) | agrees |
| S79MutCounter | 13 mutants of the four r79 rules: 5 killed, 8 survive; the r79 counter still accepts NF6a (declaration in a line that refuses the quarantine — the prereg's stated limit), NF6b (token and target matched as substrings of other paths, MEDIUM), NF8 (a range member that is a directory), NF10 (byte-equal MOVED copy in an unrelated subtree at the right round) | qualification on C2: 5 → 0 holds on the frozen population; the instrument is not complete — NF6b/NF8/NF10 and the detector rows DM01/DM07/DM11 routed r80 |
| S79Reviewer | C1 predicate met on W1 bytes conditioned on the inherited disposition (MEDIUM-1); MEDIUM-2 the domain trial's fixed 3 s delay can miss a fast gate; LOW-5 new fail-closed paths (config rc check, contract-checker bound, NUL truncation) | MEDIUM-2 fixed before the trial ran (signal when a second marked process exists); LOW-5 recorded (all fail closed) |
| S79CriticClaims | HIGH-1 SCORECARD/LOG "kill rule is met at A" read as a pass while A is red; MEDIUM-2 K-b/K-c INT arms are launch artefacts; MEDIUM-3 group clause untested; MEDIUM-4 s3/s4; MEDIUM-5 domain trial receipt absent | HIGH-1 accepted: wording now "C1 FAILS its frozen kill rule at A" in SCORECARD, LOG and this lesson; MEDIUM-2/3/4 recorded as qualifications; MEDIUM-5 closed by the trial receipt |
| S79Sentinel | MEDIUM M1 `$gate_tmp/o` re-opened by path: a writer on a non-sticky 0777 TMPDIR parent can redirect it (default /tmp sticky, not exploitable); M2 TMPDIR inside the lane fails clean (closed) and echoes its own scratch path | routed r80 (open the output file once / refuse a non-sticky shared TMPDIR) |
| S79Scribe | drafts for S325/S326 rows, the knowledge entry, Q142/Q143, census validate | **wrote its knowledge draft over the lane's tracked `corpus/knowledge/gate-signal-handling.md`** (03:17; scope breach, M5); the L1 restored the committed text and kept its own entry |
| S79CriticDiscern | sources agree (code is the right citation for the group behaviour); F1 M1's "shown able to fail" was false; F2 two dangling receipts; F3 prereg omits "signal ignored on entry"; F4-F7 lesson wording | F1/F4/F5/F7 applied to Mistakes and Gate; F2 closed by landing census-after and the trial receipt; F3 stated in the report |

## Mistakes (wave)

| # | class | evidence pointer | captured-by | fix |
|---|---|---|---|---|
| M5 | seat scope breach: S79Scribe wrote its draft over a tracked lane file instead of its seat directory | `git diff` of `corpus/knowledge/gate-signal-handling.md` at 03:17 equals `census/round-79/records/wave-w1/seats/S79Scribe/knowledge-gate-signal-handling.md` | the L1's `git status --porcelain` before integration | restored from master; next wave contexts name the drafted file's seat path in the item's acceptance line and forbid the lane path by name |
| M6 | an unverified sentence in the L1's own knowledge draft: "killing the group is the part that matters" — the frozen rows cannot tell a pid kill from a group kill (timeout's PR_SET_PDEATHSIG) | S79MutGate M01/M02 survive 11/11 | S79MutGate, S79CriticClaims MEDIUM-3 | sentence rewritten with the PDEATHSIG fact (S326 lines 608-610); a grandchild row routed r80 |

## Routed to round 80

- (a) C1 instrument successor: shim argv recorded at the mark and the subcommand asserted (M1); signal dispositions
  reset in each gate child and printed (M2/M3); a per-row duration bound and `timeout`'s own group in the r78
  counter's cleanup (r78 routed (a)).
- (b) the check-4 300 s backstop row (carried since r77).
- (c) r76 K03/K04; the status-trusting and unguarded lane tools (receipt writer, pointer and freeze checks, landing
  gate, `souji-verify.sh:550,594`, `souji-census.sh`), and the foreground-`timeout` lane tools S79Connector listed
  (`tools/souji-quarantine.sh`, `tools/souji-vault-verify.sh`).
- (d) wave routes: a grandchild/escape row and a group-kill-only row for C1 (S79ExecEvade MEDIUM-1, S79MutGate
  M01/M02); the gate's output file opened once or a non-sticky TMPDIR refused (S79Sentinel M1); C2 counter rows
  NF6b, NF8, NF10 and detectors DM01/DM07/DM11 (S79MutCounter).
