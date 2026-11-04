# Proposed append-only r58 errata (integration authority: SoujiR58)

These are delivery text, not applied production corrections. Preserve all historical counter, source-capture, receipt, report and registry bytes.

## ERRATUM-R58-KNOWLEDGE-R57-QUOTE2

Supersedes only the phrase **“Second located quote (17 words)”** at `corpus/knowledge/inline-html-comment-visibility-r57.md:16-17`: its located S279 quote has **19 whitespace-separated words**, not 17. The quoted text is unchanged:

> the text must not start with the string " > ", nor start with the string " -> ".

This extends `ERRATUM-R57-3` in `corpus/lessons/round-57.md:106-110` to the knowledge-entry mention omitted from that correction's named targets. The r57 non-author spot-check independently confirms 19 (`corpus/lessons/round-57-verifier-spotcheck.md:135,186-190`). It does not change the ≤25-word admission decision, validate the counter's Markdown grammar, or repair its second-opener/code-span/escape/link/TAB/lazy-paragraph defects. Original S279 cells, `census/round-57/records/source-quotes.txt`, captures and knowledge-entry historical text remain as filed; append this note rather than replacing them.

## ERRATUM-R58-REPORT-R57-FINAL-REGISTRY

Supersedes only the **“202 → 205 registry rows (2 admitted, 1 rejected)”** tally under `## Trend verdicts` in the fleet report `.ufo/reports/round-57/souji.md:153-155` (report final lane revision `dcbcd05c467508f00a04f35bf544d0d83f745e73`). **202 → 205** describes the intermediate sources commit `805482129d022b13db672654f5478952def607a6`; the final r57 registry is **202 → 207**. The five new rows are S279/S280/S282/S283 (tier A, including two superseding correction rows) and S281 (tier B, rejected). The same report's `## Sources & frontier`, lines 130-137, already records 207; the outside spot-check confirms the three snapshots (`corpus/lessons/round-57-verifier-spotcheck.md:148-153`). Expansion remains **unchanged**: no new uncovered coverage-map ground or frontier promotion follows from this tally correction. Append this erratum in an authorized r58 record; do not rewrite the historical fleet report or its evidence.

## Supplemental citation correction (outside the two C1 assertions)

For the r57 report's C2 before measured-commit cell (`.ufo/reports/round-57/souji.md:78`), the abbreviated `d749f7ee…` denotes `d749f7ee081ec1b382b2f92577eb22bfba1c7761`. This is a citation expansion only, not a new measurement and not an r58 C1 counter assertion. It may be appended by the integration owner; no fleet report edit is authorized to this seat.
