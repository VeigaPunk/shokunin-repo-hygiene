# AttackE14b — adversarial falsification of the W1 finding for C1 item E14b

Seat: SwarmReviewer14 (r34 w2). Lane `/home/vgpnk/Projects/shokunin/souji-shokunin`; base `9c76c7222a8abff027af42e37f0d160d52526bba`; frozen list/prereg re-pin `2b0171e2071fdc9c16a69bed12b0d040e574d8c8`; lane HEAD at read time `51acb5fb6fa38a6b593b3badb674cec559d7eb2c`. Read-only: no lane file outside `.ufo/waves/round-34/w2/` was written; scratch `/fast/scratch/hyaku/souji-r34/AttackE14b/` (peak 2 private clones ≈ 17 MB, removed).

## Status

CONFIRMED-WITH-ADDITION. W1's mechanism claim for E14b is real and correctly diagnosed: sha256sum's stdin marker makes the run print `<digest>  -`, so the frozen `$`-anchored predicate can never match, at any revision. The do-nothing MISMATCH verdict is correct, deterministic, and not load-sensitive (not an artifact). However, W1 drafted no correction and its table's "none" leaves the item's reachability open. This seat **executed** an honest, rule-conforming repair route through the frozen counter bytes: an **argv correction** (tight-pipe `cut`) with cause `315422ba9970f03c27f8a9184446783b7fcdf0a7` — the unique writer of the row's line — yields **AGREE at base and at tip**. Two adjacent routes a drafter would plausibly try are reproduced dead ends: `same` argv → `BAD-CAUSE` (value drift unsatisfiable), spaced-pipe argv → `BAD-ROW(cells=9)` (restatement row parser splits cells on the literal `" | "`). No counter or frozen-artifact modification is proposed; the defect is in the frozen row's notation binding, and the frozen repair machinery already admits the fix.

## Evidence

Frozen inputs (all read at the re-pin `2b0171e2` unless stated):

