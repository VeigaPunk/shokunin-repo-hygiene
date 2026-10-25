# W2Misroot — fleet-root misroot sweep at round-23 tip

**Verdict: survives.** Zero souji-round-23 artifacts at the fleet root. No copy/cmp/delete
sequence is owed to L1.

- Sweep time: 2026-10-25T05:40:31-03:00, root HEAD `40e56126`
- Lane tip: `1026900` (round-23: wave-2 spec, runner decode hardening, prereg mechanism note)
- Command (exactly as specified, no pathspec):

```
$ GIT_OPTIONAL_LOCKS=0 git -C /home/vgpnk/Projects/shokunin status --porcelain -uall
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

`-uall` was used to un-collapse any untracked directory; the untracked set is 5 files, not a
directory summary. `git status --porcelain` (collapsed form) returned the same 5 paths.

## Classification of every untracked entry

| Entry | Class | Evidence |
|---|---|---|
| `.omp/mcp.json` | orchestrator/harness state | 285 B; top-level keys exactly `["$schema","mcpServers"]`, one server `rea`; mtime 2026-10-24 18:07, i.e. before the round-23 lane commits (05:31–05:36). Not a lane artifact. |
| `.scratch/goal-20261025-hyaku-12h.md` | orchestrator state — **never a misroot** | `.scratch/` is orchestrator-owned by contract; file's own line 1: `<!-- ORCHESTRATOR-OWNED run state (hyaku run 6). Not a misroot: lanes and seats never move, copy-then-delete, or edit this file. -->`. hyaku run 6, not souji. |
| `.ufo/state/kotoba.report-baseline` | orchestrator state | `68 e3b0c442…b855` — round counter + sha256 of the empty string, identical format to every tracked baseline (e.g. `.ufo/state/kagi.report-baseline` = `28 e3b0c442…`, `.ufo/state/mori.report-baseline` = `44 e3b0c442…`). `kotoba-shokunin/` exists. |
| `.ufo/state/kotodama.report-baseline` | orchestrator state | `69 e3b0c442…b855`; `kotodama-shokunin/` exists; baseline for the kotodama lane. |
| `.ufo/state/revenger.report-baseline` | orchestrator state | `68 e3b0c442…b855` (byte-identical to kotoba's, sha256 `c0b92e9f…`); `revenger-shokunin/` exists. |

None of the five is souji-round-23. None is another lane's *work product*; the three baselines are
orchestrator bookkeeping for other lanes.

## Why no lane file can appear at the fleet root

`/home/vgpnk/Projects/shokunin/.gitignore:1` is `*-shokunin/`. Verified:

```
$ GIT_OPTIONAL_LOCKS=0 git check-ignore -v souji-shokunin
.gitignore:1:*-shokunin/	souji-shokunin
```

The entire lane directory is invisible to root status, so every lane artifact (committed or not)
is structurally incapable of showing up as a root misroot. The only real misroot channel is a
copy *outside* `souji-shokunin/`, which is what the sweep tests.

Content test for a leaked copy (lane-unique tokens, lane dir excluded):

```
$ grep -rl --exclude-dir=souji-shokunin --exclude-dir=node_modules --exclude-dir=.git \
    -e 'W2Misroot' -e 'round-23/preregistration' .
./.ufo/reports/round-63/revenger.md
./revenger-shokunin/.ufo/waves/round-63/falsify-spec.json
./revenger-shokunin/.ufo/waves/round-63/falsify/swarm-registry.json
./revenger-shokunin/.ufo/waves/round-63/falsify/W2MisrootSweep.md
./revenger-shokunin/.jj/working_copy/tree_state
./tabi-shokunin/.ufo/waves/round-23/w2/swarm-registry.json
./tabi-shokunin/.ufo/waves/round-23/w2/W2CorrRegistry.md
./tabi-shokunin/.ufo/waves/round-23/w2/W2Misroot.md
./tabi-shokunin/.ufo/waves/round-23/gen-w2.mjs
./tabi-shokunin/.ufo/waves/round-23/w2-spec.json
```

Every hit is inside another lane's own gitignored directory (tabi round-23, revenger round-63) or
a revenger report — sibling lanes running the same wave template, not copies of souji files. No
hit at the root tree. Hash cross-check of the lane's round-23 files against the five untracked
root files: no sha256 matches (`54dc8772…`, `2d964d24…`, `b3544a89…`, `74f7a56a…` vs
`3439a008…`, `76f6a821…`, `c0b92e9f…`, `5d709ee8…`).

## Disclosure — live churn during the sweep (not a misroot)

The first sweep (05:38-ish) also listed `?? .ufo/reports/round-44/mori.md` (17061 B, sha256
`10a266bb…`). It was gone by the second sweep. Cause, verified:

```
$ GIT_OPTIONAL_LOCKS=0 git log --oneline -2 -- .ufo/reports/round-44/mori.md
40e56126 round-44: mori report
```

The mori lane committed it mid-sweep and root HEAD advanced to `40e56126`. Classification:
another lane. Consequence for the round: a root sweep is a time-stamped snapshot, and this report
pins HEAD `40e56126` so a re-run can be diffed against it rather than read as a contradiction.

## Disclosure — round-23 report registration at the root (orchestrator state)

```
$ cat .ufo/state/souji.report-baseline
23 e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

The baseline is modified (round `22` → `23`, mtime 05:03 today), and the hash is the sha256 of the
empty string, i.e. the orchestrator has bumped souji to round 23 and expects no report yet. Root
`.ufo/reports/round-23/` holds 11 tracked lane reports and **no `souji.md`**; the lane's own
`.ufo/reports/round-23/` is likewise empty. This is normal mid-round state, not a misroot. No
action for the round beyond finishing the wave and producing the report.

## Lane-local untracked entries (in scope of `souji-shokunin`, correctly placed)

```
$ GIT_OPTIONAL_LOCKS=0 git -C .../souji-shokunin status --porcelain
?? .ufo/waves/round-23/report-draft.md
?? census/operator-sweep-20261019/
```

- `.ufo/waves/round-23/report-draft.md` — souji-round-23, inside the lane, correct location. It is
  untracked at tip `1026900`, so it will not reach the lane commit unless someone commits it.
  **Disclose** to L1: the draft is not yet in the lane history.
- `census/operator-sweep-20261019/` — operator material inside the lane working tree. Contents not
  opened (contract: no operator-sweep contents). Not a fleet-root misroot; operator-owned, leave in
  place.

## What the round must do

- **Accept** the sweep: no misroot, no fix, no delete sequence.
- **Disclose** the two items above (untracked `report-draft.md`; the mori commit that moved root
  HEAD during the sweep).

## Method limits

- Read-only throughout; only `status`, `ls`, `stat`, `cat`, `head`, `sha256sum`, `git log`,
  `check-ignore`, `grep`, `jq`. No git/jj mutation, no writes outside this file.
- `[INFERENCE]` Nothing beyond the quoted commands was executed to establish lane attribution of
  the three baselines; the attribution rests on their byte format matching tracked baselines plus
  the existence of the corresponding `*-shokunin/` directories.
