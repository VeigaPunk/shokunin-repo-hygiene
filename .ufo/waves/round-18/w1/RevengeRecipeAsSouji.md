STATUS: DONE — `--as souji` was a deliberate, disclosed pin authored while helper v1 accepted any id; helper v2's lane-id refusal (landed 23 min after the recipe) retroactively made it souji-only. Routed R1 owner-id fix is the correct reconciliation.

Seat `SoujiR18.RevengeRecipeAsSouji` · 2026-10-20 · lane `/home/vgpnk/Projects/shokunin/souji-shokunin` · base `b5763415cc67ecff1e8fe56c58c39a6fb106d7a3` (b576341) · leaf, no subagents, no clones, no writes outside this report.

## Question

Was the `--as souji` pin in `tools/souji-quarantine.sh` `q_jj_commit_recipe` a souji-only recipe intended for souji's own repo, or an oversight?

## Verdict

**Intended pin, overtaken assumption — not an authoring oversight, but its souji-only effect is accidental.** The r17 seat wrote and disclosed the pin consciously; at authoring time (fleet helper v1) it was a *souji default* that worked from any jj lane repo, because v1's `commit` accepted any well-formed `--as` id. Fleet helper v2 added the per-repo lane-id refusal 23 minutes after the recipe landed, converting the default into a hard souji-only recipe. The override the r17 disclosure promises does not exist anywhere in the tool. The r17 closure already routed exactly this as R1 (owner-id fix), and its fail-closed assessment is correct.

## Evidence chain

### 1. Birth of the recipe — single commit, no later refinement

```
$ git -C <lane> log -L '/q_jj_commit_recipe/,+6:tools/souji-quarantine.sh' --oneline
ddb7347 round-17: C1 census D1/D2, C2 seat-audit precision + r16 transcripts bundle, C3 jj-aware receipt roots/novelty, D6 gate exact ids + replays, vadv54 stub, regenerate verdict
$ git -C <lane> log --oneline -S '--as souji' -- tools/souji-quarantine.sh
ddb7347 …
```

Only `ddb7347` (2026-10-20 12:42:34 -0300) ever touched the function or the pin. Current worktree text, `tools/souji-quarantine.sh`:

- :245 `q_jj_colocated() { [ -d "$1/.jj" ] && [ -e "$1/.git" ]; }` — any colocated repo qualifies.
- :246-251 the recipe: `printf 'jj-lane.sh commit %s --as souji -m %s -- %s %s' …`.
- Emitted at :549 (dry-run) and :574 (real run, after `QSTAGE stage2`), both gated `tracked=1 && q_jj_colocated` — i.e. **any** jj-colocated repo, tracked target only.
- CLI contract :26-29: `<repo>` is "the git repo the targets belong to" — no restriction to souji's repo anywhere in the tool.

### 2. The pin is documented in the landing spec, with a promised override

`.ufo/waves/round-17/w1/QuarantineJjRoots.md` (grep `q_jj_commit_recipe|--as souji`, one grep, the only `JjQuarantineRecipe*`-named candidate in the dir listing — none exists):

