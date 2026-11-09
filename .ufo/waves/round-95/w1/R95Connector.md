# R95Connector — cross-lane overlap, C2-class pattern list, planning data-walk

Seat: R95Connector (r95 w1, leaf; no subagent dispatch). Lane: `souji-shokunin`.
Measured state: lane HEAD `dd5206842fcead3b1e7301d3dbaaec42b625dd54` (after receipts), base
`93c3ef13a9eb9678483518562f3692124db714c2`. Read-only on the lane; every file this seat wrote is under
`.ufo/waves/round-95/w1/R95Connector/` plus this report. Scratch dir `/fast/scratch/hyaku/souji-r95/R95Connector`
was created and is deleted at exit (receipt in §6). No git/jj mutation, no subagents, no tool installs.

Evidence files in this seat dir:

| file | content |
|---|---|
| `scan-instruments.py` | AST scanner for the two C2-class surfaces over `census/round-80..95` |
| `scan-raw.tsv` | 365 rows; `A-*` = child run with no `timeout=`, `B-*` = strict-UTF-8 read, guard flag |
| `sibling-scan.txt` | every sibling grep/command with its hit list |
| `rule2-sources-diff.txt` | the frozen `git diff <base> -- corpus/SOURCES.md` plus HEAD/status header |

---

## 1. Sibling overlap verdict

**No sibling lane owns the r95 crash-sentinel surface, and none owns the C2 exit-2 setup-refusal discipline.**
The only sibling artifact on the four channels is *inverse in purpose*: `kake-shokunin/scripts/cache_key_conformance.py:418`
lists `"sys.monitoring"` among the audit-hook events its sandbox **denies** to a candidate (the gate forbids a
candidate from observing execution), so kake treats the capability as a hazard, not as a sentinel.

