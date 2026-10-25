# ExecReportAssemble — round 26 wave 1 report

## Status

STATUS: PASS — the assembler is written and exercised end to end: it renders the six canonical report sections plus exactly one `## SHONEN` heading from the prereg, receipts, lesson, LOG, SCORECARD and results json; `--check` passes on the rendered draft and rejects every mutation arm; absent data renders as `RECEIPT-PENDING`. Two receipt-integrity defects were measured and are reported below rather than papered over.

## Evidence

- Delivery: `.ufo/waves/round-26/w1/report-assemble.py`, 818 lines, `sha256=cb9252bb9cf2f2c201cca0c97c3a98413f5a05a62a0a97a8889a9cad75b5f524`. Lane tip during assembly `166baa18f808071bc385187691713044a26bd663`. Rendered draft `.ufo/waves/round-26/w1/report-rendered.md` (122 lines, 14 `RECEIPT-PENDING` markers at this snapshot).
- Render, default (verification on), run from the lane root:
  `python3 -B .ufo/waves/round-26/w1/report-assemble.py`
  → `rendered=.../report-rendered.md results=absent receipts=9 verify=on sections=6 shonen=1 boxes=4 check=PASS problems=0` (rc 0).
- Structural check:
  `python3 -B .ufo/waves/round-26/w1/report-assemble.py --check`
  → `check=PASS file=.../report-rendered.md sections=6 shonen=1 boxes=4 problems=0` (rc 0).
- Negative arms (mutated copies under `/var/tmp/souji-r26-ExecReportAssemble/`):
  - `## SHONEN` renamed → `section '## SHONEN' occurs 0 times`, `exactly one '## SHONEN' heading is required`, `SHONEN box lines: 0 (want 4)`, rc 1.
  - second `## SHONEN` appended → `occurs 2 times`, rc 1.
  - `## Landed changes` body emptied + duplicate `## Trend verdicts` → `has an empty body`, `occurs 2 times`, `required sections are not in canonical order`, rc 1.
  - missing file → `cannot read draft`, rc 2.
- Results-json handling (synthetic fixtures only, under `/var/tmp`, never in the lane): `seats` list shape → `seats=3 returned=2 dead=1; roles=critic:1, executor:1, scribe:1` plus the dead-seat error text; `members` dict shape → `seats=2 returned=1 dead=1`; the real `w1/swarm-registry.json` (members without status) is refused as `not a results json` and rendered `RECEIPT-PENDING` instead of being misread.
- Receipt verification, frozen runner (`python3 -B tools/souji-receipt-run.py verify --root . <receipt>`): `c2-gate.tsv`, `c2-k4-after.tsv`, `c2-k4-base.tsv`, `c3-after.tsv` → `verify=ok` rc 0; `c1-before.tsv`, `c1-after.tsv`, `c2-before.tsv`, `c2-after.tsv`, `c3-before.tsv` → `RECEIPT-COUNTS-ABSENT` rc 2. Mechanism re-derived with the repository's own parser: `counts_line()` returns None for the c1/c2 stdout; `COUNTS_RE` does not match any of `markers=`, `grounded_f1=`, `registry_rows=`, `axis_check_tool=`.
- Writes: only `.ufo/waves/round-26/w1/report-assemble.py`, `.ufo/waves/round-26/w1/report-rendered.md` and this report. No git/jj mutation, no commit; scratch `/var/tmp/souji-r26-ExecReportAssemble/` removed. No tool installs or updates.

## Findings

1. **Five of nine round receipts cannot verify under the frozen runner — attack candidate, routed, not resolved here.** `census/round-26/records/c1-before.tsv:9`, `c1-after.tsv:9`, `c2-before.tsv:9`, `c2-after.tsv:9`, `c3-before.tsv:9` all fail `verify` with `RECEIPT-COUNTS-ABSENT`. Cause: `tools/souji-receipt-run.py:67` `COUNTS_RE` has no `markers=`/`grounded_f1=`/`registry_rows=`/`axis_check_tool=` alternative, so the counters' stdout can never satisfy `counts_line()` (`tools/souji-receipt-run.py:94`). The prereg claims the opposite: `.ufo/waves/round-26/preregistration.txt:65` and `:144` say `each verify=ok`, and `corpus/lessons/round-26.md:91` says `all verify=ok`. The draft renders per-receipt status in its verify column and prints a refusal summary, so the filed report will not repeat the claim unless the L1 does. `c3-after.tsv` verifies only incidentally, through its `cases=12 pass=12` line.

2. **After receipts predate the recorded landing tip.** `c1-after.tsv` rev `07f83e6`, `c2-after.tsv` rev `e0f8dcd`, `c3-after.tsv` rev `c594901`; lane tip at assembly `166baa1`. The frozen values are stated as landing-tip readings (`.ufo/waves/round-26/preregistration.txt:42` and the C2/C3 after lines), so each after receipt needs a re-run at the final tip or an explicit disclosure. The draft emits an `After-receipt rev lag` note naming exactly these three.

3. **No wave results json exists yet.** Neither `.ufo/waves/round-26/w1-results.json` nor `.ufo/waves/round-26/w1/results.json` is present; `.ufo/waves/round-26/w1/swarm-registry.json` declares 87 seats but no statuses. The draft renders `RECEIPT-PENDING` for seats/dead-seat/role-mix and states the registry count as declared-only. Re-run the assembler after the results file lands.

4. **LOG.md has no Round 26 entry at assembly.** Latest heading is `## 2026-10-25 — Round 25 honest stop` (`LOG.md:1723`); the draft marks the LOG row `RECEIPT-PENDING`. The L1 must land the Round 26 entry before filing or keep the pending row.

5. **The C1 byte-diff annex is not in any input.** `.ufo/waves/round-26/preregistration.txt` C1 names the byte-diff of the protected spans as the claim margin and `corpus/lessons/round-26.md` § Receipts calls it "byte-diff annex in the round report", but no receipt or lesson file holds it. The draft emits `RECEIPT-PENDING` rather than reconstructing a kill-rule annex it did not measure.

6. **Lesson wording vs receipt header for C3.** `corpus/lessons/round-26.md:89-91` places `c3-after.tsv` "at tip 0c92c2e", while the receipt header records `rev=c5949013f89fe0b8289bdb7050ab64a47e08c911` (the file was rewritten at `0c92c2e` without a new measurement). The assembler reports the header rev; the filed report should phrase it as "committed at 0c92c2e, measured at c594901".

7. **Design boundaries of the check.** `--check` enforces: the title line, each of the six required `##` sections exactly once and in canonical order, a non-empty body per section, exactly one `## SHONEN` heading (no `## SHONEN ...` variants), and exactly four SHONEN box lines. It deliberately does not fail on `RECEIPT-PENDING` (the contract allows data-pending sections) and does not judge claim truth. SHONEN lines fall back to `SHONEN.md`'s boxes with the historical pointer labelled as such and an `RECEIPT-PENDING r26 pointer` marker; a landed `.ufo/waves/round-26/w1/shonen-lines.md` with four box lines is used verbatim instead.
