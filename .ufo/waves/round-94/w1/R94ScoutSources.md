# R94ScoutSources — round 94 scout seat (sources)

Scope of this seat: (1) re-open the round's two new sources live and verify the S357/S358 rows
against them; (2) find one more candidate source on how a mutation tool classifies a crashing
run and judge it admit/reject against `corpus/QUALITY.md` and `PROVINCE.md`.

Lane read-only. All writes are under `.ufo/waves/round-94/w1/R94ScoutSources/` and this report.
Scratch under `/fast/scratch/hyaku/souji-r94/R94ScoutSources/` (deleted before yield).

Tool installs: none (no tool needed for this round).

---

## FALSIFIES-WORDING

Two sentences of the frozen preregistration are falsified by artifacts of this seat. Neither
changes the C1 predicate output (I re-ran it: it still prints the preregistered summary — see
`receipts/c1-predicate-after.out`), so these are wording defects, not numeric defects. Under
Amendment 59 the L1 records both as narrowing amendments in `plans/round-94.md`.

### FALSIFIES-WORDING 1 — C1 STATED LIMITS (ii) does not list SystemExit, and the sentinel misses it

Preregistration, C1, `STATED LIMITS` (ii), verbatim:

> The sentinel covers an uncaught exception in the main thread of a Python process started with
> site enabled; os._exit, signals, thread exceptions and a counter that legitimately exits 70 are
> not distinguished.

Two independent problems, both shown below.

**(a) The enumeration is incomplete.** The limit lists `os._exit`, signals, thread exceptions and a
legitimate exit 70 as the not-distinguished cases. It does not list **SystemExit**, which CPython
routes around `sys.excepthook` entirely: the interpreter handles `SystemExit` itself and never
calls the hook. A counter that ends in `raise SystemExit(1)` therefore exits **1** — the counter's
own "not every item resolved" status — and the r94 rule cannot see it as a crash.

Reproducer (uses the frozen search's own `HOOK` bytes and `verdict()` function; nothing under
`census/` is executed or written):

```
python3 -B .ufo/waves/round-94/w1/R94ScoutSources/repro-sysexit-gap.py
```

Output (`repro-sysexit-gap.out`):

```
CASE RuntimeError (h-crash-late shape): child rc=70 verdict=errored
CASE SystemExit(1): child rc=1 verdict=yes
CASE os._exit(1): child rc=1 verdict=yes
GAP-REPRODUCED
```

The reproducer's scratch is a `tempfile.mkdtemp(dir="/var/tmp")` removed by its own `finally`
(QUALITY Q4: `grep -c 'TMPDIR:-/tmp'` → 0, `grep -c '/var/tmp'` → 1, no residue after the run).

**(b) The gap is reachable through the real harness, and it flips the verdict.** The reproducer
above is synthetic at the `verdict()` level. I also ran the **real** frozen harness
(`census/round-93/c1-false-row-harness.py`, unchanged) against two counter variants that differ
only in the exception type raised at one crash site, with the frozen `HOOK` on `PYTHONPATH`:

- `receipts/e2e-sysexit-early-harness.out` — counter raises `SystemExit(1)` at the crash site
  (the same site as the frozen `h-crash-index` fixture). Harness output row:
  `ROW LD6 where=ledger-trim rev=BASE item=P04 class=- expect=MOVED/0 got=- rc=1 match=no`.
  No `rc=70` row exists. Applying the frozen `verdict()` to this real harness output gives
  **`yes`** (killed).
- `receipts/e2e-runtimeerror-early-control.out` — identical counter, `RuntimeError` instead
  (the frozen `h-crash-index` shape). Row: `... got=- rc=70 match=no`. Same frozen `verdict()`
  gives **`errored`**.

So the same crash site, same harness, same frozen scoring rule, one byte of difference in the
raised exception type, flips the mutant between `errored` and `killed`. The r94 rule's own
docstring says a crash is "a crash, whatever the exception" — the exception *type* decides, and
`SystemExit` is the one type the sentinel cannot see.

