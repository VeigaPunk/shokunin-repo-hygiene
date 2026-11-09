# R93Scribe — souji round 93 lesson draft (leaf seat, no subagents)

Lane: `souji-shokunin`, base `91c9bcb1041b18be154ca466ac3c047ac7862fe1`, instruments P1 `2c82d362`, controls P2 `0d6442cc`.
Seat dir: `.ufo/waves/round-93/w1/R93Scribe/` (receipts below). Scratch `/fast/scratch/hyaku/souji-r93/R93Scribe/` was
created, used and removed (verified). No commit, no git mutation (read-only `git rev-parse --show-toplevel` and
`git show 91c9bcb1…:corpus/SOURCES.md`). Tools installed: none.

## FALSIFIES-WORDING

1. **Sentence (search docstring, r93 kill rule, item 1):** "A harness exit 2, or an exit 1 whose only failing rows are
   `match=error` (the counter crashed, rc 2), is `errored`." Source: `census/round-93/c1-survivor-search.py` lines 4–7
   and `verdict()` lines 86–93.
   **Reproducer:** `.ufo/waves/round-93/w1/R93Scribe/fk1-import-crash-r93-harness.txt` and `fk1-verdict.txt`. FK1 = the
   r92 import-time crash (`raise RuntimeError` inserted after `census/round-87/c1-pointer-counter.py` line 127), run
   through the r93 harness on the r93 population: `SUMMARY rows=66 mismatches=10 accepted=0 refused_true=0 errors=56`,
   harness rc 1, ten `ROW ... match=no` rows (LD1, LD1b, LD1c, LD2, LD2b, LD3, LD4, LD4r, LD5, LD6) and 56
   `match=error`. `verdict()` on that run returns `yes` (killed). The crash is not rc 2 at all; it is rc 1 with
   counter-side markers absent, so the ledger rows read `got=-` and print `match=no`.
   **Consequence:** the r93 rule as worded in the prereg (exit 1 AND ≥1 `match=no`) is satisfied by a crashed counter.
   The prereg's "tighter than r84–r92" and the docstring's "crash is errored" are wider than the instrument. The same
   receipt pair for the r92 population is `.ufo/waves/round-92/w1/R92MutC1/harness-import-crash-r92.txt` (8 `match=no`,
   56 `match=error`); re-applying the r93 `verdict()` to it returns `yes` as well (no harness run; text re-scored).
   **C1's own sentences are not falsified by this** (the two targets are not crashes; see attribution below). The
   wording that is falsified is the crash-exclusion reading. Recommended amendment: narrow the kill-rule sentence in
   `plans/round-93.md` to "killed = exit 1 with ≥1 `match=no`; a counter crash that prints `match=no` ledger rows is
   also killed (FK1)".

Checks that did NOT falsify anything (NO-FALSIFICATION for these): the C1 controls (`census/round-93/controls/c1-control-r92-population.txt`,
`killed=0 survived=2`), the C2 r92-fixture control (`c2-control-r92-fixture-probe.txt`, `rejected=5`, EXIT 1), the S356
quote and capture sha (below), and the SOURCES diff (below). I did not audit the C2 reference function's independence
beyond a grep (it contains no `decode`/`codecs` call; the only match in lines 367–420 is the comment); reviewers own
that falsification.

## Supporting receipts (C1 attribution, re-run by this seat on the committed bytes)

`.ufo/waves/round-93/w1/R93Scribe/c1-attribution-r93.txt`: the r93 harness with each target's exact edit
(`h-ok-admits-one`: line 552 `== len(pop)` -> `>= len(pop) - 1`; `a491c22-<-to-<=`: line 491 `len(r) < 3` -> `len(r) <= 3`):
- `h-ok-admits-one`: rc 1, match=no ids = `['LD5']`, match=error 0, verdict yes.
- `a491c22-<-to-<=`: rc 1, match=no ids = `['LD6']`, match=error 0, verdict yes.
So each kill is carried by its own binding row, not by a crash. `census/round-93/records/c1-after.txt` prints
`killed=yes rc=1` for both but does not name the row; this file does.

