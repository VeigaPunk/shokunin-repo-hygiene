## Status

CONFIRMED — the reported W3 mismatch is a real counter/contract defect, not shown unreachable by another frozen clause. This is source/committed-receipt confirmation; I did not rerun the leg.

## Evidence

- Frozen revision `2b0171e2071fdc9c16a69bed12b0d040e574d8c8`; base `9c76c7222a8abff027af42e37f0d160d52526bba`.
- Frozen leg contract `census/round-34/c2-legs.tsv:5-9` says witness PASS requires the rev run to print the base run's last digit-bearing line, with “scratch paths normalized to <TMP>”. W3 is `bash tools/souji-census.sh --selftest` at `c2-legs.tsv:36`.
- Counter `census/round-34/c2-counter.py:82-84` implements `last_digit` as whitespace collapse only (`" ".join(x.split())`); it does not substitute/normalize scratch-path components.
- Committed receipt `census/round-34/records/feasibility-final.txt:3` records W3 FAIL, both rc=1, with lines differing in randomized `bwrap.44kaonca` vs `bwrap.8cyddgji` scratch paths and `souji-census-selftest.WMYNZy` vs `...MvpCRa` paths. The report `w1/SwarmScribe35.md:60-64` identifies the same mismatch and implementation.
- The independent frozen clauses for W1-W4 require output-line agreement (contract `c2-legs.tsv:5-9`); no clause exempts W3 from comparison. The special W2 self-tracing exception is explicitly limited to W2 at `c2-legs.tsv:10-13`, not W3.

## Findings

1. **W3 normalization defect confirmed from source and committed output.** Whitespace collapse cannot make those differing path strings equal. The frozen contract explicitly requires scratch-path normalization, so this is not an optional presentation detail.
2. **No evidence of a benign alternate explanation defeating the finding.** Randomized paths are expected from separate sandbox/scratch runs, but that explains the differing bytes rather than making the contract inapplicable. The W3 arm remains subject to the witness clause; W2's special exception does not apply.
3. **Measurement limitation:** I did not execute a probe; reproduction is the committed W3 receipt above. No claim is made about a fresh run or current host behavior.

## Attack log

- Read W1 finding `w1/SwarmScribe35.md:60-64`.
- Read frozen leg text `census/round-34/c2-legs.tsv:5-13, 33-37` and counter `census/round-34/c2-counter.py:82-84`.
- Read committed output `census/round-34/records/feasibility-final.txt:3`.
- LSP status/references/definition/diagnostics could not be requested: no `lsp`/`omp-lsp` executable was available. This report therefore relies on literal source lines and committed receipt, not semantic LSP proof.
- No commands were run to execute the fixture/counter; no scratch was created.

## Deliveries

- `.ufo/waves/round-34/w2/AttackC2W3PathNormalization.md`
