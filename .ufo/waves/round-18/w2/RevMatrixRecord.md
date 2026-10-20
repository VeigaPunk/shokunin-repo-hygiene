STATUS: DONE — requested C1 matrix cross-checks reconcile

# Attacked claim
C1 operability — internal integrity of `census/round-18/c1-matrix-worktree.json`.

# Findings by severity
None. No discrepancy was found in the requested hash, suite-count, leftover-PID, or invalid-suite checks. Smallest fix: none.

# Evidence

## Arm script digests
The three revision-arm digests recorded in the matrix match the hashes of `tools/souji-census.sh` obtained with `git show`; the changed-arm digest also matches the current worktree file.

| Matrix arm | Revision | Matrix SHA-256 | Independently observed SHA-256 | Result |
|---|---|---|---|---|
| `pre-harm` | `a31642d14006830ec62edf40b0354c3699728c4a` | `6a000c59fe7486fbde7e5f68663c61cf60404cadb4185e84205b56fe4648c026` | `6a000c59fe7486fbde7e5f68663c61cf60404cadb4185e84205b56fe4648c026` | match |
| `r14-harm` | `cc2168325768d5356a82c039dcdf787377c55784` | `fcff8b057b3e7dc57d0fe6a5ed4c7ccb2c89c3ea4bd3c0eb3a93e26ea869aee9` | `fcff8b057b3e7dc57d0fe6a5ed4c7ccb2c89c3ea4bd3c0eb3a93e26ea869aee9` | match |
| `r17-base` | `b5763415cc67ecff1e8fe56c58c39a6fb106d7a3` | `006b98231f8d138b3bb13595cc3f9cd9133247d2e88b4683140735ca0759e9fd` | `006b98231f8d138b3bb13595cc3f9cd9133247d2e88b4683140735ca0759e9fd` | match |
| `changed` | `WORKTREE` | `7e6a92d415f8f256a4e46b0776add6e3645b687abd8be6e67aca520587120bcd` | `7e6a92d415f8f256a4e46b0776add6e3645b687abd8be6e67aca520587120bcd` | match |

Exact revision-hash command:
```sh
for rev in a31642d cc21683 b576341; do
  printf '%s ' "$rev"
  git -C /home/vgpnk/Projects/shokunin/souji-shokunin show "$rev:tools/souji-census.sh" | sha256sum
done
```
Output:
```text
a31642d 6a000c59fe7486fbde7e5f68663c61cf60404cadb4185e84205b56fe4648c026  -
cc21683 fcff8b057b3e7dc57d0fe6a5ed4c7ccb2c89c3ea4bd3c0eb3a93e26ea869aee9  -
b576341 006b98231f8d138b3bb13595cc3f9cd9133247d2e88b4683140735ca0759e9fd  -
```
The worktree check was `sha256sum /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh`, which returned `7e6a92d415f8f256a4e46b0776add6e3645b687abd8be6e67aca520587120bcd`.

## Per-suite failed counts
Counts below are `failed / total` from the four suite records; selftest is `failed / checks`.

| Arm | r14 namespace | r15 config | r17 hygiene | r18 bounded | Selftest |
|---|---:|---:|---:|---:|---:|
| `changed` (`WORKTREE`) | 0/12 | 0/20 | 0/29 | 0/8 | 0/62 |
| `pre-harm` (`a31642d`) | 10/12 | 8/20 | 21/29 | 6/8 | 0/36 |
| `r14-harm` (`cc21683`) | 0/12 | 16/20 | 14/29 | 5/8 | 0/38 |
| `r17-base` (`b576341`) | 0/12 | 0/20 | 0/29 | 5/8 | 0/49 |

This confirms the specifically claimed `b576341` bounded result (5 of 8 failed) versus the changed arm (0 of 8 failed). The matrix also reports `invalid_suites: []` (`c1-matrix-worktree.json:1760`); the per-suite `valid` values are true. These validity flags coexist with expected failed cases in historical arms—the separate `failed` fields above record those failures.

Evidence locations: matrix changed-arm failure counters at lines 63, 159, 336, 399 and selftest at 415; `pre-harm` at 497, 593, 770, 833, 849; `r14-harm` at 931, 1027, 1204, 1267, 1283; `r17-base` at 1365, 1461, 1638, 1701, 1717. Suite totals are within the corresponding arm blocks (`:1-437`, `:438-871`, `:872-1305`, `:1306-1739`).

## Leftover process identities
For every arm, the `r15-config` record has `leftover_procs_count: 44` and 44 listed PIDs; the `r17-hygiene` record has count 14 and 14 listed PIDs. The other listed suites and selftest have zero leftovers. In the changed arm these fields and arrays are at `c1-matrix-worktree.json:159-206` and `:336-353`; corresponding counts repeat in the other arm blocks.

Compared the combined 58 matrix PIDs against the PID column in `census/round-18/leaked-procs-before-1631.txt:1-58`. Exact check output:
```text
baseline_pid_count=58
matrix_pid_count=58
set_diff_lines=0
```
Thus the 44/14 arrays are exactly the same PID set already captured in the older-orphan baseline, with no additional identity in the matrix arrays. The baseline rows describe the earlier census processes (including their command paths and timestamps); this supports treating these as pre-existing orphans rather than new PIDs from these arms.

# Verdict
Holds for the requested matrix-integrity checks: revision/worktree digests match, suite failure counts reconcile with the per-case records, the 44/14 PIDs reconcile exactly to the prior orphan list, and `invalid_suites` is empty.

# Residual risk and verification gaps
This was an internal record-consistency review, not an independent rerun of the census suites or a source-level audit of C1 runtime behavior. The matrix contains no explicit run timestamp; the orphan conclusion here is based on exact PID identity against the named prior snapshot. No tools were installed or updated.