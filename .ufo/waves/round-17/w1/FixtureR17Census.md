STATUS: DONE — r17-census-hygiene.py landed (26 cases): 5fa6017 fails every repair case (13), preserves/refuses all else; worktree cd41d26a is 25/26 — R17-20 reds a real landed defect: `emit_soft_diag` drops the config-unsupported line when both channels hold findings.

# FixtureR17Census — C1 hygiene fixture + first falsifier run

## Owns
`tests/fixtures/r17-census-hygiene.py` (new, executable, python3 stdlib only).
Modeled on `r15-census-config.py`: `--census <path>` (+ `--tool` alias per
ConnGateRegistryRows; same dest), `CASE\t<ID>\t<PASS|FAIL>\t<detail>` lines,
`SUMMARY\ttotal=N\tfailed=M`, exact ordered `EXPECTED_IDS` tuple check, private
`/var/tmp` tempdir per run, pinned `HOME`/`XDG_CONFIG_HOME`/`GIT_CONFIG_*`, git
spy on PATH. Each CASE detail opens with `class=preserve|repair|refuse`.
Never touched `r15-census-config.py` / `r14-census-boundary.py` (pinned).

## Case map (R17-01..26)

| id | class | case |
|---|---|---|
| 01 | repair | local `showUntrackedFiles` `no/false/0/off` + untracked file → dirty |
| 02 | repair | `no` via include.path to benign .git file → dirty |
| 03 | repair | `no` via worktreeConfig + config.worktree → dirty |
| 04 | repair | `all` vs `normal`: same collapsed dirty=1 for a 3-file dir |
| 05/06 | preserve | `no` with no untracked / only ignored file → clean |
| 07 | repair | hardlinked attributes (+dirt+unpushed) → b `error`, a/c byte-identical |
| 08 | repair | FIFO attributes → same; 60s killpg timeout (124=FAIL) if blocked |
| 09 | repair | symlink→FIFO inside gitdir → same |
| 10 | refuse | hardlinked `config` → whole-run exit 2 |
| 11 | preserve | regular attributes (with stat-dirty provoker) → clean |
| 12 | refuse | bad attributes + protected include (~/.omp/agent) → exit 2 |
| 13 | refuse | bad attributes + hardlinked objects/info/alternates → exit 2 (early-return falsifier) |
| 14 | repair | bad attributes in linked-worktree ADMIN → x-main `error` (:790); `--root b --include-root` → b `error` (:873) |
| 15 | repair | bad attributes in COMMON gitdir → x-main `error` (:831); `--root b --include-root` → b `error` (:891 commondir branch) |
| 16 | repair | linked wt admin config.worktree `no` → x-main `clean,wt-dirty` |
| 17 | preserve | invalid value → status-unverifiable on ALL arms (git parses repo config eagerly; verified rc 128 with and without `-u`) |
| 18 | refuse | gitfile→admin bad attributes + commondir hardlinked config → exit 2 (L1 constraint 1, site :891) |
| 19 | refuse | admin attributes symlink escaping gitdir (→/dev/zero) → exit 2 (:790 soft must not skip :791; F2 falsifier) |
| 20 | repair | bad attributes + soft config (~user include) → `error` row with BOTH diagnostics |
| 21 | preserve | directory at attributes → normal row (EISDIR; pinned, Sentinel F4) |
| 22 | preserve | in-gitdir dangling symlink → normal row (ENOENT) |
| 23 | refuse | out-of-gitdir dangling symlink → exit 2 git-metadata-symlink |
| 24 | repair | unix socket at attributes → degrade |
| 25 | refuse | symlink→/dev/zero → exit 2 (RLIMIT_AS=1G so unguarded arms die ENOMEM, not the host) |
| 26 | repair | divergent commondir (W/.git→admin A; A/commondir→N/.git, FIFO attrs): N errors, M `clean,wt-dirty`, no git -C W (L1 constraint 3; 2 diagnostics naming N) |

Oracles: `error` row = `0\t0\t0\t0\t\terror`; exactly one
`git-metadata-unsupported` stderr line per affected row naming repo-or-path;
no `git -C <degraded>` (spelled or realpath); clean rows byte-identical to a
run with bads parked outside the fleet. Provoker = `os.utime` bump (stat-dirty
tracked file) in every D2 repo so guardless arms really reach the attr open.

## First falsifier run (verbatim CASE tables)

Command: `python3 tests/fixtures/r17-census-hygiene.py --census <arm>`;
arms extracted `git show <rev>:tools/souji-census.sh > /var/tmp/…/<rev>.sh`.

