# R94Connector — souji round 94 (connector seat)

Status: complete. Report path: `.ufo/waves/round-94/w1/R94Connector.md`. Lane: `souji-shokunin`, lane base
`eddb1be6c34c2e0bef8c1e8ae6ea2f4b381c5536`. Wave: v1, 12 seats. This seat owns only this file and
`.ufo/waves/round-94/w1/R94Connector/`; it never committed, pushed, mutated git/jj, or wrote outside those paths.

Method: read the frozen preregistration first; read the lane read-only (`git diff`, `git status`, source reads); read
sibling lanes read-only; ran three cheap control reproducers against lane instruments with cwd the lane and every
write under `/fast/scratch/hyaku/souji-r94/R94Connector/`; copied their text output into this seat dir and deleted the
scratch before yielding. No full predicate run was made here (the L1/executor seats own the after arms).

Seat-dir receipts:

| file | what it is |
|---|---|
| `repro-exit-codes.txt` | the three exit codes (1, 1, 1) |
| `repro-harness-missing-counter.txt` | `census/round-93/c1-false-row-harness.py` with a missing `--counter` → `FileNotFoundError`, exit 1 |
| `repro-battery-missing-counter.txt` | `census/round-90/c1-clause-battery.py` with a missing `--counter` → `FileNotFoundError`, exit 1 |
| `repro-probe-existing-empty-work.txt` | `census/round-93/c2-forgery-probe.py` with an existing empty `--work` → `FileExistsError`, exit 1 |

## 1. Sibling overlap verdict

**Verdict: no sibling owns the r94 C1/C2 surface as a whole.** Three sibling artifacts are compatible prior art on
its parts: (a) kama owns the *doctrine* and one implementation of setup-vs-verdict exit codes; (b) revenger owns a
mutation search but explicitly does not separate a crash from a kill; (c) audio owns a `sitecustomize.py` loaded from
`PYTHONPATH` but it is a library stub, not an exception sentinel. No sibling lane installs a `sys.excepthook` that maps
an uncaught exception to a distinct exit status in order to score a mutation.

| surface | sibling owner? | path / commit | evidence | gap vs r94 |
|---|---|---|---|---|
| mutation search that separates crashes from kills | **No** | `revenger-shokunin/reports/round-99/mutants/mutate8.py` (tracked, `0126676`, 2026-11-05) | docstring `--kill-tree`: "KILLED when the verdict set ... or the exit code differs from the unmutated run"; `kill_tree` tags `timeout` / `rc+verdict` / `verdict-set` / `rc` (lines 499-512); no `errored`/`runtime error` state. `revenger-shokunin/.ufo/waves/kaika-r1/mutation-post-l2.md:7`: "`killed` = mutant fails the pristine run OR accepts a forgery..." | a mutant that crashes (nonzero exit, different/empty verdict set) is counted `killed`; exactly the C1 defect class, in a sibling mutation harness |
| same surface, doctrine only | **Doctrine, not search** | `kama-shokunin/.ufo/waves/round-20/build/out/KnowErrorVerdict/error-is-not-a-verdict.md` (tracked, `33a67778`, 2026-10-21) | "A verdict, an error and could-not-evaluate are three outcomes"; rules 1-4 include "Exit 1 alone is never a verdict"; Stryker Runtime error vs PIT `RUN_ERROR` (`isDetected()` true); CPython exit table (uncaught exception = 1, `sys.exit("msg")` = 1) | states the rule r94 C1 implements; contains no mutation search and no sentinel |
| `sys.excepthook` / `sitecustomize` sentinel | **No instrument** | `audio-shokunin/corpus/live/r72-reviewer/ldstub/sitecustomize.py` (tracked, `f5d7fafb`) | docstring: "environment stub — simulate a host WITHOUT libsndfile.so.1. Placed on PYTHONPATH so it runs before the fixture's module body"; it monkeypatches `ctypes.CDLL`, never `sys.excepthook`; listed in `corpus/live/r72-reviewer/evidence-manifest.txt:25` | the PYTHONPATH-`sitecustomize` mechanism is the same; the effect (library stub) is not a crash sentinel |
| same, report-only near-miss | **No code** | `kotoba-shokunin/.ufo/waves/round-55/build/CriticC2Sizing.md:12` | describes a shadow `verifiers/argparse.py` that "installs an excepthook that exits 2" in a counter arm S′ | the same lane's `falsify/CriticC2Landed.md:33` says the landed diff has no `excepthook`; no such file is tracked or present in kotoba's tree, so this is an unreproducible arm note, not an owned instrument |
| setup-vs-verdict exit-code discipline | **Partly** | `kama-shokunin/tests/llamacpp-live/install-tree-grid.py` (tracked, `33a67778`) | docstring lines 16-23: `rejected` on exit 1 with stdout starting `INVALID `, `accepted` on exit 0, "timeout or a launch failure is `error`: no verdict was observed", exit 2 = "could not evaluate"; classification at lines 152-181 | the discipline exists for a truth-grid gate; no sibling applies it to a forgery probe or to a mutation search's own exit |

