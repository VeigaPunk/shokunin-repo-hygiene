STATUS: PARTIAL — lesson skeleton drafted in the round-17 section shape with every measured number left as `TBD-L1`; the lesson file itself was not written (contract: this seat writes only its report; L1 lands `corpus/lessons/round-18.md`).

Draft target (for L1 to land verbatim, numbers filled at integration): `/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/lessons/round-18.md`
Baseline: `b576341` (base `b5763415cc67ecff1e8fe56c58c39a6fb106d7a3`). Scope: wave 1 build plus first falsifiers.

---

# Round 18 — census hang bound, a governed process-residue surface, and dangling evidence pointers

Declared claims, in order (baseline `b576341`, the round-17 admitted tip; landed code `TBD-L1`): **C1 operability** (lane axis 8) — no single repository can hang the fleet census, and no lane fixture leaves a blocked process behind. `tools/souji-census.sh` runs each `census_one` in its own process group (`set -m` only around that fork) with stdout to a private temp file; a watchdog sends SIGTERM to the group after the bound and SIGKILL 2 s later; a timed-out repository becomes the row `<repo>\t0\t0\t0\t0\t\terror` plus stderr `souji-census: repo-timeout <N>s <repo>`, other repositories are measured, exit 0. Bound: `--repo-timeout N` or `SOUJI_CENSUS_REPO_TIMEOUT` (integer seconds 1..86400; default 600; invalid → usage exit 2). `census_one` exit 2 (protected refusal) still exits the whole run 2; other nonzero still exits 1. Every fixture subprocess runs with `start_new_session=True` and on timeout `os.killpg(..., SIGKILL)`. The reproduced hang: a FIFO swapped in for `.git/info/attributes` after `guard_git_files` (`tools/souji-census.sh:546-585`) blocks git's `open(2)` forever (outer `timeout 15` → rc 124, zero rows); simulated by a PATH `git` shim. **C2 calibration** (lowest axis, 7) — the lane's authority files must not cite evidence that does not exist. New landing-gate finding `LG-DANGLING-PTR` (`tools/souji-landing-gate.py`, applies only when `--round N` ≥ 18, so pinned historical replays in `census/round-17/gate-replays-expected.json` stay identical). Every repo-relative path token under `census/`, `tests/`, `tools/`, `corpus/`, `.ufo/waves/` cited in SKILL.md, SCORECARD.md, PROVINCE.md, `corpus/QUALITY.md`, `corpus/README.md`, `corpus/knowledge/*.md`, `corpus/lessons/round-N.md` and LOG.md's round-N section must resolve at REV (`path:line` suffix stripped; simple `{a,b}` braces expanded; tokens containing `<`, `>`, `*` or `round-N` skipped; `round-6..11` ranges expanded). A token resolving only in the fleet repo is reported as `fleet`, not a finding; deliberate non-files are exempt only through a committed `corpus/pointer-exemptions.tsv` (path, reason). Also closes Q25(b): a frozen record whose `measured_commit` does not resolve is `LG-FROZEN-MEASURED`. **C3 coverage** (lane axis 8) — process residue becomes a governed surface: a new read-only, dry-run-only `tools/souji-proc-census.sh` lists processes of the current uid whose cwd is deleted, or whose argv names a path under `/var/tmp`, `/tmp` or `/dev/shm` that no longer exists, with pid, ppid, pgid, age, state/wchan, reason and a redacted, truncated command; it never signals anything.

Routed, non-claim fixes (closure applies): R1 `tools/souji-quarantine.sh:246-251` `q_jj_commit_recipe` hardcodes `--as souji`, which fleet helper `scripts/hyaku/jj-lane.sh:516-517` refuses for any id other than the repo's recorded lane id (`jj config get user.name` minus `-shokunin`) or `protocol`. R2 dangling `gate-replays-ddb7347.json` pointers (SKILL.md:163,165). R3 SCORECARD "22 repos" → 21. R4 QUALITY Q7 raw-git rule narrowed to plain repositories by a superseding row.

Frontier step: new SOURCES rows S064+ (opened this round; URL; access 2026-10-20; located quote ≤25 words); one mined mistake (R18-M1); C1 rests on the new rows.

## Measurements

Counting commands, measured at `TBD-L1` unless named. Before-values are recorded from this round's reproductions; after-values are L1's integration run.

