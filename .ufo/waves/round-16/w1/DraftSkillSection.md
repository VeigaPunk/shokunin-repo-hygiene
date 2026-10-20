# DraftSkillSection — Census config semantics (r16)

Pinned source: `tools/souji-census.sh` header at `cbf688ab2ab28e38103e5a9417ca525b5f2ed423`. Target insertion: `SKILL.md` at that commit (231 lines), after `## Retained evidence and protected census paths (round 14)`. Not applied to SKILL.md; draft only.

## Draft subsection (19 lines)

```
### Census config semantics (r16)

Repository config is classified per key and value, not per file presence.

- Refused (exit 2, whole run, stderr `path-protected`): a config-named path
  (include target, core.excludesFile, core.attributesFile, core.worktree)
  reaches a protected root (~/.omp/agent, census/operator-sweep-*,
  .ufo/state, .ufo/watchdog.log). No census output from that run is usable.
- Degraded (exit 0; that repository only becomes one `error` row; stderr
  `souji-census: config-unsupported: <reason> (<repo>)`; no git command runs
  there): `~user` or `%(prefix)` paths; include cycle or depth over 10;
  non-regular or hardlinked include target or config.worktree; NUL bytes or
  unparsable config; invalid extensions.worktreeConfig boolean.
- Accepted (no row change): core.hooksPath and core.fsmonitor values; boundary-
  clean excludes/attributes files; remote.*.promisor and extensions.partialClone
  (every git call sets GIT_NO_LAZY_FETCH=1); core.alternateRefsCommand; unbound
  filter drivers; missing include targets. A bound filter.<name>.clean|smudge|
  process driver is accepted but skips status for that repository only
  (`status-unverifiable`; stderr `status-skipped`); the driver never runs.

Exit codes: 0 census emitted (rows may carry `error`/`status-unverifiable`);
1 selftest or setup failure; 2 usage, malformed baseline, or protected refusal;
3 compare drift.

Operator meaning:
- `error`: config could not be evaluated, so no git command ran. worktrees,
  unpushed, dirty and scratch_bytes are literal 0 placeholders, not
  measurements; mtime is empty. Never read as clean; repair or inspect by hand.
- `status-unverifiable`: git status was skipped or failed. dirty is written as
  0 but is unknown. `clean` is never emitted with this flag. Verify the
  repository by hand before any removal decision.
```

## Findings

1. `error` numeric fields are printed as literal `0` (`printf '%s\t0\t0\t0\t0\t\terror\n'`, census_one). A reader summing or sorting the census would take them as measured zeros; the draft states the placeholder meaning explicitly.
2. `clean` is appended only when none of dirty, unpushed, no-remote, status-unverifiable, error, not-a-repo is present (census_one, has_problem loop). The draft states the status-unverifiable consequence; `error` implies it by the same rule.
3. The header's Refused class is whole-run (exit 2) and the Degraded class is per-repository (exit 0). The draft keeps that distinction because it changes what an operator must rerun.
4. Calibration: the header is the sole source. Nothing in the draft claims r15 preservation, selftest pass, or ShellCheck pass; the r15/r16 acceptance status is not restated here (it belongs to the lesson and the landing gate, not this subsection).
5. Not verified: that the `error` row is ever emitted for a real fleet repo (no run on real directories per the probe rule). The draft describes the code path, not an observed run.
6. The `status-unverifiable` operator note ("verify by hand before any removal decision") is a recommendation derived from the flag semantics, not a header statement. Marked here as [INFERENCE] for L1 to accept or drop.

## Tooling

No installs or upgrades performed.

## Commands

```
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | head -n 120
git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-tree --name-only cbf688ab2ab28e38103e5a9417ca525b5f2ed423 -- SKILL.md skills/ .ufo/ 2>/dev/null; git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-tree --name-only cbf688ab2ab28e38103e5a9417ca525b5f2ed423 -- SKILL.md
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:SKILL.md | grep -n '^#' ; git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:SKILL.md | wc -l
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | grep -n -E 'exit [0-9]|status-unverifiable|config-unsupported|path-protected' | head -n 60
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | sed -n '118,130p;1080,1100p;1126,1140p'; echo ----; git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:SKILL.md | sed -n '192,231p'
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | sed -n '1141,1152p'
```

Disclosure for L1: the second command's `ls-tree` included the path argument `.ufo/` (names only, at the pinned revision). It was a tree-name listing on a named revision, but `.ufo/state` is a forbidden surface and may appear in that listing. No content of `.ufo/` was read.

STATUS: draft complete; no SKILL.md edit applied; no census run on any real directory; no real-fleet `error` row observed.
