# Round 94 — a crash is not a kill: a sentinel exit code lets the survivor search see it; the forgery probe keeps setup failures off its verdict code

Lane base `eddb1be6c34c2e0bef8c1e8ae6ea2f4b381c5536` (r93 closed admitted; spot-check
`corpus/lessons/round-93-verifier-spotcheck.md`). Instruments P1 `24cd67b0`, controls P2 `39d4163a`; freeze F
`4ad74b9d`; after receipts A `b065b7f0`. Wave: one v1 wave, 12 seats, `w1`. Attempt 1 (SoujiR94).

## Claims

- **C1 (calibration 7, the lane's lowest owned non-retired axis).** The r93 kill rule scores a mutant whose counter
  raises an uncaught exception as killed: a Python crash exits 1, the counter's own "not every item resolved" code,
  and the harness marks the rows the crash spoils `match=no`. On five targets (two crash fixtures, two r93 semantic
  kills, one survivor) the r93 rule prints `errored=0 killed=4 survived=1`
  (`census/round-94/controls/c1-control-r93-rule.txt`). The r94 search puts a `sitecustomize.py` on PYTHONPATH whose
  `sys.excepthook` exits 70 (S358 EX_SOFTWARE), so the crash reaches the harness's ROW lines as `rc=70`, and scores
  any rc=70 as `errored` (S357's Runtime error state): `errored=2 killed=2 survived=1`
  (`census/round-94/records/c1-after.txt`). Forgeries FA (refuse every non-zero exit) and FB (no sentinel) both miss
  the predicate (`controls/c1-forgery-controls.txt`).
- **C2 (operability 8).** The r93 forgery probe exits 1 — "a forgery survived" — on 7 of 8 setup arms (an existing
  empty `--work`, a file as `--work`, a missing fixture/tool/before, a mute fixture, a fixture that crashes on
  forgeries); the arms counter reads `conform=3` of 10 (`controls/c2-control-r93-probe.txt`). The r94 probe runs on
  an empty existing `--work`, refuses the rest with exit 2 and a `C2-FORGERY-FATAL:` line, and keeps its verdict
  exits 0/1: `conform=10` (`records/c2-after.txt`). Forgeries GA (verdict exit 2) and GB (refuse the empty dir) each
  read `conform=9` (`controls/c2-forgery-controls.txt`).

## Gate

Registry rows added this round (all opened 2026-11-09 by the L1; S357/S358 captures committed in P1, S359 after the
wave) and the reject sample:

| row | URL | access date | located quote (<=25 words) | locator | decision |
|---|---|---|---|---|---|
| S357 | https://stryker-mutator.io/docs/mutation-testing-elements/mutant-states-and-metrics/ | 2026-11-09 | "The running of the tests resulted in an error (rather than a failed test)." (14 words) | § Mutant states, Runtime error entry; tag-stripped text of `census/round-94/srcs/stryker.html` (sha256 30071cc7…), occurrence count 1 | ADMIT, `mined`, cited by `corpus/knowledge/mutant-crash-is-not-a-kill.md` |
| S358 | https://man.freebsd.org/cgi/man.cgi?query=sysexits | 2026-11-09 | "EX_SOFTWARE (70) An internal software error has been detected." (9 words) | § DESCRIPTION, EX_SOFTWARE entry; tag-stripped text of `census/round-94/srcs/sysexits.html` (sha256 da498cbc…), occurrence count 1 | ADMIT, `mined`, cited by the same entry |
| S359 | https://docs.python.org/3/library/sys.html#sys.excepthook | 2026-11-09 | "When an exception other than SystemExit is raised and uncaught, the interpreter calls sys.excepthook with three arguments" (17 words) | § `sys.excepthook`; tag-stripped text of `census/round-94/srcs/sys.html` (sha256 310d2ebd…), occurrence count 1 | ADMIT after the wave, `mined`, cited by the same entry's r94 corrections (A1/A2) |
| — | https://raw.githubusercontent.com/hcoles/pitest/1.30.2/pitest/src/main/java/org/pitest/mutationtest/DetectionStatus.java | 2026-11-09 (R94ScoutSources) | "Something went wrong. Don't know what but it was probably bad." (11 words, `RUN_ERROR` javadoc, lines 60-63) | `.ufo/waves/round-94/w1/R94ScoutSources/receipts/pit-DetectionStatus-1.30.2.java` sha256 3bf295ad… | REJECT (not filed): out of province (souji runs no Java tool) and no consuming entry; flip: a lane instrument classifies by PIT's vocabulary, or an entry on cross-tool crash classification cites it |

Status/recheck/used-by changes to existing rows: none (`git diff eddb1be6 -- corpus/SOURCES.md` → 2 added lines, 0
removed before the wave; S359 added after it, 3 added lines total). Registry 278 → 281. Census `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji`
EXIT 0 at both ends (`census/round-94/records/sources-census-before.txt`, `sources-census-after.txt`).

Assimilation: none this round (no `merge/souji/` theme taken). considerthese: the lane has no `considerthese/` dir.

## Mistakes

- **M1 — an assumption about a crash's exit code, written into a docstring and a prereg, never run.** Class:
  unverified mechanism claim. Evidence: the r93 search docstring "(the counter crashed, rc 2)"
  (`census/round-93/c1-survivor-search.py` lines 6-7) and the r93 prereg "tighter than r84-r92"; R93Sentinel M1
  showed a Python crash exits 1. Captured-by: Q170 (written in r93 after the fact); nothing before it. Fix: r94 puts
  two crash fixtures in the targets and runs the frozen r93 rule on them first — it scores both `killed=yes`
  (`census/round-94/controls/c1-control-r93-rule.txt`), so the fix is shown able to fail; the r94 search refuses to
  score anything unless its sentinel fires in a child (`# crash-sentinel rc=70 check=pass`).
- **M2 — an instrument whose verdict exit code is also its crash/setup exit code.** Class: overloaded exit status.
  Evidence: `census/round-93/c2-forgery-probe.py` `os.makedirs(work)` on an existing empty dir → FileExistsError,
  exit 1 (r93 spot-check §5 item 5); `controls/c2-control-r93-probe.txt` shows six more setup shapes at exit 1.
  Captured-by: none (no criterion asked that exit 1 be reachable only by a verdict). Fix: the r94 probe plus the
  arms counter, which fails the r93 probe (conform=3) — shown able to fail; criterion Q171 below.
- **M3 — a limits sentence that enumerates what a mechanism misses, written from reading.** Class: non-exhaustive
  enumeration presented as the complement of a coverage claim (r93 M5's class: a clause written from reading).
  Evidence: prereg C1 limit (ii) listed os._exit, signals, threads and a legitimate 70; the wave found SystemExit
  (`.ufo/waves/round-94/w1/R94ScoutSources/repro-sysexit-gap.out`, rc=1 verdict=yes) and atexit/`__del__`
  (`.ufo/waves/round-94/w1/R94Sentinel/receipts/out-F.txt`, scored survived). Captured-by: Amendment 59 (the wave's
  own falsification), not a lane criterion. Fix: limit narrowed (plans/round-94.md A1); routed to r95: SystemExit and
  atexit crash fixtures in the targets — today's search scores them `yes`/`no`, so the fixture is able to fail.

## Wave findings

One v1 wave, 12 seats, all settled with a report (`.ufo/waves/round-94/w1-results.json`); amendments A1-A5 in
`plans/round-94.md`; ledger `.ufo/waves/round-94/claim-falsification.tsv`.

- Numbers: R94ExecC1, R94ExecC2, R94ReviewerC1, R94Critic, R94Scribe re-ran the predicates and controls on committed
  bytes; every summary matches.
- Full census (R94ExecCensus, reported): r93 rule `errored=20 killed=167 survived=76`, r94 `errored=48 killed=139
  survived=76` over 273 mutants; 28 verdicts change, all `yes`→`errored`, all with `rc=70` rows. 28 of 167 r93-rule
  kills (16.8 %) were crashes.
- Wording: A1 (SystemExit, atexit/`__del__` not seen), A2 (exit-1 premise unsourced → S359 + own receipts), A4 (the
  probe docstring's "every setup failure" — non-UTF-8 tool, file parent, write failure exit 1).
- Strength: A3 (a fitted no-sentinel rule also meets the five-target number), A5 (arm-name fitting reaches 10/10;
  edit-once and /tmp guards unbound).
- Overlap: none owned by a sibling (R94Connector); kama's `error-is-not-a-verdict` doctrine is the nearest.

## Routed to round 95

- C1: SystemExit, atexit and `__del__` crash fixtures (R94ScoutSources, R94Sentinel F1/F2); a harness-side crash
  target so the exit-70 disjunct is bound (R94MutC1 M2, R94Sentinel F3); make the precondition line truthful (M8);
  bind `endswith(' match=no')` (M6); bare `got=-` rows; carried r93 items 1 and 3.
- C2: catch decode/write exceptions in the probe as exit 2; a fixture timeout (R94ReviewerC2 T9, R94Sentinel F5);
  `--work` TOCTOU and `/tmp` itself (F7, F9); arms for edit-once and /tmp (R94MutC2 M10/M11); randomized arm names
  (R94Critic); the arms counter's own uncaught exceptions exit 1 (R94Connector, R94Sentinel F8); carried r93 item 4.