No sibling has a crash fixture scored `errored` in a mutation search, and no sibling's search prints a rule of the form
"harness exit N or any ROW `rc=N` is errored". The r94 surface is not duplicated. If the L1 wants one sentence in
`corpus/knowledge/mutant-crash-is-not-a-kill.md`, the honest cross-lane note is: kama's `error-is-not-a-verdict` already
states the doctrine; revenger's `mutate8.py` is a live counter-example; audio's `ldstub` is the mechanism precedent.

## 2. Lane pattern: instruments whose exit 1 is ambiguous

Class definition used here: the instrument's own exit 1 is produced by a verdict **and** by a setup failure or an
uncaught exception, so a consumer cannot distinguish "the subject failed" from "the instrument could not evaluate".
Two mechanisms are recorded separately: (a) own-exit ambiguity; (b) kill-rule ambiguity, where a crashed subject is
scored `killed` because the rule treats any nonzero subject exit as a kill.

### (a) own exit 1 = verdict and = setup/crash

| instrument(s) | verdict exit 1 at | setup/crash path to 1 | how known |
|---|---|---|---|
| `census/round-84/…/c1-clause-battery.py` through `census/round-91/…/c1-clause-battery.py` (8 files: `census/round-84/c1-clause-battery.py`, `85`, `86`, `87`, `88`, `89`, `90`, `91`) | `return 0 if tot == ns.expect_killed else 1` (r84:128, r85:130, r86:139, r87:147, r88:155, r89:163, r90:172, r91:185) | `raise SystemExit(f"BATTERY-FATAL: ...")` for a pin mismatch and for a subject run with no `SUMMARY` (r84:51,60; r85:53,62; r86:62,71; r87:70,79; r88:78,87; r89:86,95; r90:95,104; r91:107,116). In CPython `sys.exit(str)` exits 1, and an uncaught exception also exits 1 | code read at the cited lines; reproducer `repro-battery-missing-counter.txt` (r90 with missing `--counter`) prints a `FileNotFoundError` traceback and `rc=1`, the same code as "a mutant survived" |
| `census/round-80/…/c1-false-row-harness.py` through `census/round-93/…/c1-false-row-harness.py` (14 files, r80-r93) | `return 0 if mism == 0 and errs == 0 else 1` (r80:204, r88:418, r92:513, r93:564; same tail in all 14) | designed setup failures return 2 (pins, `/tmp` work, non-empty work, fixture build: r93:400-425), but `sha(counter)` runs outside the try at r93:420; a missing/unreadable counter raises `FileNotFoundError` → exit 1 | reproducer `repro-harness-missing-counter.txt`: r93 harness with missing `--counter`, traceback, `rc=1` |
| `census/round-92/c2-forgery-probe.py`, `census/round-93/c2-forgery-probe.py` | `return 0 if positive and rejected == len(FORGERIES) else 1` (r92:105, r93:118) | `os.makedirs(work)` is called after the emptiness check with no `exist_ok` (r93:89; r92:76), so an existing empty `--work` raises `FileExistsError` → exit 1; a missing fixture/tool/`--before` yields no `SUMMARY`, is scored `rejected=no`, and also exits 1 | reproducer `repro-probe-existing-empty-work.txt`: r93 probe with existing empty `--work`, `FileExistsError`, `rc=1`; this is the r93 routed defect 5 and C2's stated before-arm |
| `census/round-80/…/c2-signal-counter.py` through `census/round-87/…/c2-byte-arm.py` (9 counters: `round-80/c2-signal-counter.py`, `round-81/c2-vault-signal-counter.py`, `round-82/c2-vault-signal-counter.py`, `round-83/c2-tree-walk-counter.py`, `round-84/c2-late-fork-counter.py`, `round-85/c2-k4-counter.py`, `round-86/c2-k4-counter.py`, `round-87/c2-k4-counter.py`, `round-87/c2-byte-arm.py`) | `return 0 if mism == 0 and errs == 0 else 1` (r80:410, r81, r82, r83:374, r84:390, r85:242, r86, r87-k4, r87-byte-arm:225) | same shape as the harness family: setup/read helpers can raise before the row loop; only some paths are wrapped; the counters also print `EXIT=0|1` before returning, so a crashed run has no `EXIT=` line | tail read at the cited lines; same `sha`/`open` shape as the harness family. Not separately reproduced here; the harness reproducer is the same mechanism |
| `census/round-94/c2-setup-arms.py` (the r94 measuring counter) | `return 0 if conform == len(arms) else 1` (r94:119) | **no designed setup path to 1**: work-not-empty/not-a-dir and missing inputs return 2 (r94:55-67); only an uncaught exception could collide with the nonconforming verdict | code read; no reproducer (this is the disciplined counterpart, recorded so r95 does not mistake it for the old class) |
| `census/round-91/c2-variant-probe.py` | `return 0 if detected == expect_detected * len(VARIANTS) else 1` (r91:84) | **no setup path to 1**: fixture rc 2 is converted to `R91-PROBE-FATAL` exit 2 (r91:64-65) and no-CASE output exits 2 (r91:76-77); only an uncaught exception exits 1 | code read; contrast case: this is the exit-code discipline C2 wants, already present in an older instrument |

