# ConfigRepair — round 15 w1 report

Seat: SoujiR15.ConfigRepair (executor, leaf). Owned file: `tools/souji-census.sh`.
No runtime checks, tests, probes, or fixture runs were executed per contract.
One syntax check (`bash -n`, twice) was run against the file itself only.

## STATUS: INCOMPLETE — file has an unresolved syntax error

`bash -n` reports: `line 1368: syntax error near unexpected token '}'` (the
`}` closing `list_repos`). Edits were in flight when the operator wrap-up
halted work. **The file in tree does NOT parse.** L1 must either complete the
repair or revert to `cc21683` before any acceptance run; do not ship this
state as working.

## What landed (design only, unverified)

Replaced the key-name-blind `case "$keys"` refusal (`git-config-unsupported`)
with a value/effect-aware closure scan:

- **Globals/env**: `GIT_NO_LAZY_FETCH=1` exported (line ~151); `CFG_DRIVERS`
  and `CFG_SOFT_REASON` added; `soft_fail()` maps config failures to a
  per-repo `error` row instead of whole-run exit 2.
- **`guard_git_files`**: added `info/attributes`, `info/sparse-checkout`.
- **`read_meta_file`/`read_meta`**: whole-file gitdir/commondir pointer reads
  (interior LF/CR/NUL refused) — fixes the first-line read fail-open.
- **`handle_commondir`**: symlinked commondir now resolves to its file and is
  read; prints `resolved<TAB>spelled`.
- **`scan_config_file`**: per-key, per-value parsing via
  `git config --file F --no-includes --list -z` (keys split first-dot/last-
  dot; section+var lowercased, subsection preserved). Collects non-empty
  `filter.*.{clean,smudge,process}` drivers; boundary-checks every
  `core.worktree`; queues `include.path`/`includeIf.*.path` targets.
- **`_cfg_condition_applies`**: gitdir:/gitdir/i: matched via `_wm_match`
  (conservative bash-glob superset of wildmatch, `**` collapse handling,
  both spelled+resolved gitdir spellings); onbranch: read from context HEAD;
  hasconfig: always applicable; `worktree:` treated applicable (2.56 fwd);
  unknown keywords inert (2.55). Provably-false conditions are skipped
  entirely — target never opened or checked.
- **`_cfg_include`**: targets boundary-checked via `guard_target` BEFORE any
  read; `~/` expands via HOME, `~user`/`%`/empty are soft-refused; missing
  and directory targets inert (not opened); FIFO/non-regular →
  `git-include-nonregular` (exit 2); nlink>1 refused; cycle/depth-10 →
  soft `error` row (git dies there too).
- **`scan_worktree_cfg`**: `config.worktree` scanned when
  `extensions.worktreeConfig` parses true in common config; metadata
  (nlink/nonregular/symlink) checked unconditionally (worktree list stats it
  for the bare check even when the extension is off — MetadataFlow).
- **`scan_common_config`**: scans common config per worktree context (main +
  each registered worktree admin); extension flag read with
  `git config --type=bool --get` (last-wins, rc1=absent, else soft).
- **`count_dirty`**: `status_path_overrides` builds per-worktree `-c` set:
  hooksPath=/dev/null and fsmonitor=false always; excludesFile/attributesFile
  honor the effective local value boundary-resolved via
  `git -C wt config -z --get` (ABSENT → operator XDG default honored only
  after lexical protected check + resolve_guarded + -f on resolved path;
  INERT → /dev/null; protected reach → whole-run exit 2). Selected-driver
  check: `ls-files -z` (same excludes) | `check-attr -z --stdin filter` |
  awk driver match → `unsupported` → `error` row; never neutralizes a
  selected driver (false-clean avoided).
- **Honest counts**: `count_worktrees`/`count_unpushed`/`for-each-ref`/
  `rev-list` failures now yield `ERR` → `error` flag instead of silent 0.
- **`guard_git_surface`**: rewritten; returns 1 soft / exit 2 protected.
  Callers updated: `census_one` (error row), `worktree_extra_flags`
  (wt-dirty), `list_repos` (`|| true` + still lists repo).