Note the `os._exit(1)` case scores `yes` too, which the entry already discloses ("A counter that
calls `os._exit(1)` ... is not caught"). The SystemExit case is **not** disclosed anywhere, in
the preregistration or in `corpus/knowledge/mutant-crash-is-not-a-kill.md`.

**Reachability.** The frozen counter (`census/round-87/c1-pointer-counter.py`, sha256
`fd0a8e24…`) contains no `SystemExit`, no `os._exit` and no `threading` token
(`grep -c` → 0/0/0), so the frozen five targets cannot reach it. But the counter's own exit path
is `sys.exit(main(sys.argv[1:]))` (line 578) — the counter's *normal* exit is a `SystemExit`, and
the frozen sentinel deliberately does not intercept it. That is precisely why the sentinel is
usable at all: intercepting `SystemExit` would turn every normal counter exit into `rc=70`. The
sentinel's correctness therefore *depends* on CPython's `SystemExit` exclusion — a behaviour that is
currently grounded by nothing in `corpus/SOURCES.md` (S357 covers Stryker's mutant states, S358
covers `EX_SOFTWARE`; there is no row for `sys.excepthook`). The r93 defect being fixed was
exactly this: "a Python crash exits 1, the counter's own 'not all resolved' code"
(Q170). A mutant that converts an early exit into `SystemExit` reproduces the r93 defect on the
r94 rule.

**Recommended narrowing (for the L1 to record).** Amend C1 `STATED LIMITS` (ii) to add
`SystemExit` to the not-distinguished list, e.g.: "…`os._exit`, signals, thread exceptions,
**`SystemExit`**, and a counter that legitimately exits 70 are not distinguished; a counter that
ends in `SystemExit` exits 1, the counter's own status, and is scored `killed`." The corpus
knowledge entry `corpus/knowledge/mutant-crash-is-not-a-kill.md` needs the same sentence added to
its `## Limits` section. A ground row for CPython's `sys.excepthook`/`SystemExit` behaviour is
needed either way (candidate below); the counter-intrinsic `sys.exit` dependency deserves a line
in the entry's `## Limits` too.

### FALSIFIES-WORDING 2 — C1 STATED LIMITS (ii) says "signals", but the sentinel does not see signals either, and the corpus does not ground the claim's exit-code premise

Preregistration, C1, `STATED LIMITS` (ii), the same sentence quoted above, contains the clause
"a status no harness verdict (0, 1) or setup error (2) uses" in the S358 `teaches` cell and
"70 is S358's EX_SOFTWARE" in the entry. My check of the *claim's* own numeric premise is
separate and does **not** falsify the preregistration: the C1 predicate re-runs green
(`receipts/c1-predicate-after.out` prints exactly
`SEARCH-SUMMARY generated=5 ambiguous=0 uncompiled=0 hung=0 scored=5 errored=2 killed=2 survived=1`,
EXIT 0, with `h-crash-late` and `h-crash-index` both `killed=errored`). The C1 *numbers* verify.

The falsification is narrower and is about the corpus row's `teaches` cell, which asserts the
premise "a Python crash exits 1" that the r93 defect rested on. That premise — that an uncaught
Python exception exits **1** — is the load-bearing fact of the whole r94 correction, and it is
**not** stated in S357 or S358, and it is not in `corpus/SOURCES.md` at all:

```
grep -c 'excepthook' corpus/SOURCES.md      → 0
grep -n 'uncaught' corpus/SOURCES.md        → no row
```

The knowledge entry's `## Why the r93 rule miscounts` asserts "A Python program that raises an
uncaught exception exits 1" as a bare fact with no source row behind it (its `source:` line names
only S357 and S358). The entry's `verified-at:` records the two page digests but does not ground
this interpreter fact. This is exactly the class of gap QUALITY Q1/Q2 and the r93 M1 lesson
("an assumption about a crash's exit code, written into a docstring and a prereg, never run")
are about. Recommend the L1 record this as a second narrowing amendment and add a ground row (the
candidate below is the natural one) before the entry is cited as grounding the exit-code premise.

I do **not** claim C1's numbers are wrong: the predicate output verifies exactly. I claim the
*stated limit* is wrong about coverage (SystemExit) and the *corpus grounding* of the entry's
exit-code premise is missing.

---

## Per-row verification table (S357, S358)

Both sources re-opened live on **2026-11-09** from the URLs filed in `corpus/SOURCES.md`. Both
pages are byte-identical to the frozen captures: no dynamic-page drift, so the tag-stripped-text
diff fallback was not needed.

| row | URL | HTTP | live bytes | live sha256 | filed bytes | filed sha256 | hash match |
|---|---|---|---|---|---|---|---|
| S357 | https://stryker-mutator.io/docs/mutation-testing-elements/mutant-states-and-metrics/ | 200 | 27068 | `30071cc7b6578a114843f18da568c305b192a08d098511896e7cb4a90a5f89da` | 27068 | `30071cc7b6578a114843f18da568c305b192a08d098511896e7cb4a90a5f89da` | **yes** |
| S358 | https://man.freebsd.org/cgi/man.cgi?query=sysexits | 200 | 59385 | `da498cbc711a743ae309b603ae8615f1164690cb6d4a67dea2e650175cbae139` | 59385 | `da498cbc711a743ae309b603ae8615f1164690cb6d4a67dea2e650175cbae139` | **yes** |