## Mistakes (draft `## Mistakes` block for `corpus/lessons/round-93.md`)

| # | class | evidence pointer | captured-by | fix (able-to-fail status) |
|---|---|---|---|---|
| M1 | a kill rule that scores a non-zero exit as killed (r92): a counter crash is a kill. The r93 rule is narrower but still kills the crash class | r92: `.ufo/waves/round-92/w1/R92MutC1.md` §1a–1c, `plans/round-92.md` A3. r93 rule: `census/round-93/c1-survivor-search.py` lines 86–93. Crash still killed: `.ufo/waves/round-93/w1/R93Scribe/fk1-verdict.txt` | the r92 round's own mutation-tester (R92MutC1, pre-close) for r92; R93Scribe FK1 reproducer for r93 | r93: killed only on exit 1 + `match=no`. **Not shown able to fail for crashes**: FK1 scores `yes`. Open fix: a ledger/forge row counts as a verdict only when the counter printed its marker; FK1 prints none, so FK1 must score `errored` before any crash wording is written. |
| M2 | a faithfulness-only fixture (KFF18: head is SOME prefix, tail SOME suffix) passes a boundary-respecting cut that is in the wrong place: three one-edit forgeries (F5 `surrogatepass`, F6 `len(...) >= 1`, F7 head cut forward) pass 20/20 | `.ufo/waves/round-92/w1/R92MutC2.md` (forgery table; D/E analysis); r92 control `census/round-93/controls/c2-control-r92-fixture-probe.txt` (F5–F7 `rejected=no`, `rejected=5` EXIT 1) | R92MutC2 (r92 wave, before close); routed as `corpus/lessons/round-92-verifier-spotcheck.md` §7 item 1 | fixed in r93 by KFF19 (excerpt EQUAL to the reference cell, 14,586 payloads) and KFF20. Able to fail: the r92 control refuses 5/8. After: `census/round-93/records/c2-forgery-after.txt` refuses 8/8; F5, F6, F7 each fail only `KFF19`. Limit: finite sweep (prereg C2 limit i). |
| M3 | an unfiled source row's anchor edited in place (S355 `id="G7404"` -> `id="G27506"` in round 92; `G7404` wraps the §3.9 heading, not Table 3-7) | `corpus/lessons/round-92-verifier-spotcheck.md` §1(a), §7 item 4; `plans/round-92.md` A4; `corpus/SOURCES.md` line 294 | R92ScoutSources (re-open of the live page); the r92 non-author spot-check §1(a) | r93 appends S356 only: `git show 91c9bcb1041b18be154ca466ac3c047ac7862fe1:corpus/SOURCES.md \| diff - corpus/SOURCES.md` prints one `>` line (S356, line 295) and no `<` line. Able to fail: the r92 `git diff` showed the `-`/`+` S355 pair (spot-check §1(a)), so the same diff form detects an in-place edit. The rule text (routed item 4) was not located: `corpus/CORPUS.md` does not exist in the lane, so I did not verify the rule wording. |
| M4 | the L1 started three controls as background jobs in one shell call (`&` ... `wait`); the shell tool panicked (`JoinHandle polled after completion`) and two controls were lost | `plans/round-93.md` A0.2 (L1 account, present, so "L1 account pending" does not apply); `census/round-93/controls/` holds all three receipts; the two C2 controls were re-run sequentially | the L1's own disclosure (A0.2) after the loss; no check caught it earlier | controls re-run one at a time on the committed bytes; each receipt ends in `EXIT=`. Check: `grep -L '^EXIT=' census/round-93/controls/*.txt` lists only `prefreeze-feasibility-note.txt` (a note, not a receipt). Able to fail: the same grep on a synthetic truncated receipt lists it (run in scratch, deleted). |
| M5 | the r93 fix for M1 wrote a wider sentence than its test (the docstring says "crash = errored"; FK1 says "killed"): the M4 class of r92, now in the fix itself | `census/round-93/c1-survivor-search.py` lines 4–7 vs `.ufo/waves/round-93/w1/R93Scribe/fk1-verdict.txt` | R93Scribe (this seat), by running the reproducer the docstring's claim needed | recorded as FALSIFIES-WORDING above; the docstring must be narrowed or FK1 made `errored`. |