- change-table row 5 (report :21): the CMD `jj-lane.sh commit <repo> --as souji -m … -- <rel> <qpath>` naming BOTH paths is listed as **delivered contract**, not incidental.
- :76-78: the dry-run CMD example repeats the pin.
- :113: "the recipe line is guidance, not enforcement" (F1 hazard returns if the operator commits with plain git).
- :114 (risk #3): **"The recipe pins `--as souji`; a different lane identity must override it."**

So the seat knew non-souji identities exist and disclosed the pin — deliberate, not a typo.

### 3. The promised override does not exist

```
$ grep -n -E '--as|SOUJI_Q_LANE|lane_id' tools/souji-quarantine.sh
246|q_jj_commit_recipe() { …
*247|  printf 'jj-lane.sh commit %s --as souji -m %s -- %s %s' \
```

The only `--as` token in the 1842-line tool is the hardcoded printf. No flag, no env, no derivation. "A different lane identity must override it" resolves to hand-editing the printed string — the exact failure path :113 warns leads back to the F1 half-commit hazard.

### 4. Fleet helper timeline — the refusal postdates the recipe by 23 minutes

```
$ git -C /home/vgpnk/Projects/shokunin show -s --format='%h %ci %s' 67a3123 14df5b9 23efcab
67a3123 2026-10-20 11:11:34 -0300 ops(hyaku): jj lane VCS … jj-lane.sh helper (init/commit/push/state) …
14df5b9 2026-10-20 13:05:01 -0300 ops(hyaku): jj-lane.sh v2 … foreign-identity guards …
23efcab 2026-10-20 16:03:19 -0300 round-17: souji L0 questions …
```

- Helper **v1** (`67a3123`, 11:11): `git show 67a3123:scripts/hyaku/jj-lane.sh | grep -n -E '\-\-as|lane_id|protocol'` → `--as` parsed at :172, **no** `lane_id`/`protocol` guard anywhere. Any lane id was accepted.
- Recipe lands in the lane at **12:42** (`ddb7347`) — under v1 semantics, `--as souji` was valid from every jj repo. A *default*, not a *restriction*.
- Helper **v2** (`14df5b9`, **13:05**) adds, at the current `scripts/hyaku/jj-lane.sh:516-517`:

  ```bash
  [ "$id" = "$lane_id" ] || [ "$id" = protocol ] || {
    err "--as must be the lane id ($lane_id) or protocol: $id"; exit 1; }
  ```

  with `lane_id_jj()` at :105-111 = `jj --ignore-working-copy config get user.name`, strip `-shokunin` (:108-109), written at init as `user.name=${id}-shokunin` (:427); plus the init-only `snapshot.auto-track = "none()"` guard (:519-521).

### 5. Resulting behavior split

For a repo init'd by `jj-lane.sh init <dir> souji` (the souji lane's own repo — `user.name` `souji-shokunin` → lane id `souji`): the printed recipe passes both guards and is correct. `[INFERENCE]` the lane repo is init'd this way: the r17 closure ran `jj-lane.sh state`/push through it and ddb7347 is authored `souji-shokunin <souji@shokunin.local>`.

For every sibling lane repo (`mint`, …): the recipe is emitted unchanged, then refused:

```
err: --as must be the lane id (mint) or protocol: souji     (exit 1)
```

Fail-closed, no damage — the closure's assessment. But the printed runbook is unusable as printed, and the fallback (hand-commit, plain git) re-opens the F1 half-commit hazard the recipe exists to prevent. Additional precondition even for souji-id repos: init'd by the helper (auto-track guard), else refusal "snapshot.auto-track is not …".

### 6. The lane's own authority already contradicted the pin

`corpus/lessons/round-17-verifier-spotcheck.md` (r17 closure, non-author integrator), R1 row: *"…hardcodes `--as souji`. `scripts/hyaku/jj-lane.sh:516-517` refuses any `--as` other than the repo's lane id or `protocol`, so the printed recipe fails for every sibling jj lane. SKILL.md's own rule says 'the OWNING lane's helper … `--as <owner-id>`'. This fails closed (the helper refuses; no damage), but the report's 'quarantine prints the helper runbook' is wrong for every repo except souji's own. Fix the recipe to use the owner id and add a fixture assertion."* I did not open SKILL.md itself (not a named file for this seat); the quote is the closure's.

## Reconstruction

1. **Intended?** Yes, deliberately: the pin is in the landing report's change table as delivered contract and disclosed as risk #3 (:114). Not an unnoticed hardcode.
2. **Souji-only intended?** No. At authoring time (helper v1) nothing restricted `--as`, so the seat's mental model was "souji is the default identity"; the risk note even contemplates other identities overriding it. The souji-only *effect* is an accident of ordering: helper v2's foreign-identity guard landed 23 minutes after `ddb7347` and retroactively invalidated the pin for every non-souji lane, and the closure (16:xx) caught it as R1.
3. **Oversight?** The residual defect is real and twofold: (a) the promised override mechanism never existed in the tool — the disclosure describes a capability that is not there; (b) the recipe contradicts the lane's own SKILL owner-id rule. Both are exactly what R1 routes; the r17 admission was correct to carry it rather than block.

