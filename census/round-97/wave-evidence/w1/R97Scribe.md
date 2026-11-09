# R97Scribe — round-97 lesson drafting (souji)

Seat: R97Scribe (scribe). Lane: souji-shokunin, lane base `210084b24de1dd1f1fd499f49b0c70744f099f5f`, lane master
`053287d4eea5dc6c0e1aff9c2295cff0f0a2a3d9`. Date: 2026-11-09. Scope: draft the round-97 `## Mistakes` rows, one
`corpus/QUALITY.md` criterion, and the `## Gate` source-rows block, from committed evidence only. Read-only on the lane;
every file I wrote is under `.ufo/waves/round-97/w1/R97Scribe/`; scratch under `/fast/scratch/hyaku/souji-r97/R97Scribe/`
(deleted at yield). No git/jj mutation, no corpus/census edit, no tool install.

## 0. What I read, and what I ran

Read: `census/round-97/preregistration.txt` (the frozen contract), `census/round-97/controls/*.txt` (9 files),
`census/round-97/c1-survivor-search.py`, `census/round-97/c2-setup-arms.py`, `census/round-97/c2-forgery-probe.py`,
`census/round-97/c2-forgery-controls.py`, `census/round-97/declared-shapes.py`, `census/round-97/shapes/` (14 scripts),
`corpus/lessons/round-96.md`, `corpus/lessons/round-95.md`, `corpus/lessons/round-96-verifier-spotcheck.md`,
`corpus/QUALITY.md`, `corpus/SOURCES.md`, `corpus/knowledge/crash-channels-beyond-excepthook.md`,
`corpus/knowledge/deadline-owned-reaping.md`, `plans/round-96.md`, `plans/round-97.md`.

Ran (all receipts under `.ufo/waves/round-97/w1/R97Scribe/receipts/`):

| what | command (abbreviated) | result |
|---|---|---|
| shape table, r97 hook | `python3 -B census/round-97/declared-shapes.py --search census/round-97/c1-survivor-search.py --scripts census/round-97/shapes --work <scratch>` | `SHAPES-SUMMARY shapes=14 mismatched=0`, EXIT 0 (`receipts/shapes-r97-requal.txt`) |
| shape table, r96 hook (control) | same, `--search census/round-96/c1-survivor-search.py` | `shapes=14 mismatched=2` (x1/x2 `hooked=1`), EXIT 1 (`receipts/shapes-r96-requal.txt`) |
| shape table, r95 hook (control) | same, `--search census/round-95/c1-survivor-search.py` | `shapes=14 mismatched=2` (t1/t4 `hooked=70`), EXIT 1 (`receipts/shapes-r95-requal.txt`) |
| sources census, HEAD | `bash scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` | **EXIT 1**, `souji E01 S372 fields=7` (+94 pre-existing W04 cross-scope warnings) (`receipts/sources-validate.txt`) |
| sources census, lane base | same, against `git show 210084b2:corpus/SOURCES.md` | E11 only (all `used-by` paths unresolvable from a `--file` copy) — **no E01**, so E01 is new in r97 (`receipts/sources-validate-base.txt`) |
| probe output cap | r97 probe with a 300 KB fixture, `--max-output 65536` | `C2-FORGERY-FATAL: the positive control exceeded --max-output 65536 bytes; its process group was killed`, EXIT 2 (`receipts/probe-maxoutput.txt`) |
| T1 grandchild vs the r97 probe | r97 probe, `--timeout 5`, pipe-holder fixture | probe EXIT 2; **1 survivor** after probe exit, `ppid=1525`, own pgrp/session (`receipts/t1-probe-r97-exp.txt`) |
| T1 grandchild vs the r96 probe | same with `census/round-96/c2-forgery-probe.py` | probe EXIT 2; **1 survivor** after probe exit, own pgrp/session (`receipts/t1-probe-r96-exp.txt`) |
| T1 arm, committed counter + r97 probe | trimmed copy of `c2-setup-arms.py` (arms tuple reduced to T1 only; the lane file is untouched) | `ARM T1 exit=2 want=2 line=yes conform=yes survivors=0`; `T1.out` ends `--survivors 0 planted-killed 1--` (`receipts/t1-arm-r97probe.txt`) |
| T1 arm, committed counter + r96 probe | same trimmed copy, `--probe census/round-96/c2-forgery-probe.py` | identical: `survivors=0`, `planted-killed 1` (`receipts/t1-arm-r96probe.txt`) |
| T1 arm, reap removed (mutant) | trimmed copy with the T1 `os.kill` neutralised | `ARM T1 exit=2 want=2 line=yes conform=yes survivors=1`, `--survivors 1 planted-killed 0--` (`receipts/t1-arm-noreap.txt`) |
| signal exit, r97 counter | trimmed counter + a probe that SIGTERMs itself | `ARM T1 exit=-15 want=2 line=no conform=no survivors=0` (`receipts/signal-exit-rendering.txt`) |
| signal exit, r96 vs r97 counter | same probe, both counters | r96: `exit=-15`; r97: `exit=-15` — identical rendering (`receipts/signal-exit-r96-vs-r97.txt`) |
| traceback print, r96 vs r97 hook | same raising script under each hook | r96 stderr has 1 "Traceback" line; r97 stderr has 0 (`receipts/a2-traceback-order.txt`) |

