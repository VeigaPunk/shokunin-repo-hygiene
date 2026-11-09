# R94Sentinel — souji round 94, seat: sentinel

Scope: safety and robustness of the C1 crash sentinel (`sitecustomize.py` hook) and of the C2 probe's / arms
counter's setup handling. Lane: `souji-shokunin`; round dir `census/round-94/`. Seat dir:
`.ufo/waves/round-94/w1/R94Sentinel/` (receipts in `receipts/`, reproducers in `repro/`).

Tooling: **no tool was installed or upgraded** in this seat (nothing in the task needed it; no pacman, no uv, no
pip). The tooling-authorization directive was not exercised.

Scratch: `/fast/scratch/hyaku/souji-r94/R94Sentinel/` — deleted before this report was filed. The lane was read
only; `git status` in the lane shows only other seats' files (`SCORECARD.md`, `corpus/QUALITY.md`,
`corpus/lessons/round-94.md`, `plans/round-94.md`); my runs left **0** files in the lane and **0** files under the
lane's `.git/` newer than the run window.

---

## 0. What I ran (the numbers I am reporting on)

Both frozen predicates were reproduced with the frozen instruments, unmodified:

| run | command (abridged) | result | receipt |
|---|---|---|---|
| C1 after | `c1-survivor-search.py` on `c1-targets.json` | `SEARCH-SUMMARY generated=5 ambiguous=0 uncompiled=0 hung=0 scored=5 errored=2 killed=2 survived=1`, EXIT 0, `# crash-sentinel rc=70 check=pass` | `receipts/c1full-out.txt` |
| C1 control | `c1-control-r93-rule.py` (r93 rule) | `errored=0 killed=4 survived=1`, both crash fixtures `killed=yes` | `receipts/c1ctrl-out.txt` |
| C2 after | `c2-setup-arms.py` with the r94 probe | `ARMS-SUMMARY arms=10 conform=10`, EXIT 0, every arm conform=yes | `receipts/arms-predicate.out` |
| C2 control | `c2-setup-arms.py` with the r93 probe | `ARMS-SUMMARY arms=10 conform=3` (P1, P2, S2 conform; S1, S3–S8 exit 1), EXIT 1 | `receipts/arms-r93.out` |

Per-line C1 verdicts (after arm): `h-crash-late killed=errored rc=1`, `h-crash-index killed=errored rc=1`,
`h-ok-admits-one killed=yes rc=1`, `a491c22-<-to-<= killed=yes rc=1`, `a127c26-True-to-False killed=no rc=0` —
i.e. the predicate's five verdicts reproduce exactly.

**Crash mechanism confirmed from the receipts, not from the summary.** `receipts/harness-out/h-crash-late.harness.out`
shows all 66 `ROW` lines carrying `rc=70` (the counter crashes after printing every ITEM line, so every one of the
66 counter invocations dies with 70). `receipts/harness-out/h-crash-index.harness.out` shows the crash is confined to
the one row that exercises a three-column ledger row (`ROW LD6 where=ledger-trim ... rc=70 match=no`); the other 65
rows run clean (`rc=0`/`rc=1`). So the r94 rule fires on two different shapes — "every row crashed" and "exactly one
row crashed" — which is good evidence that the rule does not depend on the crash being last.

---

## 1. FALSIFIES-WORDING

One artifact of this wave falsifies a **stated sentence**. It does **not** change either counted quantity
(`errored=2 killed=2 survived=1`; `conform=10`) or either predicate.

**Exact sentence (preregistration, C1 STATED LIMITS (ii)):**

> "The sentinel covers an uncaught exception in the main thread of a Python process started with site enabled;
> os._exit, signals, thread exceptions and a counter that legitimately exits 70 are not distinguished."

**Falsified clause:** "The sentinel covers an uncaught exception in the main thread of a Python process started with
site enabled." The enumeration that follows it (`os._exit`, `signals`, `thread exceptions`, legitimate `70`) is
**not exhaustive**: there is a fifth uncovered channel — an exception raised in an `atexit` handler or in a `__del__`
finalizer. Such an exception is uncaught, runs in the main thread, and the process has site enabled, yet the sentinel
never fires: Python routes it to `sys.unraisablehook` (not `sys.excepthook`), prints "Exception ignored in atexit
callback", and **keeps the original exit status**. The counter therefore exits 0, the harness sees a clean run
(`SUMMARY rows=66 mismatches=0`), and the search scores the mutant **survived** (`killed=no`) — a crash that the
search reports as a *live survivor*, silently, with every row matching.

