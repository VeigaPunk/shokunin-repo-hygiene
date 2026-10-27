## Status
STATUS: PARTIAL — fidelity review found contract/code gaps; C2 junk fixture timed out at its 900-second inner counter deadline.

## Evidence
- Frozen contract/counter/item sources reviewed at `2b0171e2071fdc9c16a69bed12b0d040e574d8c8` (frozen prereg/list revision); target lines: `census/round-34/preregistration.txt:59-66,90-113`; code: `c1-counter.py:301-321,389-397`, `c2-counter.py:207-234,283-326`; frozen item tables: `c1-items.tsv:18-78`, `c2-legs.tsv:33-46`.
- Ran both selftests and both junk fixtures; full commands, loadavg receipts, and outputs are copied to `deliver-prereg-fidelity.txt`. C1 selftest and junk fixture passed; C2 selftest passed; C2 junk fixture exited 1 after `subprocess.TimeoutExpired` at 900 s.
- LSP device/status was unavailable (`read xd://lsp` returned “No such tool”); therefore used literal file locations, not semantic LSP proof.

## Findings
1. **High — C1 allows a statement form prohibited by frozen A1c.** `preregistration.txt:48-53` requires the row's quoted statement to be the complete digit-bearing output line; A1 explicitly binds it to the collapsed LAST digit-bearing line. But `c1-counter.py:308-310` treats any restatement `statement` beginning `RESULTS:` as a record predicate and skips the last-line equality at `311-313`. Thus a valid `RESULTS:<path>:<n>` statement can validate without being the claimed last output line. The junk test only rejects `RESULTS:…:0`, not this positive-count bypass (`c1-counter.py:324-337`; executed control receipt in `deliver-prereg-fidelity.txt`).
2. **High — G2 allows paths outside C2's frozen touch set.** C2 scope is only `census/round-34/c2-*` and `tests/fixtures/r34-*` (`preregistration.txt:111-113`); G2 says the outside-namespace changed-path set must equal empty (`:94-96`). Actual guard instead accepts any `census/round-34/**`, any `corpus/` path including arbitrary corpus files, and SCORECARD/SKILL (`c2-counter.py:210-214`). A change such as `corpus/knowledge/unrelated.md` or another non-C2 r34 file can pass G2, so the checked set is not the frozen C2 allowlist.
3. **Medium — landing commit is not re-derivable from the frozen plan.** Target clauses refer to “the C1 landing commit” and “the C2 landing commit” (`preregistration.txt:59-62,104-106`) but do not define how either commit is identified (e.g. a named commit/hash or deterministic boundary rule). The tip is distinct and defined, but the landing point cannot be independently reconstructed from the preregistration.

Kill-rule assessment: the plan says any other reading, including could-not-evaluate, is MISSED (`preregistration.txt:61-62,104-106`), so a nonzero crash/no-summary or partial summary cannot satisfy the exact target. The counters do not emit an explicit `MISSED` receipt on abrupt termination (C1 target/exit at `c1-counter.py:389-397`; C2 final summary only at `c2-counter.py:322-326`), but the frozen kill rule itself leaves no alternate successful reading. Do-nothing and main target counters were not rerun.

## Attack log
None; findings are plan/implementation fidelity defects, not proposed changes to frozen predicates.

## Deliveries
- `.ufo/waves/round-34/w1/deliver-prereg-fidelity.txt` — run receipts and observed outputs.
