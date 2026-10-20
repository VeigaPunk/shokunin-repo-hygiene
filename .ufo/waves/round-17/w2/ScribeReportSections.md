# ScribeReportSections — round 17 (souji), draft for `/home/vgpnk/Projects/shokunin/.ufo/reports/round-17/souji.md`

STATUS: PARTIAL — both sections drafted from context numbers; the measured records behind C1–C3 are not committed at ddb7347 or HEAD d7e648d (C1 landed-rev matrix absent entirely), and the gate-replay record carries an unreconciled sha256 mismatch flag. Draft is author-side; not written to the fleet report.

## Verification performed (read-only)

- `git -C souji-shokunin cat-file -t ddb7347` → commit; `git ls-tree --name-only ddb7347 census/round-17/` → 5 files (gate-replays-expected.json, gate-replays.py, run-matrix.py, seat-audit-replay.py, transcript-manifest.py); `tests/fixtures/` lists r17-census-hygiene.py and r17-jj-receipts.sh.
- `git cat-file -e {ddb7347,HEAD}:<path>` for census/round-17/{c1-matrix.json, seat-audit-r16-replay-{base5fa6017,ddb7347}.json, jj-receipts-{base5fa6017,ddb7347}.txt, gate-replays-ddb7347.json} → **all ABSENT** at both commits.
- `git status --short -- census/round-17 tools tests` → those files are present in the worktree as **untracked** (`??`).
- `git diff --stat ddb7347 -- tools census tests corpus` → only `tests/fixtures/r15-preservation-frozen/{expected.json,record.json}` differ (26+/26−); HEAD d7e648d is the commit that regenerates that record (`git diff --stat ddb7347 d7e648d` shows the same two files), so tools/census/tests at HEAD equal ddb7347 except that record.
- Replay record re-tally (`read …json?q=…`) of `seat-audit-r16-replay-*.json`: matches the context numbers exactly (table in C2 below).
- `jj-receipts-*.txt` headers: git 2.56.0; jj 0.45.1 (`/home/vgpnk/.local/bin/jj`); summaries read (`SUMMARY total=20 failed=0 skipped=0` changed; `SUMMARY total=18 failed=7 skipped=2` base).
- `gate-replays-ddb7347.json`: `replays` match/finding_count/exit = r13-admitted a31642d 0/0; r14-landing cc21683 0/0; r15-landing b410186 5/1; r16-landing 6ff91f5 0/0; r16-precarry 79bbe7a 29/1 — all `match: true`, consistent with context.
- Scope disclosure: `git ls-files --others --exclude-standard census tools tests` listed **file names** under `census/operator-sweep-20261019/` (operator-owned). No contents were opened, read, staged, or deleted. Listed names only.

Tool installs/updates by this seat: none.

## Before → after measurements

Measured commit: **ddb7347** where the context states it. Counting commands below are as recorded in the artifacts or the context; where the artifact is not committed, that is noted per row.

### C1 operability — `tools/souji-census.sh`

- Counting command: `python3 census/round-17/run-matrix.py --changed <rev> --output <f>` (per arm, same fixtures every arm).
- Measured commit: context reports the changed arm as a **WORKTREE run by L1 before landing**; the landed-rev run writing `census/round-17/c1-matrix.json` was **in progress** and that file is absent at ddb7347 and HEAD. The changed-arm numbers below are therefore **not yet confirmed at ddb7347**.
- Notation: the context writes `X/Y` without defining it. Rendered verbatim below; the word "fail" appears only on the hygiene column of the pre-harm and r16 rows. Read the second number as failures only after L1 confirms the notation.

| arm (rev) | hygiene (26 cases) | r15-config (20 cases) | r14-ns | selftest |
|---|---|---|---|---|
| pre-harm `a31642d` (before) | 26/20 fail | 20/8 | 12/10 | 36/0 |
| r14-harm `cc21683` (before) | 26/13 | 20/16 | 0 | 38/0 |
| r16 `5fa6017` (before; every repair case fails) | 26/13 fail | 0 | 0 | 38/0 |
| changed (WORKTREE, pending ddb7347 confirmation) | 26/0 | 0 | 0 | 49/0 |

- `bash -n` and `shellcheck -S warning`: clean on every arm (context).
- Live exposure: 0/22 repos set `status.showUntrackedFiles`; 0/22 gitdirs have `info/attributes` (ScoutFleetUntrackedCfg, ScoutFleetInfoAttrs). Context-measured; no live-fleet effect of the repair.