- Item row: `census/round-34/c1-items.tsv:55` — `E14b | SCORECARD.md:67 | 0 | ^09bb8e0d9906b0dfef44775a9e5cd7c8f8a27d9bcdf559e2d371a3ef7ff1ed6d$ | tools/souji-size-census.py | {REV} | bash -c "git show 778747eb671f8e85ef5387bc3d7023337b30467c:tools/souji-size-census.py | sha256sum"`. Column contract: `census/round-34/c1-items.tsv:16-19` ("files … a restatement's cause commit must touch one"; `{REV}` = measured revision).
- Counter bytes verified: working tree `census/round-34/c1-counter.py` sha256 `1ad8c86c9d78b79f095661850ca9883994a5d5a9d5ee629cb69e26dcd6ff9a20` == `git show 2b0171e2:census/round-34/c1-counter.py` (executed).
- SCORECARD.md is byte-identical base→list-rev (`git diff --stat 9c76c72 2b0171e2 -- SCORECARD.md` empty, executed), so the item's `where` line 67 is stable; base is an ancestor of list-rev (`git merge-base --is-ancestor`, executed).
- Committed do-nothing record: `census/round-34/records/controls-c1-do-nothing.txt:39` — `ITEM E14b MISMATCH original rc=0 expect_exit=0 predicate fails last=09bb8e0d…ed6d - load=11.10`. W1 reruns concur: `.ufo/waves/round-34/w1/deliver-c1-do-nothing-check.txt:44`, `deliver-q76-honoring.txt:48`.
- W1 claim under test: `.ufo/waves/round-34/w1/SwarmExecutor13.md:32` ("predicate/notation binding — E14b (sha256sum's trailing ` -`)") and table row `:54` (stated `0; ^09bb8e0d…ed6d$`, observed `0; 09bb8e0d…ed6d -`, prior correction row: none).
- Rules: `census/round-34/preregistration.txt:47-57` (AGREE iff exit+predicate; restatement cells; cause executed: value drift "holds at the cause's parent, fails at the cause"; argv correction "the cause wrote the row and the row's argv already failed at the cause"; Q76 prior binding; append-only), `:138-147` (amendment A1(a) corrected argv is evaluated at --rev; A1(b) corrected argv must name a row file; A1(c) restated statement must equal the run's collapsed LAST digit-bearing line).

Executed probes (commands and outputs):

1. Probe reproduction, lane cwd:
   ```
   $ bash -c "git show 778747eb671f8e85ef5387bc3d7023337b30467c:tools/souji-size-census.py | sha256sum"
   09bb8e0d9906b0dfef44775a9e5cd7c8f8a27d9bcdf559e2d371a3ef7ff1ed6d  -
   rc=0
   ```
2. Predicate replay with the frozen bytes' own `frozen_pred` (`c1-counter.py:163-164`: bare regex vs collapsed last digit-bearing line; `collapse` :72-73):
   - `frozen_pred("^09bb8e0d…ed6d$", ["09bb8e0d…ed6d  -"], …)` → `(False, 'predicate fails')`
   - collapsed observed line → `'09bb8e0d…ed6d -'` (the ` -` survives collapse; `$` cannot match)
   - `frozen_pred(<same pred>, ["09bb8e0d…ed6d"], …)` → `(True, 'predicate holds')`
3. Cause discovery (executed): full line 67 text (1361 chars, the r24 "C1 F2 debris census" row) occurs exactly once in base SCORECARD.md; `git log --format=%H -S <that text> -- SCORECARD.md` returns exactly one commit, `315422ba9970f03c27f8a9184446783b7fcdf0a7` ("round-24: final — post-wave-2 repairs …"); its parent `d3666c3ef291c0c6c7827ffcfb58471c4b8d54f7` lacks the text, the commit contains it → it is the unique writer of the row's line (the counter's argv-correction cause test, `c1-counter.py:293-298`). It also touches `tools/souji-size-census.py` (satisfying even the stricter TSV-header reading, line 16) and is an ancestor of list-rev (executed). Note: the tool digest at the cause is `c5690681…` ≠ the pinned blob's `09bb8e0d…` — the cause post-dates the r24 measurement; inert for E14b because the argv pins blob `778747eb` explicitly.
4. Q76 prior-binding scan (executed, base blobs): SCORECARD.md lines containing `souji-size-census`/`09bb8e0d`/`SCORECARD.md:67…` are :41, :67 (the row itself), :92 (an r25-era row quoting the tool sha), :174, :398 (`L33` binding cell `:174`, not `:67`). Zero hits in SKILL.md. No prior correction row binds cell `:67` — concurs with W1 finding 3 (`SwarmExecutor13.md:30`).
5. Route executions — `judge()`/`load_restatements` from the frozen counter bytes, on synthetic SCORECARD text = list-rev bytes + appended `### Round 34 registry restatements` + one row (append-only shape, counter `:374-378`):
   - **Route A, `same` argv** quoting the observed line `09bb8e0d…ed6d -`, cause `315422ba`:
     `('E14b', False, 'BAD-CAUSE(original at parent=False at cause=False; need True/False)', 'restated')` (`c1-counter.py:291`). Executed proof that value drift is unsatisfiable: the frozen argv pins blob `778747eb` (no `{REV}` in it), so its output — and hence the original verdict — is identical at the parent, the cause, base and tip; the original predicate holds at no revision.
   - **Route B, corrected argv written with spaced pipes** `` `bash -c "git show 778747eb…:tools/souji-size-census.py | sha256sum | cut -d' ' -f1"` ``: parsed into **9 cells** by `load_restatements` (`c1-counter.py:105` splits on the literal `" | "`; the argv cell shatters at both spaced pipes) → `('E14b', False, 'BAD-ROW(cells=9)', 'restated')` (`:254`).
   - **Route C, corrected argv with tight pipes** (no `" | "` sequence anywhere in the row): **AGREE at base and at tip**:
     ```
     ROUTE C at base: ('E14b', True, "rc=0 expect_exit=0 statement is the run's last digit-bearing line last=09bb8e0d9906b0dfef44775a9e5cd7c8f8a27d9bcdf559e2d371a3ef7ff1ed6d load=1.24", 'restated')
     ROUTE C at tip : ('E14b', True, "…same… load=1.30", 'restated')
     ```

## Findings

