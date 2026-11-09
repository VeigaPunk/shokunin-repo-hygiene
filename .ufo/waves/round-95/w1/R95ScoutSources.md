# R95ScoutSources — souji r95: S360–S364 re-opened live, one candidate judged

Seat: R95ScoutSources (scout, leaf member — no dispatch). Lane: souji-shokunin (`/home/vgpnk/Projects/shokunin/souji-shokunin`).
Round 95, wave 1. Read-only over the lane tree; every write is under
`.ufo/waves/round-95/w1/R95ScoutSources/` (this report + receipts) and the scratch
`/fast/scratch/hyaku/souji-r95/R95ScoutSources/` (deleted at end of run).
No tool was installed (none needed). No git/jj state touched; no lane file edited.

## 0. Verdict summary

- **All five rows re-open live and reproduce exactly**: live bytes == committed capture
  bytes (sha256 + size identical to the row's), the quoted sentence occurs in the
  whitespace-normalized tag-stripped text with the row's word count and occurrence
  count, and the row's locator names a real structure on the page — with **one
  exception: S361's locator `§ Functions` names no heading on the captured page**
  (the enclosing heading is `Reference`). Routed as **DEFECT-1** below.
- **NO-FALSIFICATION** of C1 or C2 stated wording. The two routed items are corpus-row
  wording defects (S361 anchor cell; undisclosed observation in the S361 grounds cell),
  not claim falsifications: neither claim sentence depends on an anchor cell.
- **Candidate verdict: REJECT for this round (queue as a lead), flip condition stated** —
  `faulthandler`, § Candidate below.

## 1. Method (recovered, byte-exact)

The committed `.txt` beside each capture is reproduced **byte-for-byte** by:

```
html.parser.HTMLParser(convert_charrefs=True)
  skip <script>/<style> content
  collect handle_data parts
  text = re.sub(r"\s+", " ", " ".join(parts))     # join with ONE space, do NOT strip
```

Joining with a single space and **not** stripping reproduces all five committed `.txt`
files exactly (13897 / 51756 / 187481 / 54974 / 5587 bytes). The naive
`"".join(parts)` variant is 200–3700 bytes shorter and does not reproduce them, so the
rows' occurrence counts were computed with the join-with-space variant — this is the
method the rows state ("whitespace-normalized tag-stripped text").
Reproducer: `.ufo/waves/round-95/w1/R95ScoutSources/verify_rows.py`
(+ `verify-rows.json`, `verify-rows.txt`).

## 2. Per-row verification table

Live fetch 2026-11-09 (curl -sSL and urllib, both HTTP 200). `live==capture` = the
fetched bytes are byte-identical to `census/round-95/srcs/<stem>.html`.

| row | URL | live bytes | live sha256 | == row sha256/bytes | == committed capture | quote | words (row) | count (row) | locator resolves on the capture |
|---|---|---|---|---|---|---|---|---|---|
| S360 | https://docs.python.org/3/library/sys.monitoring.html | 74653 | `cd85fa73159a682f403607b7e539fd005546a9ac90edc99e2ad51743dfc52b98` | yes | **identical** | "An exception is raised, except those that cause a STOP_ITERATION event." | 11 (11) ✓ | 1 (1) ✓ | **yes** — `Events ¶` is a heading; quote at text offset 5178, inside the Events block (Events at 3204, next heading `Local events ¶` at 5995) |
| S361 | https://docs.python.org/3/library/threading.html#threading.excepthook | 181498 | `d6f8ca655ef4dff896685b8cf761c8d4b662233673bbd2d5defcb37709fb0361` | yes | **identical** | "Handle uncaught exception raised by Thread.run() ." | 7 (7) ✓ | 1 (1) ✓ | **NO** — the capture has no `Functions` heading (0 hits for a `Functions` heading line; the enclosing heading is `Reference ¶`). The page's prose says "This module defines the following functions:" — prose, not a heading. → **DEFECT-1** |
| S362 | https://docs.python.org/3/library/os.html#os._exit | 791364 | `078e69b12c66fd922353577d209e5a7c2f82a70b1b65eafe64a7910e635427fe` | yes | **identical** | "Exit the process with status n , without calling cleanup handlers, flushing stdio buffers, etc." | 15 (15) ✓ | 1 (1) ✓ | **yes** — `Process Management ¶` is a heading and the `_exit` entry lies inside that block (PM at 136676, `_exit` at 141411, next heading at 174979) |
| S363 | https://docs.python.org/3/library/subprocess.html#subprocess.Popen.returncode | 208648 | `7f5772d756be5dd6b8b440ea12999afaf12119e7cfd9bb3db16287e49fcc3cad` | yes | **identical** | "A negative value -N indicates that the child was terminated by signal N (POSIX only)." | 15 (15) ✓ | 2 (2) ✓ — once per entry (offsets 6041 under `class subprocess. CompletedProcess` → `returncode`; 34969 under `Popen. returncode`) | **yes, as an entry** — `Popen. returncode ¶` is a literal line and the attribute is named; lane precedent: S286 (same URL) uses the identical anchor string `CompletedProcess.returncode` |
| S364 | https://docs.python.org/3/library/atexit.html | 29643 | `765f26c2d69949d6bf3b0e4198cabef3b23f83ad8188e5c1db3a502785c44bf8` | yes | **identical** | "If an exception is raised during execution of an exit handler, a traceback is printed (unless SystemExit is raised) and the exception information is saved." | 25 (25) ✓ | 1 (1) ✓ | **yes** — `atexit — Exit handlers ¶` heading; quote at 1132, `atexit. register` at 2730, so "the module introduction before the `atexit.register` entry" holds |

Row-cell facts (11 columns, no `|` inside a cell) hold for all five: kinds `docs`,
tiers `A`, statuses `mined`, opened `2026-11-09`, recheck `365d`, used-by
`corpus/knowledge/crash-channels-beyond-excepthook.md` (exists). The lane's own census
commands over the committed `corpus/SOURCES.md`: rows **286**, malformed rows **0**,
duplicate ids **none**, `mined` rows with missing used-by paths **none**.

**Census note for the L1's after-census (W04, warning class, not a finding):** my
replicate of the fleet `sources-census.sh validate` rules over the committed registry
shows exactly two new W04 lines touching the new rows — `S362 duplicate url
docs.python.org/3/library/os.html across scopes` (with S288/S289) and `S363 duplicate url
docs.python.org/3/library/subprocess.html across scopes` (with S261/S286/S287). The
lane's r40 lesson records duplicate-URL-across-scopes as a warning, not a finding, and
both new rows have a distinct scope, so neither is E04. The pre-round census record
`census/round-95/records/sources-census-before.txt` lists no S36x rows (it stops at
S351), so these two lines appear for the first time in the after-census.
Reproducer: `census-replicate.txt`.

## 3. Do the rows claim more than the quotes say? (grounds-cell audit)

| row | grounds cell claim | verdict |
|---|---|---|
| S360 | "a RAISE callback sees the SystemExit `sys.excepthook` never sees (S359) and **the frame that first raised it**; the per-frame re-firing it relies on is **observed on CPython 3.14.8, not stated here**" | **Honest on the re-firing** (disclosed as observation; I re-observed it, see §4). **Two nits**: (a) the scope cell's "SystemExit included" is an *inference* from the quoted sentence — the captured page contains **zero** occurrences of "SystemExit"; the grounds cell routes the excepthook half to S359, so the composition is stated, but the page never names SystemExit. (b) "the frame that first raised it" is documented on the page only in the *Callback function arguments* section (`code` = "the code object where the event was triggered"), which is outside the row's declared scope ("the RAISE event entry only"). → routed as **OBS-1** (scope/wording, not falsification) |
| S361 | "a crash in a thread reaches this hook, **not the r94 excepthook**, and **the main thread keeps its exit status**" | "not the r94 excepthook" is supported by the same entry ("If this function raises an exception, sys.excepthook() is called to handle it"; "See also sys.excepthook() handles uncaught exceptions"). **"the main thread keeps its exit status" is an observation the page does not state** (captured page: 0 hits for "exit status") and the grounds cell does **not** disclose it as observed, unlike S360 and S364 which do. → **DEFECT-2** (undisclosed observation in a grounds cell) |
| S362 | "no hook or atexit callback runs … also explains why `h-osexit` loses the counter's buffered stdout" | Supported by the quote's own wording ("without calling cleanup handlers, flushing stdio buffers, etc."). The page never names `atexit` (0 hits) — standard reading of "cleanup handlers"; acceptable. **OK** |
| S363 | "the harness prints the counter's `p.returncode`, so a counter killed by SIGKILL shows `rc=-9`, which the r94 rule read as an ordinary mismatch" | Supported: quote states the negative-value meaning; the harness prints `rc={p.returncode}` (`census/round-93/c1-false-row-harness.py`). The "occurrence count 2, once per entry" is confirmed at the two attribute entries. **OK** |
| S364 | "grounds why `h-atexit` survives the r94 rule (a printed traceback, not a status change) and, with the introduction's reverse-order sentence, why the sentinel's handler registered first runs last; **the page does not name `sys.unraisablehook`**, the CPython 3.14.8 route the sentinel hooks is **observed**" | Fully honest and verified: (a) "unraisable" occurs **0** times in the capture — the negative statement is true; (b) the reverse-order sentence is in the introduction ("At exit, all registered exit handlers are called in the reverse order in which they were registered"); (c) the atexit→unraisablehook route is real on 3.14.8 — I observed `sys.unraisablehook` called with `err_msg='Exception ignored in atexit callback …'`; (d) on 3.14.8 an exception in an atexit callback does **not** change the exit status (rc stayed 0 with no explicit exit; stayed 3 with `sys.exit(3)`) — matching "a printed traceback, not a status change". **OK** |

## 4. Host observations (CPython 3.14.8) behind the rows' disclosed observations

Reproducers in the seat dir (`probe_host_behaviour.py`, `probe_atexit_unraisable.py`,
`host-behaviour.txt`, `atexit-unraisable.txt`):

- `sys.monitoring` RAISE fires **per frame** for one SystemExit: frames
  `helper:SystemExit` then `<module>:SystemExit` (2 events) — exactly the per-frame
  re-firing S360's grounds cell discloses as observed-on-3.14.8.
- `threading.excepthook` received the thread's `ZeroDivisionError`; the main thread
  continued and the script exited 0 — the substance of S361's "the main thread keeps its
  exit status" (undisclosed in the row: DEFECT-2).
- An exception in an `atexit` callback reached `sys.unraisablehook`
  (`err_msg='Exception ignored in atexit callback …'`) and left the exit status
  unchanged — the route S364's grounds cell discloses, and the channel the C1 claim's
  `h-atexit` fixture rides.
- A `SystemExit(7)` raised in an `atexit` callback was likewise reported as
  "Exception ignored in atexit callback" and left rc unchanged on 3.14.8. The atexit
  page's *next* sentence ("the last exception to be raised is re-raised") is therefore
  **narrower in practice than the prose** on this host — a limit to state if a future
  row leans on it.

## 5. Candidate source judged (task 3)

Screened four candidate sources for "detecting abnormal Python exits", all fetched live
into scratch (not into `corpus/`).

### Candidate: `faulthandler` — **VERDICT: REJECT for this round; queue as a lead**

- URL: https://docs.python.org/3/library/faulthandler.html — HTTP 200, 47437 bytes,
  sha256 `f50bb09a3b0ca29e457ac411f08e52b74e533f8bd76ee50824ec1425d9f925bb`,
  accessed 2026-11-09 (capture kept in the seat dir as `candidate-faulthandler.html`).
- Located quote (19 words, occurrence count 1, in the module introduction before
  `§ Dumping the traceback`):
  > "Call faulthandler.enable() to install fault handlers for the SIGSEGV , SIGFPE , SIGABRT , SIGBUS , and SIGILL signals."
- Ground it could serve: the C1 claim's STATED LIMITS (iii) list "signals other than
  SIGKILL" and "C-level crashes" as uncovered; this page is the only official
  statement of which fatal signals CPython's own fault handler covers. Host re-run on
  3.14.8: `faulthandler.enable()` then SIGABRT → "Fatal Python error: Aborted" plus the
  C stack, shell rc 134, and the **parent observed returncode -6** — i.e. it dumps a
  traceback but does **not** change the exit status.

**Reasons for rejection in this round**
1. **Out of the frozen claims' ground.** No C1/C2 sentence needs it; SOURCES-CONTRACT-v1
   rule 1 admits a row only in the round that writes the claim it grounds ("a row is a
   claim"), and rule 4 says expansion is knowledge, not rows. Adding it now would be an
   unmined row (`used-by` would be "—", status `queued`) with no knowledge entry behind it.
2. **It cannot ground a verdict.** The page says nothing about exit status (0 hits for
   "exit status"/"exit code"), so it cannot support a claim about how a crash is *scored*
   — only about a diagnostic dump.
3. **It does not cover the r95 channel it appears to.** The page's signal list omits
   SIGKILL, so it cannot close the `h-sigkill` leg, and it is a fault-trap mechanism, not
   the sentinel's exit-70 mechanism.
4. **PROVINCE check**: admissible in principle — it is the same class of Python-docs
   evidence as S357–S364 for souji's own census instrument, and the crash-channel
   knowledge entry is already in `corpus/knowledge/` — but QUALITY Q1 (name the version
   verified on and the host version re-run on) can only be satisfied by a knowledge
   entry with its own Gate, which this round does not need.

**Flip condition** (admit as a tier-A `docs` row plus a knowledge entry): a future round
whose claim must **distinguish a counter that died on a fatal signal** (SIGSEGV /
SIGFPE / SIGABRT / SIGBUS / SIGILL family) from one that produced no verdict — e.g. a
survivor search that must classify a C-level crash — should then admit it with the
honest scope: *the fault handler dumps a traceback; it does not change the exit status
(observed 3.14.8: parent saw returncode -6 for SIGABRT), and the page's signal list
does not include SIGKILL.*

### Screened and rejected alongside
- **PEP 669** (https://peps.python.org/pep-0669/, 59204 bytes, sha256
  `10f8475934c39842c966f4505d338f1a9844215bc8ac842ab2809b108b2421dc`): its RAISE
  sentence is the **same sentence** S360 quotes (occurrence count 1) — but the PEP is the
  design record; the shipped `sys.monitoring` documentation is the authority for
  behaviour. **REJECT**: redundant scope with S360 at lower authority. Flip: if the
  shipped `sys.monitoring` page were withdrawn.
- **PEP 578** (https://peps.python.org/pep-0578/, 58142 bytes, sha256
  `b8e24ccee72a4a0218687ece7ae8a2e526ead2021b887410c6e180273cbca73a`): audit hooks. The
  page names no exit, crash, excepthook, unraisablehook, os._exit or atexit (0 hits
  each). **REJECT**: out of scope for abnormal-exit detection.
- **`sys.audit`** (https://docs.python.org/3/library/sys.html): the captured page has no
  `Audit events` section (0 hits) and audit events do not report process death; the URL
  also collides with S359's URL/scope (W04 class). **REJECT**.

## 6. NO-FALSIFICATION

**NO-FALSIFICATION** — nothing produced in this wave falsifies a stated sentence of C1
or C2. What I tried and what came out:

- Re-fetched all five URLs live: bytes and sha256 identical to the rows and to the
  committed captures → no page drift to diff.
- Reproduced the committed tag-stripped texts byte-exactly and re-counted every quoted
  sentence: word counts and occurrence counts match all five rows.
- Re-checked each locator against the captured page's heading set, including by running
  the lane's own predicate (`tests/fixtures/r23-locator-heading.py::headings`, the Q54
  heading-set rule) over the captures: "Events", "Process Management", "atexit" resolve;
  **"Functions" does not** (S361) and "CompletedProcess.returncode" resolves only as an
  *entry* (S363, same as lane precedent S286). The r23 fixture itself reports
  `UNSCOPED` for `corpus/knowledge/crash-channels-beyond-excepthook.md` (the entry names
  no `snapshot:`), so Q54 does not bind this entry — the S361 defect is a SOURCES
  anchor-cell defect, not a Q54 violation.
- Re-observed every behaviour the grounds cells attribute to CPython 3.14.8 (RAISE
  per-frame re-firing; atexit→`sys.unraisablehook`; thread exception → `threading.excepthook`
  with the main thread continuing) → all observations hold on this host.
- Replicated the registry census rules over the committed table → 0 malformed rows, no
  duplicate ids, no missing used-by paths, and only the two expected W04 warning lines
  (S362, S363).

### Routed items for the L1 (corpus wording, not claim wording)

- **DEFECT-1 (S361 anchor cell).** `corpus/SOURCES.md` row S361's anchor reads
  `§ Functions, the `threading.excepthook` entry`; the captured page has **no**
  `Functions` heading — the enclosing heading is `Reference ¶` (and the page's own
  sentence is the prose "This module defines the following functions:"). The same string
  is repeated in `corpus/lessons/round-95.md`'s Gate table. The quote, its word count and
  its occurrence count are all correct, and the claim wording does not depend on the
  anchor; only the locator is wrong. Per SOURCES-CONTRACT-v1 rule 2 (append-only; a
  correction is a new row whose `teaches` opens `supersedes S0NN —`), the fix is a
  superseding row with the anchor corrected to `§ Reference, the `threading.excepthook`
  entry`, not an in-place edit of S361.
- **DEFECT-2 (S361 grounds cell).** "the main thread keeps its exit status" is an
  observation (true on 3.14.8) that the page does not state and the cell does not
  disclose as observed — inconsistent with S360's and S364's explicit "observed on
  CPython 3.14.8, not stated here" wording.
- **OBS-1 (S360 scope/grounds wording).** "SystemExit included" in the scope cell is an
  inference (the captured page never names SystemExit; the grounds cell leans on S359
  for the excepthook half), and "the frame that first raised it" is documented on the
  page only in the `Callback function arguments` section, outside the row's declared
  "RAISE event entry only" scope.
- **CENSUS-NOTE.** The after-census will show two new W04 lines (S362 os.html, S363
  subprocess.html) — warning class, expected, distinct scopes.

## 7. Files written by this seat

- `.ufo/waves/round-95/w1/R95ScoutSources.md` — this report.
- `.ufo/waves/round-95/w1/R95ScoutSources/`: `verify_rows.py`, `verify-rows.json`,
  `verify-rows.txt`, `verify_locators.py`, `verify-locators.json`, `verify-locators.txt`,
  `census_replicate.py`, `census-replicate.txt`, `probe_host_behaviour.py`,
  `probe_atexit_unraisable.py`, `host-behaviour.txt`, `atexit-unraisable.txt`,
  `locate_candidate_quote.py`, `candidate-quote.txt`, `candidate-faulthandler.html`.
- Scratch `/fast/scratch/hyaku/souji-r95/R95ScoutSources/` **deleted** at end of run
  (no clone, no work tree, nothing above 1 MB retained).
