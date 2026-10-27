## Status

CONFIRMED — W1's AttackC2W3PathNormalization finding is supported by frozen contract, counter source, and committed receipt. No fresh execution performed.

## Evidence

- Frozen revision `2b0171e2071fdc9c16a69bed12b0d040e574d8c8`; base `9c76c7222a8abff027af42e37f0d160d52526bba`.
- `census/round-34/c2-legs.tsv:5-9` expressly requires matching the base's last digit-bearing line with scratch paths normalized to `<TMP>`. W3 is at `c2-legs.tsv:36`.
- `census/round-34/c2-counter.py:82-84` collapses whitespace only and has no path normalization.
- `census/round-34/records/feasibility-final.txt:3` records W3 FAIL with equal rc=1 but different randomized `bwrap.*` and `souji-census-selftest.*` path components. The W2-specific exception at `c2-legs.tsv:10-13` does not extend to W3.
- No fixture execution/probe was performed. The conclusion is grounded in committed receipt plus source, not a newly reproduced run.

## Findings

The mismatch is a real frozen-contract implementation defect, not a measurement artifact or a clause-exempt W3. Different scratch names are the expected reason for normalization, not a benign reason to omit it.

## Attack log

Read `w1/SwarmScribe35.md:60-64`, `census/round-34/c2-legs.tsv:5-13,33-37`, `census/round-34/c2-counter.py:82-84`, and `census/round-34/records/feasibility-final.txt:3`. LSP tooling was unavailable (`lsp` and `omp-lsp` absent); no semantic LSP claims made. No execution or scratch writes.

## Deliveries

- `.ufo/waves/round-34/w2/AttackC2W3PathNormalization.md`
- `.ufo/waves/round-34/w2/SwarmReviewer27.md`
