author: hyaku closure (non-author integrator, @m_zfl)

# Round 94 verifier spot-check — souji (non-author, hyaku closure)

Lane: `souji-shokunin`, branch `master`. Lane base `eddb1be6c34c2e0bef8c1e8ae6ea2f4b381c5536` (r93 closed); lane
HEAD after the round `22060315c479e6af49e96fc23d84951752dd1f59`. Report `.ufo/reports/round-94/souji.md`. Closed
2026-11-09 (UTC 05:1x).

Dispatch/complete digest copied from this round's closure prompt (mutable `.ufo/watchdog.log`; the live log shows
the same two lines at 3450/3455):

`2026-11-09T01:14:17-03:00 launch souji round=94 pgid=2194192 driver=hyaku-inline attempt=1`
`2026-11-09T02:14:31-03:00 complete souji round=94; hyaku-inline attempt=1`

## 1. Step-1 conformance

- **Report identity: PASS.** `git log --format='%an %ae %H' -- .ufo/reports/round-94/souji.md` -> `souji-shokunin
  souji@shokunin.local 3242664061887eb7ad8591b0b913bba300788d8b`; committer date 02:13:49-03:00, after the lane tip
  (`22060315` committer 02:13:34) and before the 02:14:31 complete line. Not a marker: six round commits, receipts,
  three source rows, a checkable tip.
- **`SHONEN` heading: PASS.** One `## SHONEN` heading, four `[~]` lines each with a pointer; `SHONEN.md` has 4 boxes
  (`grep -c '^- \['` -> 4), none `[x]`. `SHONEN.md`, `SKILL.md`, `PROVINCE.md`, `tools/` unchanged (`git diff
  --name-status eddb1be6 22060315 -- SHONEN.md SKILL.md PROVINCE.md tools/ corpus/QUALITY.md corpus/knowledge/` -> only
  `M corpus/QUALITY.md`, `A corpus/knowledge/mutant-crash-is-not-a-kill.md`).
- **Cited lane commits: PASS.** `git cat-file -t` -> commit and `git merge-base --is-ancestor <h> refs/heads/master`
  exit 0 for the base, `24cd67b0`, `39d4163a`, `4ad74b9d`, `b065b7f0`, `0e5bc086`, `22060315`; `git log
  eddb1be6..master` lists exactly these six, all authored `souji-shokunin`, order P1 -> P2 -> F -> A -> integration ->
  wave evidence (committer dates monotonic 01:23:25 .. 02:13:34). `24cd67b0`'s author date (01:13:26) precedes the
  launch line: a jj change-creation stamp, committer date 01:23:25 is after launch — informational, not a defect.
- **Lane state: PASS.** `scripts/hyaku/jj-lane.sh state` -> `branch=master local=22060315… remote=22060315… ahead=0
  behind=0 head=detached tracked=0 untracked=0`; `git status --porcelain` empty (also after my re-runs);
  `ls-remote origin refs/heads/master` -> `22060315c479e6af49e96fc23d84951752dd1f59`.
- **Prompt: PASS.** `.ufo/prompts/souji-round-94.md` (committed by `souji-shokunin` in `428127d6`, 1002 lines) carries
  §1 mission/axes binding (lowest-axis duty), §2 claims, §2b frontier step, §3 L2 floor, §4 report contract (path,
  SHONEN, hash citation, LOG tie), §5 commit/push scope/L0 channel, §6 hyaku addendum, §7 scratch, §8 Amendment 59.
- **Diff shape.** `git diff --stat eddb1be6 22060315` -> 800 files, 60298 insertions; `git diff --numstat` rows with a
  nonzero deletion count: none (append-only round).

## 2. Per-claim re-check (re-measured, not only evidence-verified)

Instruments exported with `git archive 22060315` into `/fast/scratch/hyaku/souji-r94/CloseSoujiR94/x` (removed
after), `TMPDIR` set under it, `--lane` pointing at the lane checkout (r93 A4: the harness needs a git repo). Pins
re-derived with `sha256sum`, all matching the preregistration and receipts: search `97b8defa…`, targets `0117cad7…`,
r93-rule control `b733032f…`, r94 probe `e3ebe6e9…`, arms counter `3bb8c1b9…`, r93 probe `f3c84c49…`, counter
`fd0a8e24…`, harness `1868a570…`, population `d6439f65…`, fixtures `ed15094e…`/`2c9bd76c…`, tool `fc0e35c2…`,
before `21e5c740…`. F `4ad74b9d` touches only `census/round-94/preregistration.txt`; the after receipts (A
`b065b7f0`) follow it.

### C1 — calibration 7: RE-MEASURED, VERIFIES (limit (ii) narrowed by A1)