## Smallest fix (advisory, for the R1 executor)

In `q_jj_commit_recipe` (:246-251), derive the owner id the same way v2 does, without invoking jj: parse `user.name = "<id>-shokunin"` from the repo's jj repo config (`$1/.jj/repo/config.toml` — `[INFERENCE]` standard colocated layout; v2 writes it via `jj config set --repo` at :427) and emit `--as <id>`; if the identity is absent or lacks the `-shokunin` suffix, emit the recipe with a `<owner-id>` placeholder plus a stderr note (stay fail-closed; never fall back to a git add/commit recipe). Add the closure-required fixture assertion: a non-souji lane-id colocated fixture whose emitted CMD carries that id and no `git (add|commit)` line. Rejected alternative: `--as protocol` (accepted by :516 for any lane) — it would pass the guard but misattributes lane-owned staging commits and still contradicts the SKILL owner-id rule.

## Commands run (all read-only; exact)

1. `git -C /home/vgpnk/Projects/shokunin/souji-shokunin log -L '/q_jj_commit_recipe/,+6:tools/souji-quarantine.sh' --oneline` → single commit ddb7347, hunk adding :245-250.
2. `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show ddb7347 --stat` → r17 landing; `tools/souji-quarantine.sh` +186/-12 among 160 files.
3. `git -C /home/vgpnk/Projects/shokunin/souji-shokunin log --oneline -S '--as souji' -- tools/souji-quarantine.sh` → only ddb7347.
4. `git -C /home/vgpnk/Projects/shokunin show -s --format='%h %ci %s' 67a3123 14df5b9 23efcab` → 11:11:34 / 13:05:01 / 16:03:19 -0300.
5. `git -C /home/vgpnk/Projects/shokunin show 67a3123:scripts/hyaku/jj-lane.sh | grep -n -E '\-\-as|lane_id|protocol'` → `--as` at :172 only; no guard in v1.
6. `grep` (tool) `q_jj_commit_recipe|--as souji` on `.ufo/waves/round-17/w1/QuarantineJjRoots.md` (full read of that file too) → change-table row 5, CMD :76-78, risk :114.
7. `grep` (tool) on `tools/souji-quarantine.sh`: `q_jj_commit_recipe` → :246, :549, :574; `--as|SOUJI_Q_LANE|lane_id` → :247 only.
8. `read` of `tools/souji-quarantine.sh` (:1-63 header/CLI, :225-280 recipe region) and `scripts/hyaku/jj-lane.sh` (:495-545 commit guards, `lane_id_jj` :105-111, init :427).

## Bounds conformance

Probe rule: only exact named files read/grepped (`tools/souji-quarantine.sh`, `.ufo/waves/round-17/w1/QuarantineJjRoots.md` — named plus dir-listed, no `JjQuarantineRecipe*.md` present, `corpus/lessons/round-17-verifier-spotcheck.md`, `scripts/hyaku/jj-lane.sh`); read-only `git log/show -S/-L` on the two named repos; no jj invocation; no exec items; nothing signalled; no installs or upgrades (`pacman`/uv/npx untouched — nothing needed). Not audited under my named-file bounds, flagged for L1: sibling r17 reports likely also cite the recipe (candidates from the dir listing, unopened: `SentinelJjFixture.md`, `RevHelperQuarantine.md`, `VaultJjRoots.md`, `VerifyJjRoots.md`, `SimplifyJjRoots.md`), and the r17 wave-plan task text (whether the dispatcher specified the literal `--as souji`) was not readable within bounds.