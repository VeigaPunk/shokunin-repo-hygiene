# S66SentinelScope — scope and safety audit, souji round 66 (post-freeze w1)

Seat: S66SentinelScope (sentinel). Read-only mandate: no host-changing commands, no sysctl/sudo/pacman,
no git mutations outside a self-created scratch clone (none created; only `git show` reads against the lane).
Scratch: /fast/scratch/hyaku/souji-r66/S66SentinelScope/ (base writer bytes for diffing only).
Method: source reading only. Instruments were NOT executed by this seat; candidate audit is byte-level.

## Part A — instruments (frozen at 4576f101a9200206de00ef00923dd38a7b2dbc7d)

### A1. c1-counter.py — write surface: CONFIRMED, only under --work and --receipt

Exhaustive sweep of write primitives (open-for-write, makedirs, rmtree, copyfile/copytree, symlink, chmod,
replace) — every site resolves under the `--work` join or is the explicit `--receipt` path:

- Slot extraction: `work/slots/{base,new}.py` via write_exec (c1-counter.py:577-581, :906-911).
- Regress fixture copy: `work/regress/r60-receipt-write.py` (:921-925); lane clone `work/laneref` via
  `git clone --shared` (:590-594) — reads lane objects through alternates, writes nothing to the lane.
- Per-case fixtures: `build_repo` rmtree+creates `work/<letter>/<which>/repo` (:335-360); pre-run
  mutations `mutate()` write only inside the fixture repo (:375-442); `build_case` adds
  `work/<letter>/<which>/out` (:450). Wrapped-command helper code strings (EDIT_CODE/RESTORE_CODE/
  CHMOD_CODE/RETARGET_CODE, :186-189, :242-247) are always argv-joined onto the fixture repo path
  (inrun_argv, :251-279) — no path escapes the case dir.
- Selftest: `work/selftest/**` synthetic TSVs and stub slots (:763-810).
- Receipt: `write_receipt` opens exactly `ns.receipt` (:747-756). This is the ONE caller-chosen
  write target and it carries NO guard (see A4 findings).
- No `tempfile` import, no mkstemp/mkdtemp, no other /tmp use anywhere. The only /tmp mentions are the
  refusal guard itself (:862-868).

### A2. clean_env() — CONFIRMED, strips all five required groups

c1-counter.py:313-324. Explicitly dropped: GIT_DIR, GIT_WORK_TREE, GIT_INDEX_FILE,
GIT_OBJECT_DIRECTORY, GIT_ALTERNATE_OBJECT_DIRECTORIES, GIT_REPLACE_REF_BASE, GIT_CONFIG_COUNT,
GIT_CONFIG_PARAMETERS, GIT_CONFIG_GLOBAL, GIT_CONFIG_NOSYSTEM, GIT_CONFIG_SYSTEM,
GIT_NO_REPLACE_OBJECTS; plus prefix drops GIT_CONFIG_KEY_* and GIT_CONFIG_VALUE_* (:320), which cover
the numbered pair form GIT_CONFIG_KEY_<n>/GIT_CONFIG_VALUE_<n> at any count. That is the complete
documented git config-env surface; every name the assignment requires (GIT_CONFIG_*,
GIT_OBJECT_DIRECTORY, GIT_ALTERNATE_OBJECT_DIRECTORIES, GIT_REPLACE_REF_BASE, GIT_NO_REPLACE_OBJECTS)
is stripped. Sets GIT_OPTIONAL_LOCKS=0 (:321). Note: clean_env is used for the counter's OWN git calls
(git_run :327-329, git_show :543-548, clone :592-594) and for the writer subprocess env baseline
(run_slot :494-513) — E-row injection values are re-added ONLY via run_slot env_extra, never into
counter git calls.

### A3. E-row fixtures — CONFIRMED beside the repo (case dir), never inside tools/

mutate() env_kind branch (:425-442): `case_dir = os.path.dirname(repo)` =
`work/<letter>/<which>/` — excludes.txt (:427-429) and E3's global.gitconfig (:430-432) are written
at case-dir level, beside repo, not inside the fixture repo's tools/. E4's objects-copy and E5's
alternates-empty live inside the fixture repo's own .git (:433-440); E6 writes nothing (env value
only, case_env :483-486). The injection values are passed to the writer subprocess env only via
case_env → run_slot env_extra (:489-517); the counter's own git calls never see them (clean_env
strips the same names it injects — no leak path from case_env into git_run).

### A4. Host exposure of E-row fixtures — NO host/global config write; NO write outside work

- No fixture sets a host-global config. The E3 file literally named "global.gitconfig" is written
  under the case dir (:430-432) and referenced only through the writer subprocess's
  GIT_CONFIG_GLOBAL value (:476). The host's real ~/.gitconfig is never read by that row (the
  writer is required to repoint GIT_CONFIG_GLOBAL to the null device) and never written.