| channel searched | sibling hits (outside `souji-shokunin`) | verdict |
|---|---|---|
| `sys.excepthook` replacement | no sibling *instrument* replaces it; every hit (scan includes each repo's `.ufo/` tree) is a CPython stdlib source capture (`mado-shokunin/.ufo/waves/round-22/w1/sources/SourceThread/threading-v3.14.8.py`), docs captures (`tameshi-shokunin/.ufo/evidence/round-79/80/sources/sys*.html`, `tsukuroi-shokunin/.ufo/waves/round-96/97/...sys315.html`) or prose (`kama`/`kotoba`/`kagi` reports) | none owns it |
| `threading.excepthook` | no instrument; the same CPython stdlib source captures plus Python-docs/HTML captures | none owns it |
| `sys.unraisablehook` | no `.py` hits; only docs/changelog captures (tameshi/tsukuroi `sys*.html`, kagi `chlog*.body`) | none owns it |
| `os._exit` replacement | zero `os._exit = ...` assignments; the `os._exit` call sites (`audio-shokunin/corpus/fixtures/measure_audio.py`, `chousa-shokunin/corpus/evidence/round{30,54,55,56,62,78}/*`, `kama-shokunin/tools/*`, `mado-shokunin/quality/counters/*`) are deliberate child exits, not interception | none owns it |
| `sys.monitoring` | one instrument: `kake-shokunin/scripts/cache_key_conformance.py:418` (and its receipt snapshot `kake-shokunin/.ufo/waves/round-90/w1/ExecSandbox/receipts/gate_worktree_snapshot.py:370`), the **deny-list** entry; plus one sibling *source assessment*: `kama-shokunin/.ufo/waves/round-58/w1/out/Q02SourcePyTrace.md:8,12` judges `sys.monitoring` "complementary" to `sys.setprofile` for **execution observation/profiling**, not for crash classification; the rest are docs/changelog captures (`kagi` chlog, `tameshi`/`tsukuroi` pins) | inverse / analysis, not a sentinel |
| `faulthandler` (adjacent crash channel) | only the same kake deny list | none owns it |
| `sitecustomize` on `PYTHONPATH` (the r95 hook vehicle) | `audio-shokunin/corpus/live/r72-reviewer/ldstub/sitecustomize.py` (19 lines) — replaces `ctypes.CDLL` to simulate a missing `libsndfile`; **no exception hook** | mechanism prior art only, no crash channel |
| "crash sentinel" phrase | `game-dev-2d-shokunin/reports/round-97/r97-verifier.md:53`, `round-100/r100-critic.md:13,196`, `round-101/mutations/ver9_extract_baseline.py:56` — a **CASES-row dedupe** in a Godot battery, not an exception sentinel | none owns it |
| `*sentinel*` files | `audio-shokunin/corpus/live/r77-boundary/p6_sentinel.py` = a "split sentinel" rotation-counter probe; the rest are seat names/notes | none owns it |

**Probe fixture timeout.** The *practice* is widespread outside this lane, so r95's timeout half is not novel:
`chousa-shokunin/corpus/evidence/round29/c1-count.py:266` (`timeout=opts.timeout`), `round45/c1-count.py:62`,
`round49/c1-count.py:183`, `round50/c1-count.py:61` (all `timeout=120`); `game-dev-2d-shokunin/corpus/fixtures/run_battery.py:935,951`
(`timeout=timeout_seconds`; default 8/60 at :2751); `audio-shokunin/corpus/live/r96-simplifier/probe_c4.py:46-49`
(`pactl` `timeout=12`) and `:143` (`mal.wait(timeout=10)`, its forgery-control child);
`audio-shokunin/corpus/fixtures/measure_audio.py:414,521,1052` (process-group SIGKILL deadlines). What no sibling has
is the C2 *combination* — a forgery probe whose setup failures are forced to exit 2 with a named FATAL line, plus a
default fixture deadline — so the C2 claim is lane-local and not duplicated elsewhere.

**Second-order risk (record, do not act on).** The one sibling *instrument* that names `sys.monitoring` denies it to sandboxed
candidates (`kake-shokunin/scripts/cache_key_conformance.py:414-418` also denies `sys.settrace`, `sys.setprofile`,
`sys._current_frames`, `sys.addaudithook`). If a future round runs the counter under that kind of sandbox, the r95
sentinel would be blocked by design and its check line would fail loudly (`SOUJI-R95-SENTINEL no free
sys.monitoring tool id`) rather than silently degrade — that is the only cross-lane coupling this seat found.

Commands and counts: `sibling-scan.txt`.

---

## 2. Lane instruments with the C2-class surfaces (census/round-80..95)

Method: `python3 -B .ufo/waves/round-95/w1/R95Connector/scan-instruments.py . scan-raw.tsv` parses every `.py`
under `census/round-8*` and `census/round-9*`, flags (A) a `subprocess` call with no `timeout=` keyword (a `Popen`
counts only when no later `communicate`/`wait` with `timeout=` uses the handle), and (B) `open(...)`/`read_text` with
`encoding` utf-8/utf8, reporting whether the call is lexically inside a `try` handling `UnicodeDecodeError`/
`UnicodeError`/`OSError`/`Exception`. Excluded: `records/` and `srcs/` subtrees (captures/receipts, not
instruments) and bare non-subprocess functions named `run`/`call` (the first scan pass counted those; filtered).
Every row below was re-read in source.

### 2.1 Class A — a fixture/candidate child run with no deadline

| instrument | line(s) | what is run, no `timeout=` | verified |
|---|---|---|---|
| `census/round-92/c2-forgery-probe.py` | 55 | `subprocess.run([python, -B, <fixture>, ...])` per forgery; a hanging fixture hangs the probe | `run()` has no timeout; no `TimeoutExpired` anywhere |
| `census/round-93/c2-forgery-probe.py` | 68 | same | same |
| `census/round-94/c2-forgery-probe.py` | 77 | same (this is the C2 claim's *before* arm; listed for completeness, not as "other") | same |
| `census/round-91/c2-variant-probe.py` | 59 | `subprocess.run([python, -B, <fixture>, --tool <variant>, ...])` per variant | no timeout in file |
| `census/round-94/c2-setup-arms.py` | 102 | `subprocess.run([python, -B, <probe>, ...])` per arm — this is why S12 read `exit=hung` only after the *r95* counter added `--arm-timeout` | no timeout; no `TimeoutExpired` |
| `census/round-80..93/c1-false-row-harness.py` (the whole family, one copy per round) | r93: 458, 499, 519, 540 (`subprocess.run([python, -B, <counter>, ...])`); r93: 181 (`git -C ...`), 195 (`git clone --shared`) | every counter run and the lane clone | `grep timeout` on r93 = zero hits; the r95 search wraps *this* harness with `--timeout 300` and a process-group kill, so the reservoir is bounded only when driven by r95 |
| `census/round-95/c1-forgery-controls.py` | 55 | runs a forged search copy with no deadline (the search bounds each *harness* run, but the runner bounds nothing) | verified |
| `census/round-95/c2-forgery-controls.py` | 54 | runs the arms counter with no deadline (bounded inside by `--arm-timeout`, not by the runner) | verified |
| `census/round-94/c1-forgery-controls.py`, `census/round-94/c2-forgery-controls.py` | 52, 51 | same pattern in the r94 copies | verified |

Not class A (checked so the list is not over-broad): `census/round-95/c1-survivor-search.py` (`Popen(...harness...)`
+ `communicate(timeout=ns.timeout)`, default 300; and the precondition `subprocess.run(..., timeout=60)`),
`census/round-90..91/c1-clause-battery.py` (`run()` passes `timeout=120`), `census/round-95/c2-setup-arms.py`
(`communicate(timeout=ns.arm_timeout)`, default 300), `census/round-95/c2-forgery-probe.py`
(`communicate(timeout=timeout)`).

### 2.2 Class B — a CLI input read as strict UTF-8 with no setup refusal

Same class as the r94 probe's `open(tool, encoding="utf-8")`: a `UnicodeDecodeError` (or `FileNotFoundError`)
escapes as a traceback, exit 1, which the tool's own convention reserves for a *verdict*, not a setup failure.

| instrument | line(s) | input read | verified failure mode |
|---|---|---|---|
| `census/round-92/c2-forgery-probe.py` | 80 | `--tool`, `--before` (`open(..., encoding="utf-8")`) | no `isfile` check either; missing/non-UTF-8 → traceback exit 1 (the r94 routed defect, pre-r94 shape) |
| `census/round-93/c2-forgery-probe.py` | 93 | `--tool`, `--before` | same |
| `census/round-94/c2-forgery-probe.py` | 109 | `--tool`, `--before` (isfile check added at :104-108, decode still unguarded) | the C2 claim's before arm |
| `census/round-95/c1-survivor-search.py` | 333, 340 | `--counter`, `--ids` (`open(..., encoding="utf-8")`, `json.load`) | **r95's own new C1 instrument**: no `read_utf8`-style guard and no catch-all around `main()`; a non-UTF-8 `--counter`/`--ids` exits 1 (its convention: 0 ran, 2 setup, 130 interrupt) |
| `census/round-95/c2-setup-arms.py` | 103 | `tool_bytes.decode("utf-8")` on the filed `--tool` | **r95's own new C2 counter**: a non-UTF-8 `--tool` raises before any arm; exit 1 means "arms not conforming" — the exact confusion C2 exists to remove, now inside the counter |
| `census/round-93/c1-false-row-harness.py` | 411, 443 | population (`--population`, after a sha pin) and the lane ledger file named by the row | the population read is effectively safe only because the sha pin must match; the lane ledger read at :443 is unguarded, and an uncaught exception exits 1 from the harness |
| `census/round-87/c1-pointer-counter.py` (the counter under test) | 486 (`_ledger`), 556 (`--forge`) | `--ledger`, `--forge` | a non-UTF-8 ledger/forge file dies with a traceback exit 1 instead of the counter's `C2-COUNTER-FATAL:` exit 2 |
| `census/round-90/c1-clause-battery.py` | 148, 149 | `--counter`, `--mutants` JSON | `open(counter, encoding="utf-8")` / `json.load(open(ns.mutants, ...))` unguarded; same shape in the r84-r91 battery copies |

`census/round-95/c2-forgery-probe.py:108-124` is the **fix**, not a member: `read_utf8()` converts
`UnicodeDecodeError` to `Fatal` and `write()` converts `OSError`, and `cli()` (:181-193) turns `Fatal`/`OSError`/any
`Exception` into exit 2. The same discipline is absent everywhere else in the list above.

**Scope note.** These are routed-defect candidates for r96, not falsifications: neither claim's stated wording
mentions the inputs of these instruments, and the claim predicates supply valid UTF-8 inputs. See §5.

---

## 3. Planning data-walk

### 3.1 `corpus/lessons/round-94-verifier-spotcheck.md` §5 routed items

| # | routed item (spot-check §5) | status | r95 file / evidence |
|---|---|---|---|
| 1 | C1 sentinel blind spots (A1): SystemExit, `os._exit`, atexit/`__del__` (unraisablehook), thread exceptions | **answered** | `census/round-95/c1-survivor-search.py`: HOOK :81-152 (`sys.excepthook` :138, `sys.unraisablehook` :139, `threading.excepthook` :140, `os._exit` :141, RAISE callback :147, atexit check :132-136); five fixtures in `census/round-95/c1-targets.json`; `census/round-95/records/c1-after.txt:14-18` all `killed=errored`; precondition line `:3` |
| 2 | C1 harness-side crash target: no target binds the "harness exit 70" disjunct (R94MutC1 M2, R94Sentinel F3) | **carried** | `census/round-95/c1-targets.json` holds exactly ten ids — five channel fixtures plus the five r94 counter targets (`h-crash-late`, `h-crash-index`, `h-ok-admits-one`, `a491c22-<-to-<=`, `a127c26-True-to-False`); none makes the *harness* exit 70 |
| 3 | C2 probe exits 1 on non-UTF-8 `--tool`/`--before`, file-parent `--work`, mid-run write failure (A4); no fixture timeout (F5); `--work` TOCTOU and `/tmp` itself (F7, F9) | **partly** | answered: non-UTF-8 (`read_utf8`, probe :108-115; arms S9/S10), file-parent `--work` (:147-150, S11), timeout (:91-105, `--timeout` default 120; S12), `/tmp` (realpath guard :134-135; S13). Not answered: no arm binds a write failure *after* the checks (the code converts it, `write()` :117-124, but the prereg limit (i) names it as the wave's to try) and TOCTOU/read-only-mid-run is deferred by the same limit |
| 4 | Carried from r93: item 1 harness reproducibility from committed bytes; item 3 m5/m6/g2 clauses and the 76 residual survivors; item 4 KFF19 second length/filler and fixture-scorer exceptions | **carried** | `census/round-95/preregistration.txt`, C1 limit (iv): "r93 routed items 1 and 3-4 ... are not addressed" |
| 5 | Seat hygiene: seat temp under `/fast/scratch/hyaku/souji-r95/`, not `/var/tmp` | **answered for this wave** | the seat spec's scratch clause; this seat used only `/fast/scratch/hyaku/souji-r95/R95Connector` (deleted, §6), no `/var/tmp` or `/tmp`. Round-level proof is the L1's receipt check in `plans/round-95.md` (not yet written at this seat's read) |

### 3.2 `SCORECARD.md` `### Planned (r95)` (lines 2342-2357)

| planned item | status | r95 evidence |
|---|---|---|
| C1: SystemExit crash fixture | **answered** | `h-sysexit` in `c1-targets.json`; `records/c1-after.txt:14` `killed=errored` |
| C1: atexit crash fixture | **answered** | `h-atexit`; HOOK `_souji_unraisable`; `c1-after.txt:15` |
| C1: `__del__` crash fixture | **partly** | the unraisablehook leg is installed (:139) and `h-atexit` exercises the atexit→unraisable route, but no `__del__`-only target exists in `c1-targets.json` |
| C1: harness-side crash target binding the exit-70 disjunct (M2/F3) | **carried** | see §3.1 row 2 |
| C1: truthful precondition line (M8) | **answered** | `c1-after.txt:3` `# crash-sentinel rc=70 check=pass excepthook=70 sysexit=70 atexit=70 thread=70 osexit=70 declared=1 argparse=2`, asserted before scoring at search :324-332 |
| C1: the `endswith(' match=no')` position (M6) | **answered** | `census/round-95/c1-survivor-search.py:226` `any(l.endswith(" match=no") ...)`; `match=error` rows with a detail tail do not count as kills (visible in `records/c1-after-harness/m0005.harness.out:5-13`) |
| C1: bare `got=-` rows | **partly** | no `got=-`-specific branch; the sentinel makes Python crashes exit 70 and the rule scores any `rc=70`/negative `ROW` as errored (:216-232), which covers every `got=-` row in the receipts (all `rc=70`); no target binds a `got=-` row with exit 1 |
| C1 carried: r93 routed 1 (reproducibility from committed bytes), m5/m6/g2 clause shapes + LD5 `unresolved=1`, 76 residual survivors, r84-r91 docstring that calls a harness error a kill | **carried** | prereg C1 limit (iv) |
| C2: catch decode and write exceptions in the probe as exit 2 | **answered** | probe :108-124, :181-193 |
| C2: a fixture timeout | **answered** | probe :91-105, `--timeout` default 120, process-group kill |
| C2: `--work` TOCTOU and `/tmp` itself | **partly** | `/tmp` answered (:134-135, S13); TOCTOU deferred by prereg limit (i) |
| C2: arms binding edit-once and the `/tmp` guard (R94MutC2 M10/M11) | **answered** | S14 (edit-twice) and S13 (work-tmp) in `census/round-95/c2-setup-arms.py:145-146`; `records/c2-after.txt:25-28,31` |
| C2: randomized arm names (R94Critic) | **carried** | arms are the fixed `P1,P2,S1..S14`; no `random`/`shuffle` in `c2-setup-arms.py` |
| C2: the arms counter's own uncaught exceptions | **carried** | `c2-setup-arms.py` has no catch-all around `main()`; `tool_bytes.decode("utf-8")` at :103 raises before any arm; exit 1 still means "not conforming" |
| C2: KFF19 second length/filler, fixture scorer exceptions, KFF20 mirrors, the r91 variant tools | **carried** | not touched by P1/P2; prereg C2 limit (i)-(iii) |
| Carried bullet (forge-return channel, p2 basename granularity, p3 punctuation lookahead, p7 `_regular` symlink leg, p8 `token_ok` hyphen marker, `fleet:` symlink leg, battery `--only`/`--expect-killed` stale defaults, r85/r86 C2 list, `_regular` pathspec framing, quarantine intro-blob digest row, r79 gate re-measurement, check-4 300 s backstop, r76 K03/K04, r17 240 s runners, r85-r87 K4 counters' print-only `rc=`) | **carried** | not addressed by the r95 instruments; nothing in the prereg claims them |

### 3.3 Draft `### Planned (r96)`

```md
### Planned (r96)

- C1 (calibration): a harness-side crash target that binds the "harness exit 70" disjunct (r94 closure routed 2;
  no r95 id does, c1-targets.json); a `__del__`-only finalizer fixture (r95's unraisablehook leg is installed but
  only h-atexit exercises it, r95 C1 status); the declared-exit boundary the r95 limits name — a counter calling
  `sys.exit(n)` inside its own helper (limit ii), a caught signal, `python -I`/`-S`, a non-Python child, a C-level
  crash (limit iii) — and the RAISE re-fire per frame re-checked on the host's CPython; give the r95 search the same
  setup refusal it gives the C2 probe for `--counter`/`--ids` (c1-survivor-search.py:333,340 read strict UTF-8 with
  no Fatal path); carried: r93 routed 1 harness reproducibility from committed bytes, m5/m6/g2 clause shapes and LD5
  `unresolved=1`, the 76 residual survivors, the r84-r91 clause-battery docstring that calls a harness error a kill.
- C2 (operability/coverage): an arm for a write failure *after* the probe's checks and for a `--work` made
  read-only mid-run (r95 C2 limit i), and a `--work` TOCTOU arm (r94 routed 3); a catch-all in
  c2-setup-arms.py and a guarded `tool_bytes.decode` (:103) so the counter can no longer exit 1 on a non-UTF-8
  `--tool` (r94 routed 3); randomized arm names (R94Critic; r95's are fixed); a per-run deadline in the forgery
  control runners (c1-forgery-controls.py:55, c2-forgery-controls.py:54, r94 copies) and in the r80-r93
  c1-false-row-harness family (r93: 458/499/519/540 counter runs, 181/195 git, no `timeout=` anywhere), whose only
  deadline today is the r95 search's wrapper; setup-refusal reads for the tool inputs of the older probes and the
  counter (r92 probe:80, r93 probe:93, r94 probe:109, r87 counter:486/556, r90 battery:148-149); KFF19 second
  length/filler, fixture scorer exceptions, KFF20 mirrors, the r91 variant tools (r93 routed 4).
- Carried: the forge-return channel (r92 limit ii), p2 basename granularity, p3 the punctuation lookahead, p7
  `_regular`'s symlink leg, p8 `token_ok`'s hyphen marker, the `fleet:` symlink leg, the battery `--only`/
  `--expect-killed` stale defaults, the r85/r86 C2 list, `_regular` pathspec framing, the quarantine intro-blob
  digest row, the r79 gate re-measurement, check-4 300 s backstop, r76 K03/K04, the r17 240 s runners, the r85-r87
  K4 counters' print-only `rc=`.
```

(Advisory only — the L1 owns `plans/round-95.md`/r96 planning. The draft deliberately keeps every r95 §STATED LIMIT
that r95 did not close and every item in §3.2 marked partly/carried.)

---

## 4. SOURCES rule 2

Command (cwd `souji-shokunin`), receipt `rule2-sources-diff.txt`:

```
git diff 93c3ef13a9eb9678483518562f3692124db714c2 -- corpus/SOURCES.md
```

- `git diff --numstat` → `5  0  corpus/SOURCES.md` (five additions, zero deletions).
- The patch has exactly one hunk, `@@ -296,6 +296,11 @@`; `git diff -U0 | grep -c '^-[^-]'` → **0**.
- The five added rows are exactly `S360 | Py`, `S361 | Py`, `S362 | Py`, `S363 | Py`, `S364 | Py`.
- Row count: 281 at base `93c3ef13`, 286 at HEAD `dd520684` (`grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'`).
- `git status --porcelain -- corpus/SOURCES.md` → 0 entries (no worktree edit by any seat).

Verdict: **PASS** — only added rows S360-S364, no edited cell.

---

## 5. Falsification ledger

**NO-FALSIFICATION.** What I tried, in order:

1. Read the C1 claim wording against the code: HOOK `:81-152` replaces `sys.excepthook`, `sys.unraisablehook`,
   `threading.excepthook`, `os._exit`, and registers a RAISE callback + an atexit check; the declared-exit logic
   (`_souji_raise` :121-130, `_souji_atexit` :132-136) matches the claim's sentence about the main-script
   SystemExit, and `CHECK`/`CHECKS` :153-178 match the check line `excepthook=70 … osexit=70 declared=1 argparse=2`.
   No sentence conflicts.
2. Read the C2 claim wording against `census/round-95/c2-forgery-probe.py`: `read_utf8` :108-115, `write` :117-124,
   timeout :91-105, uncreatable work :147-150, `/tmp` guard :134-135, `cli` :181-193 → each of S9-S12 reaches exit 2
   with `C2-FORGERY-FATAL:`; no sentence conflicts.
3. Read the receipts (`records/c1-after.txt`, `records/c2-after.txt`, `controls/c1-control-r94-rule.txt`) against the
   claim's numbers — they match the prereg's predicate/control lines; I did **not** re-run any predicate (not this
   seat's task; executors/sentinel re-measure).
4. Scanned all census instruments 80-95 for the C2 class (§2) and all sibling lanes (§1) for the surface. The gaps
   found are in *other* instruments (`c1-survivor-search.py:333,340`, `c2-setup-arms.py:103`, the older probes, the
   harness family, the control runners). They are routed-defect candidates, not falsifications: the C1 claim says
   nothing about how its search reads `--counter`/`--ids`; the C2 claim says nothing about the arms counter's own
   input handling, and its stated limit (i) explicitly leaves other setup failures to the wave.

No sentence of either claim was widened, narrowed or contradicted by anything this seat produced.

---

## 6. Scratch

`/fast/scratch/hyaku/souji-r95/R95Connector` was created at seat start and held no clone (no predicate run); it was
removed before yield — `test -e` after `rm -rf` printed `no` (receipt run 2026-11-09, seat exit). All receipts above
are text files inside this seat dir; nothing was written under `/home/vgpnk/Projects/shokunin/.ufo/` or outside
`souji-shokunin/.ufo/waves/round-95/w1/R95Connector/` (plus this report). No `/var/tmp` or `/tmp` directory was
created by this seat.