Live bytes preserved at `receipts/stryker-live.html` and `receipts/sysexits-live.html`; the
committed captures `census/round-94/srcs/{stryker,sysexits}.html` have the same digests.

### Quote / word-count / occurrence-count check

Method: strip tags, decode entities, collapse whitespace, then count occurrences of the exact
quoted sentence. Two independent texts per row: the **live** page and the **committed capture**
`census/round-94/srcs/<page>.txt` (which the row names as the counted text).

| row | quoted sentence | words (filed) | words (counted) | occurrences (live) | occurrences (capture .txt) | quote present |
|---|---|---|---|---|---|---|
| S357 | "The running of the tests resulted in an error (rather than a failed test)." | 14 | **14** | **1** | **1** | yes |
| S358 | "EX_SOFTWARE (70) An internal software error has been detected." | 9 | **9** | **1** | **1** | yes |

Both rows' word counts and occurrence counts **verify as filed**.

### Anchor / locator check

| row | filed locator | located? | note |
|---|---|---|---|
| S357 | § Mutant states, the "Runtime error" entry | **yes** | page has `<h2>Mutant states</h2>`; the entry is the 4th `<li><strong>Runtime error</strong>` in that list. Quote present exactly once. |
| S358 | § DESCRIPTION, the EX_SOFTWARE entry | **NO — wrong section** | see finding below. |

**S358 locator defect (corpus row, not a claim sentence).** The row and the round-94 lesson Gate
(`corpus/lessons/round-94.md:32`) both locate the quoted sentence at **§ DESCRIPTION**. In the
FreeBSD sysexits(3) page the quoted `EX_SOFTWARE (70)` entry is under **§ ERRORS**, not
§ DESCRIPTION. § DESCRIPTION is a different, three-sentence section:

```
DESCRIPTION Some commands attempt to describe the nature of a failure condition by using these
pre-defined exit codes. This interface has been deprecated and is retained only for compatibility.
Its use is discouraged.
```

