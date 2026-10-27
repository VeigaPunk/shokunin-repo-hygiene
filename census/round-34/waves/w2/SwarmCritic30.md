## Status
Source-level falsification review; no scratch execution or target-counter run performed. Reviewed frozen revision `2b0171e2071fdc9c16a69bed12b0d040e574d8c8` and W1 report. Finding is real as a semantic limitation of witness scope, but not demonstrated as a passing exploit against the target.

## Evidence
- W1 `deliver-c2-leg-attacks.txt:3-5` explicitly labels its witness-scope scenario as static, not reproduced. It claims a tool can emit the genuine selftest line and create irrelevant files in TMPDIR to meet the count/witness test.
- Frozen counter `census/round-34/c2-counter.py:155-179` wraps the entire command in strace, counts all matched file-create syscalls, and marks `witnessed` if any matched path includes scratch TMPDIR or the private `/var/tmp` directory. At `:201-203`, it accepts when the tip count is at least half the base count and `witnessed` is true, after matching return code and final digit-bearing line.
- The frozen contract independently describes this as a syscall-based work witness: `census/round-34/c2-legs.tsv:7-9`; preregistration `census/round-34/preregistration.txt:81-84` specifies the same witness and separately exempts W2 using its CASE proof.
- Stub control is narrow: `tests/fixtures/r34-sandbox-junk.py` (as described by W1 `SwarmCritic20.md:7,16`) tests fixed no-work echo/printf stubs, not a stub that creates irrelevant files. The counter's selftest at `census/round-34/c2-counter.py:237-255` only checks witness-leg presence and junk-only refusal; it does not test witness relevance.
- Existing committed feasibility receipt `census/round-34/records/feasibility-final.txt:1,4` records W1 and W4 passing with substantial create counts (209 and 1057 tip creates); that supports that this is a broad process-level trace, not a narrow output of the named tool. It does not establish those creates are irrelevant or that a malicious mutation passes.

## Findings
1. **Real contract/measurement gap, counterexample remains inference.** Any process in the traced shell tree can contribute matching creates under either allowed temporary location. Since the count and path predicate are not attributed to the named tool or linked to its asserted behavior, a crafted replacement could plausibly print the expected line and generate enough irrelevant temporary files. The exact threshold depends on base-run creates: tip must produce at least half the base count, and at least one qualifying create must occur under TMPDIR or the private var/tmp. W1's one-file example alone is not guaranteed to satisfy that threshold; its stronger irrelevant-file inflation scenario is the relevant counterexample. No such mutation was run here.
2. **Benign interpretation does not close the defect.** The contract deliberately uses operational syscall evidence as a proxy for work, and the legitimate tools may naturally create many transient files. The threshold filters a pure print-only stub, but it does not prove semantic work by the named tool. This is a tradeoff in the frozen operational definition, not an observed false pass.
3. **No reproduced defect / reachability qualification.** The committed feasibility receipts show W1/W4 pass, while overall C2 feasibility fails elsewhere; they do not show the proposed counterfeit was accepted. Thus do not claim an exploit was executed, nor that the frozen target was reached. J1 does not close the specific gap because its control is a no-create stub, and its recorded execution timed out (`records/feasibility-final.txt:7`).

Smallest safe correction for a future revision: add an adversarial mutation that prints the genuine result while creating enough irrelevant files in the permitted paths, and require that mutation be rejected; if it passes, narrow the acceptance rule to a tool-specific observable effect or describe the claim accurately as process-level file-creation evidence rather than proof the named tool did work. Do not alter frozen predicates in this review.

## Attack log
- Read `census/round-34/c2-counter.py:1-36,134-203,237-255`, frozen leg definitions and preregistration clauses, W1 `deliver-c2-leg-attacks.txt`, W1 `SwarmCritic20.md`, and committed feasibility receipts.
- No commands, scratch fixtures, or executions performed; no output is represented as reproduced.
- Counter-evidence: threshold plus output/exit matching reject a pure echo stub; there is no evidence in reviewed receipts that the larger irrelevant-create mutation passes.

## Deliveries
- W1 source: `.ufo/waves/round-34/w1/deliver-c2-leg-attacks.txt:5`.
- Frozen counter: `census/round-34/c2-counter.py@2b0171e2071fdc9c16a69bed12b0d040e574d8c8:155-179,188-203`.
- Frozen contract: `census/round-34/c2-legs.tsv@2b0171e2071fdc9c16a69bed12b0d040e574d8c8:7-12`; `census/round-34/preregistration.txt@2b0171e2071fdc9c16a69bed12b0d040e574d8c8:81-84`.
- Output: `.ufo/waves/round-34/w2/SwarmCritic30.md`.