- Before (do-nothing), `python3 -B census/round-94/c1-control-r93-rule.py --counter census/round-87/c1-pointer-counter.py
  --harness census/round-93/c1-false-row-harness.py --population census/round-93/c1-false-rows.tsv --lane <lane>
  --fleet-root /home/vgpnk/Projects/shokunin --jobs 5 --ids census/round-94/c1-targets.json --work <new>` ->
  `h-crash-late killed=yes rc=1`, `h-crash-index killed=yes rc=1`, `SEARCH-SUMMARY generated=5 ambiguous=0
  uncompiled=0 hung=0 scored=5 errored=0 killed=4 survived=1`, EXIT 0. Matches `controls/c1-control-r93-rule.txt`:
  2 crash fixtures scored killed.
- After, same args with `census/round-94/c1-survivor-search.py` -> `# crash-sentinel rc=70 check=pass`,
  `a127c26-True-to-False killed=no`, `a491c22-<-to-<= killed=yes`, `h-ok-admits-one killed=yes`, `h-crash-late
  killed=errored`, `h-crash-index killed=errored`, `SEARCH-SUMMARY … scored=5 errored=2 killed=2 survived=1`, EXIT 0.
  Matches `records/c1-after.txt`: 2 -> 0 crash fixtures scored killed, three non-crash verdicts unchanged.
- Mechanism (A3 reading, checked): the per-mutant harness outputs show `rc=70` rows only on the two crash fixtures —
  `grep -c 'rc=70'` -> m0003 (h-crash-late) 66, m0004 (h-crash-index) 1 (`ROW LD6 … got=- rc=70 match=no`), m0000-m0002
  0. The errored verdicts come from the sentinel, not from a fitted rule.
- Forgery controls evidence-verified (not re-run): `controls/c1-forgery-controls.txt` FA `killed=0`, FB `errored=0`,
  refused 2/2.
- Ledger rows on C1 (A1): `R94ScoutSources/repro-sysexit-gap.out` read by me — `CASE SystemExit(1): child rc=1
  verdict=yes`, `CASE os._exit(1): … verdict=yes`; R94Sentinel atexit/`__del__` goes to `unraisablehook`. These falsify
  the prereg's limit (ii) list, not the five-target predicate; A1 narrows the limit and S359 grounds it. Reconciled.

### C2 — operability 8: RE-MEASURED, VERIFIES (probe docstring narrowed by A4)

- Before (do-nothing), `python3 -B census/round-94/c2-setup-arms.py --probe census/round-93/c2-forgery-probe.py
  --fixture-pass tests/fixtures/r93-k4-flagfail.py --fixture-fail tests/fixtures/r92-k4-flagfail.py --tool
  tools/souji-record-agreement.py --before census/round-92/controls/c2-before-tool.py --work <new>` -> P1/P2/S2
  conform, S1 and S3-S8 `exit=1 … conform=no`, `ARMS-SUMMARY arms=10 conform=3`, exit status 1. Matches
  `controls/c2-control-r93-probe.txt`.
- After, `--probe census/round-94/c2-forgery-probe.py` -> P1 exit 0, P2 exit 1, S1 exit 0, S2-S8 exit 2, all
  `line=yes conform=yes`, `ARMS-SUMMARY arms=10 conform=10`, EXIT 0. Matches `records/c2-after.txt`: 3 -> 10.
- Forgery controls evidence-verified (not re-run): `controls/c2-forgery-controls.txt` GA/GB conform=9 each, refused 2/2.
- Ledger rows on C2 (A4): R94Critic (non-UTF-8 `--tool` -> UnicodeDecodeError, exit 1), R94ReviewerC2 (file-parent
  `--work` NotADirectoryError exit 1), R94Sentinel F6 (mid-run write failure exit 1) falsify the probe docstring "Every
  setup failure exits 2", which is not the claim; the claim's "every other setup arm" is scoped to the counter's ten
  arms and holds. A4 narrows the docstring statement; the uncovered setup shapes are routed (§5). Reconciled.

### Pre-file falsification ledger (Amendment 59)

`python3 scripts/hyaku/prefile-falsification.py --lane souji --round 94` -> `PREFILE-FALSIFICATION: pass claims=2
rows=23 attack_seats=7 findings=0`, EXIT 0 (same as the committed receipt `.ufo/waves/round-94/prefile-gate.txt`).
Nine `falsifies-wording` rows, each narrowing `plans/round-94.md` (A1 for C1's four rows, A4 for C2's five); every
one I read is answered by its amendment. No unreconciled row.

### Axis verdicts

| axis | verdict | basis |
|---|---|---|
| calibration | improved | crash fixtures scored killed 2 -> 0 re-measured, mechanism confirmed by `rc=70` rows; score held at 7 (no mapping) |
| operability | improved | forgery-probe arms conforming 3 -> 10 re-measured; score held at 8 (no mapping) |
| coverage | unchanged | not claimed; SCORECARD diff adds only r94 rows, no owned axis value changed |

