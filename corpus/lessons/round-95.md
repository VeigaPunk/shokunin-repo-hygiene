# Round 95 — the crash sentinel watches five more ways a counter can die; the forgery probe refuses undecodable inputs, an uncreatable work dir and a hanging fixture

Lane base `93c3ef13a9eb9678483518562f3692124db714c2` (r94 closed admitted; spot-check
`corpus/lessons/round-94-verifier-spotcheck.md`). Instruments P1 `d79bc3fe`, controls P2 `48c5efe9`; freeze F
`59fd7be0`; after receipts A `dd520684`. Wave: one v1 wave, 13 seats, `w1`. Attempt 1 (SoujiR95).

## Claims

- **C1 (calibration 7, the lane's lowest owned non-retired axis).** The r94 sentinel only replaced `sys.excepthook`,
  which never sees SystemExit (S359); an atexit-callback exception, a thread exception, `os._exit` and a signal death
  keep their own status. On five crash-channel fixtures the frozen r94 search says h-sysexit/h-osexit/h-sigkill
  `killed=yes` and h-atexit/h-thread `killed=no` (`census/round-95/controls/c1-control-r94-rule.txt`: `errored=2
  killed=5 survived=3`). The r95 search exits 70 on `sys.unraisablehook`, `threading.excepthook` (S361), any
  `os._exit` call (S362) and a SystemExit first raised inside a main-script function (a `sys.monitoring` RAISE
  callback, S360), and scores a negative `rc` errored (S363): `errored=7 killed=2 survived=1`, the five r94 targets
  unchanged (`census/round-95/records/c1-after.txt`). Forgeries FA (refuse every non-zero exit), FB (no sentinel) and
  FC (no signal leg) all miss the predicate (`controls/c1-forgery-controls.txt`).
- **C2 (operability 8).** The r94 probe exits 1 on a non-UTF-8 `--tool` (S9) or `--before` (S10) and a `--work` under
  a regular file (S11), and never ends on a hanging fixture (S12): the sixteen-arm counter reads `conform=12`
  (`controls/c2-control-r94-probe.txt`). The r95 probe refuses all four with exit 2 and a `C2-FORGERY-FATAL:` line:
  `conform=16` (`records/c2-after.txt`). Forgeries GA (verdict exit 2), GB (decode with `replace`) and GC (no
  timeout) read 15, 14 and 15 (`controls/c2-forgery-controls.txt`).

## Gate

Registry rows added this round (all opened 2026-11-09 by the L1 from docs.python.org/3, Python 3.15 documentation;
captures committed in P1 under `census/round-95/srcs/`, tag-stripped text beside each):

| row | URL | access date | located quote (<=25 words) | locator | decision |
|---|---|---|---|---|---|
| S360 | https://docs.python.org/3/library/sys.monitoring.html | 2026-11-09 | "An exception is raised, except those that cause a STOP_ITERATION event." (11 words) | § Events, `sys.monitoring.events.RAISE`; `srcs/monitoring.html` sha256 cd85fa73…, occurrence count 1 | ADMIT, `mined`, cited by `corpus/knowledge/crash-channels-beyond-excepthook.md` |
| S361 | https://docs.python.org/3/library/threading.html#threading.excepthook | 2026-11-09 | "Handle uncaught exception raised by Thread.run() ." (7 words) | § Reference, `threading.excepthook` (corrected after the wave: the page has no `Functions` heading, R95ScoutSources DEFECT-1); `srcs/threading.html` sha256 d6f8ca65…, occurrence count 1 | ADMIT, `mined`, same entry |
| S362 | https://docs.python.org/3/library/os.html#os._exit | 2026-11-09 | "Exit the process with status n , without calling cleanup handlers, flushing stdio buffers, etc." (15 words) | § Process Management, `os._exit`; `srcs/os.html` sha256 078e69b1…, occurrence count 1 | ADMIT, `mined`, same entry |
| S363 | https://docs.python.org/3/library/subprocess.html#subprocess.Popen.returncode | 2026-11-09 | "A negative value -N indicates that the child was terminated by signal N (POSIX only)." (15 words) | § CompletedProcess.returncode and § Popen.returncode; `srcs/subprocess.html` sha256 7f5772d7…, occurrence count 2 | ADMIT, `mined`, same entry |
| S364 | https://docs.python.org/3/library/atexit.html | 2026-11-09 | "If an exception is raised during execution of an exit handler, a traceback is printed (unless SystemExit is raised) and the exception information is saved." (25 words) | § atexit, module introduction; `srcs/atexit.html` sha256 765f26c2…, occurrence count 1 | ADMIT, `mined`, same entry |

| — | https://docs.python.org/3/library/faulthandler.html | 2026-11-09 (R95ScoutSources) | "Call faulthandler.enable() to install fault handlers for the SIGSEGV , SIGFPE , SIGABRT , SIGBUS , and SIGILL signals." (19 words) | module introduction; seat capture `.ufo/waves/round-95/w1/R95ScoutSources/candidate-faulthandler.html` sha256 f50bb09a…, occurrence count 1 | REJECT (not filed): no r95 sentence needs it, the page says nothing about exit status (observed: SIGABRT with the handler still gives the parent -6), and its list omits SIGKILL; flip: a claim that must separate a fatal-signal death from a verdict |
| — | https://peps.python.org/pep-0669/ | 2026-11-09 (R95ScoutSources) | "An exception is raised, except those that cause a STOP_ITERATION event." (11 words; the sentence S360 quotes, occurrence count 1 per R95ScoutSources) | PEP 669 § Events | REJECT: redundant with S360 at lower authority (design record vs shipped docs); flip: the shipped page withdrawn |

Recheck cells: `365d` for all five (ISO/`NNd` schema). Status/recheck/used-by changes to existing rows: none. After the
wave, S360's scope cell and S361's locator and grounds cells were corrected in place (both rows were added in P1 this
round; `git diff --numstat 93c3ef13 -- corpus/SOURCES.md` → `5 0`). Registry 281 → 286. Census
`scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` EXIT 0 at both ends
(`census/round-95/records/sources-census-before.txt`, `sources-census-after.txt`; W04 duplicate-URL warnings only —
S362 and S363 share URLs with S289 and S261/S286/S287 under distinct scopes).

Assimilation: none this round (no `merge/souji/` theme taken). considerthese: the lane has no `considerthese/` dir.

## Mistakes

- **M1 — a limits sentence that names a classifier's false positives from reading, again.** Class: non-exhaustive
  enumeration presented as the complement of a coverage claim — the recurrence of r94 M3 (and r93 M5). Evidence: prereg
  limit (ii) "a counter that legitimately calls sys.exit inside its own helper would be scored errored"
  (`census/round-95/preregistration.txt`); the CHECK script ran two declared shapes (`declared=1`, `argparse=2`), and
  R95Labrat's shape table found six ordinary exits the r95 hook turns into 70 (`sys.exit(helper())` in main, `raise
  SystemExit(helper())`, a raise in try/finally, a SystemExit caught at module level). Captured-by: Amendment 59 (the
  wave), not a lane criterion — r94 M3's fix narrowed one sentence but installed no mechanism, so the class came back
  one round later. Fix: Q172 below (a declared-exit shape table run through the classifier before freeze).
  **Shown able to fail:** `census/round-95/records/declared-shapes.txt` runs twelve shapes (R95Labrat's scripts, the
  hook re-extracted from the frozen search — the seat's own copy differs by an escaped `\n` in two diagnostic strings)
  and prints `SHAPES-SUMMARY shapes=12 mismatched=6` on the r95 hook: the criterion's test fails on today's sentinel.
- **M2 — a count in an instrument's prose that the code did not produce.** Class: a number written in a docstring
  instead of derived. Evidence: the r95 arms counter's docstring said "fourteen arms" and `arms=14` while its table
  built sixteen; the L1's pre-freeze trial printed `ARMS-SUMMARY arms=16` (`controls/prefreeze-feasibility-note.txt`
  item 2). Captured-by: the instrument printing `len(arms)` — the trial's own output. Fix: docstring corrected before
  P1; the summary line, not the docstring, is what the predicate reads. Shown able to fail: the trial output itself
  (`arms=16` against a docstring of 14), disclosed in the note.
- **M3 — an arm credited with binding a check it does not isolate.** Class: arm attribution without a mutant. Evidence:
  the r95 arms-counter docstring and plans/round-95.md A0.0 said S13 binds the r94 `/tmp` guard (R94MutC2 M11);
  R95MutC2 PM9 removes the guard and S13 still conforms, because the fixture's own refusal also gives exit 2 + a FATAL
  line (`.ufo/waves/round-95/w1/R95MutC2/results/P-PM9.out`). Captured-by: the wave's mutation-tester (Amendment 59).
  Fix: narrowed (A5); routed to r96 — an arm that claims to bind a specific check asserts the FATAL reason text, and a
  one-edit mutant of that check is run before the arm is cited. Shown able to fail: PM9's receipt (conform=16 with the
  guard removed).
- **M4 — two control runs lost to a shell construct.** Class: tooling. Evidence: the first two P2 attempts used a
  shell function and unquoted variables inside a backgrounded tool call and failed with `command not found` before
  running anything (no receipt written; both killed, scratch removed). Captured-by: none. Fix: the P2 and A drivers are
  script files (`census/round-95/run-receipt.sh` committed; the drivers lived in the round scratch), which ran cleanly.

## Wave findings

One v1 wave, 13 seats, all settled with a report (`.ufo/waves/round-95/w1-results.json`); amendments A1-A7 in
`plans/round-95.md`; ledger `.ufo/waves/round-95/claim-falsification.tsv`.

- Numbers: R95ExecC1, R95ExecC2, R95Critic, R95Sentinel and R95Scribe re-ran predicates, controls and forgeries on
  committed bytes; every summary matches.
- Full census (R95ExecCensus, reported): r95 vs r94 search over the generated population — 263 shared ids, no verdict
  changes (killed 139, survived 76); errored 48 → 53 = the five new crash fixtures.
- Wording: A1 (SystemExit leg false positives), A2 (no unraisablehook at finalization after a SystemExit exit), A3
  (`os._exit(0)` → 70; the crash path can hang), A5 (S13 does not isolate the /tmp guard), A6 (an escaping grandchild
  hangs the probe past --timeout).
- Strength: A4 (hook scope is the whole harness subtree; tool id 5 is reserved; m02/m03 cross-wired legs survive).
- Overlap: none owned by a sibling (R95Connector).

## Routed to round 96

- C1: rewrite the SystemExit leg to decide on the terminating exception (EXCEPTION_HANDLED or a top-level record) and
  carry the declared-shape table (Q172) as a precondition; a signal-safe crash path (`os.write(2, …)` + real
  `os._exit(70)`); scope the hook to the counter; ids 3-4 only; a CHECK that asserts each channel's
  `SOUJI-R95-CRASH` reason (binds m02/m03); a finalization-time `__del__` fixture; the harness-side crash target (r94
  routed 2, still open); carried r93 items 1, 3, 4.
- C2: arms that assert the FATAL reason text (S13); reap a fixture's escaped descendants and stop waiting on held
  pipes; a write-failure-after-checks arm and a catch-all arm (PM3/PM5); `--timeout 0` (PM6); the positive-control
  conjunct (PM7); randomized arm names; per-run deadlines in the forgery runners.