Offset check on the committed capture text (`census/round-94/srcs/sysexits.txt`):
`DESCRIPTION@10597  ERRORS@10817  EX_SOFTWARE(70)@11951` → `EX_SOFTWARE` is under `ERRORS`
(10817 < 11951), not under `DESCRIPTION` (10597 < 11951 but the DESCRIPTION body ends at 10817).
This is the same defect class as QUALITY Q54 (`§ <NAME>` locator must resolve to the heading
whose content is cited) and the S255/S256/S257 supersede-rows precedent. Under SOURCES-CONTRACT-v1
rule 2 a correction is a **new** row whose `teaches` opens `supersedes S0NN —`; the frozen S358
row itself stays as filed. **I did not edit `corpus/SOURCES.md`** (frozen this round, and outside
my seat's write scope) — this is for the L1 to route.

A second, smaller S358 observation for the same correction: § DESCRIPTION carries the sentence
"This interface has been deprecated and is retained only for compatibility. Its use is
discouraged." The row's `scope` cell says "scope: the EX_SOFTWARE entry only", so the deprecation
notice is out of the row's stated scope — but a reader who follows the (wrong) locator lands on
exactly that deprecation notice and may take the row as endorsing a convention the page itself
disclaims. The corrected row should cite § ERRORS and either note the deprecation or keep §
DESCRIPTION out of scope explicitly.

Also checked, both rows:
- S357 `teaches` cell: "a state distinct from killed and left out of the mutation score" — the
  page supports both halves. "It is not represented in your mutation score." appears twice
  (Runtime error and Compile error entries); the Runtime-error entry's own text and the metric
  lines `Valid detected + undetected` / `Invalid runtime errors + compile errors` corroborate it.
  The "Killed" quote in the entry ("When at least one test failed while this mutant was active,
  the mutant is killed.") is present verbatim, count 1.
- S358 `teaches` cell: "an uncaught exception in a counter under test exits 70, a status no
  harness verdict (0, 1) or setup error (2) uses" — the exit-status claim checks out against the
  lane: the frozen harness returns 0/1 (`return 0 if mism == 0 and errs == 0 else 1`, line 560)
  and 2 for setup errors (lines 402–563); the r94 probe returns 0/1/2. No lane instrument uses
  70 for anything else (`grep -rn '\b70\b'` over `tools/` and `census/` finds only r94's own
  `CRASH_RC = 70` and unrelated numeric literals). The row's quote and word count are fine; only
  the section locator is wrong.

---

## Candidate source: PIT `DetectionStatus` (Java) — REJECT

- **URL**: https://raw.githubusercontent.com/hcoles/pitest/1.30.2/pitest/src/main/java/org/pitest/mutationtest/DetectionStatus.java
- **Access date**: 2026-11-09, HTTP 200, 2988 bytes, sha256 `3bf295ad53126560ec284c42b384fc3288f7b2e674da987f38d7380ec5d419c6`
  (byte-identical to `master`; pinned to the released tag **1.30.2**). Copy at
  `receipts/pit-DetectionStatus-1.30.2.java`.
- **Located quote (≤25 words)**, at `DetectionStatus.java:60-63`, the `RUN_ERROR` constant's own
  javadoc:
  > "Something went wrong. Don't know what but it was probably bad."
  (11 words; occurrence count 1 in the file)

**What it would teach.** PIT's `DetectionStatus` enum has a state distinct from `KILLED` and
`SURVIVED` for a run that went wrong (`RUN_ERROR`, line 63), and maps a process exit code to it
(`getForErrorExitCode`, lines 91–98: an exit code that is neither `OUT_OF_MEMORY` nor `TIMEOUT`
becomes `RUN_ERROR`). That is the same conceptual move as S357's Stryker "Runtime error" state, and
it would corroborate S357 from a second, independent mutation tool.

**Verdict: REJECT.** Reason, judged against `corpus/QUALITY.md` and `PROVINCE.md`:

1. **PROVINCE — out of province.** `PROVINCE.md` owns "fleet repository & workspace hygiene
   (掃除) — receipt-gated removal of stale, duplicate, and already-preserved artifacts" and the
   Obsidian-preservation ledger. The lane's existing mutation-testing rows are admitted as
   *ground for the lane's own instruments* (S357 grounds souji's own kill rule; S340 grounds the
   lane's own adequacy criterion). PIT's `DetectionStatus` grounds nothing souji uses: souji runs
   no Java tool, and the r94 search is Python. It would be a second-tool opinion about a
   convention, not ground for a lane instrument. A duplicate-URL/different-tool row for its own
   sake is what SOURCES-CONTRACT-v1 rule 4 ("Expansion is knowledge, not rows") and QUALITY's
   corpus-economy rules exist to prevent.
2. **QUALITY — no consumer.** Contract rule 1 makes a row a claim that must be cited by a
   `used-by` path, and QUALITY Q62 requires the citation to be **bidirectional**: a row whose
   `used-by` names `corpus/knowledge/mutant-crash-is-not-a-kill.md` while that entry's `source:`
   line does not cite the row is a defect. The r94 entry is **frozen this round** (it is a filed
   instrument, P1), so its `source:` line cannot be amended to cite a new row without breaking the
   freeze. No other entry consumes PIT's enum.
3. **QUALITY Q2 — prose beats source here.** Q2 says to cite source code at a tag where docs are
   silent or disagree. PIT's own documentation does not classify a crashing run in these terms,
   so a source row would be reachable; but Q2 is a rule for *admitted* knowledge, and there is no
   admitted knowledge to ground. The criterion does not create the consumer.

**Flip condition.** Admit if a lane instrument ever classifies a crash by a Java tool's status
vocabulary (nothing in `PROVINCE.md`'s work surfaces implies one), or if a *new* knowledge entry
whose `source:` line cites this row is admitted — for example an entry recording that mutation
tools disagree about crash classification, which would then need the Stryker page (S357), this
file, and a Python-mutation-tool source together. Note the PIT enum is a **corroborating**
counterexample, not a contradiction: PIT's `RUN_ERROR` carries `detected = true` (line 63), i.e.
PIT *does* count a crashed run as detected, whereas Stryker leaves it out of the mutation score.
That divergence is real but it is a fact about PIT and Stryker, not about souji's rule; a
knowledge entry that needed it would have to say so explicitly.

### Screened alternatives (for the L1's search log, not verdicts)

- **mutmut** (`https://mutmut.readthedocs.io/en/latest/`, HTTP 200, 51074 bytes, sha256
  `07453b3fdb3b962a4cc5aff66d7614a11016c9ce0ea482654c99e17688ec9cad`): the current docs describe
  mutmut 3's result kinds without a "crash" classification that maps to a mutant verdict. The
  word "suspicious" (mutmut 2's ambiguous-result kind) does not occur in the 3.x page at all
  (occurrence 0). No quote to ground a claim → not a candidate.
- **Python `sys.excepthook` docs** (`https://docs.python.org/3/library/sys.html#sys.excepthook`,
  HTTP 200, 280632 bytes, sha256 `0f8611f5b4bf2701e4c25ec458b31c988ef785235a8c5340bfaecc73d2205838`,
  Python 3.15.2 documentation, "Last updated on Nov 09, 2026"): the right *shape* of source for
  the missing ground (it states the `SystemExit` exclusion explicitly), but it is the **second**
  row for one knowledge claim and the r94 entry is frozen this round, so it cannot be cited
  bidirectionally now. **Recommend the L1 open it in the round that amends the entry** (or the
  round after this one) with the quote:
  "When an exception other than SystemExit is raised and uncaught, the interpreter calls
  sys.excepthook with three arguments" (17 words, occurrence 1 in the whitespace-normalized
  tag-stripped text of the live page).

---

## Other checks run (no falsification)

- **C1 predicate re-run** with the frozen instruments and the frozen ids
  (`census/round-94/c1-targets.json`, sha256 `0117cad7…`): EXIT 0, and the output is exactly the
  preregistered literal — `SEARCH-SUMMARY generated=5 ambiguous=0 uncompiled=0 hung=0 scored=5
  errored=2 killed=2 survived=1`, with `h-crash-late` and `h-crash-index` both `killed=errored`,
  `h-ok-admits-one` and `a491c22-<-to-<=` both `killed=yes`, `a127c26-True-to-False` `killed=no`.
  Instrument digests printed by the run match the prereg pins (counter `fd0a8e24…`, harness
  `1868a570…`, population `d6439f65…`, search `97b8defa…`). **C1's numbers verify.**
- **C1 sentinel inheritance** — the prereg says the sentinel is "inherited by the harness and the
  counter it spawns". Confirmed by reading `census/round-94/c1-survivor-search.py:142` (the
  harness child gets `PYTHONPATH=ns.hook`) and `census/round-93/c1-false-row-harness.py:458-460`
  (the counter is spawned with `subprocess.run([sys.executable, "-B", counter, …])` and no
  `env=` override, so it inherits the harness's `PYTHONPATH`). Confirmed empirically: the real
  harness run produced `rc=70` ROW lines under the hook.
- **C1 stated limit "a counter that legitimately exits 70"** — no lane instrument produces exit
  70 other than the sentinel; the counter's own paths are 0/1/2.
- **C1 "the harness exit 70 or any ROW `rc=70`"** — the frozen `verdict()` implements exactly
  that (`rc == CRASH_RC or any(f" rc={CRASH_RC} match=" in l for l in rows)`), and the
  real-harness control run shows the `rc=70` ROW path reaching `errored`.
- **C2** — out of this seat's read scope for a source claim; no source row bears on C2 and I made
  no C2 falsification claim. The C2 sources are the same S357/S358 (they do not ground C2's
  exit-code discipline, which the probe's own code and `C2-FORGERY-FATAL:` lines do).

## NO-FALSIFICATION

No artifact of this seat falsifies a **numeric** claim of C1 or C2: C1's predicate re-runs to the
preregistered literal with EXIT 0. The two falsifications above are of C1's **stated limit (ii)**
wording (the unlisted `SystemExit` case) and of the corpus grounding behind it (the entry's
"an uncaught exception exits 1" premise has no source row). Both are recorded for the L1 as
narrowing amendments under Amendment 59.

## Scratch and hygiene

- Scratch `/fast/scratch/hyaku/souji-r94/R94ScoutSources/` deleted before yield (harness work
  trees and the two live page copies; receipts copied into the seat dir first).
- I briefly wrote two derived files (`stryker.html.stripped.txt`, `sysexits.html.stripped.txt`)
  into the frozen `census/round-94/srcs/` while computing the tag-stripped text; both were
  deleted immediately, and `git status --porcelain` in the lane shows no trace of them (the
  remaining `M SCORECARD.md`, `M corpus/QUALITY.md`, `?? corpus/lessons/round-94.md`,
  `?? plans/round-94.md` are the L1's and other seats' work, not mine — I never wrote them).
- No commit, no push, no git/jj state mutation, no fleet-root write, no background process left
  running, no sudo, no sysctl.
- No `git`/`jj` mutation was performed anywhere: my fixture drivers are pure `python3` and
  `curl`; the lane clone the harness makes is its own read-only `git clone --shared` into its own
  `--work` tree, and the search deletes each work tree after scoring.