No owned axis harmed: `git diff eddb1be6 22060315 -- SCORECARD.md` is append-only (r94 measurement rows, capability
rows, `### Planned (r95)`), no `-` lines; zero deletions repo-wide. C1 works the lowest owned axis (calibration 7).

## 3. Discernment spot-check (`corpus/lessons/round-94.md` `## Gate`)

Re-opened live with `curl -sL` (2026-11-09): sysexits 59385 bytes, Python `sys` 280632 bytes, Stryker 27068 bytes
(byte counts equal the rows' captures), PIT `DetectionStatus.java` @1.30.2 2988 bytes; quotes counted in
whitespace-normalized, tag-stripped text.

| item | decision | re-opened source | agree/disagree | reason |
|---|---|---|---|---|
| S358 sysexits(3) EX_SOFTWARE | ADMIT (docs, A, mined) | man.freebsd.org sysexits, live | agree | "EX_SOFTWARE (70) An internal software error has been detected." found once (9 words); it is exactly the exit status the sentinel uses, and the row's scope is limited to that entry |
| S359 Python `sys.excepthook` | ADMIT (docs, A, mined; after the wave) | docs.python.org/3/library/sys.html, live | agree | 17-word quote found once; it is the sentence that makes SystemExit invisible to the hook — the falsification A1 narrows to — so the row grounds the narrowing, not a new claim |
| S357 Stryker mutant states | ADMIT (docs, A, mined) | stryker-mutator.io, live | agree | "The running of the tests resulted in an error (rather than a failed test)." found once (14 words); the Runtime error state is the `errored` class the r94 rule introduces |
| PIT `DetectionStatus.java` @1.30.2 `RUN_ERROR` | REJECT (not filed) | raw.githubusercontent.com, live | agree | javadoc "Something went wrong. Don't know what but it was probably bad." at line 61, `RUN_ERROR(true)` line 63, as the lesson says; it duplicates S357's distinction for a Java tool the lane does not run and no entry would consume it; flip stated |

New `SOURCES.md` rows: `git diff --numstat eddb1be6 22060315 -- corpus/SOURCES.md` -> `3 0`; row count 278 at base,
281 at tip (`grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'`). Quotes for S357/S358/S359 all <=25 words and present.
`scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` -> `souji ok`, EXIT 0 (W04
duplicate-URL warnings only, pre-existing; none on S357-S359).

## 4. Trend verdicts

- **expansion: improved.** Three admitted tier-A rows (live-verified) and a knowledge entry
  (`corpus/knowledge/mutant-crash-is-not-a-kill.md`, citing S357/S358/S359) on ground the lane did not hold (runtime
  error vs killed; sentinel exit status), plus two capability rows backed by re-measured commands.
- **quality: improved.** Two instruments whose exit codes misreported are fixed and re-measured by me against their
  predecessors on committed bytes (C1 2 -> 0; C2 3 -> 10); the reported census shows 28 historical crash kills the old
  rule counted. No admitted entry failed its re-check.
- **discernment: improved.** The four-item sample (three admits, one reject) agrees with the gate; the lane narrowed
  the two sentences its wave falsified (A1, A4), grounded the unsourced premise (A2) and recorded two predicate
  readings (A3, A5) instead of defending them; Q171 extends Q170 from this round's lesson.

## 5. Routed defects (lane fixes next round)

1. C1 sentinel blind spots (A1): SystemExit, `os._exit`, atexit/`__del__` (unraisablehook) and thread exceptions are
   still scored `yes`/`no`; add fixtures for each and either classify or name them in the verdict.
2. C1 harness-side crash target: no target binds the "harness exit 70" disjunct of the r94 rule (R94MutC1 M2,
   R94Sentinel F3).
3. C2 probe still exits 1 on a non-UTF-8 `--tool`/`--before`, a file-parent `--work` and a mid-run write failure (A4);
   no fixture timeout (F5); `--work` TOCTOU and `/tmp` itself (F7, F9).
4. Carried from r93 (still open): item 1 harness reproducibility from committed bytes; item 3 m5/m6/g2 clauses and
   the 76 residual survivors; item 4 KFF19 second length/filler and fixture-scorer exceptions.
5. Seat hygiene: R94ScoutSources' repro wrote a hook dir under `/var/tmp` (removed on exit per its own output) rather
   than the round scratch root; keep seat temp under `/fast/scratch/hyaku/souji-r94/`.

Operator note: SHONEN boxes remain `[~]` (author-asserted); the four pointers are checkable by a non-author, but
promotion is operator-owned and not acted on here.
