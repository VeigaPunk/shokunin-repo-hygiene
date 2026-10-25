## Status
STATUS: PASS — authored the two requested exemption rows as a draft; no lane source file changed.

## Evidence
- `read corpus/pointer-exemptions.tsv` at `e78ac7c4837b81b634db4a927605a751a7f006ba`: exactly 4 existing rows; every row has two tab-separated fields and paths are ordered lexicographically.
- `read .ufo/waves/round-27/w1/exemptions-add.tsv`: two rows in the same path order and two-field format; reasons have no tabs/newlines and are <=200 chars (row 1: 73; row 2: 196). Both paths are unique relative to the four existing paths.
- `corpus/QUALITY.md:143` (Q59): “a corpus/knowledge/registry change is a coverage surface” — in the sentence this is a surface-class example, not a citation.
- `corpus/QUALITY.md:141` (Q57) invokes `bash tests/fixtures/r25-q57-check.sh` with `corpus/lessons/round-24.md:232:S118` as a SITE argument. `tests/fixtures/r25-q57-check.sh:3-4,24-26` confirms it consumes SITE arguments as `file:line` or `file:line:ID`; `corpus/lessons/round-24.md:232` contains the S118 verdict row.
- `tools/souji-landing-gate.py:141-146,823-862` matches repository-rooted tokens then trims only trailing numeric line suffixes; `876-902,954-961` loads unique exact path exemptions and suppresses only an exact unmatched path. Revision: lane HEAD `e78ac7c4837b81b634db4a927605a751a7f006ba`.

## Findings
1. Draft row for `corpus/knowledge/registry` explains the Q59 prose-fragment over-match; reason length 73. Source: `corpus/QUALITY.md:143`.
2. Draft row for `corpus/lessons/round-24.md:232:S118` explains the composite enumerated-site token, argument use, over-match, and resolving site; reason length 196. Sources: `corpus/QUALITY.md:141`, `tests/fixtures/r25-q57-check.sh:3-4,24-26`, `corpus/lessons/round-24.md:232`.

## Attack log
- None.
