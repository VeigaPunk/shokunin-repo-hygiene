# ScoutMisroot — fleet misroot sweep, souji round 23

## Status

STATUS: PASS — fleet `git status --porcelain` (no pathspec) at fleet HEAD 23629d9885883ff452d896e6a8c00259da516d03 yields 5 untracked entries; none names souji or round-23 by path or content, none carries lane bytes. Misroots: 0. Copy candidates: 0. Nothing deleted, moved, or copied; `.scratch/` and `.ufo/state/` contents not read.

## Evidence

Contract read first: `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-23/preregistration.txt` (lane base `1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd`, matches lane `git rev-parse HEAD`). Axis of this seat: coverage (8) on the fleet-hygiene question; calibration (7) and operability (8) unharmed (no writes outside the report).

1. Sweep, verbatim (`git -C /home/vgpnk/Projects/shokunin status --porcelain`, 2026-10-25):

```
 M .ufo/state/chousa.report-baseline
 M .ufo/state/kagi.report-baseline
 M .ufo/state/kaidoku.report-baseline
 M .ufo/state/kake.report-baseline
 M .ufo/state/kama.report-baseline
 M .ufo/state/kasegi.report-baseline
 M .ufo/state/kengaku.report-baseline
 M .ufo/state/kumitate.report-baseline
 M .ufo/state/mado.report-baseline
 M .ufo/state/mori.report-baseline
 M .ufo/state/souji.report-baseline
 M .ufo/state/tabi.report-baseline
 M .ufo/state/tameshi.report-baseline
 M .ufo/state/tsukuroi.report-baseline
 M .ufo/watchdog.log
 M scripts/hyaku/hyaku.env
 M scripts/hyaku/lane-addendum.md
?? .omp/mcp.json
?? .scratch/goal-20261025-hyaku-12h.md
?? .ufo/state/kotoba.report-baseline
?? .ufo/state/kotodama.report-baseline
?? .ufo/state/revenger.report-baseline
```

2. `git ls-files --others --exclude-standard` → exactly the 5 `??` paths above. `git check-ignore -v` on each → `(not ignored)` for all 5 (so they are genuine porcelain pollution, not ignored scratch).

3. `stat -c '%n %s %y'`:
   `.omp/mcp.json` 285 B 2026-10-24 18:07:20; `.scratch/goal-20261025-hyaku-12h.md` 2667 B 2026-10-25 04:34:55; `.ufo/state/kotoba.report-baseline` 68 B 2026-10-24 22:45:19; `.ufo/state/kotodama.report-baseline` 68 B 2026-10-25 03:23:34; `.ufo/state/revenger.report-baseline` 68 B 2026-10-25 03:23:38.

4. Name test on untracked entries — `git ls-files --others --exclude-standard | grep -i -E 'souji|round-23'` → no output, rc=1. Content test on the three readable candidates — `grep -l -E 'souji|round-23' .ufo/state/{kotoba,kotodama,revenger}.report-baseline` → no output, rc=1. `.scratch/goal-20261025-hyaku-12h.md` was not opened (`.scratch/` contents are out of bounds); its classification rests on path convention alone, which the context declares decisive.

5. `.omp/mcp.json` content shape (keys only): `json.load` → top-level `['$schema','mcpServers']`, `mcpServers=['rea']`; `grep -n -E 'souji|round-23|shokunin'` → no hit. mtime predates the round-23 wave by ~9 h.

6. Baseline-shape test: `git cat-file -s HEAD:.ufo/state/{souji,mori,tabi}.report-baseline` → 68, 68, 68. The three untracked baselines are 68 B, i.e. the same per-lane baseline shape as the 14 tracked ones. `git cat-file -s HEAD:.ufo/state/kotoba.report-baseline` → fatal (exists on disk, not in HEAD), consistent with "lane added this round, baseline not yet committed".

7. Repo topology: `git -C souji-shokunin rev-parse --show-toplevel` → `/home/vgpnk/Projects/shokunin/souji-shokunin` (separate repo, HEAD = lane base). Fleet `.gitignore` contains `*-shokunin/`, plus `!scripts/fixtures/sources-census/**/*-shokunin/`, `.ufo/waves/*/*-scratch/`, `r80-baseline-frozen-worktree/`. Lane has no `.gitignore`.

8. Other-lane repos named by the untracked baselines exist: `/home/vgpnk/Projects/shokunin/{kotoba,kotodama,revenger}-shokunin`.

9. Precedent for the omp config: `kake-shokunin/.ufo/waves/round-51/w1/ScoutMisroot.md:26` and `tameshi-shokunin/.ufo/waves/round-41/w1/ScoutMisroot.md:41` both classify `.omp/mcp.json` as tool/operator config, not a lane artifact; `kotoba-shokunin/.ufo/waves/round-59/misroot-sweep.txt:16` shows the same `??` line persisting across rounds.

10. Fleet-side script ownership: `scripts/hyaku/lane-addendum.md` and `hyaku.env` are tracked fleet orchestrator scripts (`git ls-tree -r --name-only HEAD -- scripts/hyaku/` lists them); last commit touching them is `23753dbf` (2026-10-24, orchestrator §10 rework). The only `souji` token in `lane-addendum.md` is line 336, policy prose enumerating lanes lacking a `considerthese/` dir.