- **Selftest**: new `cfgok-shokunin` (hooksPath, excludesFile covering
  skip.log, promisor=false, worktreeConfig=false + stray config.worktree,
  include.path=inc.cfg, provably-false includeIf gitdir: → missing file) and
  `cfgbad-shokunin` (untracked `.gitattributes * filter=x` + non-empty
  filter.x.clean → error row). Row count 4→6. Audit regex extended with
  fetch-pack/receive-pack/upload-pack/--alternate-refs.
- **Header** rewritten: promisor markers admitted under GIT_NO_LAZY_FETCH;
  per-family effect statements; soft error-row contract documented.
- **`unset -f`**: added `tr wc cat dirname`.

## Deliberately dropped bans (per seat rulings + parent)

`core.hooksPath` (no hook-capable census call; status -c override),
`core.alternateRefsCommand` (no alternate-refs consumer in the tool; audit
regex now guards the command set), `remote.*.promisor`/`partialCloneFilter`/
`extensions.partialClone` presence (admitted under GIT_NO_LAZY_FETCH; missing
objects surface as error/unverifiable rather than silent 0), `fsmonitor`,
`extensions.worktreeConfig=false` and guarded `=true`.

## Known unfinished/limitations (all unverified)

1. **`bash -n` fails at line 1368** — a structural imbalance from in-flight
   edits (the `include-root` if/elif in `list_repos` lost a `fi` mid-edit;
   one was restored at 1334 but the parse still fails). MUST be fixed or
   reverted before L1 acceptance; this is the top blocker.
2. `_cfg_condition_applies` gitdir matcher is a superset approximation; some
   exotic patterns are treated as applicable (safe over-check). `~user` gitdir
   patterns not expanded — treated as `**/…` prefix which may under/over-match
   (residual).
3. Scan order for promisor/partialClone: valueless `extensions.partialClone`
   is not refused at scan time — git dies on it at census, yielding error row
   (honest, matches "config errors map to error").
4. `status_path_overrides` runs `git -C wt config` per worktree — this is a
   post-guard git call whose output feeds `-c`; its own include-following is
   safe because the closure was already scanned.
5. Per-worktree `CFG_DRIVERS` is a union across scanned contexts; a driver
   defined only in the common config's unselected context still triggers a
   selection check (over-cautious, no false clean).
6. hasconfig targets declaring `remote.*.url` → soft error (git dies).
7. `scan_common_config` per-worktree rescan re-reads common config per
   registered worktree — O(worktrees × closure), no shared memo.
8. Linked-worktree `admin` fallback `$entry` when no `.git` pointer — admin
   files scanned but no config (correct: git ignores it).
9. `emit_census` keeps buffered rows: soft-error repos emit `error` rows; any
   protected-path reach still exits 2 with empty stdout (namespace gains
   retained).
10. `count_unpushed`/`count_worktrees` ERR → error flag; pre-existing
    status.showUntrackedFiles/assume-unchanged issues untouched per parent
    directive (residual, recorded not fixed).
11. Dirty-fidelity: honored local excludesFile/attributesFile restore
    pre-r14 semantics for safe paths; /dev/null fallback for inert/protected
    values is disclosed in header.
12. Fixture `tests/fixtures/r15-census-config.py` is owned by ConfigFixture;
    my semantic locks were relayed to it (soft `error` row for
    config-unusable, exit 2 only for protected/non-regular/hardlink,
    per-worktree driver selection via check-attr).

## Checklist for L1 (unrun)

- `bash -n tools/souji-census.sh` — currently FAILS at :1368.
- After parse fix: `bash tools/souji-census.sh --selftest` (rows now 6).
- `python3 tests/fixtures/r14-census-boundary.py` (12/12 namespace).
- `tests/fixtures/r15-census-config.py` once landed (paired red/green).

## Tooling installs

None. Boundary: no lane-root or census recursive searches were issued by
this seat; only explicit file reads/edits and two `bash -n` syntax checks.
No credential/auth/agent.db paths touched.