- Every file write is under `--work`; main() pins --work with realpath checks: must exist (:859-860),
  must not be /tmp, /var/tmp or realpath($TMPDIR) (:861-868), must not be inside realpath(--root)
  (:869-871). realpath resolution defeats a symlinked work dir pointing into the lane or /tmp.
- Fixture git operations (init/config/add/commit in build_repo :338-370) run repo-local
  (user.name/user.email set with plain `git config`, repo-local by default) with clean_env — the
  counter never runs `git config --global` and never touches ~/.gitconfig.

Residual observations (not defects in the frozen predicate, LOW):
- LOW-1 `--receipt` is unguarded (:747-756): if a caller pointed it into the lane or /tmp the
  counter would write there without complaint. The --work guard does not extend to it. Operators
  pass fleet-owned paths; risk is operator error, not instrument misbehavior. Smallest remediation:
  apply the same realpath guard to ns.receipt's parent (or require it under --work).
- LOW-2 The counter's own fixture git calls (git init/add/commit, :338-370) run with caller env
  scrubbed but WITHOUT GIT_CONFIG_NOSYSTEM=1, a core.excludesFile pin, or hooks isolation, so the
  HOST's real global/system git config still applies inside fixture builds (reads only; e.g. a host
  core.hooksPath would execute on fixture commits, a host core.excludesFile could make `git add -A`
  skip a seed file and fail the build). Read-only w.r.t. the host; robustness/reproducibility
  exposure only. Smallest remediation: pass GIT_CONFIG_NOSYSTEM=1 and `-c core.excludesFile=<null>`
  in clean_env's baseline (behavior change is post-freeze, so file as next-round note only).

### A5. c2-mutate.py — CONFIRMED, writes only --out; never executes the writer

Full read. Writes: a single mkstemp in `dirname(abspath(--out))` then os.replace to --out
(c2-mutate.py:44-58); refuses when --out already lexists (:32-34); unlinks the temp on any failure
(:56-57). The mutant is compile()-checked in memory (:49-53) — byte-compiled output is never
written, no __pycache__. No tempfile default dir use (dir is explicit), no /tmp. Reads only
--writer. Refusal exits (2) precede any write; anchor/needle checks (:21-29) guarantee a 3-line
surgical deletion. No subprocess at all.

## Part B — candidate writer audit

Candidate: .ufo/waves/round-66/w1/S66ExecWriter/candidate/souji-receipt-write.py
sha256 a8c47d362a901c222f9582b8b96609fba39cb5e0e662d4057e724db96c1097fc (matches CANDIDATE-READY marker;
verified by sha256sum on the copied bytes). 1478 lines vs base-r65 1374; unified diff 173 lines
(base 045e103478fa4a7eff77db2cab5b9e2f26959a0a:tools/souji-receipt-write.py, sha256
6be46a05358aa8f3fc97402ffbeeda05ba010efbef568693b1f3ca40b0ef6cf0). Marker appeared on poll 0 of the
bounded wait (no 60s iterations consumed). Byte-level audit only; the candidate was not executed by this seat.

**Verdict: no HIGH, no MEDIUM. All six requested checks conform to the frozen predicate. LOW observations below.**

- (a) env VALUE echo — PASS. No `os.environ[...]` interpolation exists anywhere in the file; the new gate
  (:288-306) prints sorted variable NAMES only (`', '.join(cfg_env)` / `', '.join(redirect_env)`), and the r65
  F4 defect is redacted: the GIT_INDEX_FILE refusal now reads "(value not shown)" (:305-306) where r65 echoed
  `{os.environ['GIT_INDEX_FILE']!r}` (base :278-280). The added selftest cases 31/32 even assert the planted
  values ("/nonexistent-r66-secret", "/nonexistent-r66-index") do not appear on stderr. Remaining refusal
  messages echo only argv/computed values (rev, root, out, instrument relpath, git stderr), which are not
  environment values.
- (b) refusal path writing a file — PASS. The receipt temp exists only from mkstemp (:507) onward; every
  refusal before it (env gates :293-306, rev/root/arg checks :310-335, index-flag/status/instrument/out checks
  :341-431) and both post-run refusals (RECEIPT-STATE-CHANGED-DURING-RUN :480, overflow :482) fire before any
  byte is created. The single refusal inside the temp window is the os.link EEXIST race (:519); refuse() →
  sys.exit(2) → SystemExit → the `finally` (:525-532) unlinks the leftover temp. SIGTERM/SIGINT handlers
  (:257-265, registered :1472-1473) unlink the temp too. SIGKILL is documented (r60 amendment) and mitigated
  by the stale-`<out>.*.tmp` sweep (:500-505); a temp is never named OUT, so the judge's lexists(out) probe
  can never see one.
