# Fresh fixture-oracle review — calibration

**Axis:** calibration (C1). **Method:** bounded source-only review; no target code, tests, fixtures, build, lint, or smoke was run. I compared the preregistered expected cases to the auditor's embedded source selftest. No separately named external fixture-source paths were included in the permitted read set; the relevant fixture source available here is `tools/souji-seat-audit.py`'s `selftest()`.

**Observed source identity:** lane HEAD `12516f7dcdd5b165e5ee208d44a38d63b5bd5812` (the preregistered baseline); the six permitted implementation files were modified in the worktree. First reader snapshot tags and the read-only working-byte SHA-256 measurements were:

| path | reader tag | SHA-256 |
|---|---|---|
| `tools/souji-seat-audit.py` | `1A5C` | `8f7b16473755215f4f90a85e3c1a9da2e31d47614919fd631866ddf01c31e2c9` |
| `tools/souji-rev-pin.py` | `18FF` | `0b9018e52553d6517b8f805f07163b6a4093d6e842fa79314876084d7b64f756` |
| `census/round-13/run-verification.py` | `8EBD` | `a10d66ca6728f641fb4144c7fcfb2996ff1940fd7c6e2f69e30230073a9116e8` |
| `census/round-14/run-verification.py` | `658E` | `45e6896c9b24e45c58a49efed38c0f09e642f0779c60dacf3bd1ab487e9b3502` |
| `census/round-14/run-targeted.py` | `7C4E` | `2d8c61809a0cb99a4f975f9e0e290bf30ef8cd4f4d7267a6569f759da5df6895` |
| `census/round-14/cache-demonstration.py` | `0E04` | `3ad63d5b927fedc3aee70c2b2a13c91ad9c83d7bba9c71c5d85844507ef4213b` |

## Counterexample to fixture completeness

`preregistration.txt:3` requires the C1 oracle to reject each unrequested `.patch/.py/.json/.tsv/.txt`, allow one exact requested sibling delivery and reject its four alternatives, reject cross-seat stems, and exercise exact `OWN ONLY` and `r19w2` scratch grants. The inspected implementation has relevant code paths: `delivery_paths()` filters explicit item directives against the report stem and five suffixes (`tools/souji-seat-audit.py:124-135`), `run()` passes those deliveries into `audit_seat()` (`:337-371`), and `target_verdict()` admits only an exact member of `allowed` (`:224-255`).

But the embedded oracle does not exercise that positive grant path. Its delivery-focused cases are only unrequested `.patch`, unrequested `.py`, a neighboring `.patch`, and a tools write (`:490-499`). The table loop calls `audit_seat()` with no `deliveries` argument (`:501-505`), so none of those cases tests `delivery_paths()` or its wiring. The `run()` fixtures later in the selftest test summary and scratch wiring only (`:512-544`); neither item has a delivery directive. No case in the complete `cases` table (`:402-500`) attempts the preregistered exact requested artifact, the four alternatives, or unrequested `.json/.tsv/.txt`. Thus a regression that clears every same-stem suffix after one directive—or one that rejects the requested exact artifact—can leave these fixtures green while contradicting the preregistered expected table. This is a source-level coverage gap, not an observed runtime failure.

There is a second preregistered case not represented by the visible selftest: scratch fixtures use direct `/var/tmp/souji-r9-S` values (`:401`, `:465-470`) and the run-level wiring fixture uses `souji-r9-A/B` (`:525-544`), not an explicit `r19w2-<Name>` item/context grant and a different-slot attempt. The implementation regex permits a `w<N>` slot (`:138-150`), but its correctness is not independently exercised here. Likewise the direct `owned-write` case supplies a precomputed `owned` list (`:406`) rather than validating the `OWN ONLY` prompt-to-path parser (`:117-121`).

**Independent expected values:** for an item whose sole directive is `DELIVER: <report-stem>.patch`, writing that exact `.patch` is allowed; its `.py`, `.json`, `.tsv`, and `.txt` siblings are major scope violations. With no delivery directive, all five are major scope violations. A neighboring report stem remains major. These outcomes follow the exact per-item authorization rule, not the current fixture implementation.

**Smallest safe oracle correction:** add one end-to-end `run()` fixture with a single exact `DELIVER:` directive and a transcript attempting the requested sibling plus all four same-stem alternatives; assert no violation for only the requested exact path and a major scope violation for each alternative. Add/retain a no-directive pass over all five suffixes so the positive grant cannot mask unconditional same-stem allowance. This exercises prompt parsing and audit wiring without weakening any policy.

**Evidence:** preregistered table `souji-shokunin/.ufo/waves/round-20/preregistration.txt:3`; prior harm/required exact-request rule `souji-shokunin/corpus/lessons/round-19-verifier-spotcheck.md:66-70`; implementation and oracle `souji-shokunin/tools/souji-seat-audit.py:117-151,224-255,280-394,397-546`.

**STATUS: OPEN.** The exact-delivery acceptance criterion is not independently established by the embedded fixture source. Until the run-level exact-grant/alternative oracle is present in an allowed fixture source, C1's registered grant boundary is not calibrated by these fixtures; this finding does not assert a product-code failure or authorize changing the exact per-item policy.

Report: .ufo/waves/round-20/recovery/FixtureOracle.md