**Reproducer:** `repro/counter-atexit.py` (the frozen r87 counter with the `h-crash-late` edit replaced by an
`atexit.register(...)` that raises) driven by `repro/expF.py`; the driver imports the frozen
`census/round-94/c1-survivor-search.py` and calls its own `verdict()` on the real harness's stdout.

**Observed (receipt `receipts/out-F.txt`):**

```
atexit-shutdown-crash: harness_rc=0 r94_verdict='no' distinct_row_rcs=['0','1'] rows=66
  harness SUMMARY: ['SUMMARY rows=66 mismatches=0 accepted=0 refused_true=0 errors=0']
```

Compare the same counter crashing in the *main body* (`h-crash-late`): harness rc=1, all 66 rows `rc=70`,
`killed=errored` (`receipts/harness-out/h-crash-late.harness.out`).

**Mechanism** (why the hook cannot see it): `sys.excepthook` is invoked only for an exception that escapes the
interpreter's main thread. An `atexit` callback and a `__del__` finalizer run *during interpreter shutdown*, where
the exception is reported through `sys.unraisablehook`; CPython prints "Exception ignored in atexit callback" and
leaves the exit status at whatever `main()` returned. The hook is therefore structurally blind to it — no change to
the hook's body can fix this; only a different detection channel could.

**Also falsified — the same sentence in the filed r94 knowledge entry**
(`corpus/knowledge/mutant-crash-is-not-a-kill.md`, P1, listed in the prereg header as the entry the claim is
grounded in):

> "The hook covers uncaught exceptions in the main thread of a Python counter."

Same narrowing. `repro/expE.py` shows the `__del__` variant too (`del-raise`): the counter exits 0 and the mutant is
scored `killed=yes` (a **false kill** — see F2 for the direction).