### Arm pre-harm a31642d (sha 6a000c59…0026) — SUMMARY total=26 failed=20
```
CASE	R17-01	FAIL	class=repair	r-suf-no: dirty=0 want 1; verdict_flags=clean want dirty (all 4 spellings)
CASE	R17-02	FAIL	class=repair	r-suf-inc: dirty=0 want 1; verdict clean want dirty
CASE	R17-03	FAIL	class=repair	r-suf-wtc: dirty=0 want 1; verdict clean want dirty
CASE	R17-04	FAIL	class=repair	r-suf-all: dirty=3 want 1; all (3) != normal (1)
CASE	R17-05	PASS	class=preserve	ok
CASE	R17-06	PASS	class=preserve	ok
CASE	R17-07	FAIL	class=repair	b normal row ['1','1','1','0',iso,'dirty,unpushed']; no diag; git -C b ran
CASE	R17-08	FAIL	class=repair	fleet run timed out (blocked on non-regular metadata)	exit=124
CASE	R17-09	FAIL	class=repair	fleet run timed out	exit=124
CASE	R17-10	FAIL	class=refuse	exit=0 want 2 (no guard exists at a31642d)
CASE	R17-11	PASS	class=preserve	ok
CASE	R17-12	FAIL	class=refuse	exit=0 want 2
CASE	R17-13	FAIL	class=refuse	exit=0 want 2
CASE	R17-14	FAIL	class=repair	x-main clean row; no diag; git -C ran
CASE	R17-15	FAIL	class=repair	x-main clean row; no diag; git -C ran
CASE	R17-16	FAIL	class=repair	x-main verdict clean want clean,wt-dirty
CASE	R17-17	PASS	class=preserve	ok
CASE	R17-18	FAIL	class=refuse	exit=0 want 2
CASE	R17-19	FAIL	class=refuse	exit=0 want 2
CASE	R17-20	FAIL	class=repair	b clean row; no diags; git -C ran
CASE	R17-21	PASS	class=preserve	ok
CASE	R17-22	PASS	class=preserve	ok
CASE	R17-23	FAIL	class=refuse	exit=0 want 2
CASE	R17-24	FAIL	class=repair	b clean row; git -C ran
CASE	R17-25	FAIL	class=refuse	exit=0 want 2
CASE	R17-26	FAIL	class=repair	fleet run timed out (divergent common FIFO)	exit=124
```

### Arm r14-harm cc21683 (sha fcff8b05…aee9) — SUMMARY total=26 failed=13
```
CASE	R17-01	FAIL	(dirty=0 as above, all spellings)
CASE	R17-02	FAIL	exit=2 want 0 (path-protected:git-config-unsupported — include refused outright)
CASE	R17-03	FAIL	exit=2 want 0 (git-config-unsupported)
CASE	R17-04	FAIL	dirty 3 vs 1 as above
CASE	R17-05..06	PASS
CASE	R17-07	FAIL	b normal row; git -C b ran (cc21683 guard lacks info/attributes)
CASE	R17-08	FAIL	timed out (hang on FIFO)	exit=124
CASE	R17-09	FAIL	timed out	exit=124
CASE	R17-10..13	PASS	(refusals kept: config/attrs+include/attrs+alternates all exit 2)
CASE	R17-14..15	FAIL	x-main clean row; no diag; git -C ran
CASE	R17-16	FAIL	exit=2 want 0 (git-config-unsupported — worktreeConfig scan refused)
CASE	R17-17	PASS	status-unverifiable as predicted
CASE	R17-18..19	PASS
CASE	R17-20	FAIL	exit=2 want 0 (git-config-unsupported)
CASE	R17-21..23	PASS
CASE	R17-24	FAIL	b clean; git -C ran
CASE	R17-25	PASS	exit=2 symlink
CASE	R17-26	FAIL	timed out	exit=124
```

