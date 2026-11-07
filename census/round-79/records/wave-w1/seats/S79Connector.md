# S79Connector Report: Separation, Overlap Scan & Bounded Proposal
## 1. Causal Separation: SEPARABLE
- Command: `git show --name-only c8c3fbca 17009fa1 4a9bbb30 feebf2ba`
- Commits: W1/R1/R2 touch ONLY `tools/souji-pre-report-gate.sh`; W2 touches ONLY `census/round-79/c2-pointer-counter.py`.
- Bind/Instrument: C1 receipts (`c1-after.txt`, `c1-regress-*`, `controls/c1-*`) bind gate & c1 counters; 0 C2 bytes read. C2 receipts (`c2-after.txt`, `c2-regress-*`, `controls/c2-*`) bind c2 counter/harness/forges; 0 gate bytes read.
- Verification: C1 verifies if W2 absent; C2 verifies if W1/R1 absent. Verdict: SEPARABLE.
## 2. Souji Lane Tools (Foreground Timeout / Orphan Risk)
| File:Line | Traps | gate_run Applies |
| :--- | :--- | :--- |
| `tools/souji-quarantine.sh:379,593,595,792,802,841,1255` | 1564,1886 (EXIT only) | YES |
| `tools/souji-vault-verify.sh:213,1301` | 1564 (EXIT only) | YES |
| `tests/fixtures/r13-repo-structure.sh:258,264` | 192 (EXIT), 193 (ERR) | YES |
| `tests/fixtures/r17-jj-receipts.sh:257,266,277,966,986,1031` | 166 (EXIT,INT,TERM,HUP; rm only) | YES |
## 3. Sibling Overlap Scan
| Lane | File:Line | Exposed | Traps |
| :--- | :--- | :--- | :--- |
| chousa | `tools/research-gate.sh:358,466,574,636,8134,8625` | YES | 4500,4509 (EXIT only) |
| chousa | `tools/parent-lifetime.sh:82` | YES | NONE |
| kama | `tools/kama-probe.sh:808` | YES | 125 (EXIT,INT,TERM; rm only) |
| mado | `tools/mado-verify.sh:144,3383,3412,3431,3509,3605` | YES | NONE |
| mori | `tools/mori-census.sh:606,2651` | YES | 3017 (selftest only) |
| tameshi | `tools/mutate-and-run.sh:475,923,924` | YES | NONE |
| tsukuroi | `tools/recheck-drift-r54.sh:56` | YES | NONE |
## Findings
- HIGH: `souji-quarantine.sh` has 7 foreground timeout calls (bounds up to 300s) with no signal trap; TERM orphans child pgid.
- HIGH: `chousa research-gate.sh` (pre-report gate) runs foreground `$(timeout)` at 6 sites with no signal trap.
- MEDIUM: `souji-vault-verify.sh` runs foreground `$(timeout)` without signal trap.
- MEDIUM: `mado-verify.sh` runs `$(tmo)` at 30+ sites with zero traps; `mori-census.sh` runs `$(timeout)` without top-level trap.
- LOW: `r17-jj-receipts.sh` traps signals to clean `$T` but fails to kill child process group.
## Bounded Proposal
- Evidence: C1 fixed `souji-pre-report-gate.sh` via async `gate_run_file` (`timeout ... &; wait $!`) and signal trap killing child pgid; `souji-quarantine.sh` and sibling gates remain vulnerable.
- Affected Axes: Operability (prevents hung/orphaned children on caller termination across lane tools); Reliability.
- Proposed Move: Extract `gate_run` into a shared lane helper `tools/souji-run-bounded.sh` and adopt in `souji-quarantine.sh` & `souji-vault-verify.sh`.
- Risks: Command output buffering in tempfiles requires strict cleanup traps; subshell status propagation must preserve exit codes 124/137.
- Verification: Reproduce `c1-signal-counter.py` shim pattern on `souji-quarantine.sh` with SIGTERM to assert 0 orphans.
Files written: `.ufo/waves/round-79/w1/S79Connector.md`, `.ufo/waves/round-79/w1/S79Connector/overlap-scan.tsv`.