**Reachability, stated honestly:** in r94's own frozen corpus this channel is **not reachable** — the r87 counter
registers no `atexit` handler, and the search's mutation operators (comparison flips, `and`/`or`, `not`-deletion,
`True`/`False`, `0`/`1`) plus the five named hand edits cannot introduce one. So the falsification is of the
**stated coverage/limits sentence** (and of the corpus entry's identical sentence), *not* of the counted quantity
and *not* of the predicate. It matters for the next rounds that add hand edits, and it must be amended in
`plans/round-94.md` rather than silently ignored.

**Second, weaker wording narrowing (same section, flagged so the L1 can decide):** the limits sentence says the
uncovered channels are "not distinguished". For two of the four named channels the residue is not merely
"undistinguished" — it lands in the **killed** bucket, i.e. a false kill that inflates the kill tally (F2). That is
the doctrine the round exists to remove (`corpus/knowledge/mutant-crash-is-not-a-kill.md`: "A mutant whose counter
crashes is a runtime error, not a kill"). The wording "not distinguished" does not say "scored as a kill", so I record
it as a finding (F2) rather than a second falsification.

**No other wording is falsified.** Specifically verified *not* falsified: the C1 counted quantity and predicate; the
C2 counted quantity and predicate; the claim that the r93 rule "reports both crash fixtures `killed=yes`" (the
control does exactly that); the claim that the crash fixtures are scored `errored`; the claim that the r94 rule
keys on "a harness exit 70 or any ROW `rc=70`" (both halves are implemented as written).

---

## 2. Findings

### F1 — MEDIUM-HIGH — an `atexit`/`__del__` crash is invisible to the sentinel and is scored a SURVIVOR
(Falsification of the coverage sentence; see §1.)

*Exploit path:* a counter that finishes its work correctly and then raises at interpreter shutdown (a deferred
`atexit` cleanup that throws, or a `__del__` finalizer that throws). The hook never fires, the counter exits 0, the
harness reports `mismatches=0`, and the search prints `SEARCH <id> ... killed=no` — a crash filed as a live survivor,
to be "fixed" in a later round as if it were a semantic miss.

*Evidence:* `repro/expF.py` + `repro/counter-atexit.py` → `receipts/out-F.txt`; `repro/expE.py` → `receipts/out-E.txt`
(`del-raise` → `r94_verdict=yes`, a false kill).

*Impact:* a crash is reported as a survivor (or, for `__del__`, as a kill). The mutation-score direction of the
error is inverted; the crash sentinel's whole purpose is defeated for this channel. Reachability in r94's corpus:
none; forward risk: high (any later hand edit that defers a raise into a finalizer/atexit path, or any counter that
registers a cleanup hook).

*Smallest remediation:* the hook cannot fix this (the exception never reaches `sys.excepthook`). The smallest change
is in the search's `verdict()`/rule: treat a non-zero *stderr* signature of the counter as a crash signal too —
e.g. also fire on the harness stdout lines' `detail=` carrying "Exception ignored in atexit callback" / "Exception
ignored while calling deallocator", or (cleaner) have the harness record the counter's stderr unconditionally and let
the rule test it. Alternatively, narrow the limits sentence and the corpus entry to name the `atexit`/`__del__`
channel explicitly, so the next round does not inherit the over-promise. **Amendment required either way.**

### F2 — MEDIUM — the residual crash channels are scored as genuine KILLS (false kill), not merely undistinguished
`os._exit(1)`, `SIGSEGV` and `SIGKILL` in the counter all make the harness exit 1 with `match=no` rows, and the r94
rule (as the r93 rule did) maps "harness exit 1 + a `match=no` row" to `killed=yes`.

*Evidence:* `repro/expE.py` (real r93 harness + real r94 `verdict()`), receipt `receipts/out-E.txt`:

```
os._exit(1)    harness_rc=1  r94_verdict=yes  distinct_row_rcs=['1']
sigsegv        harness_rc=1  r94_verdict=yes  distinct_row_rcs=['-11']
sigkill        harness_rc=1  r94_verdict=yes  distinct_row_rcs=['-9']
```

*Impact:* a crashing mutant is counted in the kill tally — precisely the failure the r94 change set out to remove
for the two hand fixtures. The r94 rule moves crashes to `errored` only for *main-thread uncaught exceptions*; every
other crash shape still scores as a detection. Reachability in r94's corpus: none (the r87 counter has no `os._exit`
and the mutation operators cannot synthesise one); forward risk: high (a later hand edit that calls `os._exit(1)` —
the classic "counter dies early" shape — reintroduces the r93 defect silently, with the run still printing
`# crash-sentinel rc=70 check=pass`).

*Smallest remediation:* the cheapest correct fix is in the rule, not the hook: treat any *negative* counter exit
status (killed by a signal) and any counter exit status that is neither 0, 1, 2 nor 70 as `errored` rather than
letting it fall into the `killed` branch. `os._exit(1)` is indistinguishable from the counter's legitimate
"not all resolved" status 1 and cannot be separated by exit code alone — that one needs the stderr/traceback channel
(F1's remediation) to be separable at all. Note also `thread exceptions`: a crash in a thread leaves the counter's
exit status at 0, so the mutant is scored **survived** (`repro/expG.py`, `receipts/out-G.txt`), a third direction
of the same defect.

### F3 — MEDIUM — a harness-side crash is indistinguishable from five mutant crashes; the run still exits 0
The r94 rule treats "harness exit 70" as `errored`, and the harness inherits the hook, so an uncaught exception
*inside the harness* (an instrument bug, not a mutant) makes every mutant `errored`.

*Evidence:* `repro/harness-crash.py` (the frozen r93 harness with one `raise RuntimeError` added after the fixture
build) driven by the frozen search, receipt `receipts/out-B-harness.txt`:

```
SEARCH a127c26-True-to-False line=127 killed=errored rc=70
SEARCH a491c22-<-to-<=      line=491 killed=errored rc=70
... (all five)
SEARCH-SUMMARY generated=5 ambiguous=0 uncompiled=0 hung=0 scored=5 errored=5 killed=0 survived=0
EXIT=0
```

*Impact:* an instrument failure is reported as a measurement ("5 mutants crashed"), the search exits **0** ("the
search ran"), and the two semantic kills and the survivor are all lost with no killed/survived signal in the summary.
The counted quantity check (`errored=2 killed=2 survived=1`) does catch it downstream, so it is detectable — but only
by a reader who diffs the whole summary. The prereg's rule names "harness exit 70" explicitly, so this is within the
stated rule; it is an operability/attribution gap, not a wording falsification.

*Smallest remediation:* have the search distinguish "the harness died" from "the counter died" — e.g. treat a
harness exit of 70 with **no** `ROW` lines (or with a `--stderr--` section containing a traceback) as a run-level
setup failure (exit 2), and reserve `errored` for mutants whose ROW lines carry `rc=70`.

### F4 — MEDIUM — the sentinel's own precondition check does not exercise the chain that matters
The search prints `# crash-sentinel rc=70 check=pass` after running the hook in a **direct child of the search**
(`subprocess.run([sys.executable, "-B", "-c", "raise ..."])`). It never checks that the *harness* hands the hook to
the *counter*. A harness that scrubs `PYTHONPATH` from its own environment restores the r93 defect completely, and
the receipt still says `check=pass`.

*Evidence:* `repro/harness-nopythonpath.py` (the frozen harness plus `os.environ.pop("PYTHONPATH", None)`), receipt
`receipts/out-A-harness.txt`:

```
# crash-sentinel rc=70 check=pass
SEARCH h-crash-late  line=574 killed=yes rc=1      <-- back to the r93 defect
SEARCH h-crash-index line=494 killed=yes rc=1
SEARCH-SUMMARY generated=5 ... errored=0 killed=4 survived=1
EXIT=0
```

*Impact:* the predicate's `# crash-sentinel rc=70 check=pass` line is not evidence that the two crash fixtures will
be seen as crashes. The frozen r93 harness does propagate the hook (it spawns the counter without `env=`, inheriting
the search's environment — confirmed by the `rc=70` rows in `receipts/harness-out/*.harness.out`), so this is latent
today; the check would not catch a regression in that inheritance.

*Smallest remediation:* make the precondition check run the hook the way the counter runs it — i.e. spawn the
harness's own spawning shape, or have the harness echo the hook's presence (e.g. `import sitecustomize` /
`sys.excepthook is not sys.__excepthook`) into a line the search can assert on. The corpus entry already names this
gap in prose ("a harness that changed how it starts the counter would need its own check"); the check itself does not
implement it.

### F5 — MEDIUM — the C2 probe and the arms counter have no timeout: a hanging fixture hangs the whole measurement
`c2-forgery-probe.py` runs the fixture with `subprocess.run(...)` and no `timeout=`; `c2-setup-arms.py` runs the probe
the same way. A fixture that hangs therefore hangs the probe, and hangs all ten arms of the arms counter, forever.

*Evidence:* `receipts/out-hang.txt` (probe with a `time.sleep(600)` fixture → the probe was still running when the
25 s external `timeout` fired, exit 124) and `receipts/out-armshang.txt` (the arms counter with a hanging probe →
exit 124, the arms run never finishes).

*Impact:* no exit code, no `C2-FORGERY-FATAL:` line, no cleanup — the wave's own measurement stalls with no
diagnostic. The prereg's C2 STATED LIMITS (i) explicitly lists "a fixture that hangs" as one of the failures the
wave is to try, so this is an invited finding, not a wording falsification.

*Smallest remediation:* give the probe's `run()` and the arms counter's `one()` a `timeout=` and treat expiry as a
setup failure (exit 2 with a `C2-FORGERY-FATAL:` line); give the arms counter a per-arm timeout so one hanging arm
cannot stall the other nine.

### F6 — MEDIUM — a write failure inside the C2 probe exits 1 — the verdict code — with no `C2-FORGERY-FATAL:` line
The probe's setup checks run once at startup; the forgery copies are written later. If a write fails (disk full,
read-only work tree, quota), the exception escapes `main()` uncaught: Python prints a traceback and exits **1** —
the same exit code as "a forgery was not rejected". The probe's own docstring promises "Every setup failure exits 2
with one `C2-FORGERY-FATAL:` line on stderr".

*Evidence:* `repro/writefail.py` (the probe is allowed to start, then `--work` is made unwritable so the forgery
copy cannot be written), receipt `receipts/out-writefail.txt`:

```
PROBE EXIT: 1
...
PermissionError: [Errno 13] Permission denied: '.../wf-work/F1-souji-record-agreement.py'
--- any C2-FORGERY-FATAL on stderr? --- False
```

A second, simpler instance of the same defect: `--work` under a non-creatable parent →
`PermissionError` traceback, exit 1 (`receipts/out-f1.txt`).

*Impact:* exactly the defect the r93 closure routed as defect 5 ("a setup failure is indistinguishable from a
surviving forgery") survives in the r94 probe for the mid-run failure class. A consumer that reads the exit code
sees "a forgery survived" where the truth is "the probe could not write". The prereg's C2 limits (i) invite
"disk full mid-run" explicitly.

*Smallest remediation:* wrap the whole body of the probe's `main()` (or at least the forgery loop) in a
`try/except OSError` that prints `C2-FORGERY-FATAL: ...` and returns 2 — one handler converts every such failure into
the documented setup code.

### F7 — MEDIUM — check-then-use TOCTOU on `--work`: writes can be redirected outside `--work`
The probe checks `--work` once (empty / not a directory) and then writes into that tree seconds later, during the
slow positive-control fixture run. An actor who can write into `--work` can plant a symlink in that window and
redirect the fixture's writes to an arbitrary directory; the probe still reports success.

*Evidence:* `repro/race.py` (a symlink `work/F1` is planted as soon as the positive control has run), receipt
`receipts/out-race.txt`: `PROBE EXIT: 0`, `FORGERY-SUMMARY forgeries=8 rejected=8 positive=pass`, and **68 files
including a whole git repository** landed in the symlink target `race-target/`, outside `--work`.

The same check-then-use shape lets a *given* `--work` that is a symlink to an empty directory redirect every write:
`receipts/out-linkdir.txt` (probe) and `receipts/out-h1.txt` (C1 search) both show the files landing in the symlink
**target**, not in the path named on the command line.

*Impact:* the "scratch only under `--work` (never /tmp)" invariant is enforced only at the moment of the check, and
the writes afterwards follow whatever the path resolves to at write time. The C1 search has the same pattern: the
hook file and all mutant work trees land in the symlink target.

*Smallest remediation:* re-validate the resolved path at write time (open with `O_NOFOLLOW`, or re-`realpath` and
compare against the `--work` realpath before each write), or build the whole run inside a private directory created
by the instrument itself (`tempfile.mkdtemp` under a non-/tmp root) and move/verify at the end.

### F8 — LOW-MEDIUM — setup errors in the C1 search and the arms counter exit 1, an undocumented code that collides with a verdict code
`c1-survivor-search.py` documents "exit 0 when the search ran, 2 on setup error, 130 when interrupted". Three setup
errors escape as an uncaught traceback with exit **1**: `--work` is a dangling symlink (`FileExistsError`),
`--work` is an existing regular file (`NotADirectoryError`), `--work` is under a non-creatable parent
(`PermissionError`). Same shape in `c1-forgery-controls.py` and in `c2-setup-arms.py` — and for the arms counter
exit 1 is exactly "some arm did not conform", which is the verdict code of the arms counter itself.

*Evidence:* `receipts/out-c1bls.txt` (search, dangling symlink → `FileExistsError`, exit 1),
`receipts/out-g1.txt` (search, `--work` a regular file → `NotADirectoryError`, exit 1),
`receipts/out-bl2.txt` (arms counter, dangling symlink → `FileExistsError`, exit 1, and **no `ARMS-SUMMARY` line
at all**), `receipts/out-c1blf.txt` (forgery controls, same).

*Impact:* an exit code the instrument never documents, and for the arms counter a code that collides with its own
"did not conform" verdict. A consumer that reads only the exit code learns nothing; only the missing summary line
reveals the setup error.

*Smallest remediation:* in each instrument, replace the `os.path.exists(...)`/`os.listdir(...)`/`os.makedirs(...)`
sequence with an `O_NOFOLLOW`-style check plus a `try/except OSError` that prints the instrument's fatal line and
returns 2 — the C2 probe already does exactly this (`os.path.lexists` + `not os.path.isdir` → exit 2), so the
r94 probe's own discipline is the model to copy into the search, the arms counter and the forgery controls.

### F9 — LOW — the `/tmp` guard's prefix test misses the directory `/tmp` itself
Every instrument guards with `os.path.realpath(work).startswith(("/tmp/", "/var/tmp/", "/dev/shm/"))`. The string
`"/tmp"` does not start with `"/tmp/"`, so a `--work` whose realpath is exactly `/tmp` (or `/var/tmp`,
`/dev/shm`) is not caught by the tmp guard.

*Evidence:* `receipts/out-g2.txt` / `out-g3.txt` / `out-g4.txt` — `--work /tmp` is refused by the *emptiness* check
("is not empty"), not by the tmp guard, i.e. the guard itself is bypassed and only an incidental property of this
host saves it. A symlink resolving to exactly `/tmp` is likewise only caught by emptiness
(`receipts/out-tlink.txt`: "C2-FORGERY-FATAL: --work ... is not empty").

*Impact:* on a host with an empty `/tmp` (containers, fresh boots) the guard would admit `--work /tmp`, defeating
the "never /tmp" invariant the instruments claim in their docstrings.

*Smallest remediation:* test `realpath in ("/tmp", "/var/tmp", "/dev/shm")` as well, or use `os.path.commonpath`.

### F10 — LOW — the hook shadows (does not chain) any other `sitecustomize`; none exists on this host
*Evidence:* the hook is placed **first** on `PYTHONPATH`, and `site` imports exactly one `sitecustomize`, so the hook
wins over a `sitecustomize.py` shipped in site-packages or the user site dir — the shadowed one never runs for the
harness or the counter. Verified ordering: with the hook first, a `sitecustomize.py` beside the script is *not*
imported (`receipts` not applicable — reproduced in-session: the hook's marker printed, the script-dir one did not);
with the other entry first, the other one wins. On **this** host there is nothing to shadow: `importlib.util.find_spec`
returns `None` for both `sitecustomize` and `usercustomize`, and no `sitecustomize.py`/`usercustomize.py` exists in
`/usr/lib/python3.14/site-packages` or `~/.local/lib/python3.14/site-packages`. `PYTHONNOUSERSITE=1` does **not**
disable the hook (it comes from `PYTHONPATH`, not the user site dir) — verified.

*Impact:* none today. Forward risk: a host or venv with a `sitecustomize.py` (coverage, a debugger, an audit hook)
would silently lose it for every harness and counter invocation, and the after-arm and the r93 control would then run
the counter under different site semantics — a silent asymmetry between the arms being compared.

*Smallest remediation:* have the hook chain to the shadowed module if one exists (import it by path and call it), or
have the search record the hook's presence in the receipt so a reviewer can see which `sitecustomize` won.

### F11 — LOW — the receipt proves a crash happened but not what it was
The counter's traceback goes to the counter's stderr; the harness surfaces the counter's stderr only on `rc == 2`
rows, as a 200-character `detail=` repr. A crash fixture (rc=70) therefore leaves **no** traceback and **no**
`detail=` in the receipt.

*Evidence:* `receipts/harness-out/h-crash-late.harness.out` and `h-crash-index.harness.out`: `grep -c
"RuntimeError\|Traceback"` = 0, `grep -c "detail="` = 0, and the `--stderr--` section is empty.

*Impact:* a receipt reader sees `rc=70` and knows "the counter crashed", but cannot tell from the receipt whether it
was the intended `h-crash-late` raise or some other fault. This is disclosed for C1 in the corpus entry ("The harness
does not surface the counter's stderr, so a rule that greps for `Traceback` in the harness output misses a crash"),
so it is an evidence-quality note rather than a defect — but it also means F1/F2's residual channels would be
invisible in a receipt too.

*Smallest remediation:* have the harness emit the counter's stderr for every row (or at least for `rc=70` rows) into
`harness.out`, so the receipt carries the crash cause.

### F12 — LOW — `os._exit(70)` in the hook skips the counter's own shutdown work
The hook flushes `sys.stdout`/`sys.stderr` and then calls `os._exit(70)`, which bypasses `atexit` handlers, `__del__`
finalizers and the interpreter's normal finalisation. Only the two standard streams are flushed, so any other
buffered stream the counter held (a log file, a `io` object) loses its tail; the counter's own cleanup never runs.

*Evidence:* mechanism is standard CPython behaviour; the flush of stdout/stderr is explicit in the hook body
(`census/round-94/c1-survivor-search.py`, the `HOOK` string), so the *stdout* loss risk is closed — verified: a
counter that writes without a newline and then raises still shows the partial text on stdout with the hook
(`receipts/out-A.txt`, case `buffered-stdout`: `stdout_has_partial=True`). The residual is the non-stdout streams and
the skipped cleanup.

*Impact:* low; relevant only if a future counter relies on shutdown cleanup for correctness (e.g. to remove a
scratch file it created) — the cleanup would not run and could leak scratch.

*Smallest remediation:* if it ever matters, have the hook call `sys.excepthook` and then `os._exit(70)` only after
running `atexit` handlers explicitly — or, cheaper, keep `os._exit(70)` but document that shutdown cleanup is
skipped (the receipt's `rc=70` is the load-bearing signal anyway).

---

## 3. Items checked with NO finding (what was tried)

* **Hook containment / leak outside the harness tree — no leak.** The hook is passed by env only: the search sets
  `env["PYTHONPATH"]` on the harness subprocess; the harness inherits it and the counter inherits it from the harness
  (the harness spawns the counter with no `env=`, so the counter gets it — this is why `rc=70` appears in the
  receipts). Nothing else in the tree gets it: the search's own process never has the hook on its `sys.path`
  (the search only adds it to the env dicts it passes to children), the harness's `git` calls do inherit it but
  `core.hooksPath=/dev/null` is set on every git invocation, and `git` is not Python. After the runs, no process of
  mine was left running (`pgrep` for my scratch: none) and the lane and the fleet root contain no file created by my
  runs.
* **Hook shadowing an existing `sitecustomize` on this host — nothing to shadow** (F10 covers the mechanism; the host
  has no `sitecustomize`/`usercustomize`).
* **`PYTHONNOUSERSITE`, `python -I`, `python -E`, `python -S` — no effect on the C1 chain as it stands.**
  `PYTHONNOUSERSITE=1` does not disable the hook (verified: the hook's marker still printed). `-I`/`-E` ignore
  `PYTHONPATH` entirely, so the hook would not load in such a child — but nothing in the C1 chain spawns the counter
  with `-I`/`-E` (the harness uses `[sys.executable, "-B", counter, ...]`), and the search's own precondition check
  would catch a hook that failed to load (it exits 2 with `C1-SEARCH-FATAL: crash sentinel did not fire`). Note the
  C2 *tool* path does use `-I` (`tools/souji-record-agreement.py`), which is unrelated to the hook.
* **Pre-set `PYTHONPATH` — preserved, and the hook still wins the `sitecustomize` slot.** The search builds
  `env["PYTHONPATH"] = ns.hook + os.pathsep + <ambient>` (hook first). An ambient `PYTHONPATH` entry that shadows a
  stdlib module does reach the counter (demonstrated: a `re.py` on an ambient `PYTHONPATH` is imported by the counter
  instead of the stdlib `re`), so the ambient environment can change the counter's behaviour — but the after-arm and
  the r93 control share the same ambient environment, so it does not bias the comparison, and the hook's own
  directory contains only `sitecustomize.py`, so it shadows nothing else.
* **Buffered stdout at the moment of the crash — not lost.** The hook flushes both standard streams before
  `os._exit(70)`; a counter that wrote a partial line without a newline still has that text on stdout with the hook
  (`receipts/out-A.txt`). F12 covers the residual (non-stdout streams, skipped shutdown cleanup).
* **os._exit(1), SIGSEGV, SIGKILL, thread crash, `atexit`, `__del__` — all characterised** (F1, F2). Measured
  exit statuses and verdicts are in `receipts/out-C.txt`, `out-E.txt`, `out-G.txt`.
* **A counter that legitimately exits 70 — scored `errored`** (as the limits sentence discloses): `repro/expG.py`,
  `receipts/out-G.txt` (`legit-exit-70 → r94_verdict='errored'`). No finding beyond the disclosure; it is the
  reason the rule's `rc=70` test alone cannot be the whole story.
* **`/tmp` writes — none.** No instrument references `tempfile`, `mkdtemp`, `gettempdir` or a literal `/tmp` path
  outside the guard strings (grepped every instrument: `census/round-94/c1-survivor-search.py`,
  `c1-control-r93-rule.py`, `c1-forgery-controls.py`, `c2-forgery-probe.py`, `c2-setup-arms.py`,
  `c2-forgery-controls.py`, `census/round-93/c1-false-row-harness.py`, `census/round-87/c1-pointer-counter.py`,
  `tests/fixtures/r92-k4-flagfail.py`, `tests/fixtures/r93-k4-flagfail.py`, `tools/souji-record-agreement.py`,
  `census/round-92/controls/c2-before-tool.py`). Empirically: with `TMPDIR` pointed at an empty probe directory, the
  C1 search and the C2 probe left that directory **empty** (`receipts/out-f4.txt`, and the C1 run's probe dir).
* **Paths written outside `--work` in the normal (non-adversarial) flow — none.** The C1 search keeps everything
  under `--work` (`hook/`, `mNNNN/`); the per-mutant harness work tree is deleted after scoring (the run left 224 K
  in `--work`). The C2 probe writes only under `--work` (`F<n>-souji-record-agreement.py`, `F<n>.out`, `F<n>/`,
  `positive/`). F7 covers the adversarial case.
* **Lane and fleet-root mutation — none.** `find .git -newermt '-3 hours'` in the lane returned 0 files; the lane's
  working tree shows only other seats' files; nothing was written under `/home/vgpnk/Projects/shokunin/.ufo/`.
* **Process cleanup — the C1 search is clean; the C2 probe is not.** The C1 search kills the whole harness process
  group on SIGINT/SIGTERM and deletes the work trees (exit 130). The C2 probe has no signal handling and no cleanup:
  killing the probe leaves the fixture running as an orphan (verified: the `hang2.py` fixture survived the probe's
  death and had to be killed separately). Folded into F5's remediation, since a timeout plus a group kill fixes both.

---

## 4. Bottom line

* **NO-FALSIFICATION of either claim's counted quantity or predicate.** Both predicates reproduce exactly
  (`errored=2 killed=2 survived=1`; `arms=10 conform=10`), both controls reproduce exactly (`errored=0 killed=4
  survived=1`; `arms=10 conform=3`), and the crash mechanism is visible in the receipts (`rc=70` on all 66 rows for
  `h-crash-late`, on the single `ledger-trim` row for `h-crash-index`).
* **One falsification of a stated sentence (F1/§1):** the sentinel's coverage sentence — in the prereg's C1 STATED
  LIMITS (ii) and, word for word, in `corpus/knowledge/mutant-crash-is-not-a-kill.md` — over-promises. An
  `atexit`/`__del__` crash is uncaught, in the main thread, site-enabled, and is **not** covered: the counter exits 0
  and the mutant is scored `survived`. The corpus entry's identical sentence is falsified too. This needs an
  amendment in `plans/round-94.md`; it does not move any number.
* **Nine further findings**, MEDIUM to LOW, none of which changes a number: F2 (the remaining crash channels score as
  false kills), F3 (a harness crash is filed as five mutant crashes, exit 0), F4 (the precondition check does not
  test the chain it certifies), F5/F6/F7/F8 (the C2 instruments' setup handling: no timeout, exit-1 escapes, TOCTOU,
  undocumented exit 1), F9 (`/tmp` guard prefix hole), F10 (hook shadowing), F11 (no crash cause in the receipt),
  F12 (`os._exit` skips shutdown cleanup).

Severity counts: 1 MEDIUM-HIGH, 5 MEDIUM, 1 LOW-MEDIUM, 5 LOW. Findings with reproducers: 12/12.
Tool installs: none. Scratch: deleted.