### C2 calibration — `tools/souji-seat-audit.py`

- Counting command (as recorded in `census/round-17/seat-audit-r16-replay-ddb7347.json` argv): `python3 census/round-17/seat-audit-replay.py --lane /home/vgpnk/Projects/shokunin/souji-shokunin --transcripts census/round-16/transcripts --specs .ufo/waves/round-16/w1-spec.json:.ufo/waves/round-16/w2-spec.json --auditor tools/souji-seat-audit.py --output <f>`. Base run uses the `5fa6017` auditor. Manifest check: `check OK: 144 files verified`.
- Measured commit: **ddb7347** (after) vs **5fa6017** (base) — record files **untracked, not committed** (see Verification).

| wave (seats) | base 5fa6017 major / minor | classes (base) | ddb7347 major / minor | classes (ddb7347) |
|---|---|---|---|---|
| w1 (65) | 1 / 19 | V-RECURSIVE 18, V-WRITE-SCOPE 1, V-WRITE-UNKNOWN 1 | 1 / 20 | V-RECURSIVE 18, V-WRITE-SCOPE 1, V-WRITE-UNPARSED 1, V-PROBE 1 |
| w2 (79) | 3 / 42 | V-RECURSIVE 42, V-WRITE-SCOPE 3 | 1 / 52 | V-RECURSIVE 42, V-PROBE 8, V-WRITE-UNPARSED 2, V-WRITE-RELATIVE 1 (major) |