### (b) kill rule treats a crash as a kill (the C1 class)

| instrument(s) | rule | evidence |
|---|---|---|
| `census/round-84/…` through `census/round-91/…/c1-clause-battery.py` | "KILLED iff the harness exits non-zero (a row mismatch or a harness error) for that population" | docstring, e.g. `census/round-84/c1-clause-battery.py:14` (same sentence at r85:14, r86:21, r87:27, r88:33, r89:39, r90 and r91 docstrings); a harness error is therefore a kill by construction |
| `census/round-92/c1-survivor-search.py` | `killed={'no' if rc == 0 else 'yes'}` — any nonzero subject exit | line 155 |
| `census/round-93/c1-survivor-search.py` | killed only on harness exit 1 with a `ROW ... match=no`; a counter crash (rc=1, no ITEM line) makes the harness print `ROW ... got=- rc=1 match=no` (ROW prints at r93 harness:471, 512, 533, 557), so the crash scores killed | `verdict()` at r93 search:86-94; harness row emission at r93 harness:471, 512, 533, 557; the r94 control `census/round-94/controls/c1-control-r93-rule.txt` records both crash fixtures `killed=yes` |
| `revenger-shokunin/reports/round-99/mutants/mutate8.py` (sibling, not this lane) | killed on rc change or verdict-set change; no error state | see §1 |

The r94 wave fixes exactly the two instruments in the claim (`census/round-94/c1-survivor-search.py`,
`census/round-94/c2-forgery-probe.py`). Every other row above is untouched by r94: the eight clause batteries still
score a harness error as a kill, the 14 harnesses and 9 counters still have an uncaught path to exit 1, and the older
forgery probes still exit 1 on setup failures. The r94 arms counter and r91 variant probe are the two disciplined
counter-examples.

## 3. Planning data-walk

### 3.1 r93 spot-check §5 routed items 1-5