- C1 (hang): `bash tools/souji-census.sh --root <FIFO-fixture-root>` at `b576341` → rc 124, zero rows, healthy neighbours lost (before, measured by L1). After: `TBD-L1` (rc 0; row `<repo>\t0\t0\t0\t0\t\terror`; stderr `souji-census: repo-timeout <N>s <repo>`; healthy neighbour rows present). Bound validation: `--repo-timeout 0|x|86401` → usage exit 2 `TBD-L1`. Lane-fixture orphans: `ps -eo pid,ppid,pgid,etimes,stat,wchan,args` filtered to dead `/var/tmp` cwd or argv: before 58 (`census/round-18/leaked-procs-before-1631.txt`, r15-census-config `r-inc-fifo rev-parse`, r17-census-hygiene `d2-fifo` status); after red-arm fixture run `TBD-L1` (required: 0).
- C1 matrix: `python3 census/round-17/run-matrix.py --changed <rev> --output <f>` (r18 arm `TBD-L1`); `bash -n` and `shellcheck -S warning` on every arm: `TBD-L1`.
- C2 (gate): `python3 tools/souji-landing-gate.py --root <lane> --rev b576341 --round 18` findings before → `TBD-L1` (L1 sweep at `b576341`: 281 tokens, 18 unresolved; among them `census/round-17/gate-replays-ddb7347.json` (SKILL.md:163,165) and `census/round-17/jj-receipts-ddb7347.txt` (corpus/knowledge/jj-colocation-receipts.md:2,44,126,148), the rest deliberate or fleet-relative). Changed gate `--rev <tip> --round 18` findings after → `TBD-L1` (required: 0). Gate selftest `TBD-L1`. Historical replays (`python3 census/round-17/gate-replays.py`) → match `TBD-L1` (required: identical to `census/round-17/gate-replays-expected.json`).
- C3 (residue): residue classes the lane governs before → after: before 0 (no surface); after `TBD-L1`. Orphans detected by `tools/souji-proc-census.sh` vs an independent counter (`ps` + `/proc/<pid>/cwd` readlink): `TBD-L1`. Read-only check: `TBD-L1`.

## Mistakes

| id | class | evidence pointer | captured-by | fix |
|---|---|---|---|---|
| R18-M1 | Evidence pointers to files that were never committed were published in an admitted knowledge entry and in SKILL. The suffix `ddb7347` names the round-17 landing revision, but the committed records are `4f48343` and `base5fa6017`. Nothing in the gate checked that a cited path resolves. | `corpus/knowledge/jj-colocation-receipts.md:2,44,126,148` cites `census/round-17/jj-receipts-ddb7347.txt`; the committed files are `census/round-17/jj-receipts-4f48343.txt` and `jj-receipts-base5fa6017.txt` (verified by `ls census/round-17/`). SKILL.md:163,165 cites `census/round-17/gate-replays-ddb7347.json`; the committed file is `census/round-17/gate-replays-4f48343.json`. | none → `LG-DANGLING-PTR` (new gate finding, round ≥ 18; sweep at `b576341` shows the two tokens) | repoint each cite to the committed revision (or land the missing record); `LG-DANGLING-PTR` makes an unresolved repo-relative token a finding at round ≥ 18; deliberate non-files need a committed `corpus/pointer-exemptions.tsv` row. |
| R18-M2 | The round-17 fixtures left blocked orphan processes: `git status` / `rev-parse` on a FIFO that the fixture never unblocked. Each fixture ran git without a process-group kill, so a red arm (the intended hang) persisted after its `timeout` returned. | `census/round-18/leaked-procs-before-1631.txt` (58 processes in `/var/tmp` directories that no longer exist, from `r15-census-config` `r-inc-fifo rev-parse` and `r17-census-hygiene` `d2-fifo` status). | none → session kill (`TBD-L1` process-kill record) + Q30 | every fixture subprocess runs with `start_new_session=True`; on timeout `os.killpg(..., SIGKILL)`; `tools/souji-proc-census.sh` reports residue read-only; a red arm must leave 0 blocked processes (`TBD-L1` measured). |
| R18-M3 | The quarantine recipe hardcoded the souji lane id. `q_jj_commit_recipe` prints `jj-lane.sh commit … --as souji`, which the fleet helper refuses for any id other than the repo's recorded lane id or `protocol`, so the printed operator recipe fails in every other lane. | `tools/souji-quarantine.sh:246-251` (`printf 'jj-lane.sh commit %s --as souji …'`); `scripts/hyaku/jj-lane.sh:516-517` (fleet helper refusal). | closure R1 | derive the id from `jj config get user.name` minus `-shokunin`, or emit the operator placeholder; `TBD-L1` selftest. |

## Gate

### Claim decisions (author; outside admission pending)