## Findings

1. **Zero misroots.** No untracked fleet entry names souji or round-23, and no untracked fleet entry is byte-plausible lane output. Every lane artifact this round lives under `/home/vgpnk/Projects/shokunin/souji-shokunin/` (separate repo, HEAD `1208bfb`), which the fleet `.gitignore` pattern `*-shokunin/` keeps out of fleet porcelain. Confirmation: lane has 10 uncommitted paths while fleet porcelain shows none of them.

2. **Table — untracked entries (the decision surface).** No row is a copy candidate, so no `cmp` pair is exercised; per row the L1's exact negative proof is given, plus the canonical pair form it would use if the row ever became a copy.

| path (fleet) | owner | action | exact command the L1 uses |
|---|---|---|---|
| `/home/vgpnk/Projects/shokunin/.omp/mcp.json` | operator (omp harness MCP config; 285 B, `mcpServers={rea}`, no souji/round-23 token, mtime 2026-10-24 18:07; precedent kake r51 / tameshi r41) | leave alone | `test ! -e /home/vgpnk/Projects/shokunin/souji-shokunin/.omp/mcp.json` |
| `/home/vgpnk/Projects/shokunin/.scratch/goal-20261025-hyaku-12h.md` | orchestrator (`.scratch/` is orchestrator-owned by design; NEVER a misroot; contents not read) | leave alone | `test ! -e /home/vgpnk/Projects/shokunin/souji-shokunin/.scratch/goal-20261025-hyaku-12h.md` |
| `/home/vgpnk/Projects/shokunin/.ufo/state/kotoba.report-baseline` | orchestrator run state for other lane kotoba (68 B = tracked baseline shape; no souji/round-23 token; `kotoba-shokunin/` repo exists) | leave alone | `test ! -e /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/state/kotoba.report-baseline` |
| `/home/vgpnk/Projects/shokunin/.ufo/state/kotodama.report-baseline` | orchestrator run state for other lane kotodama (68 B; no souji/round-23 token) | leave alone | `test ! -e /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/state/kotodama.report-baseline` |
| `/home/vgpnk/Projects/shokunin/.ufo/state/revenger.report-baseline` | orchestrator run state for other lane revenger (68 B; no souji/round-23 token) | leave alone | `test ! -e /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/state/revenger.report-baseline` |

   Canonical copy-row form (not used this round, for the L1's template): `cmp /home/vgpnk/Projects/shokunin/<path> /home/vgpnk/Projects/shokunin/souji-shokunin/<path>` must exit 0 byte-exact **before** the fleet copy is deleted; with the fleet copy deleted the same `cmp` must exit nonzero (ENOENT).

3. **Tracked-modified entries are all orchestrator-owned, leave alone:** the 14 `M .ufo/state/*.report-baseline` (including `souji.report-baseline` — the orchestrator writes lane baselines, the lane does not), `M .ufo/watchdog.log`, `M scripts/hyaku/hyaku.env`, `M scripts/hyaku/lane-addendum.md`. None is a lane artifact; the only `souji` occurrence in the addendum (line 336) is orchestrator policy prose.

4. **`.omp/mcp.json` is unignored and permanent pollution** (present as `??` in at least rounds 41, 51, 59, and now 23-of-souji). It costs every round's sentinel a decision row. The remedy (a fleet `.gitignore` line) is an operator/L1 call — not this seat's write scope. [INFERENCE on remedy effect; the persistence itself is observed.]

5. **Inverse-direction item for the L1, no action taken:** the lane working tree carries untracked `census/operator-sweep-20261019/` (operator-owned sweep contents; 25 entries listed by name only — contents never read, per bound). It must never be staged. It also sits inside C1's K4 predicate: `git show HEAD:corpus/pointer-exemptions.tsv | grep -c '^uncommitted:'` → **0**, so at this moment every lane working-tree path is an uncounted mismatch. The predicate-legal repair is a committed `uncommitted:` exemption row for the operator-owned path (deleting it is barred by the bound); committing it is barred by "no operator-sweep contents staged". This is C1's territory — flagged, not touched.

6. **Lane porcelain is live-mutating while siblings run:** two read-only lane `status --porcelain` calls minutes apart returned 11 then 10 paths. Any K4 reading is valid only for the instant it is taken; the landing-time reading is the one that counts. [observed]

7. **Stated blind spot of this sweep:** because fleet `.gitignore` ignores `*-shokunin/`, `.ufo/waves/*/*-scratch/` and `r80-baseline-frozen-worktree/`, a lane byte written under any of those paths is invisible to `git status --porcelain`. This sweep therefore proves "no misroot at a visible fleet path"; it does not prove absence inside ignored paths, which are out of scope by construction (and `.scratch/`, `r80-baseline-frozen-worktree/` are operator/orchestrator-owned).

## Attack log

No attack filed — this seat is a hygiene sweep, not a counter attack. One calibration note recorded in Findings 6 (K4 reads a live-mutating tree); the frozen predicate is not proposed for change.

Tooling: no install or upgrade performed this run.
