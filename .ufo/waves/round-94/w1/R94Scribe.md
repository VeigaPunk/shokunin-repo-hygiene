# R94Scribe — souji round 94 lesson draft (leaf seat, no subagents)

Lane: `souji-shokunin`, base `eddb1be6c34c2e0bef8c1e8ae6ea2f4b381c5536` (r93 closed admitted; its non-author
spot-check is `corpus/lessons/round-93-verifier-spotcheck.md`). Instruments P1 `24cd67b0`, controls P2 `39d4163a`,
freeze F `4ad74b9d`, after receipts A `b065b7f0`.
Seat dir: `.ufo/waves/round-94/w1/R94Scribe/` (receipts below). Scratch `/fast/scratch/hyaku/souji-r94/R94Scribe/`
was created, used and removed (verified). No commit, no push, no git/jj mutation anywhere (read-only
`git log`/`git show`/`git diff`/`git status` only). Tools installed: none.
Read-only lane access; the frozen instruments (`census/`, `corpus/`, `tests/fixtures/`, `tools/`) were not modified.

**Seat scope note.** `corpus/QUALITY.md` and `corpus/lessons/round-94.md` already carry an uncommitted L1 draft in
the working tree (`git status`: ` M corpus/QUALITY.md`, `?? corpus/lessons/round-94.md`). Everything below is
DRAFT TEXT for the L1 to integrate; I wrote only under my seat dir and this file.

---

## NO-FALSIFICATION (of C1 or C2 stated wording)

I tried to falsify both claims' stated wording and could not. What I did:

- **C1 predicate, re-run by me** on the two crash ids only (fresh `--work`, `--jobs 5`):
  `python3 -B census/round-94/c1-survivor-search.py --counter census/round-87/c1-pointer-counter.py --harness
  census/round-93/c1-false-row-harness.py --population census/round-93/c1-false-rows.tsv --lane . --fleet-root
  /home/vgpnk/Projects/shokunin --work <empty> --jobs 5 --ids <["h-crash-late","h-crash-index"]>` →
  `# crash-sentinel rc=70 check=pass`, `SEARCH h-crash-late line=574 killed=errored rc=1`,
  `SEARCH h-crash-index line=494 killed=errored rc=1`, `SEARCH-SUMMARY generated=2 ambiguous=0 uncompiled=0 hung=0
  scored=2 errored=2 killed=0 survived=0`, EXIT 0.
  Receipt: `.ufo/waves/round-94/w1/R94Scribe/receipts/c1-r94-crashids.txt`.
- **C1 do-nothing control, re-run by me**: `python3 -B census/round-94/c1-control-r93-rule.py … --ids
  <["h-crash-late","h-crash-index"]>` → both `killed=yes rc=1`, `SEARCH-SUMMARY … errored=0 killed=2 survived=0`,
  EXIT 0 (search sha256 `6089260b…`, the frozen r93 search).
  Receipt: `.ufo/waves/round-94/w1/R94Scribe/receipts/c1-r93rule-crashids.txt`.
- **C1 wording spot-checks**: the sentinel really is inherited twice over — the search puts `sitecustomize.py` in
  `PYTHONPATH` for the harness process (`census/round-94/c1-survivor-search.py:140`) and the harness spawns the
  counter with the inherited environment, so the counter's crash reaches the harness as `rc=70` on the ROW lines
  (66 such rows for `h-crash-late` in `census/round-94/records/c1-after-harness/m0003.out`, 1 for `h-crash-index` in
  `m0004.out`). The two semantic kills stay `killed=yes` and the survivor `killed=no`
  (`census/round-94/records/c1-after.txt`). No widened sentence found.
- **C2 predicate, re-run by me** on the same setup arms the r93 probe fails (existing empty `--work`, a missing
  `--tool`/`--fixture`/`--before`): the r93 probe exits **1** on each with a Python traceback
  (`FileExistsError` at `census/round-93/c2-forgery-probe.py:89` `os.makedirs(work)`, `FileNotFoundError` at
  `:92`/`sha()`); the r94 probe exits **2** with one `C2-FORGERY-FATAL:` line on each
  (`--tool … is not a readable regular file`, `--fixture …`, `--before …`), and on an existing empty `--work` it
  runs to completion with `FORGERY-SUMMARY forgeries=8 rejected=8 positive=pass` (EXIT 0).
  Receipt: `.ufo/waves/round-94/w1/R94Scribe/receipts/r93-probe-setup-exit-codes.txt`.