### Arm r16 5fa6017 (sha 64a60fd0…7c4) — SUMMARY total=26 failed=13
```
CASE	R17-01	FAIL	repair: dirty=0 want 1 (all 4 spellings)
CASE	R17-02	FAIL	repair: dirty=0 want 1
CASE	R17-03	FAIL	repair: dirty=0 want 1
CASE	R17-04	FAIL	repair: dirty=3 want 1; all!=normal
CASE	R17-05..06	PASS	preserve
CASE	R17-07	FAIL	repair: exit=2 want 0 (git-metadata-hardlink — whole-run, wrong blast radius)
CASE	R17-08	FAIL	repair: exit=2 want 0 (nonregular — no hang, clean refusal)
CASE	R17-09	FAIL	repair: exit=2 want 0 (nonregular)
CASE	R17-10..13	PASS	refuse
CASE	R17-14	FAIL	repair: exit=2; b: exit=2
CASE	R17-15	FAIL	repair: exit=2; b: exit=2
CASE	R17-16	FAIL	repair: x-main clean want clean,wt-dirty
CASE	R17-17	PASS	preserve (status-unverifiable — discriminates nothing, liveness case)
CASE	R17-18..19	PASS	refuse
CASE	R17-20	FAIL	repair: exit=2 want 0
CASE	R17-21..23	PASS
CASE	R17-24	FAIL	repair: exit=2 want 0 (socket → nonregular)
CASE	R17-25	PASS	refuse
CASE	R17-26	FAIL	repair: exit=2 want 0
```

### Arm WORKTREE tools/souji-census.sh — sha256 `cd41d26aca55f4859dd67762e4cd1cf22b4169ee75eae9396896c622c4fd81fa` (CensusD1D2 in-flight edit; earlier shas this session: 64a60fd0→3efa9190→cd41d26a) — SUMMARY total=26 failed=1
```
CASE	R17-01..15	PASS	(all D1 repairs incl. linked worktrees; all D2 degrades + :790/:873/:891 callsites)
CASE	R17-16..19	PASS
CASE	R17-20	FAIL	class=repair	config-unsupported missing from stderr	observed_exit=0
CASE	R17-21..26	PASS	(incl. divergent-commondir wt-dirty, socket degrade, /dev-zero refusal)
```
R17-20 reproduction (manual fleet, worktree bytes): b `error` row printed with
`souji-census: git-metadata-unsupported git-metadata-hardlink …/b/.git/info/attributes`
and NO `config-unsupported` line for its soft `include.path = ~nobody/…`.

## Finding (advisory, for CensusD1D2/L1)

**F-1 (real, landed):** `emit_soft_diag` (tools/souji-census.sh:648-657) is an
either/or: `if [ -n "$META_SOFT_REASON" ] … else printf config-unsupported`.
When a repo carries BOTH a metadata degrade and a config soft, the config line
is silently dropped — SentinelFifoHostile S-C5 required both channels to print.
Smallest fix: print the metadata line AND, when `CFG_SOFT_REASON` is set, the
config line (two lines per degraded row when both fire; adjust "exactly one"
wording to "exactly one metadata line per row"). R17-20 reds until fixed.
Note: my oracle counts SOFT lines per bad repo (1/repo) — printing both lines
does NOT trip it (config line is a different prefix).