All nineteen receipts live in `.ufo/waves/round-97/w1/R97Scribe/receipts/`: `shapes-r95-requal.txt`,
`shapes-r96-requal.txt`, `shapes-r97-requal.txt`, `sources-validate.txt`, `sources-validate-base.txt`,
`probe-maxoutput.txt`, `t1-probe-r97-exp.txt`, `t1-probe-r96-exp.txt`, `t1-arm-r97probe.txt`, `t1-arm-r96probe.txt`,
`t1-arm-noreap.txt`, `grep-exit-signal.txt`, `quote-occurrence.txt`, `process-cleanup.txt`, `signal-exit-rendering.txt`,
`signal-exit-r96-vs-r97.txt`, `signal-exit-markers.txt`, `a2-traceback-present.txt`, `a2-traceback-order.txt`.

The two trimmed/mutant copies live only in scratch (`/fast/scratch/hyaku/souji-r97/R97Scribe/t1/`), derived from the
committed counter; the lane's `census/round-97/c2-setup-arms.py` was never edited (`git status --porcelain` clean at
yield).

**Process hygiene.** Every fixture run above forks a `setsid()` grandchild that sleeps an hour. The reap-mutant run
(`t1-arm-noreap.txt`) left **2** such grandchildren alive under my scratch tree, as designed; I found them by scanning
`/proc/*/cmdline` for my scratch path and SIGKILLed both, then re-scanned: **0 processes** under
`/fast/scratch/hyaku/souji-r97/R97Scribe/` remain (`receipts/process-cleanup.txt`). No background job, service or
long-lived process from this seat is left running; the scratch tree is deleted at yield.

---

## 1. Draft `## Mistakes` rows (for `corpus/lessons/round-97.md`)

Format follows `corpus/lessons/round-96.md` (class · evidence · captured-by · fix · shown able to fail). Every row below
carries an evidence path under this seat's directory or a committed lane path.