## Draft QUALITY criterion (Q169; next free number after Q168 in `corpus/QUALITY.md`)

| Q169 | Extends Q166 and Q165 (they stand): an excerpt's cut POSITION is pinned by an exact check against an independent reference cut, not by a faithfulness property alone. "The head is a prefix and the tail a suffix of the full rendering" holds for every boundary-respecting cut, so a forgery that moves a cut too far, not far enough, or across ill-formed bytes passes it. Every such property is paired with an exact-equality case over a boundary-class sweep whose reference is written from the specification's algorithm and shares no code with the tool (no call to the library routine the tool uses). The measure is the count of one-edit forgeries that move the cut only and are refused: a fixture that refuses none of them is not a position check. | every fixture, sweep or battery that asserts where a window, excerpt or chunk boundary falls | `python3 -B census/round-93/c2-forgery-probe.py --fixture tests/fixtures/r93-k4-flagfail.py --tool tools/souji-record-agreement.py --before census/round-92/controls/c2-before-tool.py --work <empty>` must print `FORGERY-SUMMARY forgeries=8 rejected=8 positive=pass`; the same probe with `--fixture tests/fixtures/r92-k4-flagfail.py` must print `rejected=5` and exit 1 (the able-to-fail control) | `census/round-93/records/c2-forgery-after.txt` (F5, F6, F7 each `failed=KFF19`); `census/round-93/controls/c2-control-r92-fixture-probe.txt`; `corpus/lessons/round-93.md` M2; `corpus/knowledge/utf8-cut-position-reference.md` |

Note for the L1: the Q169 counting command was not re-run by this seat (the receipts are the r93 after and control runs).

## Draft `## Gate` block for S356

- **S356 — WHATWG Encoding Standard (Living Standard, Last Updated 19 October 2026), §8.1.1 UTF-8 decoder**
  (https://encoding.spec.whatwg.org/#utf-8-decoder; access date 2026-11-09; per the S356 row, `corpus/SOURCES.md`
  line 295: HTTP 200, 591022 bytes; this seat did not re-fetch). Capture `census/round-93/srcs/encoding.html`,
  sha256 `e1421f1791b202717883c452a6267129ce5fb3ca13652e5022a2b6d2a11fc262` (re-checked by this seat with
  `sha256sum`: match). Locator: `id="utf-8-decoder"`, §8.1.1.
- **Quote (11 words):** "If byte is 0xE0, then set UTF-8 lower boundary to 0xA0." One occurrence in the
  whitespace-normalized tag-stripped text `census/round-93/srcs/encoding.txt` (re-counted by this seat: `1`, normalized
  offset 62998). The companion "If byte is 0xED, then set UTF-8 upper boundary to 0x9F." occurs once at offset 63054.
- **Reject sample:** [SLOT — R93ScoutSources to fill; not drafted by R93Scribe].

## Receipts in this seat dir

- `fk1-import-crash-r93-harness.txt`, `fk1-verdict.txt` — FK1 on the r93 harness (rc 1; killed by `verdict()`).
- `h-ok-admits-one-r93-harness.txt`, `a491c22-lt-to-lteq-r93-harness.txt`, `c1-attribution-r93.txt` — row attribution.
- `SOURCES.base.md` — the lane's `corpus/SOURCES.md` at the lane base (text copy, for the diff in M3).

## Process notes (this seat)

- One mistake in this seat's own run: my first FK1 call printed the harness result, then raised `TypeError` in my
  verdict print (I passed bytes to a str check). The receipt was saved before the error; `fk1-verdict.txt` was recomputed
  from the saved file. The reported numbers come from the saved receipts.
- Scratch was deleted (`shutil.rmtree`; verified absent). No file was written outside the seat dir and this report.
- No fleet-root leftovers for round 93 (checked; the M5-r92 misroot class did not recur).