## Deferred critic items (with reason)
- CriticC1Harm "inotify IN_OPEN on hardlink partner": not implemented — the spy +
  timeout oracles cover "no git call that could read it"; strace-free by design
  (r15's strace needs were different). Recorded as coverage note, not defect.
- ".git-dir commondir site :849": indirectly covered via R17-26 (commondir branch
  of a gitfile repo) and R17-15; a direct :849 case needs a valid synthetic common
  dir for a .git-dir repo (hand-crafted commondir leaves git unusable → all arms
  row-error → no discrimination). Disclosed.
- S-H4 on a31642d (/dev/zero unguarded): covered via RLIMIT_AS=1G env; observed
  exit=0 on a31642d (git was killed or skipped — FAIL either way, host safe).
- Sentinel F5 surfaces (worktrees/*/gitdir, info/grafts, shallow, refs FIFOs):
  out of D2 claim scope; not cases. Recommend routing to next round.
- "no git call" oracle is spy-based (`git -C`); `git config --file` is allowed
  (does not read attributes). Symlinked -C target caught via realpath match.

## Evidence
- Fixture: `tests/fixtures/r17-census-hygiene.py`, py_compile OK, executable.
- Run artifacts captured under `/var/tmp/souji-r17-FixtureR17Census/` (deleted
  after this report): out-a31642d.txt, out-cc21683.txt, out-5fa6017.txt,
  out-WORKTREE2.txt; arm copies a31642d.sh/cc21683.sh/5fa6017.sh (shas above).
- Verified `git status --porcelain` semantics directly (git 2.56.0):
  config `no`/`all`/`bogus` each honored over the CLI default; `-u` flag
  overrides `no`/`all` but NOT a bogus repo-config value (eager parse, rc 128).
- Installs/updates: none (all checks ran with system python3/git/bash).

## Risks
- Worktree arm is a moving target (64a60fd0→3efa9190→cd41d26a during this seat);
  re-run after CensusD1D2 lands + fixes F-1 for a clean 26/26.
- a31642d refuse-case FAILs are expected (the arm predates all guards), matching
  r15 fixture precedent.
- The `:849` (commondir of a .git-dir repo) callsite is covered only via the
  gitfile commondir (:891) and divergent (:26) paths; a crafted direct :849
  repo can't host a *valid* divergent commondir without git worktree metadata.

# WAVE-2 update (2026-10-20): cases R17-27..29 added per L1/SentinelCensusD2 F1/F2/F4

- **R17-27 (preserve, F1)**: empty `info/attributes`, `info/exclude`,
  `packed-refs`, `config`, `objects/info/alternates` — all clean rows, rc 0
  (`regular empty file` under `%F` is regular, not non-regular).
- **R17-28 (preserve, F2)**: benign a/b/c fleet under `LANGUAGE=de
  LC_ALL=en_US.UTF-8` → rc 0 all clean. Vacuity guard: probes `stat -c %F`
  *through bash* (bare-stat probes resolve gettext differently — verified:
  `reguläre Datei` inside bash, English in a direct exec) and records a
  note when no de catalog is reachable.
- **R17-29 (refuse, F4)**: FIFO `HEAD` in dot-named admin dir
  `.git/worktrees/.wtdot` (renamed after `worktree add`; `.git` file
  repointed) → rc 2 git-metadata-nonregular; 60s timeout = FAIL. Unguarded
  arms hang in `git worktree list` (observed rc 124).

`EXPECTED_IDS` extended to R17-01..29 in order; `run_tool` gained
`extra_env`.

## Wave-2 run (verbatim)

Command: `python3 tests/fixtures/r17-census-hygiene.py --census <arm>`;
arms extracted via `git show <rev>:tools/souji-census.sh`.

### Arm r16 5fa6017 (sha 64a60fd0…) — SUMMARY total=29 failed=14
Identical to wave-1 table (all 13 repair fails) plus:
```
CASE	R17-27	PASS	class=preserve	ok	observed_exit=0
CASE	R17-28	PASS	class=preserve	ok	observed_exit=0
CASE	R17-29	FAIL	class=refuse	exit=124 want 2; finding path-protected missing	observed_exit=124
```
(R17-16 detail updated to `clean,wt-dirty`; otherwise unchanged.)

### Arm ddb7347 (sha 688ff8ad…0f59 — the D2-landed revision SentinelCensusD2 reviewed) — SUMMARY total=29 failed=3
```
CASE	R17-01..26	ALL PASS (R17-20 fixed: dual diagnostics emitted)
CASE	R17-27	FAIL	class=preserve	exit=2 want 0	observed_finding=path-protected:git-metadata-nonregular
CASE	R17-28	FAIL	class=preserve	exit=2 want 0	observed_finding=path-protected:git-metadata-nonregular
CASE	R17-29	FAIL	class=refuse	exit=124 want 2	observed_exit=124 (hang: dot-admin escapes worktrees/* glob)
```
Exactly the F1/F2/F4 regressions SentinelCensusD2 reported: empty metadata
files false-refuse (first repo hit: `.git/config` under `regular empty
file`), German-locale stat output refuses every config, dot-admin FIFO
HEAD hangs the whole run.

### Arm WORKTREE tools/souji-census.sh — sha256 `006b98231f8d138b3bb13595cc3f9cd9133247d2e88b4683140735ca0759e9fd` — SUMMARY total=29 failed=0
```
CASE	R17-01..29	ALL PASS
```
L1's fix (LC_ALL=C stat, `regular empty file`, dot-admin glob) plus the
R17-20 dual-diagnostic fix are all verified green. R17-29 exits 2 with
`path-protected:git-metadata-nonregular` — the hang is closed for this
shape.

## Notes for L1
- ddb7347 fail-list is precisely {R17-27, R17-28, R17-29}: the fixture
  reproduces all three sentinel regressions and nothing else.
- WORKTREE 29/29 green includes R17-20 — the wave-1 `emit_soft_diag`
  either/or defect is fixed (both `git-metadata-unsupported` and
  `config-unsupported` now print).
- Sentinel F3 (TOCTOU swap→FIFO) is NOT covered by a case: it needs a
  racing writer; recommend the `timeout --kill-after` wrapper he proposed
  rather than fixture coverage.
- Run artifacts: /var/tmp/r17w2/{out,err,rc}-{5fa6017,ddb7347,WORKTREE}.txt
  (scratch retained until L1 ack, then delete).