| # | item | r94 status | r94 file(s) that answer it | evidence |
|---|---|---|---|---|
| 1 | C1 harness not reproducible from committed bytes (A4) | **carried** | `census/round-94/preregistration.txt:53-54` (stated limit iii: "not addressed"); harness unchanged at `census/round-93/c1-false-row-harness.py` (pin `1868a570…`) | no r94 file mentions reproducibility/A4 (`grep -rE 'reproduc|A4' census/round-94` → only the prereg sentence); the harness still builds a `git clone --shared` fixture from `--lane` (r93:195), so a plain export still cannot supply it |
| 2 | kill rule scores an uncaught counter exception as killed; re-score the r93 targets | **partly** | `census/round-94/c1-survivor-search.py` (HOOK `CRASH_RC=70`, `verdict()`), `census/round-94/c1-targets.json`, `census/round-94/records/c1-after.txt`, `census/round-94/controls/c1-control-r93-rule.txt` | traceback half answered: the sentinel makes the counter exit 70 and the rule maps any `ROW rc=70` to `errored`; `records/c1-after.txt` shows both crash fixtures `killed=errored`, the r93 semantic kills `killed=yes`, survivor `killed=no`. But a **bare `got=-` row that is not a Python traceback** (e.g. a counter that exits 0 without printing `ITEM`) still reaches the `rc==1 + match=no` branch and is scored `killed`; the r94 rule keys on `rc=70`, not on `got=-`. The r93 target re-score is the three r93 ids in `c1-targets.json`, not the full r93 population (limit i) |
| 3 | clauses, not spellings: m5/m6/g2 survive; 76 residual survivors unclassified | **carried** | `census/round-94/preregistration.txt:54` (limit iii: "not addressed") | zero r94 mentions of m5/m6/g2/76 (`grep -rE 'm5|m6|g2' census/round-94` → only the prereg sentence) |
| 4 | KFF19 one payload length/filler; catch in-process exceptions (plus KFF20 mirrors, r91 variants) | **carried** | `census/round-94/preregistration.txt:85-86` (C2 limit ii: "routed defect 4 ... is not addressed"); `census/round-94/c2-forgery-probe.py` keeps the r93 `FORGERIES` (F1-F7/N0) | zero r94 mentions of KFF19/KFF20; the probe's eight forgeries are the r93 ones |
| 5 | `c2-forgery-probe.py` exits 1 on an existing `--work` (setup failure indistinguishable from a surviving forgery) | **answered** | `census/round-94/c2-forgery-probe.py` (exit 2 + `C2-FORGERY-FATAL:` for setup; existing empty dir used), `census/round-94/c2-setup-arms.py` (arms S1-S8), `census/round-94/records/c2-after.txt`, `census/round-94/controls/c2-control-r93-probe.txt` | `records/c2-after.txt`: `ARM S1 exit=0 want=0 conform=yes`, S2-S8 `exit=2 want=2`, `ARMS-SUMMARY arms=10 conform=10`; the r93-probe control records `conform=3`, exit 1 |

### 3.2 SCORECARD `### Planned (r94)` component by component (`SCORECARD.md:2303-2316`)