- **M1 — a clear scoped by the frame name of the handler, not by whether the exception still terminates.** Class: a
  predicate gate whose eligibility rule names a *site* (the `<module>` frame) instead of the *event* that decides the
  outcome (S372's RERAISE), so a rule that is right for one shape silently covers the opposite class. Evidence:
  `census/round-97/controls/shapes-r96.txt` (the frozen r96 hook on the fourteen-shape table: `x1-module-finally-term.py`
  and `x2-module-reraise-term.py` score `plain=1 hooked=1 MISMATCH`, `SHAPES-SUMMARY shapes=14 mismatched=2`, EXIT 1) and
  `census/round-97/controls/shapes-r95.txt` (the r95 hook on the same table: `t1-catch-module-falloff.py` and
  `t4-reraise-at-module.py` score `plain=0 hooked=70 MISMATCH`, `mismatched=2`, EXIT 1) — the r96 rule traded one shape
  class for the other, so neither do-nothing control reaches `mismatched=0`. Re-derived independently:
  `.ufo/waves/round-97/w1/R97Scribe/receipts/shapes-r96-requal.txt` and `shapes-r95-requal.txt` (same two numbers,
  same two shapes). Captured-by: the r96 wave — `plans/round-96.md` A1 and `corpus/lessons/round-96.md` M1 (M1 there
  records the same class; `corpus/lessons/round-96-verifier-spotcheck.md` §2 adjudicates it as "real and reconciled").
  Fix: the r97 search's RERAISE-aware pending-clear latch (`census/round-97/c1-survivor-search.py:173-211`: the foreign
  mark latches at `RAISE-<module>`, a module-level `EXCEPTION_HANDLED` records a *pending* candidate, a `RERAISE` of the
  same object cancels it, `atexit` flushes a still-pending candidate), plus the two new table shapes
  `census/round-97/shapes/x1-module-finally-term.py` and `x2-module-reraise-term.py`; the r97 hook scores the whole table
  `shapes=14 mismatched=0` (`.ufo/waves/round-97/w1/R97Scribe/receipts/shapes-r97-requal.txt`). **Shown able to fail:**
  `census/round-97/controls/c1-forgery-controls.txt` — `FORGERY FD` (the EH callback is not registered) and `FORGERY FE`
  (the RERAISE callback is not registered) each leave the ten-target summary unchanged but print `shapes=2` on the same
  table and are `refused=yes`; i.e. the latch is load-bearing in both directions, and dropping either leg breaks the table
  exactly as the r96 rule did. The r97 hook's own reason strings (`SOUJI-R97-CRASH SystemExit first raised in …`) are the
  second binding (Q172's reason-text rule), and the r97 hook asserts the reason per channel
  (`census/round-97/c1-survivor-search.py:262-264`, checked at `:410-414`), so a cross-wired channel fails closed with
  `C1-SEARCH-FATAL`. **Mechanism note carried to §4 F-6/F-7:** the A2 leg of the **C1** claim's wording — that the
  excepthook/thread channels "write before the traceback print" — is implemented in the r97 bytes as a *removal* of the
  traceback print from those two channels, not a reorder: the r97 hook calls neither `sys.__excepthook__` nor
  `threading.__excepthook__`, and `_souji_crash` ends the process with `os._exit(70)`
  (`census/round-97/c1-survivor-search.py:134-136,147-150`, `:109,130`; the r96 versions called the traceback printers
  first, at `census/round-96/c1-survivor-search.py:118,131`). Live comparison:
  `.ufo/waves/round-97/w1/R97Scribe/receipts/a2-traceback-order.txt` (r96 stderr carries 1 "Traceback" line, r97 carries
  0). The A2 *effect* — the blocking print cannot hold the exit hostage — holds; the traceback is simply gone.

- **M2 — a kill sentence written about the counter's own reach instead of the process's, and a survivor count that
  never moved.** Class: a stated-limit about another process's fate, copied from intent (r96's M3) — and, in r97, a count
  in the predicate (`survivors=0`) that the one artifact able to move it cannot reach. Evidence: `plans/round-96.md` A4
  (the r96 counter's `killpg(probe.pid)` cannot reach the `setsid()` grandchild; 1 survivor after a counter-style kill,
  2 after the probe's own exit) and `corpus/lessons/round-96.md` M3; in r97 the escape is still live under the *frozen
  probe*: `.ufo/waves/round-97/w1/R97Scribe/receipts/t1-probe-r97-exp.txt` (r97 probe, pipe-holder fixture: probe EXIT 2
  and **1 survivor** after the probe exits, `ppid=1525`, own pgrp and own session) and
  `receipts/t1-probe-r96-exp.txt` (same under `census/round-96/c2-forgery-probe.py`: **1 survivor**). Captured-by: the r96
  wave (`R96Sentinel.md` F-4 E6a-E6d) and the r96 spot-check §2 (C2-A4, "real and reconciled"); the r97 re-measurement
  confirms the escape persists, so the r97 counter's own reap is what closes it. Fix: the r97 counter reaps by planted
  identity — `census/round-97/c2-setup-arms.py:255-338`: snapshot the arm's own-uid identity set *before* the arm, then
  SIGKILL only processes whose argv carries the arm's absolute fixture path and whose `(pid, starttime, boot_id)` is not
  in that before-set, then count the survivors that are not in it; the run prints `survivors=<n>` on the T1 ARM line and
  `planted-killed <k>` in `T1.out` (`receipts/t1-arm-r97probe.txt`: `--survivors 0 planted-killed 1--`).
  **Shown able to fail:** the counter-side mutant — a trimmed copy of the committed
  counter with the T1 `os.kill` neutralised — leaves the grandchild alive and prints `ARM T1 … survivors=1` and
  `--survivors 1 planted-killed 0--` (`.ufo/waves/round-97/w1/R97Scribe/receipts/t1-arm-noreap.txt`; the mutant's copy is
  `sha256=a066eb0e…`), while the unmutated committed counter prints `ARM T1 … survivors=0` and
  `--survivors 0 planted-killed 1--` on the same arm (`receipts/t1-arm-r97probe.txt`). The mutant's two escaped
  grandchildren were found alive after the run and killed by this seat (see §0) — the leak the fix prevents, observed.
  **Limit on the fix, stated here because the r97 control set cannot show it:** no *probe-side* edit can move this
  number — `census/round-97/controls/c2-forgery-controls.txt` shows `FORGERY GD` (`arms_exit=0`,
  `summary=arms=20,conform=20`, `refused=no`), because the GD forgery edits the probe's refusal *message* and the counter
  reaps regardless of what the probe says; and the same control's own
  `C2-FORGERY-CTL-SUMMARY forgeries=4 refused=3` (EXIT 1) shows GD is not refused. `plans/round-97.md` A8 already discloses
  this ("no forgery-refusal gain, reported honestly"), and my re-measurement agrees with A8's mechanism: the reaping is
  the counter's, not the probe's, so the reaping claim is not probe-sensitive and the forged probe cannot bind it. The
  honest consequence for the lesson: **the r97 control set contains no artifact in which `survivors` is non-zero**, so
  the counter-side mutant above is the only witness that the number can move; a future round must give that arm a
  committed receipt.

- **M3 — a registry row written with a missing cell block, so the lane's own census gate fails closed.** Class: a row
  appended in the shape the author had in mind rather than the shape the contract names — the corpus's own E01 check
  (`scripts/sources-census.sh` `NF!=13`) is the mechanism that was supposed to catch it and did not run before the row
  was committed. Evidence: `census/round-97/controls/…` is unaffected; the defect is in `corpus/SOURCES.md:311` — the
  `S372` row has **7** populated cells against the contract's 11 (`id, source, kind, tier, scope, anchor, teaches,
  status, opened, recheck, used-by`): `status`, `opened`, `recheck` and `used-by` are absent, and the `used-by` value
  (`corpus/knowledge/crash-channels-beyond-excepthook.md`) is glued inside the `teaches` cell ("…cannot clear the foreign
  mark. Used-by: corpus/knowledge/crash-channels-beyond-excepthook.md"). The row was added at P1 (`053287d4`;
  `git show --numstat 053287d4 -- corpus/SOURCES.md` → `1 0`), so the defect entered the registry with the row.
  `bash scripts/sources-census.sh validate --root
  /home/vgpnk/Projects/shokunin souji` now exits **1** with `souji E01 S372 fields=7`
  (`.ufo/waves/round-97/w1/R97Scribe/receipts/sources-validate.txt`), where the lane base
  `210084b24de1dd1f1fd499f49b0c70744f099f5f` produces no E01 at all
  (`receipts/sources-validate-base.txt`: E11 only, an artifact of validating a `--file` copy outside the repo). The
  census number for the lesson's Gate block is therefore 293 → **294 rows** with a **failing** validate, not the "EXIT 0 at
  both ends" shape of `corpus/lessons/round-95.md` and `round-96.md`. Captured-by: the census script itself, on the
  committed bytes. Fix (for the L1, since `corpus/` is not mine to edit): give `S372` its four missing cells —
  `status mined`, `opened 2026-11-09`, `recheck 365d`, `used-by corpus/knowledge/crash-channels-beyond-excepthook.md` —
  and move the `Used-by:` sentence out of the `teaches` cell; that restores `NF=13` and the census's EXIT 0. **Shown able
  to fail:** the row is one cell-block short and the census says so by name (`E01 S372 fields=7`); the quote's own
  location is unaffected — "An exception is re-raised, for example at the end of a finally block." occurs exactly once in
  the r97 capture `census/round-97/srcs/monitoring.html` (sha256 `2b281793…`, and the capture differs from the r96 capture
  `cd85fa73…` only in the page's "Last updated" line), so the *content* is sound and only the row shape is wrong.
  **Second defect in the same row (label):** its anchor cell says the quote is "14 words", but the corpus's own
  convention — whitespace tokens, as in S365 (4), S366 (9), S368 (17), S371 (22) — gives **13**
  (`receipts/quote-occurrence.txt`: `S372 … words=13`); 14 is only reachable by splitting the hyphen in "re-raised".
  Fix: write 13, matching the convention the rest of the registry uses.

- **M4 — the A8 leg of the C2 fix: a docstring promising a marker the code never prints, and a rendering the r96
  counter already had.** Class: a mechanism described in an instrument's prose that the code does not implement (the r95
  M2 class, recurring) — here with a second, sharper edge: the promised fix is not merely misdescribed, it is **absent**,
  so the frozen claim sentence that names it has no artifact behind it. Evidence:
  `census/round-97/c2-setup-arms.py:6-7` says the counter "records a signal exit (-15) distinctly (never coerce it) and
  **prints it as exit=signal**"; the string `exit=signal` occurs nowhere in the tree except that docstring line
  (`grep -rn 'exit=signal' census/round-97/` → 1 hit,
  `.ufo/waves/round-97/w1/R97Scribe/receipts/grep-exit-signal.txt`). The ARM line is printed at
  `census/round-97/c2-setup-arms.py:348` as `ARM <id> exit=<rc> …` with `<rc>` the raw `p.returncode` (`:282`), so a
  signal death prints `exit=-15` — **the same field, the same spelling, no mark**. Two measurements settle it:
  (i) a live run of the committed r97 counter against a probe that SIGTERMs itself prints
  `ARM T1 exit=-15 want=2 line=no conform=no survivors=0`
  (`receipts/signal-exit-rendering.txt`); (ii) the **r96** counter, run the same way, prints
  `ARM T1 exit=-15 want=2 line=no conform=no` — the r97 line differs only by the appended `{tail}` survivors suffix
  (`receipts/signal-exit-r96-vs-r97.txt`). The rc-handling block is byte-identical between the two counters (the `rc`
  block diff is empty), and the r97 counter has **no** `rc < 0` branch (the only match for `rc < 0` is the comment at
  `:296`). Captured-by: the two live runs plus the byte diff, on the committed bytes. Fix: either emit the promised marker
  (`exit=signal`) from the print, or — cheaper and matching what the corpus already says
  (`corpus/knowledge/deadline-owned-reaping.md:51`: "A killed-by-signal child prints as `exit=-15` in the ARM line (A8):
  it never reads as a verdict exit") — rewrite the docstring to describe `exit=-15` and drop the A8 claim, so the r97
  lesson does not credit a leg that was never implemented. **Shown able to fail:** the r96-vs-r97 rendering comparison
  (`receipts/signal-exit-r96-vs-r97.txt`) shows the two counters produce the *same* rendering of a signal exit, so the
  r97 counter cannot be said to have "recorded a signal exit distinctly" relative to the instrument that the same
  preregistration describes as printing it "inside the same `exit=` field with no mark to tell it from a verdict exit
  (A8)". See §4 F-2 and §5 for the wording consequence.

## 2. Draft `corpus/QUALITY.md` criterion (next free number: **Q173**)

`corpus/QUALITY.md` currently ends at **Q172** (`grep -oE '^\| Q[0-9]+' corpus/QUALITY.md | tail -1` → `| Q172`), so the
next free id is **Q173**. It extends Q172 (the shape-table criterion r95 wrote) rather than replacing it — Q172's
sentence stands. Draft, in the file's `| id | criterion | applies-to | test | lesson |` row shape:

| id | criterion | applies-to | test | lesson |
|---|---|---|---|---|
| Q173 | Extends Q172 (it stands): a classifier that separates *terminating* outcomes from *handled* ones names the events it registers and carries a table of the exit shapes that straddle the line it draws — a module-level `finally` that unwinds, a module-level re-raise, a caught-at-module exit, each classified on both sides of the rule — and the table is read by a counting command that prints one row per shape with the shape's plain and hooked exit codes and a `mismatched` total, so the rule's reach is a measurement rather than a sentence. The count must be able to move on the rule's own terms: the row for a shape that terminates through a handler the rule clears is the row that fails when the rule is wrong. Where the classifier's job also includes ending a process (a counter that reaps an escaped descendant), the same table carries a survivor count per arm with its counting command, and the count is witnessed by a mutant of the instrument that removes the kill — a count that cannot go non-zero on any artifact is not evidence of a kill. | crash sentinels, setup-arm counters, any instrument whose verdict depends on which event fired | `python3 -B census/round-97/declared-shapes.py --search census/round-97/c1-survivor-search.py --scripts census/round-97/shapes --work <empty>` prints `SHAPES-SUMMARY shapes=14 mismatched=0` with per-shape `plain=`/`hooked=` codes, while the same table under `census/round-96/c1-survivor-search.py` prints `mismatched=2` (x1/x2 at `hooked=1`) and under `census/round-95/c1-survivor-search.py` prints `mismatched=2` (t1/t4 at `hooked=70`) — the count moves on both sides of the rule; the counter side is witnessed by a trimmed counter with the T1 `os.kill` removed, which prints `survivors=1` where the committed counter prints `survivors=0` (`planted-killed 1`) | `corpus/lessons/round-96.md` M1 (the EH-clear trade) and M3 (the kill-reach sentence); `corpus/lessons/round-95.md` M1 (Q172's origin); r97 receipts `shapes-r9{5,6,7}-requal.txt` and `t1-arm-noreap.txt` under `.ufo/waves/round-97/w1/R97Scribe/receipts/` |

Rationale for the shape of this criterion (one sentence for the L1): Q172 asks for a shape table of *ordinary* exits but
does not require the table to contain the shapes that straddle the classifier's own rule, nor does it say the count must be
able to move on the rule's terms; the r96 trade and the r97 grandchild are exactly the two gaps — M1's table had no
terminating shape on the far side of the EH clear, and the r97 `survivors` count has no committed artifact on which it is
non-zero.

## 3. Draft `## Gate` block (for `corpus/lessons/round-97.md`)

Follows the `corpus/lessons/round-95.md` `## Gate` shape (registry-rows table + rejected-candidates table + a census
paragraph). The rows below are the ones this round's two claims rest on: **S365, S366, S367** are carried forward
(opened 2026-11-09, re-verified against the r97 capture where one exists), **S372** is this round's new row, and
**S368** is the row C2's sourced claim rests on. All five quotes and locators are re-verified by me against the committed
captures (occurrence count 1 each — `receipts/quote-occurrence.txt`).

Registry rows cited this round (all opened 2026-11-09; capture committed under `census/round-97/srcs/`):

| row | URL | access date | located quote (<=25 words) | locator | decision |
|---|---|---|---|---|---|
| S365 | https://docs.python.org/3/library/sys.monitoring.html | 2026-11-09 | "An exception is handled." (4 words) | § Events, `sys.monitoring.events.EXCEPTION_HANDLED`; `census/round-96/srcs/monitoring.html` sha256 `cd85fa73…` and `census/round-97/srcs/monitoring.html` sha256 `2b281793…` (same page, re-fetched), occurrence count 1 | ADMIT, `mined` (teaches superseded by S369); grounds the latch's EH leg |
| S366 | https://docs.python.org/3/library/os.html#os.set_blocking | 2026-11-09 | "Set the blocking mode of the specified file descriptor." (9 words) | § File Descriptor Operations, `os.set_blocking`; `census/round-96/srcs/os.html` sha256 `078e69b1…`, occurrence count 1 | ADMIT, `mined` (teaches superseded by S370); grounds the A3 fd-2 restore |
| S367 | https://docs.python.org/3/library/subprocess.html | 2026-11-09 | "If start_new_session is true the setsid() system call will be made in the child process prior to the execution of the subprocess." (22 words) | § Popen Constructor, `start_new_session`; `census/round-96/srcs/subprocess.html` sha256 `7f5772d7…`, occurrence count 1 | ADMIT, `mined` (teaches superseded by S371); grounds the setsid premise of the reap |
| S368 | https://man7.org/linux/man-pages/man2/setsid.2.html | 2026-11-09 | "The calling process also becomes the process group leader of a new process group in the session" (17 words) | § DESCRIPTION; `census/round-96/srcs/setsid.2.html` sha256 `52cbc190…`, occurrence count 1 | ADMIT, `mined` (r96 row); grounds C2's "a group kill cannot reach a new session" |
| S372 | https://docs.python.org/3/library/sys.monitoring.html | 2026-11-09 | "An exception is re-raised, for example at the end of a finally block." (13 words) | § Events, `sys.monitoring.events.RERAISE`; `census/round-97/srcs/monitoring.html` sha256 `2b281793…`, occurrence count 1 | ADMIT, `mined`, cited by `corpus/knowledge/crash-channels-beyond-excepthook.md` — **row shape defective: 7 of 11 cells, `E01 S372 fields=7`; see M3** |

Rejected or screened candidates: **left open for the scout seat** (`R97ScoutSources`, whose scope is exactly this row and
whose finding is not yet in the tree). No rejection is asserted here, and the Gate block must not name one until the
scout's artifact lands with a reason and a flip condition.

Status/recheck/used-by changes to existing rows: none. Recheck cells: `365d` for S365-S367, S368, S372.

Sources-census before/after (`scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji`): registry
293 → **294** rows (S372 added; no existing cell touched — `git diff --numstat 210084b2 -- corpus/SOURCES.md` → `1 0`).
The validate **exits 1** at HEAD with `souji E01 S372 fields=7` (94 W04 cross-scope duplicate-URL warnings are pre-existing
and expected); at the lane base the same script on the same registry reports **no E01** (the E11 rows in the base receipt
are an artifact of validating a `--file` copy outside the repo, where `used-by` paths cannot resolve). Receipts:
`.ufo/waves/round-97/w1/R97Scribe/receipts/sources-validate.txt` and `sources-validate-base.txt`. The lesson's Gate
paragraph must state EXIT 1 with the E01 named, not "EXIT 0 at both ends" — the difference from rounds 95/96 is M3.

Knowledge entries touched this round: `corpus/knowledge/crash-channels-beyond-excepthook.md` (r97 audit section: the
pending-clear latch, the A2/A3 repairs, the CPython-3.14.8 interleaving as an observation) and
`corpus/knowledge/deadline-owned-reaping.md` (r97 fix section: reaping by planted identity, the output cap, the signal
exit). Both are committed at P1 and both cite rows this block lists. **Pointer check for the L1:** both entries cite
`census/round-97/records/shapes-r97.txt` and `census/round-97/records/c2-after.txt`, and `census/round-97/records/` is
**empty** at HEAD (`ls census/round-97/records/` → nothing). The after-receipts are the files the L1's after-arm run will
land, so these pointers resolve only once that commit exists; until then they are dangling under Q31/Q139.

Assimilation: none this round (no `merge/souji/` theme taken). considerthese: the lane has no `considerthese/` dir.

## 4. Findings that touch the two claims (for the L1's ledger)

These are the wave-artifact findings I produced; each is stated as the exact frozen sentence it bears on, with a
reproducer path. I record them here rather than as amendments — the L1 owns `plans/round-97.md`.

**F-1 (narrowing-grade, wording of a stated limit).** The C2 CLAIM paragraph says the r97 counter "reaps the T1
grandchild by argv identity (its absolute fixture path, verified at act time; it signals only processes it planted)". The
shipped code matches that sentence (`census/round-97/c2-setup-arms.py:255-338`: before-set snapshot of
`(pid, starttime, boot_id)`, then SIGKILL only argv-matching identities not in the set). What the sentence does *not*
say, and what the r97 control set cannot show, is that the number moves: `survivors=0` in every committed r97 receipt, and
the only forged probe aimed at it is not refused (`FORGERY GD … refused=no`, `C2-FORGERY-CTL-SUMMARY forgeries=4
refused=3`). Reproducer: `.ufo/waves/round-97/w1/R97Scribe/receipts/t1-arm-noreap.txt` (mutant: `survivors=1`) versus
`receipts/t1-arm-r97probe.txt` (committed counter: `survivors=0`, `planted-killed 1`). This is the "shown able to fail"
witness the C2 claim's counted quantity lacks; §1 M2 states the limit.

**F-2 (FALSIFIES-WORDING — narrowing-grade; the A8 leg of the C2 CLAIM paragraph).** The frozen C2 CLAIM paragraph
(`census/round-97/preregistration.txt:96`) says the r97 counter "reaps the T1 grandchild by argv identity (the arm's
absolute fixture path, verified at act time; it signals only processes it planted) and prints a `survivors=<n>` count per
T1 run, **recording a signal exit (-15) distinctly (A8)**." The r97 counter does **not** record a signal exit
distinctly: it renders `exit=-15` in the same `exit=` field with no mark, which is byte-for-byte the rendering the r96
counter already produced — and the same preregistration describes the r96 behaviour as the defect ("a signal exit (-15) is
printed inside the same `exit=` field with no mark to tell it from a verdict exit (A8)", `preregistration.txt:92`). Exact
sentences:

> "a signal exit (-15) is printed inside the same `exit=` field with no mark to tell it from a verdict exit (A8)"
> (`census/round-97/preregistration.txt:92`, describing r96)

> "recording a signal exit (-15) distinctly (A8)"
> (`census/round-97/preregistration.txt:96`, claimed of the r97 counter)

Reproducer (both runs against a probe that SIGTERMs itself, T1 arm only, trimmed scratch copies of the committed
counters; the lane files are untouched):
`.ufo/waves/round-97/w1/R97Scribe/receipts/signal-exit-r96-vs-r97.txt`

```
r96 counter:  ARM T1 exit=-15 want=2 line=no conform=no
r97 counter:  ARM T1 exit=-15 want=2 line=no conform=no survivors=0
```

The only difference is the appended survivors suffix; the rc-handling block is byte-identical between the two counters
and the r97 counter has no `rc < 0` branch. `grep -rn 'exit=signal' census/round-97/` returns one hit — the counter's
own docstring at `census/round-97/c2-setup-arms.py:7` (`receipts/grep-exit-signal.txt`), i.e. the promised marker exists
only in the prose that promises it. **Scope of the finding (stated so the L1 can cut it the right way):** the *reaping* half
of the same sentence is true and I verified it (see F-1 and §1 M2); the *signal-exit* half is not implemented and the
r97 counter's rendering is indistinguishable from the r96 counter's. The corpus entry already states the true behaviour
(`corpus/knowledge/deadline-owned-reaping.md:51`: "prints as `exit=-15` in the ARM line (A8): it never reads as a verdict
exit"), so the corpus does not carry the false claim — only the counter docstring and the preregistration sentence do.
The counted quantity is untouched: `conform=20` and `survivors=0` are unaffected, and no number moves.

**F-3 (corpus shape, gate-breaking).** `corpus/SOURCES.md:311` (S372) has 7 of the contract's 11 cells; the lane's own
census now exits 1 (`E01 S372 fields=7`). Reproducer: `receipts/sources-validate.txt` (HEAD) and
`receipts/sources-validate-base.txt` (lane base, no E01). §1 M3.

**F-6 (wording-precise; the A2 mechanism is named as a *reorder* but implemented as a *removal*).** The C1 CLAIM
paragraph (`census/round-97/preregistration.txt:34-35`) says the r97 search "reorders the excepthook/thread crash
channels to write before the traceback print (A2)". The bytes do something different: the r97 hook's
`_souji_excepthook`/`_souji_thread` no longer call `sys.__excepthook__`/`threading.__excepthook__` at all
(`census/round-97/c1-survivor-search.py:134-136,147-150`; the r96 versions did, at
`census/round-96/c1-survivor-search.py:118,131`), and `_souji_crash` ends the process with `os._exit(70)`
(`:109,130`), so **no traceback print occurs on those channels at all**. Live, same raising script under each hook
(`receipts/a2-traceback-order.txt`):

```
r96 hook:  Traceback (most recent call last): … RuntimeError: boom-excepthook-channel
            SOUJI-R96-CRASH uncaught RuntimeError          (exit 70)
r97 hook:  SOUJI-R97-CRASH uncaught RuntimeError          (exit 70)   <- 0 "Traceback" lines
```

So the marker is not "written before the traceback print" — the print is gone. The claim's stated *effect* (the blocking
TextIOWrapper print cannot hold the exit hostage) is achieved, and more strongly than described; no number moves and
the r97 hook still satisfies every CHECK reason (`receipts/a2-traceback-present.txt`). I record it as wording-precise,
not as a falsification of the sentence's effect, and flag one consequence the lane may want to state: **the r97 sentinel
no longer prints a traceback on the excepthook or thread channel**, so a counter that dies there now reports only the
channel marker, with no Python traceback to diagnose it. The in-code comment at
`census/round-97/c1-survivor-search.py:134-135` says "crash FIRST on the raw write, **then print**" — the "then print"
describes a print that cannot occur, because the same function exits the process. The atexit/unraisable channel is
unaffected and still prints first (`_souji_unraisable`, `:139-145`, unchanged from r96), which is consistent with the
claim naming only the excepthook/thread channels.

**F-4 (evidence-pointer, both knowledge entries).** `corpus/knowledge/crash-channels-beyond-excepthook.md:134` and
`corpus/knowledge/deadline-owned-reaping.md:46` cite `census/round-97/records/shapes-r97.txt` and
`census/round-97/records/c2-after.txt`; `census/round-97/records/` is empty at HEAD. Resolves when the after-arm receipt
commit lands; until then Q31's LG-DANGLING-PTR class applies to both entries.

**F-5 (wave-evidence durability, carried from the r96 spot-check §7.5).** Every r96 artifact this lesson cites as
evidence for M1/M2 (`plans/round-96.md` A1/A4, `R96Sentinel.md` F-4, `R96Scribe/reapcheck.out`) lives under
`.ufo/waves/round-96/`, which the lane `.gitignore:1` excludes (`git check-ignore -v` confirms; `git ls-files
.ufo/waves/round-96` → 0 files). The r97 plan A0.3 commits a byte-exact capture into `census/round-97/wave-evidence/`;
that capture does not exist yet (`ls census/round-97/wave-evidence` → no such directory), so the M1/M2 evidence
pointers above are, today, on-disk-only. My own receipts under this seat's directory have the same property until the
L1's capture step runs.

**F-7 (consequence of F-6, for the L1 to state or dismiss).** Because the r97 sentinel no longer prints a traceback on
the excepthook/thread channels, a counter that dies on either channel now yields a single `SOUJI-R97-CRASH <channel>`
line and exit 70, with no Python traceback to diagnose the failure. The r96 sentinel printed both. This is a diagnostic
regression traded for the A2 fix; the preregistration describes the trade as a *reorder*, so a reader of the frozen text
would expect the traceback to still be there.

## 5. FALSIFIES-WORDING

**One wording falsification: the A8 leg of the C2 CLAIM paragraph** (F-2 above, narrowing-grade). The frozen sentence
"recording a signal exit (-15) distinctly (A8)" (`census/round-97/preregistration.txt:96`) is not borne out by the
committed bytes: the r97 counter renders a signal exit as `exit=-15` in the same `exit=` field with no mark — byte-identical
to the r96 counter's rendering, which the same preregistration names as the defect (`:92`). Reproducer:
`.ufo/waves/round-97/w1/R97Scribe/receipts/signal-exit-r96-vs-r97.txt`. The reaping half of the same sentence is
verified true (§4 F-1, §1 M2), the counted quantity is untouched, and no number moves.

**No FALSIFIES-NUMBER.** No number in either claim moves under any artifact I produced.

**C1's A2 wording is imprecise but its effect holds** (F-6): the frozen sentence "reorders the excepthook/thread crash
channels to write before the traceback print (A2)" describes a *reorder*, while the bytes *remove* the traceback print
from those channels entirely (the r97 hook calls neither `sys.__excepthook__` nor `threading.__excepthook__`, and
`_souji_crash` ends the process with `os._exit(70)`). The claimed effect — the blocking TextIOWrapper print cannot hold
the exit hostage — is achieved, indeed more strongly than described, and every CHECK reason still passes. I record this
as wording-precise rather than as a falsification of the sentence's effect, and flag the diagnostic consequence (F-7: the
r97 sentinel no longer prints a traceback on those two channels) for the L1 to state or dismiss. Reproducer:
`.ufo/waves/round-97/w1/R97Scribe/receipts/a2-traceback-order.txt`.