1. **The W1 mechanism claim is real (executed, not inferred).** The observed last digit-bearing line is `09bb8e0d…ed6d -` (sha256sum's two-space stdin marker, `probe 1`), and the frozen bare-regex predicate is anchored `$` (`c1-items.tsv:55`), matched via `re.search` against the collapsed line (`c1-counter.py:163-164`). No benign alternate explanation exists: exit is 0 as stated, output is revision-independent, load irrelevant (contrast W1's load-sensitive E32, `SwarmExecutor13.md:33`). The MISMATCH at base is the frozen, required do-nothing behavior — a calibration surface, not a round defect.
2. **An honest rule-conforming repair route exists and was executed (W1 left it undrafted).** Exact admissible row for `### Round 34 registry restatements` (executed AGREE at base and tip, route C):
   ```
   | E14b | SCORECARD.md:67 | restated | 0 | `bash -c "git show 778747eb671f8e85ef5387bc3d7023337b30467c:tools/souji-size-census.py|sha256sum|cut -d' ' -f1"` | `09bb8e0d9906b0dfef44775a9e5cd7c8f8a27d9bcdf559e2d371a3ef7ff1ed6d` | 315422ba9970f03c27f8a9184446783b7fcdf0a7 | notation fix: sha256sum prints '<digest>  -' on stdin so the frozen ^digest$ anchor cannot match; tight-pipe cut emits the bare digest the row already quotes |
   ```
   Rule conformance, clause by clause: corrected argv names the row's own script (`souji-size-census.py`, `c1-counter.py:267-268`); exit 0 equals the run's rc; restated statement equals the run's collapsed LAST digit-bearing line (A1c, `:311-313`); cause `315422ba` is full-40, an ancestor of list-rev, provably wrote the row's line (`:293-298`), and the row's own argv already fails at the cause (`:299-300` — trivially, at every revision); the cause even touches the item's `files` entry; SCORECARD.md stays append-only (`:374-375`).
3. **Two reproduced traps for the drafter/L1.** (a) A `same`-argv row — the natural "quote what the run prints" repair — is always rejected: `BAD-CAUSE(original at parent=False at cause=False)` (route A), because value drift presupposes the original held somewhere, which it never did for E14b. (b) Any corrected argv containing the character sequence `" | "` (the conventional spaced pipeline) destroys the row at parse time: `BAD-ROW(cells=9)` (route B). The delivered row must keep every pipe tight (or use a space-free filter, e.g. `|sha256sum|awk '{print $1}'`). Cross-seat risk: the same trap applies to every argv-correction row of the 25-item batch — each delivered row should be re-parsed through `load_restatements` before landing.
4. **Rule-semantics note (no repair implied).** For notation-bound rows like E14b, the argv-correction cause test "the row's own argv already failed at the cause" (`:299-300`) is trivially satisfiable, so its evidential force reduces to the writer test (`:297-298`) — which the counter does execute. This matches the frozen prereg wording (`preregistration.txt:52-53`) and mirrors W1's own honest argv correction for E05 (`.ufo/waves/round-34/w1/deliver-c1-E05.md:70`), so it is reported as semantics, not defect.
5. **Scope check.** The route touches only SCORECARD.md (C1 namespace), keeping G5's C1/C2 per-commit disjointness intact; no tools/ or pinned bytes are involved (G6's `e6a984b1…` digest unaffected).

## Attack log

1. Read preregistration (`census/round-34/preregistration.txt`), frozen item row (`c1-items.tsv:55`), committed do-nothing record, W1 classification + reruns; verified counter working-tree bytes == `2b0171e2` blob (sha256 above).
2. Reproduced the probe verbatim (output `09bb8e0d…ed6d  -`, rc 0); replayed `frozen_pred` from the frozen bytes on the exact line (False) and on the bare digest (True).
3. Verified geometry: SCORECARD.md/SKILL.md byte-identical base→list-rev; base ancestor of list-rev; line-67 text unique in base.
4. Discovered and validated the unique cause `315422ba` (`-S` + parent/cause membership + touched-files + ancestry); recorded the tool digest at cause vs the pinned blob.
5. Q76 scan of base SCORECARD/SKILL: no prior row binds cell `:67`.
6. Executed `judge()` route A (`same` → BAD-CAUSE), route B (spaced pipes → BAD-ROW(cells=9)), route C (tight pipes → AGREE at base and tip) on synthetic append-only SCORECARD text.
7. Removed scratch (`/fast/scratch/hyaku/souji-r34/AttackE14b/` probe work dir); no lane file outside `w2/` written; no tool installed or upgraded.

## Deliveries

- `.ufo/waves/round-34/w2/AttackE14b.md` — this report.
- `.ufo/waves/round-34/w2/SwarmReviewer14.md` — scoped seat findings (same verdict, condensed evidence).
- For the L1: the executed rule-conforming E14b restatement row (finding 2) plus the two transcription traps (finding 3) for the whole 25-row batch.

Verification gaps (labeled): route executions ran `judge()`/`load_restatements` from the frozen bytes on synthetic SCORECARD text rather than a committed landing commit — the counter's `main()` append-only and full-60 target path were not re-run with the row landed (bounded-probe contract, no lane mutation). The `holds`-at-parent/`holds`-at-cause values quoted in route A are the counter's own executed outputs (embedded in the `BAD-CAUSE` detail), not hand readings.