- **C1 operability — `TBD-L1`.** Against `b576341` the changed census completes a FIFO-swapped repository in ≤ bound + 2 s, measured by `TBD-L1`; healthy neighbour rows survive. Not claimed: no-harm against the pre-fix matrix arms beyond the measured arms; TOCTOU swaps inside a repository are bounded, not prevented.
- **C2 calibration — `TBD-L1`.** Scoped to the repository-relative tokens the gate reads (listed in the claim); the rule is literal path resolution, so it does not judge whether the cited file says the right thing. `LG-DANGLING-PTR` is inert below round 18 by design.
- **C3 coverage — `TBD-L1`.** Scoped to processes whose cwd is deleted or whose argv names a missing `/var/tmp`, `/tmp` or `/dev/shm` path, of the current uid. The census is dry-run only; it does not clean. Not claimed: completeness against processes not matching these predicates.
- **Rejected / not claimed:** `TBD-L1` (L1 records rejected alternatives at integration).

### Sources opened this round (URL · access 2026-10-20 · located quote ≤25 words)

- **S064** `TBD-L1` (C1 rests on it; opened by the wave-1 frontier step; quote located by a re-opening seat).
- **S065**+ `TBD-L1`.

Registry changes (old → new): `TBD-L1` (S064+ absent → opened 2026-10-20, recheck on-release; used-by per row).

Source census `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji`: start `TBD-L1`; end `TBD-L1` (recorded in the report).

## Seat-reported failures

Round 18 (every gate-channel STATUS line, flagged by `python3 tools/souji-landing-gate.py --root <lane> --rev b576341 --round 18` before carry: `TBD-L1` markers, `TBD-L1` uncarried; quoted verbatim, disposition on the same line):

- `TBD-L1`

Non-vocabulary defect findings carried by reading: `TBD-L1`.

## Corrections

- **R1 (routed, closure applies).** `tools/souji-quarantine.sh:246-251` hardcodes `--as souji`; see R18-M3. Fleet helper `scripts/hyaku/jj-lane.sh:516-517` is the refusal point; the fix is in the Souji lane only.
- **R2 (routed, closure applies).** Dangling `census/round-17/gate-replays-ddb7347.json` pointers at SKILL.md:163,165; re-cite `census/round-17/gate-replays-4f48343.json` or the committed replay record; see R18-M1.
- **R3 (routed, closure applies).** SCORECARD "22 repos" → 21 (fleet count).
- **R4 (routed, closure applies).** QUALITY Q7 raw-git rule narrowed to plain repositories by a superseding row; the jj-colocated lanes are governed by the receipts entry.
- `TBD-L1`: dangling `jj-receipts-ddb7347.txt` cites at `corpus/knowledge/jj-colocation-receipts.md:2,44,126,148` (R18-M1; the closure's routing is not yet decided, so this lesson records the fix as `TBD-L1`).

## Process

- L1 holds the §3 planner seat (the validator rejects `planner`); bounded planning data-walks rode scout/connector items.
- Wave 1 (build): `TBD-L1` seats (`TBD-L1` by role). Dead seats: `TBD-L1`.
- Wave 2 (falsify): `TBD-L1` seats.
- Round total: `TBD-L1` seats. Seat models: `TBD-L1`.
- Tool installs/updates: `TBD-L1` (record tool, version, channel, reason; pacman is paused host-wide, so no pacman channel).

## Residuals (open)

- Census: the TOCTOU FIFO swap inside a repository is bounded by the watchdog, not prevented (round-17 sentinel F3); `TBD-L1` for whether the bound covers every blocking path (a symlink loop or out-of-gitdir symlink at `info/attributes` keeps the whole-run symlink refusal, documented).
- Inherited contractions against `a31642d` (L0 `souji | round-16`), `:(optional)` on `core.worktree`, nested-layout pathspec excludes, `emit_compare` against `error` rows, newline worktree paths — unchanged.
- Receipts: census `unpushed` column branch-based in jj lanes; `census/round-13/run-verification.py:384` and `census/round-14/cache-demonstration.py:166` still pin `HEAD`; keep-ref lifetime unmeasured (only `jj util gc` removes them).
- Gate: `LG-DANGLING-PTR` checks path resolution only, not content; wrap-truncated quotes and non-vocabulary STATUS lines remain invisible to it.
- Operator: disposition of `census/operator-sweep-20261019/` (L0 question; not opened by any seat this round).
- Q30 and the session-kill record: `TBD-L1`.

---

## Seat notes (for L1)

- The three candidate mistakes are grounded: R18-M1 pointers and their absence were confirmed by directory listing (`census/round-17/` holds `jj-receipts-4f48343.txt`, `jj-receipts-base5fa6017.txt`, `gate-replays-4f48343.json`, not the `ddb7347` names); R18-M3 was confirmed by reading `tools/souji-quarantine.sh:246-251`; R18-M2's evidence file `census/round-18/leaked-procs-before-1631.txt` exists.
- Not run (this seat is a drafter, no executable checks assigned): gate, census, matrix, `ps` counts. Every `TBD-L1` is an unrun check, not a pass.
- Tools installed/updated by this seat: none.
