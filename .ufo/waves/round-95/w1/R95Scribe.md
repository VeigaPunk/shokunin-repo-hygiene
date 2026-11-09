# R95Scribe — round 95 lesson-block drafts (scribe seat)

Seat: R95Scribe (scribe). Lane: souji-shokunin. Round 95. Date: 2026-11-09.
Scope: draft the round-95 lesson blocks (`## Mistakes`, the `corpus/QUALITY.md` criterion, the `## Gate` block for
S360-S364) from committed evidence. This seat writes files and findings only: it did not commit, push, or touch
`census/`, `tests/fixtures/`, `tools/`, `corpus/`, `MANIFEST.json`, `.ufo/state/*` or `.scratch/*`.
Scratch used: `/fast/scratch/hyaku/souji-r95/R95Scribe/` (live source re-fetches + the sources-census validate run);
deleted before this yield. Receipts kept (text only) under `.ufo/waves/round-95/w1/R95Scribe/receipts/`.

**Verdict: NO-FALSIFICATION.** Nothing I produced falsifies a stated sentence of C1 or C2. The drafts below are
lesson/QUALITY/Gate text; they assert only what the committed receipts show. What I tried and what I saw is listed in
`## What this seat checked` (bottom).

---

## DRAFT 1 — `## Mistakes` block for `corpus/lessons/round-95.md`

Format follows `corpus/lessons/round-94.md` (`## Mistakes`, rows `**M<n> — <title>.** Class: … Evidence: …
Captured-by: … Fix: …`), each row citing one evidence path. A fix is counted only once it is shown able to fail, and
the "shown able to fail" receipt for both rows is a **r95 control receipt** (`census/round-95/controls/`), not the
after receipt — the after receipt is the passing side, the control is the failing side.

Draft text (paste under `## Mistakes`):

- **M1 — a crash sentinel's coverage was stated as the complement of one hook, and the list it named was not the list
  it missed.** Class: a coverage claim whose enumeration of what it does NOT cover is written from reading, not
  measured (r93 M5's class; r94 M3's recurrence). Evidence: the r94 sentinel replaced `sys.excepthook` alone
  (`census/round-94/c1-survivor-search.py` lines 60-75: `HOOK = f'''# souji r94 crash sentinel …` and
  `sys.excepthook = _souji_r94_crash`), and r94's limit (ii) named only `os._exit`, signals, thread exceptions and a
  counter that legitimately exits 70 as not distinguished (`census/round-94/preregistration.txt` lines 51-53; that file
  was written once, at freeze commit `4ad74b9d`, and never edited — `git diff eddb1be6..master -- census/round-94/preregistration.txt`
  adds the file only) — SystemExit and an atexit callback were neither covered nor listed, so the sentence read as the
  full complement of the mechanism. Captured-by: the r94 wave
  (R94ScoutSources FW1, R94Sentinel F1/F2), recorded as `plans/round-94.md` A1 and `corpus/lessons/round-94.md` M3; no
  lane criterion covered it before r95. Fix: r95 names the channels it covers instead of the channels it misses
  (`census/round-95/c1-survivor-search.py` lines 5-22 and the sentinel's five hook legs at lines 138-141 plus the
  `sys.monitoring` RAISE leg at 143-151) and carries one fixture per named channel
  (`census/round-95/c1-targets.json`: `h-sysexit`, `h-atexit`, `h-thread`, `h-osexit`, `h-sigkill`), with a
  precondition check that runs one child per channel and refuses to score unless every channel returns the sentinel
  exit status (`census/round-95/c1-survivor-search.py` lines 153-177, 313-332). **The fix is shown able to fail:**
  the frozen r94 rule on the same ten targets reads `h-sysexit killed=yes`, `h-atexit killed=no`, `h-thread killed=no`,
  `h-osexit killed=yes`, `h-sigkill killed=yes` — five channels scored as verdicts, not crashes
  (`census/round-95/controls/c1-control-r94-rule.txt` lines 14-18, `SEARCH-SUMMARY … errored=2 killed=5 survived=3`),
  and the counting command `grep -cE '^SEARCH h-(sysexit|atexit|thread|osexit|sigkill) .*killed=errored' census/round-95/controls/c1-control-r94-rule.txt`
  prints **0** on the control and **5** on the after receipt
  (`census/round-95/records/c1-after.txt` lines 14-18, `errored=7 killed=2 survived=1`).

