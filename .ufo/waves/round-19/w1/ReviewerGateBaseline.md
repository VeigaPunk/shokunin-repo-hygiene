STATUS: DONE — D3 is correctly characterized: 61/0 is receipt-backed, while the older 33 count is static-only.

# Findings

- **Low — historical provenance wording needs qualification if reused.** `corpus/lessons/round-18.md:98` describes `b576341` as having run 33 gate cases. The identified source instead calls 33→53 a static case count and says execution was not rerun (`.ufo/waves/round-18/w2/RevGatePointerCode.md:7,19`). D3 correctly identifies a missing committed run receipt / labeling defect, not evidence that the static count itself is numerically wrong (`corpus/lessons/round-18-verifier-spotcheck.md:147`). The r19 correction labels the old 33 baseline static (`corpus/lessons/round-19.md:124-125`).

# Evidence

- **Committed 61/0 baseline receipt:** `census/round-18/final-verification-4800fd7.json:2,5,29-39` records `measured_commit` 4800fd7, the gate tool SHA-256, the `--selftest` command and exit 0; its output summary is pass=61, fail=0. The r18 closure independently names this receipt for 61/0 (`corpus/lessons/round-18-verifier-spotcheck.md:82`). The receipt is present in the 3ab2c81 tree (blob `0d37a0567b0e87e8407fff24c68800bd4cd4251d`); the inspected working copy matches that base path.
- **Source of 33:** `.ufo/waves/round-18/w2/RevGatePointerCode.md:1,7,19` identifies a static review of b576341→5efb519 and derives 33→53 from added selftest cases; it is not an executed 33/0 receipt. The same distinction is stated in D3 at `corpus/lessons/round-18-verifier-spotcheck.md:147`.
- **R19 after-result, if reported:** `census/round-19/final-verification-63bb887.json:4-6,26-47` records measured commit 63bb887, the changed gate digest, and selftest pass=65/fail=0. The record is committed at 1db7108 (blob `056cf57c43611034fb23e8eb5bed0b07f0f3ce0c`); its inspected working copy matches that commit. This supports the after-result, not the 61 baseline or the older 33 count. `corpus/lessons/round-19.md:17-18,124-125` preserves the same distinction.

# What the r19 report may cite

1. Cite `census/round-18/final-verification-4800fd7.json` for the previous gate's executed 61-pass / 0-fail result, naming its measured revision 4800fd7.
2. Cite `census/round-19/final-verification-63bb887.json` for the r19 65-pass / 0-fail result, naming its measured revision 63bb887.
3. Cite `.ufo/waves/round-18/w2/RevGatePointerCode.md:19` only as the **static** source for the older 33 case count. Do not describe 33 as a committed execution, a 33/0 result, or a run at b576341. Do not use `corpus/lessons/round-18.md:98` as runtime evidence.

# Residual risk and verification gaps

- The available mounted tools have no LSP device; attempting to read `xd://lsp` returned “No such tool.” Literal search was used only to locate references; findings above are grounded in the opened records and reports, not grep output as semantic proof.
- I did not rerun the gate or either selftest. This is a read-only provenance review of committed receipts and static source attribution.

# Commands run

- Read-only `git ls-tree 3ab2c81` and `git log -1` confirmed the r18 receipt's committed path; `git diff --quiet 3ab2c81 --` the cited r18 records returned 0.
- Read-only `git log -1 --all` located the r19 acceptance record at 1db7108; `git ls-tree 1db7108` and `git diff --quiet 1db7108 -- census/round-19/final-verification-63bb887.json` confirmed the committed record and matching worktree bytes.
- Literal reference search was used during discovery. No gate, selftest, fixture, or other runtime command was executed.

# Contract compliance

- No subagents, installs, scratch files, signals, lane-tool executions, or changes outside this assigned report. No tool install/update was made.
- **Boundary breach disclosed:** one initial broad literal search named the whole `census/` subtree and returned matches from operator-owned `census/operator-sweep-20261019/`. That violated the no-open boundary. I stopped using that result, did not copy its content into this report, and made no changes there. Subsequent reads were restricted to the cited non-operator paths.