- (c) subprocess bypassing git() — PASS. In the non-selftest region the only subprocess sites are git()
  itself (:98-99) and the wrapped-command Popen (:434), which is the receipt's payload by design, not git
  plumbing; all target-repo reads (cat-file :315, rev-parse :340, ls-files :348, status :361, ls-tree :383,
  cat-file blob :401) go through git(). The wrapped command inherits the writer env, but the gate refuses all
  injected-config/redirect/index env before Popen, so it can never run with them. Selftest-region bare
  subprocess calls target only selftest-owned fixture dirs (r65 pattern, unchanged; new cases 31-33 reuse
  _fixture/_run/_py, no new direct git subprocess).
- (d) GIT_CONFIG_GLOBAL repoint — PASS, cannot read or write a real global config. The gate intentionally
  does NOT refuse GIT_CONFIG_GLOBAL (frozen E3 design: refuse later as "lane worktree is dirty"), and git()
  overwrites `env["GIT_CONFIG_GLOBAL"] = os.devnull` unconditionally (:95) on every child, alongside
  GIT_CONFIG_NOSYSTEM=1 (:96) and GIT_NO_REPLACE_OBJECTS=1 (:97) plus the per-call
  `-c core.excludesFile=<devnull>` pin (:98-99). git reads an empty config from /dev/null instead of
  ~/.gitconfig; the writer never invokes any config-writing command (`git config --global` appears nowhere in
  the main flow), so no real global config is read or written through this route. Any caller-set
  GIT_CONFIG_GLOBAL value is overwritten before the first child spawns.
- (e) env-name coverage — PASS per the frozen surface. Refused on presence (empty value included):
  GIT_CONFIG_COUNT, GIT_CONFIG_PARAMETERS, GIT_CONFIG_KEY_* and GIT_CONFIG_VALUE_* (prefix tests via a tuple
  startswith, :288-292 — covers the numbered pair form at any index) with RECEIPT-ENV-CONFIG-SET; and
  GIT_OBJECT_DIRECTORY, GIT_ALTERNATE_OBJECT_DIRECTORIES, GIT_REPLACE_REF_BASE with RECEIPT-ENV-REDIRECT-SET
  (:295-299). GIT_CONFIG_GLOBAL is deliberately not in the refusal set — it is neutralized by the repoint, and
  the frozen matrix expects E3's refusal class to be "lane worktree is dirty", which this produces. This
  matches the counter's clean_env mirror exactly. Residual (named-scope observation, LOW-3): git-resolution
  variables outside the frozen six (GIT_COMMON_DIR, GIT_NAMESPACE, GIT_CEILING_DIRECTORIES, GIT_CONFIG_SYSTEM)
  are neither refused nor all pinned; GIT_CONFIG_SYSTEM is dead once NOSYSTEM=1 is pinned, but GIT_COMMON_DIR
  could in principle repoint .git discovery. The frozen C1 enumerate is the six names, so this is out of
  scope for round 66 — record for a future round.
- (f) mode mask widening — PASS. The snapshot records `oct(os.stat(full).st_mode & 0o7777)` (:176). 0o7777 is
  exactly rwx bits ×3 + setuid/setgid/sticky; the file-type bits (S_IF*) and everything above stay masked
  out, so the writer records permission bits and nothing else (no uid/gid, no timestamps, no type). The
  change sits in the regular-file branch only; symlinks still take the record-name-and-target branch (M5
  rule unchanged), so no follow-the-link widening. Distinct encodings (0o644 vs 0o4644 vs 0o1644) give
  MOD2/MOD3 their visibility.

### Candidate LOW observations
- LOW-4 (candidate, information): the stale-temp sweep (:500-505) unlinks any `<out>.*.tmp` in OUT's
  directory matching the writer's own naming pattern; a foreign file coincidentally matching that glob would
  be swept. r60-frozen behavior, unchanged this round — noted for completeness, no action.
- LOW-3 above (env names beyond the frozen six) is the only forward-looking item.

## Cross-checks

- Counter ↔ candidate: the gate's refused-name set is exactly the counter's clean_env strip set minus
  GIT_CONFIG_GLOBAL (repointed by both) — matrix rows E1/E2 (RECEIPT-ENV-CONFIG-SET), E4-E6
  (RECEIPT-ENV-REDIRECT-SET), E3 (dirty), MOD2/MOD3 (state-changed via 0o7777), SY3 (state-changed via target
  string) each have a matching candidate mechanism before any git call or at the snapshot.
- Instruments were not executed by this seat (read-only mandate); all findings are from source reading.
- Tooling installed: none. No pacman/uv/pip actions taken. No host state touched, no sysctl, no sudo.
- Scratch /fast/scratch/hyaku/souji-r66/S66SentinelScope/ held only the two extracted writer copies and the
  diff; removed after the audit (files' content is quoted inline above).