- **M2 — a probe's docstring promised "every setup failure exits 2" while three setup shapes exited 1 and one never
  ended.** Class: a docstring sentence that states a mechanism's coverage in the abstract, with no per-shape fixture
  to hold it (r94 A4's class: a clause written from reading). Evidence: the frozen r94 probe's docstring
  (`census/round-94/c2-forgery-probe.py` lines 5-6: "Every setup failure exits 2 with one `C2-FORGERY-FATAL:` line on
  stderr: …") enumerates only the shapes it happened to guard, and the r94 wave falsified the sentence on a non-UTF-8
  `--tool`/`--before`, a `--work` whose parent is a regular file and a mid-run write failure
  (`plans/round-94.md` A4). Captured-by: the r94 wave (R94Critic, R94ReviewerC2 T3/T6/T7/T9, R94Sentinel F6), recorded
  as `plans/round-94.md` A4; Q171 (`corpus/QUALITY.md` line 437) already required that setup failures exit 2 with one
  named FATAL line, but named no shape list and no fixture, so it did not catch the four. Fix: r95 turns each shape
  into a refusal with its own named line and its own arm — a non-UTF-8 `--tool`/`--before`
  (`census/round-95/c2-forgery-probe.py` lines 6-8, 113-120), an uncreatable `--work` (lines 8-9, 149-152), a write
  failure after the checks and a fixture outliving `--timeout` (lines 8-10, 96-102, 121-124), plus a catch-all that
  turns any other exception into exit 2 (lines 184-189) — and the sixteen-arm counter carries one arm per shape
  (`census/round-95/c2-setup-arms.py` lines 24-28 and the arm table at 130-147: S9 non-UTF-8 tool, S10 non-UTF-8
  before, S11 file-parent `--work`, S12 hanging fixture). **The fix is shown able to fail:** on the frozen r94 probe the
  same counter reads `ARM S9 exit=1`, `ARM S10 exit=1`, `ARM S11 exit=1`, `ARM S12 exit=hung` — all four `conform=no` —
  and `ARMS-SUMMARY arms=16 conform=12`, EXIT 1 (`census/round-95/controls/c2-control-r94-probe.txt` lines 25-31); the
  counting command `grep -cE '^ARM .*want=2.*conform=yes' census/round-95/controls/c2-control-r94-probe.txt` prints
  **9** on the control and **13** on the after receipt, where all sixteen arms read `conform=yes`
  (`census/round-95/records/c2-after.txt` lines 25-31, `ARMS-SUMMARY arms=16 conform=16`, EXIT 0).

- **M3 — a fixture per named channel, but no per-channel receipt: the r95 crash claim is carried by one summary line
  and five `SEARCH` rows whose channel identity is only in the fixture's name.** Class: a count whose denominator is
  implicit in a name (the r93 M5 family — a causal clause written from reading rather than measured: a bound that is
  asserted rather than counted). Evidence: the after
  receipt names the channels in the check line (`census/round-95/records/c1-after.txt` line 3: `# crash-sentinel rc=70
  check=pass excepthook=70 sysexit=70 atexit=70 thread=70 osexit=70 declared=1 argparse=2`) and the five fixtures by
  id (lines 14-18), but nothing prints "five channels named, five fixtures, five errored" as one counted number, so a
  reader must diff two lists by hand to know the claim's denominator was met. Captured-by: this seat's read of the
  r95 receipts; no lane criterion asks a claim to print its own denominator (Q171 asks for the exit-code discipline,
  not the coverage count). Fix: the r95 counting commands, already re-derived here, make the denominator a printed
  number — `grep -oE '(excepthook|sysexit|atexit|thread|osexit)=' census/round-95/records/c1-after.txt | wc -l` prints
  **5** (channels named by the check line) and
  `grep -cE '^SEARCH h-(sysexit|atexit|thread|osexit|sigkill) .*killed=errored' census/round-95/records/c1-after.txt`
  prints **5** (fixtures that reached them); the same two commands on the control print **0** and **0**
  (`census/round-95/controls/c1-control-r94-rule.txt`), so the count can fail. Rounded into the Q172 criterion below
  rather than left as prose.

---

## DRAFT 2 — `corpus/QUALITY.md` criterion (next free Q number)

The last Q number in `corpus/QUALITY.md` is **Q171** (line 437, `## Round 94 criteria`; the file's `## Round 95
criteria` section does not exist yet). The next free number is therefore **Q172**, to be filed under a new
`## Round 95 criteria` heading with the same five-column table
(`| id | criterion | applies-to | test | lesson |`) as the existing sections. `corpus/QUALITY.md` is frozen for this
seat — the L1 files this row.

Draft row (one line; the `|` characters inside the prose are escaped as `\|`):

| id | criterion | applies-to | test | lesson |
|---|---|---|---|---|
| Q172 | A claim that a mechanism covers a set of channels NAMES the channels it covers, carries one fixture per named channel, and PRINTS ITS OWN DENOMINATOR: the number of channels named equals the number of fixtures that reach them, and both numbers are counted by a command, not read off two lists by hand. A limits or docstring sentence that enumerates what the mechanism does NOT cover is not the complement of what it misses — it is one more partial enumeration, and the channels it forgot to list read as covered. The r94 sentinel replaced `sys.excepthook` alone (`census/round-94/c1-survivor-search.py` lines 60-75) and its limit (ii) named only `os._exit`, signals, thread exceptions and a counter that legitimately exits 70 (`census/round-94/preregistration.txt` lines 51-53), so SystemExit and an atexit callback were neither covered nor listed; the r94 probe's docstring promised "every setup failure exits 2" (`census/round-94/c2-forgery-probe.py` lines 5-6) while a non-UTF-8 input, a file-parent `--work` and a hanging fixture did not (`plans/round-94.md` A4). The same rule holds for a refusal claim: each named setup shape carries its own arm and its own expected exit, and the count of refusing arms is printed. | every instrument whose claim is a coverage claim over a set of channels: crash sentinels, setup-refusal probes, and any docstring or limits sentence that enumerates failure shapes ("every setup failure exits 2", "signals are not distinguished") | the count is printed, on both sides of the control, and the two sides differ. C1: `grep -oE '(excepthook\|sysexit\|atexit\|thread\|osexit)=' census/round-95/records/c1-after.txt \| wc -l` prints 5 (channels named) and `grep -cE '^SEARCH h-(sysexit\|atexit\|thread\|osexit\|sigkill) .*killed=errored' census/round-95/records/c1-after.txt` prints 5 (fixtures that reached them); on the frozen r94 rule (`census/round-95/controls/c1-control-r94-rule.txt`) the same two commands print 0 and 0, and its `h-sysexit killed=yes` / `h-atexit killed=no` rows show the channels were scored as verdicts. C2: `grep -cE '^ARM .*want=2.*conform=yes' census/round-95/records/c2-after.txt` prints 13 of 13 refusing arms; on the frozen r94 probe (`census/round-95/controls/c2-control-r94-probe.txt`) it prints 9, with `ARM S9 exit=1`, `S10 exit=1`, `S11 exit=1`, `S12 exit=hung` all `conform=no`. | `corpus/lessons/round-95.md` M1, M2, M3 |

---

## DRAFT 3 — `## Gate` block for S360-S364

Format follows `corpus/lessons/round-94.md` `## Gate` (a table with columns row / URL / access date / located quote /
locator / decision). Every locator below was re-derived by this seat, not copied: the capture sha256 was recomputed
from the committed bytes, the quote's word count and occurrence count were recomputed from the committed tag-stripped
text, and each page was re-fetched live on 2026-11-09 and compared byte-for-byte with the committed capture. The
reject slot is left for the scout seat (`R95ScoutSources`); no row is claimed as rejected here.

Registry rows added this round (opened 2026-11-09 by the L1; captures committed in P1 `d79bc3fe` under
`census/round-95/srcs/`, tag-stripped text beside each):

| row | URL | access date | located quote (<=25 words) | locator | decision |
|---|---|---|---|---|---|
| S360 | https://docs.python.org/3/library/sys.monitoring.html | 2026-11-09 | "An exception is raised, except those that cause a STOP_ITERATION event." (11 words) | § Events, the `sys.monitoring.events.RAISE` entry, in the whitespace-normalized tag-stripped text of the capture: "An exception is raised, except those that cause a STOP_ITERATION event." (11 words, occurrence count 1) | ADMIT, `mined`, cited by `corpus/knowledge/crash-channels-beyond-excepthook.md` |
| S361 | https://docs.python.org/3/library/threading.html#threading.excepthook | 2026-11-09 | "Handle uncaught exception raised by Thread.run() ." (7 words) | § Functions, the `threading.excepthook` entry, in the whitespace-normalized tag-stripped text of the capture: "Handle uncaught exception raised by Thread.run() ." (7 words, occurrence count 1) | ADMIT, `mined`, same entry |
| S362 | https://docs.python.org/3/library/os.html#os._exit | 2026-11-09 | "Exit the process with status n , without calling cleanup handlers, flushing stdio buffers, etc." (15 words) | § Process Management, the `os._exit` entry, in the whitespace-normalized tag-stripped text of the capture: "Exit the process with status n , without calling cleanup handlers, flushing stdio buffers, etc." (15 words, occurrence count 1) | ADMIT, `mined`, same entry |
| S363 | https://docs.python.org/3/library/subprocess.html#subprocess.Popen.returncode | 2026-11-09 | "A negative value -N indicates that the child was terminated by signal N (POSIX only)." (15 words) | § CompletedProcess.returncode and § Popen.returncode, in the whitespace-normalized tag-stripped text of the capture: "A negative value -N indicates that the child was terminated by signal N (POSIX only)." (15 words, occurrence count 2, once per entry) | ADMIT, `mined`, same entry |
| S364 | https://docs.python.org/3/library/atexit.html | 2026-11-09 | "If an exception is raised during execution of an exit handler, a traceback is printed (unless SystemExit is raised) and the exception information is saved." (25 words) | § atexit, the module introduction before the `atexit.register` entry, in the whitespace-normalized tag-stripped text of the capture: "If an exception is raised during execution of an exit handler, a traceback is printed (unless SystemExit is raised) and the exception information is saved." (25 words, occurrence count 1) | ADMIT, `mined`, same entry |
| — | (reject slot — for the scout seat `R95ScoutSources`) | 2026-11-09 | — | — | REJECT (not filed): to be filled by the scout's own candidate search; this seat filed no rejection and claims none |

Recheck cells: `365d` for all five (ISO/`NNd` schema). Status/recheck/used-by changes to existing rows: none.

Re-open by this seat (non-author) on 2026-11-09, all five pages HTTP 200:

| row | live bytes | live sha256 | committed capture sha256 | identical | quote words / occurrences (recomputed) |
|---|---|---|---|---|---|
| S360 | 74653 | `cd85fa73159a682f403607b7e539fd005546a9ac90edc99e2ad51743dfc52b98` | `cd85fa73159a682f403607b7e539fd005546a9ac90edc99e2ad51743dfc52b98` | yes | 11 / 1 |
| S361 | 181498 | `d6f8ca655ef4dff896685b8cf761c8d4b662233673bbd2d5defcb37709fb0361` | `d6f8ca655ef4dff896685b8cf761c8d4b662233673bbd2d5defcb37709fb0361` | yes | 7 / 1 |
| S362 | 791364 | `078e69b12c66fd922353577d209e5a7c2f82a70b1b65eafe64a7910e635427fe` | `078e69b12c66fd922353577d209e5a7c2f82a70b1b65eafe64a7910e635427fe` | yes | 15 / 1 |
| S363 | 208648 | `7f5772d756be5dd6b8b440ea12999afaf12119e7cfd9bb3db16287e49fcc3cad` | `7f5772d756be5dd6b8b440ea12999afaf12119e7cfd9bb3db16287e49fcc3cad` | yes | 15 / 2 |
| S364 | 29643 | `765f26c2d69949d6bf3b0e4198cabef3b23f83ad8188e5c1db3a502785c44bf8` | `765f26c2d69949d6bf3b0e4198cabef3b23f83ad8188e5c1db3a502785c44bf8` | yes | 25 / 1 |

Receipt: `.ufo/waves/round-95/w1/R95Scribe/receipts/s360-s364-recheck.txt` (capture hashes, byte counts, quote word
counts, occurrence counts, live-vs-capture comparison, and the recomputed-vs-row sha256 check for each of the five
`corpus/SOURCES.md` rows). Note for the L1: the S360 capture file is `census/round-95/srcs/monitoring.html` but the
URL that reproduces it is `https://docs.python.org/3/library/sys.monitoring.html`; the bare
`https://docs.python.org/3/library/monitoring.html` is a 404 page (9548 bytes, "Page not found"), which is why the
live re-fetch of that spelling does not match the capture. The SOURCES row already carries the correct `sys.` URL.

Registry: 281 rows at the lane base (`git show 93c3ef13:corpus/SOURCES.md | grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'`
→ 281) → **286** rows now (5 added: S360-S364). Census
`scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` → `souji ok`, EXIT 0, 92 lines of
output (91 `W04` duplicate-URL warnings, all pre-existing across scopes, plus the `ok` line); receipt
`.ufo/waves/round-95/w1/R95Scribe/receipts/sources-census-validate-r95scribe.txt` (sha256
`8e2d33a58aae1b95299f5cabe7d2d65975495afb6da847657850651070184d54`). The lane's own before-receipt is
`census/round-95/records/sources-census-before.txt` (91 lines, `souji ok`, EXIT 0); the lane's after-receipt for the
round is not yet committed and is the L1's to run.

---

## What this seat checked (evidence, not inference)

Committed bytes read (read-only; the lane was not modified):

- `census/round-95/preregistration.txt` (the contract), `census/round-95/controls/` (4 receipts + the pre-freeze
  note), `census/round-95/records/c1-after.txt`, `census/round-95/records/c2-after.txt`,
  `census/round-95/c1-survivor-search.py`, `census/round-95/c2-forgery-probe.py`, `census/round-95/c2-setup-arms.py`,
  `census/round-95/c1-targets.json`.
- `census/round-94/c1-survivor-search.py` (lines 60-75), `census/round-94/c2-forgery-probe.py` (lines 4-10),
  `census/round-94/preregistration.txt` (lines 50-54).
- `corpus/lessons/round-94.md` (`## Mistakes` row format, `## Gate` table format), `corpus/lessons/round-94-verifier-spotcheck.md`
  (§5 routed items), `corpus/QUALITY.md` (last row Q171 at line 437), `corpus/SOURCES.md` (rows S360-S364, lines 299-303),
  `corpus/knowledge/crash-channels-beyond-excepthook.md`, `plans/round-94.md` (A1, A4), `plans/round-95.md`.

Instrument pins re-derived (all match the prereg's pins and the receipts' own header lines):

| instrument | sha256 |
|---|---|
| `census/round-95/c1-survivor-search.py` | `6066508fa4b113f5e7d9d269e4e3516c104d0e5cc9236cc5e4c6aa8a0d649740` |
| `census/round-95/c1-targets.json` | `fb40bf4e046c074845ec00c587173b49c7a095a6236cb188880a2183d7ba5b8e` |
| `census/round-95/c1-control-r94-rule.py` | `fb90b3873232900def423a33aa9945dabec9c6a9c453e59f94a814d3b887a26f` |
| `census/round-95/c1-forgery-controls.py` | `753083b70ca9075c15d6bcf21be717e46046f78637def9395f27a4f7f25ef0b2` |
| `census/round-95/c2-forgery-probe.py` | `bd83e120a71fe01073f63f5bdbafedd468bd772b9fc46fc12b893abc479fdc73` |
| `census/round-95/c2-setup-arms.py` | `dd2da59b7c9f5ecbc043ff826a13fe848c5f99ef31b775aa4fee274353b2569d` |
| `census/round-95/c2-forgery-controls.py` | `337fae896bcacfe66fb670c0f63296273c1ae02eedf46300d326acb6e0d7a7a8` |
| `census/round-87/c1-pointer-counter.py` (unchanged) | `fd0a8e244a5e0afe58f9e8bfa85d314722b77a1bcbe6837298683f74a755220b` |
| `census/round-93/c1-false-row-harness.py` (unchanged) | `1868a570b9100559637ab454e6f7737bfdc881339cf8045d75cc22b3060a84a4` |
| `census/round-93/c1-false-rows.tsv` (unchanged) | `d6439f65a632cf83fb9d47c78bd0d32d1f9104d2f6443bdfd770e1c1c5e1a88e` |

Receipt numbers re-read from the committed bytes (this seat did not re-run the predicates; it did not re-run any
harness, so it neither confirms nor denies the receipts' runs beyond reading them):

- C1 after (`census/round-95/records/c1-after.txt`): check line names five channels
  (`excepthook=70 sysexit=70 atexit=70 thread=70 osexit=70 declared=1 argparse=2`), the five channel fixtures all read
  `killed=errored` (lines 14-18), `SEARCH-SUMMARY generated=10 … scored=10 errored=7 killed=2 survived=1`, EXIT 0.
- C1 control (`census/round-95/controls/c1-control-r94-rule.txt`): `h-sysexit killed=yes`, `h-atexit killed=no`,
  `h-thread killed=no`, `h-osexit killed=yes`, `h-sigkill killed=yes`; `errored=2 killed=5 survived=3`, EXIT 0.
- C1 forgeries (`census/round-95/controls/c1-forgery-controls.txt`): FA `errored=9 killed=0 survived=1`, FB
  `errored=1 killed=6 survived=3`, FC `errored=6 killed=3 survived=1`; `C1-FORGERY-SUMMARY forgeries=3 refused=3`.
- C2 after (`census/round-95/records/c2-after.txt`): all sixteen arms `conform=yes`, including S9-S12 at exit 2;
  `ARMS-SUMMARY arms=16 conform=16`, EXIT 0.
- C2 control (`census/round-95/controls/c2-control-r94-probe.txt`): S9/S10/S11 exit 1, S12 exit `hung`, all four
  `conform=no`; `ARMS-SUMMARY arms=16 conform=12`, EXIT 1.
- C2 forgeries (`census/round-95/controls/c2-forgery-controls.txt`): GA conform 15, GB 14, GC 15;
  `C2-FORGERY-CTL-SUMMARY forgeries=3 refused=3`.
- Mechanism read (not re-run): the r95 after receipt's per-mutant harness outputs
  (`census/round-95/records/c1-after-harness/m0000..m0009.harness.out`) carry crash rows on seven of the ten files —
  five files with 66 `rc=70` rows each (m0003, m0005, m0006, m0007, m0008), one with a single `rc=70` row (m0004) and
  one with 66 `rc=-9` rows (m0009) — so the signal leg is bound by a row, not only by the summary line. The
  mutant↔file mapping is not stated in the receipts, so this seat claims the counts only, not which `m000N` is which
  named fixture.

Commands this seat ran (all read-only or into its own scratch):

1. `sha256sum` on the ten instruments above and on the five source captures (recomputed vs the SOURCES rows).
2. `grep`/`wc` counting commands on the committed receipts, as quoted inline in each draft row (each was run and its
   printed number is the number quoted).
3. `curl -sSL` re-fetch of the five S360-S364 URLs, then `cmp`/`sha256sum` against the committed captures.
4. `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` → EXIT 0 (output into scratch, then
   copied into the seat's receipts dir).

No tool was installed or upgraded for this seat (nothing in the task needed one). `curl 8.23.0` was already present and
was the only external tool used.

## NO-FALSIFICATION (Amendment 59)

Nothing this seat produced falsifies a stated sentence of C1 or C2, and no FALSIFIES-WORDING / FALSIFIES-NUMBER
section is owed. What I tried: re-read the prereg and both controls and both after receipts; re-derived every
instrument pin and compared it to the prereg's pins and to the receipts' own headers; re-derived the five source
captures' hashes and quote occurrence counts and re-fetched all five pages live (byte-identical); ran the counting
commands that the M1/M2/M3 fixes rely on, against both the control and the after receipt, so that each fix is shown
able to fail. The only observation that touches a claim's wording is M3 above, and it is about the *presentation* of
the receipt (the denominator is not printed as one number), not about the claim's stated predicate or number — the
predicate, the `errored=7 killed=2 survived=1` summary and the five `killed=errored` rows are all present as worded.
The L1 may therefore file the M1/M2/M3 rows and the Q172 criterion as lessons without an amendment; if the L1 judges
M3 to be a wording matter, it should be recorded as a narrowing in `plans/round-95.md`, not repaired silently.

## Out of scope for this seat (not touched, not claimed)

- `corpus/QUALITY.md`, `corpus/lessons/round-95.md`, `corpus/SOURCES.md`, `plans/round-95.md` — the L1's to file; the
  drafts above are text for that filing.
- The reject slot in the Gate block — the scout seat's (`R95ScoutSources`).
- The wave's other findings, the no-harm census and any falsification the attack seats file — not this seat's material.
- Git/jj state, commits, pushes, MANIFEST.json, `.ufo/state/*`, `.scratch/*`, `census/`, `tests/fixtures/`, `tools/`.
