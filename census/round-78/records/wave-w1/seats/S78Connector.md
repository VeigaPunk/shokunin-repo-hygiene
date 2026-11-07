# S78Connector Report: Round 78 Cross-Claim Separation & Sibling Overlap Scan

### 1. Causal Separation: SEPARABLE
- Command: `git show --name-only ed22dc9cb7a6b61a7d0bd150db4a95191b1333aa d90740fec1862556ed504aafcd21e89d5dece0f0 87d456179668738ca59e607c3176de056e6a9991`
- Evidence: W modifies only `tools/souji-pre-report-gate.sh`; K captures `.ufo/waves/round-{27,53,68}/`; L2 edits `c2-pointer-ledger.tsv`. File sets are disjoint.
- Receipts: C1 receipts (`c1-after.txt`, `c1-regress-*.txt`) bind only gate, writer, C1 counter/population; zero C2 bytes. C2 receipts (`c2-after.txt`, `c2-pointer-check-after.txt`) bind C2 counter, population, ledger, forgeries, `LOG.md`; zero gate bytes.
- Verdict: SEPARABLE. C1 verifies with K/L/L2 absent; C2 verifies with W absent.

### 2. Other Lane Tools: UNGUARDED (Findings: HIGH, MEDIUM)
- Lane tools executing `git` on lane root with NO discovery-source guard and NO timeout:
  - `tools/souji-receipt-write.py:159` `subprocess.run(["git", "-C", root, ...])` [HIGH: receipt recorder blocks indefinitely on FIFO config/HEAD]
  - `tools/souji-pointer-check.py:47` `subprocess.run(["git", "-C", root, *args])` [MEDIUM: pointer check blocks on FIFO]
  - `tools/souji-freeze-check.py:107` `subprocess.run(["git", ...])` [MEDIUM: freeze check blocks on FIFO]
  - `tools/souji-landing-gate.py:258,270` `subprocess.run(["git", "-C", root, ...])` [MEDIUM: landing gate blocks on FIFO]
- r78 pre-check (`gitsrc_scan` in `souji-pre-report-gate.sh:10-92`) covers ONLY the gate before check 1; does NOT cover writer or other tools.

### 3. Sibling Overlap Scan
| Lane | Uncommitted UFO Cites in LOG.md | Pre-Report Gate Unguarded Git | Exposed |
|---|---|---|---|
| kaidoku | 35 / 419 | `tools/round-78/surface-recheck.py:414` (no timeout) | YES |
| kama | 28 / 284 | `tools/pre-report-gate.py:666` (600s timeout, no src guard) | YES |
| tabi | 24 / 205 | `scripts/check-user-round-contract.mjs:167` (no timeout) | YES |
| tsukuroi | 22 / 255 | `tools/_revision.py:70` (60s timeout, no src guard) | YES |
| mado | 19 / 189 | `quality/check-cited-revisions.py:56` (no timeout) | YES |
| kengaku | 14 / 145 | `plans/pkg_gate.py:260` (no timeout) | YES |
| kumitate | 11 / 99 | `scripts/round-gate.mjs:298` (20s timeout, no src guard) | YES |
| 10 lanes | 100 total (chousa 11, kasegi 10, mori 10, kotoba 10, kake 10, ...) | kasegi `r46-landing-gate.py:73`, mori `mori-retention-gate.py:163` | YES |
| audio, 3d, kagi | 0 uncommitted | `game-dev-3d/run_gate.sh` (guarded); kagi/audio none | NO |
- Fleet tools: `scripts/hyaku/jj-lane.sh:225,244` runs `git rev-parse` and `git ls-remote` with no timeout / no source check.

### 4. UFO-FSD Connector Move: Shared Git-Source Guard
- Affected axes: C1 (operability) and C2 (calibration).
- Move: Extract `gitsrc_scan()` into `tools/souji-gitsrc-guard.py` and call it as a pre-check inside `tools/souji-receipt-write.py` and `tools/souji-pointer-check.py`.
- Benefit: Closes the HIGH finding where a FIFO discovery source hangs receipt generation without altering gate semantics or C2 resolution logic.
- Risks & Verification: Zero-dependency stdlib module; verify via `c1-gitsrc-counter.py` against writer (0 hangs).

Files written under seat directory:
- `.ufo/waves/round-78/w1/S78Connector/sibling-overlap.tsv`