- C1: every number I re-derived matches the frozen control receipts — `shapes=14 mismatched=0` for the r97 hook
  (`receipts/shapes-r97-requal.txt` vs `census/round-97/controls/shapes-r97.txt`), `mismatched=2` with x1/x2 at `hooked=1`
  for the r96 hook (`receipts/shapes-r96-requal.txt` vs `controls/shapes-r96.txt`), `mismatched=2` with t1/t4 at `hooked=70`
  for the r95 hook (`receipts/shapes-r95-requal.txt` vs `controls/shapes-r95.txt`). The two x1/x2 shapes are exactly the
  r96 trade and the r97 latch closes it, as claimed. The A3 leg is in the bytes as claimed (the no-free-tool-id fallback
  restores fd 2's blocking mode, `census/round-97/c1-survivor-search.py:233`); the A2 leg's *effect* holds as claimed
  (F-6 above) while its named mechanism does not.
- C2: the escape is real and the counter's reap closes it — `survivors=0`, `planted-killed 1` on the committed counter
  (`receipts/t1-arm-r97probe.txt`), `survivors=1` with the reap removed (`receipts/t1-arm-noreap.txt`). The probe's
  output cap refuses over-cap output with exit 2 (`receipts/probe-maxoutput.txt`), as claimed.
- The other §4 findings (F-1 coverage, F-3 row shape, F-4 pointers, F-5 wave-evidence durability) are wording/label/shape/
  pointer findings about the corpus, the docstrings and the control set's *coverage* — not falsifications of a claim's
  stated wording or numbers.

**On Amendment 59:** F-2 is a wave artifact that falsifies a stated wording of the C2 CLAIM paragraph, so under the
amendment the L1 records it as a narrowing amendment in `plans/round-97.md` (never silently). The fix is cheap and is the
L1's to choose: emit the promised `exit=signal` marker, or (my recommendation, matching the corpus) drop the A8 claim from
the preregistration sentence and from the counter docstring, and let the corpus's `exit=-15` wording stand.

## 6. Report

`.ufo/waves/round-97/w1/R97Scribe.md`