| planned component | status | r94 file / evidence |
|---|---|---|
| C1: kill rule scores a `got=-` row **or** a counter traceback as `errored` | **partly** | traceback: `census/round-94/c1-survivor-search.py` `verdict()` + `HOOK`; bare `got=-` not covered (the rule is `rc==70`, not `got=-`) — see §3.1 item 2 and §2(b) |
| C1: re-score the r93 targets under it | **partly** | `census/round-94/c1-targets.json` (3 r93 ids: `h-ok-admits-one`, `a491c22-<-to-<=`, `a127c26-True-to-False`) and `records/c1-after.txt`; the full r93 population is not re-scored (limit i) |
| C1: bind the clauses rather than two spellings — m5/m6 (`len(pop) - len(unknown)` forms), g2 (`len(r) not in (3, 4)`) | **carried** | preregistration limit iii; no r94 file |
| C1: assert LD5's `SUMMARY unresolved=1` | **carried** | zero r94 mentions of LD5/unresolved=1 |
| C1: make the harness reproducible from committed bytes (two gitignored lane-disk inputs, A4) | **carried** | preregistration limit iii; harness unchanged |
| C2: KFF19 at a second payload length and a non-`a` filler (`h_filler_a` survives) | **carried** | preregistration C2 limit ii; no r94 file |
| C2: catch in-process exceptions in the fixture's scorer | **carried** | preregistration C2 limit ii; r94 probe uses the frozen r93 fixtures/scorer |
| C2: KFF20 mirrors for `ED A0 80` / `F4 90 80 80` across the head cut | **carried** | zero r94 mentions |
| C2: retire or re-point the r91 variant tools | **carried** | `census/round-91/c2-variant-probe.py` still present; no r94 file references it |
| Carried list (forge-return channel; 76 survivors; p2 basename granularity; p3 punctuation lookahead; p7 `_regular` symlink leg; p8 `token_ok` hyphen marker; `fleet:` symlink leg; battery `--only`/`--expect-killed` stale defaults; r85/r86 C2 list; `_regular` pathspec framing; quarantine intro-blob digest row; r79 gate re-measurement; check-4 300 s backstop; r76 K03/K04; r17 240 s runners; r85-r87 K4 counters' print-only `rc=`) | **carried** | unchanged; no r94 instrument touches any of them (the r94 wave has only six `.py` files, all C1/C2 target instruments) |

### 3.3 Draft `### Planned (r95)`

- C1 (calibration): make the r94 rule cover a **bare `got=-` ROW** (a counter that exits without printing its `ITEM`
  line is `errored`, not `killed`) and add the `threading.excepthook` / `os._exit` leg r94 limit ii leaves open;
  re-score the r93 76 residual survivors under the r94 rule (A2/A3 carried) since a crash that was previously `killed`
  can now become `errored`; bind the m5/m6 (`len(pop) - len(unknown)` forms) and g2 (`len(r) not in (3, 4)`) clause
  shapes rather than the two spellings; assert LD5's `SUMMARY unresolved=1`; make
  `census/round-93/c1-false-row-harness.py` reproducible from committed bytes (commit or pin the two gitignored
  inputs, or fail with a named precondition). Also mark the r84-r91 `c1-clause-battery.py` family historical or
  re-score it under the r94 rule: its docstring still says a harness error is a kill.
- C2 (coverage): KFF19 at a second payload length and a non-`a` filler (h_filler_a survives); catch in-process
  exceptions in the fixture's scorer; KFF20 mirrors for `ED A0 80` / `F4 90 80 80` across the head cut; retire or
  re-point the r91 variant tools. Also give `census/round-94/c2-setup-arms.py` the discipline it measures: its own
  uncaught exception still exits 1, the same code as `conform<10` (the designed setup paths already return 2).
- Carried (unchanged from r94): the forge-return channel (r92 limit ii), the 76 residual survivors' classification,
  p2 basename granularity, p3 the punctuation lookahead, p7 `_regular`'s symlink leg, p8 `token_ok`'s hyphen marker,
  the `fleet:` symlink leg, the battery `--only`/`--expect-killed` stale defaults, the r85/r86 C2 list, `_regular`
  pathspec framing, the quarantine intro-blob digest row, the r79 gate re-measurement, check-4's 300 s backstop,
  r76 K03/K04, the r17 240 s runners, the r85-r87 K4 counters' print-only `rc=`.

## 4. SOURCES rule 2 check

Command (cwd `/home/vgpnk/Projects/shokunin/souji-shokunin`):

```
git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff \
  eddb1be6c34c2e0bef8c1e8ae6ea2f4b381c5536 -- corpus/SOURCES.md
```

Observed: the diff has exactly two `+` lines (S357 Stryker, S358 sysexits) and zero `-` lines; the inserted rows sit
between the S356 context row and the S331 context row. Numeric confirmation:

```
$ git diff --numstat eddb1be6c34c2e0bef8c1e8ae6ea2f4b381c5536 -- corpus/SOURCES.md
2	0	corpus/SOURCES.md
$ git diff --stat eddb1be6c34c2e0bef8c1e8ae6ea2f4b381c5536 -- corpus/SOURCES.md
1 file changed, 2 insertions(+)
```

The fleet contract this checks is `/home/vgpnk/Projects/shokunin/CORPUS.md:115-119` ("**Append-only.** Only `status`,
`recheck` and `used-by` change in place, and each change is logged old→new in the round lesson. A correction is a new
row whose `teaches` opens `supersedes S0NN —`."). **PASS:** no existing SOURCES cell was edited; the only change is
the two appended rows. (The lane working tree currently also shows two untracked files under
`census/round-94/srcs/*.stripped.txt`; they are not mine and are irrelevant to the committed-diff check.)

## 5. Falsification ledger

**NO-FALSIFICATION.**

What I tried: read both claim instruments and their records; re-derived the r93-defect controls (r93 harness missing
counter, r93 probe existing empty work, r90 battery missing counter); checked the sentinel's second-order effect in
`census/round-94/records/c1-after-harness/`. I did **not** re-run the C1/C2 after predicates (the L1/executor seats
own the after arms, and my reading of `records/c1-after.txt` and `records/c2-after.txt` shows both predicate lines and
exit 0).

Two observations that are not falsifications but that the L1 should record with the predicate:

1. `census/round-94/records/c1-after-harness/m0003.out` shows the sentinel makes *every* counter invocation in the
   crash fixture exit 70, so ROWs whose expected `rc` is `-` print `rc=70 match=yes` and ROWs expecting `rc=1` print
   `rc=70 match=no`. The r94 rule keys on `rc=70` (stated wording: "any ROW `rc=70`"), so this is consistent; but it
   means the `match=` column is not what fires the rule. The SEARCH lines for both crash fixtures print `rc=1` (the
   harness exit), so the "harness exit 70" leg is not the one that fires; the "any ROW `rc=70`" leg is. The claim
   states either leg, so no sentence is contradicted.
2. The r94 search's verdict still maps a bare `got=-` row with a nonzero harness exit and `match=no` to `killed`
   (the `rc==1`/`match=no` branch). This is not a widening of the claim (the claim's rule is exactly "harness exit 70
   or any ROW `rc=70`"), but it is the gap between the frozen claim and the `### Planned (r94)` sentence "kill rule
   scores a `got=-` row ... as `errored`". Recorded as a planning gap in §3.2, not as a claim falsification.

## 6. One bounded proposed move (connector role)

**Move:** carry the r94 crash-sentinel rule *backward* to the untouched lane instruments with a new r95 instrument
rather than an edit: run the r84-r91 clause batteries (and one representative of the r80-r87 C2 counter family) under
the same `sitecustomize` sentinel, scoring `errored` separately, and publish an append-only appendix row that says
"published kill counts at rule; crashes not distinguished". In the same instrument, wrap
`census/round-94/c2-setup-arms.py` in the same discipline it measures (an injected crash must not exit 1).

Why it is non-obvious and compatible: C1 supplies the sentinel, C2 supplies the setup/verdict exit split, and kama's
`error-is-not-a-verdict.md` supplies the contract wording; the synthesis targets the instruments the wave *froze*
instead of the two it rewrote. It also closes the connector's own pattern list: the eight batteries literally say a
harness error is a kill, and the r94 measuring counter is the one instrument of the wave that still has the ambiguous
exit it measures.

**Affected axes:** calibration 7 (historical kill counts for r84-r91 may include crashes; the appendix separates them
without changing the published rows) and operability 8 (the r94 arms counter's own exit 1 = nonconforming, and an
uncaught crash is the same code). No other axis is touched; no score is claimed to move, and no frozen record is
rewritten.

**Risks:** running the older batteries means lane clones (~0.7 GB) and minutes, and a different sentinel placement can
change historical `mismatches`; the appendix must be a new file/row, never an edit of r84-r91 records or
`SCORECARD.md` history. The `c2-setup-arms.py` wrapper must not change its 10 prescribed arms or its `ARMS-SUMMARY`
line, or the C2 predicate of record becomes ambiguous.

**Verification the L1 can run after r95 files land:** (i) the old battery on its pinned population yields the same
pristine rows and the same semantic mutant kills, with a nonzero `errored` count only when a crashing harness fixture
is injected; (ii) the wrapped arms counter with an injected crash exits 2 (or a named non-1 code) and still prints
`ARMS-SUMMARY arms=10 conform=10` on the real arms; (iii) the appendix's counts diff to zero against the historical
records for every non-crash mutant.

## 7. Tooling

No tool was installed, upgraded, or removed. Used: `python3` (stdlib), `git` read-only (`diff`, `log`, `ls-files`,
`grep`), `grep`, `sed`, `sha256sum` via the tools. No pacman, no `~/.local/bin` writes, no sudo, no background
processes, no mutating git/jj. Scratch `/fast/scratch/hyaku/souji-r94/R94Connector/` was deleted before yielding;
only the text receipts listed at the top remain in this seat dir.
