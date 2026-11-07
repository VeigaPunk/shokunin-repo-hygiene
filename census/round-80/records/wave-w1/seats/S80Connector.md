# S80Connector Report: Cross-Claim Separation & Sibling Overlap

### 1. Causal Separation
- Verdict: SEPARABLE. W1 (c1-pointer-counter.py) and W2 (tools/souji-quarantine.sh) share no bytes, instruments, or bindings.
- Command: `git show --name-only bd263c3f 836dac3e a4aa8880` & grep binds across `census/round-80/records/`.
- Observed: C1 receipts (`c1-after.txt`, `c1-regress-*.txt`) bind only `c1-false-row-harness.py`, `c1-false-rows.tsv`, `c1-pointer-counter.py`; C2 receipts bind only `c2-signal-counter.py`, `c2-population.tsv`, `souji-quarantine.sh`, `souji-verify.sh`. C1 verifies with W2 absent; C2 verifies with W1 absent.

### 2. Other Lane Tools: Timeout & Signal Handling
- `tools/souji-vault-verify.sh:213` (`out=$(timeout "$CLI_TIMEOUT" "$bin" vault:hash "$vp" ...)`): no signal trap. Fit: r79 async `gate_run` (point external CLI call capturing stdout; async `wait` + process-group kill avoids full setsid rewrite).
- `tools/souji-verify.sh:591` (`dir_digest` pipeline `find | sort -z | xargs sha256sum | sha256sum`): unbounded pipeline, no trap. Fit: r80 front/worker session if bounded (multi-process pipeline reaped safely via session scan).
- `tools/souji-census.sh:1564-1595` (watchdog reaps `kill -KILL -- "-$worker"`): fails if worker child calls `timeout` (setpgid(0,0)). Fit: r80 front/worker session (`q_kill_session` via `/proc/<pid>/stat` sid).
- `tests/fixtures/r17-jj-receipts.sh:257,266,277` (`$(timeout --kill-after=5 240 ...)`): no trap. Fit: r79 async `gate_run`.

### 3. Sibling Overlap (capped at 15 rows)
| Lane | File:Line | Exposed | Note |
| :--- | :--- | :--- | :--- |
| audio-shokunin | corpus/live/r68-critic/run_transports.sh:37 | yes | `out=$(timeout 15 sox ...)`; no trap |
| audio-shokunin | corpus/live/r81-verifier2/battery.sh:26 | yes | `out=$(timeout 900 python3 ...)`; no trap |
| game-dev-2d-shokunin | corpus/live/r89-boundary/hog_ladder.sh:8 | yes | `v=$(timeout -s KILL 25 godot ...)`; no trap |
| game-dev-2d-shokunin | corpus/live/r91-scout/run_cells.sh:27 | yes | `$(timeout 20 godot ...)`; no trap |
| game-dev-2d-shokunin | corpus/live/r93-boundary/run_matrix.sh:70 | yes | `$(timeout 20 ...)`; trap INT/TERM deferred by `$(...)` |
| game-dev-3d-shokunin | corpus/knowledge/unreal-mcp/gate/run_gate.sh:224 | yes | `C2_LOG=$(timeout 180 git clone ...)`; trap deferred |
| kagi-shokunin | corpus/checklist-run.sh:261 | yes | `out=$(... timeout ...)`; no signal trap |
| kagi-shokunin | corpus/surface-census.sh:591 | yes | `out="$(... timeout 20 ...)"`; no signal trap |
| kagi-shokunin | plans/round-48-c2.sh:62 | yes | `ex=$(... timeout 300 ...)`; no trap |
| kagi-shokunin | plans/round-50-c2.sh:106 | yes | `out=$(... timeout -k 5 ...)`; no trap |
| kaidoku-shokunin | tools/round-39/c1-run.sh:258 | yes | `rea_ver=$(timeout 120 npx ...)`; no signal trap |
| kaidoku-shokunin | tools/round-40/c1-run.sh:449 | yes | `rea_ver=$(timeout 120 npx ...)`; no signal trap |
| kotodama-shokunin | reports/round-25/audit/o18-probe-matrix.sh:66 | yes | `o=$(timeout 120 python3 ...)`; no trap |
| kumitate-shokunin | scripts/omp-binary-probe.sh:88 | yes | `out="$(... timeout -k 5 ...)"`; no trap |
| tameshi-shokunin | tools/mutate-and-run.sh:923 | yes | `out=$(... timeout ...)`; no trap |

### Findings & Durability
- Finding MEDIUM: `tools/souji-vault-verify.sh:213` foreground `$(timeout ...)` leaves orphan CLI process group on caller SIGTERM/SIGHUP.
- Finding LOW: `tools/souji-census.sh:259` `kill -- "-$worker"` does not reap `timeout`-escaped process groups.
- Files written under seat directory: `.ufo/waves/round-80/w1/S80Connector/sibling-overlap.tsv`.