- Major rows: w1 SrcGitNoLazyFetch:144 kept at major. w2 base majors ConnReadmeIndex:180, RerunGateReplayR14:225,226 → ddb7347 major ConnReadmeIndex:180 (V-WRITE-RELATIVE); the two RerunGateReplayR14 rows are now V-WRITE-UNPARSED minor (status `⇒ error`).
- L1 adjudication (context): ConnReadmeIndex is a **true attempted fleet-root write** (closure D4's "own report path" reason was wrong); the two RerunGateReplayR14 rows are unparsed failed calls.
- Selftest: severity-exact **49/49** (was 20/20 severity-blind). Measured commit not stated in context.

### C3 coverage — jj-colocated repositories as a governed edge class

- Counting command: fixture `tests/fixtures/r17-jj-receipts.sh` (git-emulated J1–J8 + real-jj J9; baseline tools at `/var/tmp/souji-r17-L1/base`). Invocation line not recorded in the context; output files are `census/round-17/jj-receipts-{base5fa6017,ddb7347}.txt` (untracked).
- Environment (from the ddb7347 record header): git 2.56.0; jj 0.45.1.

| run | cases | failed | skipped | note |
|---|---|---|---|---|
| base 5fa6017 | 18 | 7 (J1, J1-vault, J3, J3-vault, J3-quarantine, J9-file, J9-worktree) | 2 | J3/J3-vault/J3-quarantine/J9-file/J9-worktree FAIL; base J9 SAFE verdicts |
| ddb7347 | 20 | 0 | 0 | J3-series and J9 now NOT-SAFE as expected; J6 plain-repo byte identity |

- Selftests at ddb7347 (context): verify **45/0** (base 40), vault **57/0** (base 51), quarantine **101/0** (base 91). Quarantine prints the helper both-paths runbook for jj repos.
- Caveat: the base run reports `skipped=2`; the changed run reports `skipped=0`. The before/after populations differ, so "7 failing → 0" compares unequal case sets. L1 must name which cases the base skipped.

### Supporting measurements (routed fixes, not separate claims)

- D6 landing gate: `--selftest` **28/28** (was 18); `census/round-17/gate-replays-ddb7347.json` replays match expectations: b410186→5 findings (exit 1), a31642d→0, cc21683→0, 6ff91f5→0, 79bbe7a→29 (exit 1). r16 fixture 15/15.
- **Unreconciled**: that record has top-level `match: true` but `expected.gate_sha256_match: false` (gate sha256 `c7e8eea5…` vs expected `e7d2439d…`). The five replay outcomes match; the gate-file identity does not. L1 must reconcile before citing "match".
- R4-style frozen preservation: `souji-preservation-evidence.py --root . --frozen tests/fixtures/r15-preservation-frozen` rc 0; `regenerate.py` verdict clean; selftest 47/47 (context).

## Trend verdicts (author draft)

- **expansion: partial** — C3 adds a governed edge class (jj-colocated repositories) with a real-jj fixture (J9), and the landing-gate/seat-audit capabilities now carry measured selftests (D6 28/28; C2 49/49). Not counted as expansion: the planned SOURCES rows S051–S063 are **planned, not landed**; the knowledge entry `corpus/knowledge/jj-colocation-receipts.md` is an **uncommitted draft**; no frontier row advanced in the context. The fleet report should not cite source-row growth for r17.
- **quality: improved, provisional** — measured on fixtures: C1 hygiene 26/0 changed vs 26/13–20 failing on prior arms; C3 base 7 failing → 0 with J6 byte identity; C2 selftest severity-exact. Provisional because (a) the C1 landed-rev matrix is absent and the changed-arm numbers are worktree-only, (b) every measured record behind C2/C3/D6 is untracked at HEAD, (c) live-fleet effect of C1 is nil (0/22 repos exposed), so the operability gain is latent, not observed.
- **discernment: improved, with one disclosed reclassification** — the auditor now catches V-WRITE-RELATIVE and separates unparsed from parsed writes (ConnReadmeIndex confirmed as a true attempted fleet-root write by L1). But the w2 major count drop 3→1 is partly **reclassification**: two of the three base majors are now minor under the status-aware rule. The minor count rise 42→52 is new detection (8 V-PROBE, 2 V-WRITE-UNPARSED), not new defects in seats; V-RECURSIVE stayed at 18 (w1) and 42 (w2) and was not reduced. Report the reclassification in the same sentence as the drop.

## Findings for L1 (calibration)

1. **Artifacts not landed.** `c1-matrix.json`, both `seat-audit-r16-replay-*.json`, both `jj-receipts-*.txt`, `gate-replays-ddb7347.json` are untracked; none exists at ddb7347 or HEAD d7e648d. Fleet-report citations resolve only in the worktree. Commit them or cite as worktree-only.
2. **C1 landed-rev run incomplete.** The changed-arm row is a WORKTREE run; the landed-rev `c1-matrix.json` was in progress and does not exist. The "measured at ddb7347" label for C1 is not yet supported.
3. **C1 notation undefined.** `X/Y` in the context is not defined; the verbatim table above should be checked against `run-matrix.py` output before publishing.
4. **C2 major 3→1 needs the reclassification stated**: RerunGateReplayR14:225,226 moved major→minor by the status-aware rule (unparsed failed calls), not by a seat fix.
5. **C3 populations differ**: base `total=18 skipped=2` vs changed `total=20 skipped=0`. Name the two base-skipped cases.
6. **Gate record inconsistency**: `gate-replays-ddb7347.json` top-level `match: true` vs `expected.gate_sha256_match: false`. Reconcile the gate sha (`c7e8eea5…` vs `e7d2439d…`) before citing a clean replay.
7. **Planned-as-landed risk**: S051–S063 and the jj knowledge entry are not landed; the fleet report must not count them under expansion.
8. **Boundary disclosure**: a names-only `git ls-files --others` pass touched the operator-owned `census/operator-sweep-20261019/` listing (no contents opened). No edits, commits, or installs.

## Commands run (this seat)

- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin cat-file -t ddb7347`
- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-tree --name-only ddb7347 census/round-17/` (+ `tests/fixtures/`, grep r17)
- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin log -1 --format='%H %s' ddb7347`
- `git cat-file -e {ddb7347,HEAD}:census/round-17/<artifact>` for six artifacts (all ABSENT)
- `git status --short -- census/round-17 tools tests`
- `git diff --stat ddb7347 -- tools census tests corpus`; `git diff --stat d7e648d… -- tests/fixtures/r15-preservation-frozen tools census tests`; `git diff --stat ddb7347 d7e648d…`
- `git log -3 --format=…`
- `git ls-files --others --exclude-standard census tools tests` (names only; census/operator-sweep-20261019 listed, not opened)
- `read census/round-17/seat-audit-r16-replay-ddb7347.json:1-60` and `?q=` tallies on both seat-audit records
- `read census/round-17/jj-receipts-{ddb7347,base5fa6017}.txt` (header, summary tails)
- `read census/round-17/gate-replays-ddb7347.json` (head; `?q=.replays|map_values(...)`)

Not run: `souji-census.sh`, `souji-verify.sh`, `souji-vault-verify.sh`, `souji-quarantine.sh`, `run-matrix.py`, `seat-audit-replay.py`, `r17-jj-receipts.sh`, any build/test. No tool installs.

Report: this file. Absolute path: `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-17/w2/ScribeReportSections.md`.