- **C2 wording spot-checks**: the r93 probe exits 1 on exactly 7 of the 8 setup arms
  (`census/round-94/controls/c2-control-r93-probe.txt`: S1, S3, S4, S5, S6, S7, S8 at `exit=1`; S2 at `exit=2`),
  and the r94 probe keeps its two verdict arms (P1 exit 0, P2 exit 1) — `census/round-94/records/c2-after.txt`
  `ARMS-SUMMARY arms=10 conform=10`. The eight forgeries and the verdict are byte-identical between the two
  probes (`FORGERIES` tuple sha256 prefix `843209d750ac9c04` in both). No widened sentence found.

**Two precision findings that do NOT falsify either claim** (both are for the lesson's "stated limits", not for the
claims' wording):

1. **The seven r93 setup-arm exits of 1 arrive by two different mechanisms.** Five of them (S1, S3, S4, S5, S6) are
   *uncaught Python exceptions* — the interpreter's default status 1, not the probe's own `return 1` — and two (S7
   the mute fixture, S8 the crashing fixture) reach the probe's verdict `return 0 if positive and rejected == … else
   1`. Evidence: `census/round-94/controls/c2-control-arms-out/{S1,S3,S4,S5,S6}.out` each contain a
   `Traceback (most recent call last):`; `{S7,S8}.out` contain none and instead end `FORGERY-SUMMARY forgeries=8
   rejected=0`. This is exactly why the two are indistinguishable to a reader of the exit status alone, and it is
   why the r94 fix must use a status no verdict uses *and* a named FATAL line (a traceback on stderr is the other
   half of the evidence).
2. **Only one of the two halves of the r94 C1 rule is exercised by this round's targets.** The rule is
   "harness exit 70 **or** any ROW `rc=70` → errored", but in both crash fixtures the harness itself exits **1**
   (`m0003.out`: `SUMMARY rows=66 mismatches=10 …`, `m0004.out`: `SUMMARY rows=66 mismatches=1 …`) and the crash
   surfaces only as the ROW-level `rc=70`. The `harness exit 70` branch is unexercised by these five targets. The
   claim's wording ("or") permits this, but a reader should know which branch carried the round.

---

## Draft `## Mistakes` rows for `corpus/lessons/round-94.md`

Format follows `corpus/lessons/round-93.md` (`# | class | evidence pointer | captured-by | fix`). "Fix" is counted
only once it is shown able to fail, i.e. only where a control receipt shows the *old* behaviour failing the new
check. Every evidence pointer below is a path relative to the lane root.

| # | class | evidence pointer | captured-by | fix (able-to-fail status) |
|---|---|---|---|---|
| M1 | an assumption about a crash's exit code, written into a docstring and a prereg, never run: the r93 kill rule's docstring reads "A harness exit 2, or an exit 1 whose only failing rows are `match=error` (the counter crashed, rc 2), is `errored`" — but an uncaught Python exception exits **1**, the counter's own "not all resolved" code, so the guard never fires and a crash is scored `killed` | `census/round-93/c1-survivor-search.py` lines 6-7 (docstring) and `verdict()` lines 86-93; the docstring's premise is contradicted by `census/round-87/c1-pointer-counter.py` line 574 (`return 0 if ok else 1`) | Q170 (written in r93 after the fact); the r93 wave's own R93Sentinel M1 / R93Scribe FK1; nothing before it | **r94: the crash is surfaced by an exit status no verdict uses** — a PYTHONPATH `sitecustomize.py` whose `sys.excepthook` exits 70 (sysexits EX_SOFTWARE, S358), and the r94 rule scores any `ROW rc=70` (or a harness exit 70) `errored` (S357's Runtime-error state). **Able to fail: the do-nothing control runs the frozen r93 rule on the same five targets and prints `errored=0 killed=4 survived=1`, both crash fixtures `killed=yes`** — `census/round-94/controls/c1-control-r93-rule.txt` (re-run by this seat on the two crash ids alone: `.ufo/waves/round-94/w1/R94Scribe/receipts/c1-r93rule-crashids.txt`, `killed=yes rc=1` for both). The search also refuses to score anything unless its sentinel fires in a child first (`# crash-sentinel rc=70 check=pass`), and forgery FB (no sentinel on PYTHONPATH) reproduces the old miscount (`errored=0 killed=4`, `census/round-94/controls/c1-forgery-controls.txt`) |
| M2 | an instrument whose verdict exit code is also its crash/setup exit code: the r93 probe's own docstring promises "2 on setup error", but `os.makedirs(work)` on an existing empty `--work` raises `FileExistsError` and the interpreter exits **1** — the probe's "a forgery was not rejected" code; likewise a missing `--fixture`/`--tool`/`--before` (`FileNotFoundError` in `sha()`), a `--work` that is a regular file (`NotADirectoryError` in `os.listdir`), a fixture that prints nothing and a fixture that crashes (both scored `rejected=no`) | `census/round-93/c2-forgery-probe.py:89` (`os.makedirs(work)`), `:92` (`sha(v)`), `:86` (`os.listdir(work)`), `:118` (`return 0 if positive and rejected == len(FORGERIES) else 1`); the docstring's exit contract at `:25-26`; tracebacks in `census/round-94/controls/c2-control-arms-out/{S1,S3,S4,S5,S6}.out`; `FORGERY-SUMMARY forgeries=8 rejected=0` in `{S7,S8}.out` | none before r94 — no criterion asked that a verdict exit code be reachable only by a verdict; the defect reached the lane through the r93 non-author spot-check §5 item 5 | **r94: every setup failure exits 2 with one named `C2-FORGERY-FATAL:` line; an existing empty `--work` is used as is** — `census/round-94/c2-forgery-probe.py:95-100` (the `--work` guards: exists-and-not-a-directory at `:95-97`, non-empty at `:98-100`), the readable-regular-file check for `--fixture`/`--tool`/`--before` at `:102-105`, and `os.makedirs(work, exist_ok=True)` at `:106` (the r93 probe's `os.makedirs(work)` at `:89` is what raised). **Able to fail: the do-nothing control runs the frozen r93 probe under the same ten-arm counter and prints `ARMS-SUMMARY arms=10 conform=3`, EXIT 1** (`census/round-94/controls/c2-control-r93-probe.txt`; S1, S3-S8 all `exit=1`); the after arm prints `conform=10` (`census/round-94/records/c2-after.txt`), and forgeries GA (verdict exit 2) and GB (refuse the empty dir) each score `conform=9` (`census/round-94/controls/c2-forgery-controls.txt`) |
| M3 | **the routed fix for M1 was itself insufficient, and the round's own rule shows why: "score a ROW with `got=-` as `errored`" cannot see a crash that happens *after* the counter printed its items** — `h-crash-late` raises at the counter's final `return 0 if ok else 1`, i.e. after every `ITEM` line is printed, so **no** row reads `got=-` and the routed rule still scores it `killed`; only a status the verdict cannot produce separates it. A repair written as a marker-absence test was never run against a crash whose marker is present | `corpus/lessons/round-93.md` "Routed to round 94" item 1 ("score a ROW with `got=-` (or a counter traceback) as `errored`") and QUALITY Q170; the r94 crash fixture `h-crash-late` (`census/round-94/c1-survivor-search.py` HAND tuple, `raise RuntimeError("h-crash-late")` replacing the counter's last `return`); `census/round-94/records/c1-after-harness/m0003.out` (66 rows, **0** of them `got=-`, 10 `match=no`, all `rc=70`); the counter-side stderr is dropped by the harness except on its `rc == 2` branch (`census/round-93/c1-false-row-harness.py:467,508,529,548`), so a "counter traceback" is not on the harness's normal output path either | this seat (R94Scribe), by applying the three candidate rules to the round's own harness outputs | **r94: the crash is a status, not a missing marker** — the sentinel's exit 70 reaches the harness as `ROW rc=70` and the rule keys on that. **Able to fail: the rule comparison below shows the routed rule scores `h-crash-late` `killed` while the shipped rule scores it `errored`**. Receipt: `.ufo/waves/round-94/w1/R94Scribe/receipts/rule-check-output.txt` (the script: `…/receipts/rule-check.py`) |

**M3 in detail** (this is the row with a fresh reproducer, so it is worth stating the measurement in full).
The script `rule-check.py` re-implements three candidate rules and applies each to the *same* harness output:

| fixture | `got=-` rows | `rc=70` rows | R-A (r93 rule as shipped) | R-B (r93-routed fix: `got=-` ⇒ errored) | R-C (r94 rule: `rc=70` ⇒ errored) |
|---|---|---|---|---|---|
| `h-crash-late` (r93-rule run) | 0 | 0 | killed | **killed** | killed |
| `h-crash-index` (r93-rule run) | 1 | 0 | killed | errored | killed |
| `h-crash-late` (r94 run, `m0003.out`) | 0 | 66 | killed | **killed** | **errored** |
| `h-crash-index` (r94 run, `m0004.out`) | 1 | 1 | killed | errored | **errored** |

Read: the routed rule R-B is right for `h-crash-index` (one three-column ledger row → one `got=-`) and wrong for
`h-crash-late` (the crash is after the `ITEM` lines, so every row carries a `got=`); R-B scores `h-crash-late`
`killed` under **both** the r93 search and the r94 search. Only R-C — a status no verdict uses — gets both.
The lesson's generalisation: *a crash must be reported by a channel the verdict cannot imitate*; a missing marker is
such a channel only when the crash always precedes the marker, and "always" is a property of the fixture, not of the
rule.

---

## Draft QUALITY criterion (next free Q number — see the numbering note)

**Numbering note (a conflict the L1 must resolve).** The last criterion **committed** in `corpus/QUALITY.md` is
`Q170` (`git show HEAD:corpus/QUALITY.md | grep -oE '^\| Q[0-9]+' | tail -1` → `| Q170`), so "the next free number
after the last in `corpus/QUALITY.md`" is literally **Q171**. But the L1's **uncommitted** working-tree draft already
claims `Q171` (`git diff corpus/QUALITY.md` adds a `## Round 94 criteria` section with a `Q171` row). Two rows
numbered Q171 in one file is a defect. Two ways out, both the L1's to pick: (a) fold my text into the L1's Q171
row, or (b) file mine as **Q172** extending it. Below I give it as **Q172 extending Q171** (the collision-free
choice), and mark the single clause that is mine rather than the L1's.

| id | criterion | applies-to | test | lesson |
|---|---|---|---|---|
| Q172 | Extends Q171 (it stands) and Q170 (it stands): **an instrument's verdict exit code is reachable only by a verdict, and a crash is reported by a channel the verdict cannot imitate.** Two halves, each with its own counting command. (i) *Status half:* the code under test's crash must reach the instrument as an exit status that no verdict uses (r94: a PYTHONPATH `sitecustomize` `sys.excepthook` exits 70 — sysexits EX_SOFTWARE, S358 — and the rule scores any `ROW rc=70`, or a harness exit 70, `errored`; S357's Runtime-error state is a state distinct from Killed). A marker-absence heuristic is **not** this half and is not a substitute: "score a ROW with `got=-` as `errored`" cannot see a crash that happens *after* the counter printed its items, and the harness drops the counter's stderr except on its `rc == 2` branch, so a "counter traceback" is not on the normal output path either. (ii) *Setup half:* every setup failure of the instrument itself exits 2 with one named FATAL line, and a verdict exit code is never used for one (r94 probe: `C2-FORGERY-FATAL:`; S1 (existing empty `--work`) is used as is, S2-S8 refused with exit 2). A claim of this kind carries a do-nothing control on which the old instrument fails, and a blanket-refusal forgery (every non-zero exit treated as setup/crash) on which the verdict arm fails. **Counting command (status half):** `grep -c 'killed=yes' <(grep '^SEARCH h-crash' RECEIPT)` → **2** on the r93-rule control (`census/round-94/controls/c1-control-r93-rule.txt`), **0** on the r94 search (`census/round-94/records/c1-after.txt`) — the check can fail, and it fails on the old rule. **Counting command (setup half):** `grep -cE 'exit=[01] .*line=no' <(grep '^ARM S' RECEIPT)` → **7** on the r93 probe (`census/round-94/controls/c2-control-r93-probe.txt`), **0** on the r94 probe (`census/round-94/records/c2-after.txt`) — again it can fail, and it does on the old probe. (Both `grep -c` forms exit 1 when the count is 0, i.e. on the passing side; a shell that treats a non-zero status as fatal must append `|| true` — the numbers themselves are what the criterion cites.) **One combined counter over both receipts:** `awk '/conform=no/{c++} /^SEARCH h-crash/ && /killed=yes/{c++} END{print c+0}'` → **9** on the two controls, **0** on the two after receipts (`census/round-94/records/{c1-after,c2-after}.txt`) | every mutation search, forgery probe or fixture whose exit 1 (or its verdict field) means "the mutant/forgery was caught or survived" — `census/round-9*/c1-survivor-search.py`, `census/round-9*/c2-forgery-probe.py` | the two counting commands above, run on the round's own receipts (numbers in the criterion text; measured by this seat — see `.ufo/waves/round-94/w1/R94Scribe/receipts/collision-count.txt`); the status half's "marker-absence is not a status" claim is measured by `.ufo/waves/round-94/w1/R94Scribe/receipts/rule-check-output.txt` | `corpus/lessons/round-94.md` M1, M2, M3 |

---

## Draft `## Gate` block for S357/S358

Both rows were opened 2026-11-09 by the L1 and are committed in P1 (`census/SOURCES.md` lines 296-297; registry
278 → 280 rows, `grep -cE '^\|[[:space:]]*S[0-9]{3,}' corpus/SOURCES.md` → 280). The captures are committed under
`census/round-94/srcs/`. I re-derived the captures' digests and the quotes' occurrence counts from the committed
bytes; **I did not re-fetch either page live** (the live re-open is the scout's row, and this seat's slot is the
admit block only).

- **S357 — Stryker Mutator, "Mutant states and metrics"**
  (https://stryker-mutator.io/docs/mutation-testing-elements/mutant-states-and-metrics/; access date 2026-11-09;
  per the SOURCES row, HTTP 200, 27068 bytes; this seat did not re-fetch). Capture
  `census/round-94/srcs/stryker.html`, sha256 `30071cc7b6578a114843f18da568c305b192a08d098511896e7cb4a90a5f89da`
  (re-checked by this seat with `sha256sum`: match); tag-stripped text `census/round-94/srcs/stryker.txt`, sha256
  `07cb258bf94fd09bc90e7e83d66a19f5172f366a92a55d78a669e48bef191070`.
  Locator: § Mutant states (anchor `id="mutant-states"`), the **"Runtime error"** entry of the state list
  (`<strong>Runtime error</strong>` inside the § Mutant states `<ul>`; the page's `<h1>` is "Mutant states and
  metrics", its `<h2>`s are "Mutant states", "Metrics", "Test states and metrics").
  Quote (14 words): "The running of the tests resulted in an error (rather than a failed test)."
  One occurrence in the whitespace-normalized tag-stripped text `census/round-94/srcs/stryker.txt`
  (re-counted by this seat: occurrence count **1**, offset 1746 in that file); the same count holds in the
  whitespace-normalized `census/round-94/srcs/stryker.html.stripped.txt` (occurrence count 1; the two files are
  identical after whitespace normalization — re-checked by this seat).
  **ADMIT**, `docs`, tier A, `mined` — grounds the r94 kill rule's `errored` class (a crash is a runtime error, a
  state distinct from Killed and left out of the mutation score). Used by
  `corpus/knowledge/mutant-crash-is-not-a-kill.md`.
- **S358 — sysexits(3), FreeBSD Library Functions Manual**
  (https://man.freebsd.org/cgi/man.cgi?query=sysexits; access date 2026-11-09; per the SOURCES row, HTTP 200,
  59385 bytes; this seat did not re-fetch). Capture `census/round-94/srcs/sysexits.html`, sha256
  `da498cbc711a743ae309b603ae8615f1164690cb6d4a67dea2e650175cbae139` (re-checked by this seat with `sha256sum`:
  match); tag-stripped text `census/round-94/srcs/sysexits.txt`, sha256
  `bcc45177c0c89a1bedeaacaf32608c659ee968a23ad7a40d890057e4867195a0`.
  Locator: § DESCRIPTION (anchor `id="DESCRIPTION"`), the **EX_SOFTWARE** entry.
  Quote (9 words): "EX_SOFTWARE (70) An internal software error has been detected."
  One occurrence in the whitespace-normalized tag-stripped text `census/round-94/srcs/sysexits.txt` (re-counted by
  this seat: occurrence count **1**, offset 11951); the same count holds in
  `census/round-94/srcs/sysexits.html.stripped.txt` (occurrence count 1; identical to the `.txt` after whitespace
  normalization).
  **ADMIT**, `docs`, tier A, `mined` — grounds the crash sentinel's exit status (70 = EX_SOFTWARE), which no verdict
  (0, 1) and no setup error (2) uses. Used by the same knowledge entry.
- **Reject sample:** [SLOT — R94ScoutSources to fill; not drafted by R94Scribe].

---

## Receipts in this seat dir (`.ufo/waves/round-94/w1/R94Scribe/receipts/`)

| file | what it shows |
|---|---|
| `c1-r94-crashids.txt` | my re-run of the r94 search on the two crash ids: `# crash-sentinel rc=70 check=pass`, both `killed=errored`, `errored=2 killed=0 survived=0`, EXIT 0 |
| `c1-r93rule-crashids.txt` | my re-run of the r94 do-nothing control (the frozen r93 search) on the same two ids: both `killed=yes rc=1`, `errored=0 killed=2 survived=0`, EXIT 0 |
| `h-crash-late.r93rule-harness.out`, `h-crash-index.r93rule-harness.out` | the r93 search's own per-mutant harness outputs for the two crash fixtures (66 ROWs each; `got=-` 0 and 1; `rc=70` 0; `match=no` 2 and 1) — the inputs to `rule-check.py` |
| `rule-check.py`, `rule-check-output.txt` | the three-rule comparison (R-A r93 shipped, R-B r93-routed `got=-` fix, R-C r94 shipped) and its output on both fixtures under both searches — the reproducer behind M3 and behind the "marker-absence is not a status" clause of Q172 |
| `r93-probe-setup-exit-codes.txt` | my re-run of the r93 probe on four setup arms (existing empty `--work`, missing `--tool`, missing `--fixture`, missing `--before`) with a FRESH `--work` where the arm needs one: exit 1 with `FileExistsError`/`FileNotFoundError` tracebacks; the same arms under the r94 probe: exit 2 with `C2-FORGERY-FATAL:` lines, and exit 0 + `FORGERY-SUMMARY forgeries=8 rejected=8 positive=pass` on the existing empty `--work` |
| `collision-count.txt` | the combined counter over the four committed receipts: 9 collisions on the two do-nothing controls, 0 on the two after receipts, with the per-line breakdown of the 9 |

## Process notes (this seat)

- One self-correction worth recording: my first `rule-check.py` derived the harness's exit code from the presence of
  `mismatches=0`/`errors=0` as substrings, which mis-read `mismatches=10` as "contains errors=0" and printed
  `errored` for a `killed` fixture. Fixed by parsing the SUMMARY fields as integers (harness exit 0 iff
  `mismatches == 0 and errors == 0`) and re-running; the receipt shows the corrected numbers.
- Scratch discipline: `/fast/scratch/hyaku/souji-r94/R94Scribe/` held the two C1 `--work` trees (deleted by the
  search itself after each mutant) and the probe scratch dirs; the whole directory was removed before this yield
  (`rm -rf`). No background process was left running (both C1 runs were foreground, ~17 s each).
- No tool was installed or upgraded this round (none needed). No pacman transaction was attempted.

## Out of scope for this seat (reported, not acted on)

- `census/round-94/srcs/stryker.html.stripped.txt` and `census/round-94/srcs/sysexits.html.stripped.txt` are
  **untracked** files inside the frozen `census/` tree (`git status` shows them as `??`; they are byte-equivalent to
  the committed `.txt` captures after whitespace normalization). `census/` is a frozen directory for this wave; the
  L1 should decide whether they are committed, ignored, or removed.
- The L1's working tree already contains a `Q171` row and `corpus/lessons/round-94.md` with `M1`/`M2`; the numbering
  conflict noted above and the M3 row are the two things this seat adds.
