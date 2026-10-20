# R15 FixtureIsolation (SoujiR15.FixtureIsolation) — reviewer

Axes: **operability**, **calibration**. Source inspection only. No tests, probes, builds, edits outside this report, installs, or commits. No tool installed or updated.

## Scope disclosure (no-query boundary)

- Early in the seat, `_glob` ran over the whole lane root with `gitignore:false`. That returned filenames under `census/operator-sweep-20261019/` (names only). No file in that directory was opened, read, copied, or edited. Recursive `census/**` globs were also run once. Both were broad queries, outside the boundary the parent later restated. I made no further broad queries.
- Files read, all explicit: `tests/fixtures/r14-census-boundary.py`, `tests/fixtures/r14-evidence-cache.py`, `tools/souji-census.sh` (targeted ranges), `tools/souji-evidence-cache.py` (targeted greps), `.ufo/waves/round-15/w1-spec.json`, `AGENTS.md`, `SKILL.md`, `corpus/QUALITY.md` (Q4 line), `corpus/lessons/round-14.md` (targeted grep).
- No real credential, auth, or admin file was opened. Nothing under a real `~/.omp` or `~/.config` was touched.

## Source state

- `tests/fixtures/r15-census-config.py` does **not exist**. The ConfigFixture seat has not landed. Section B is design-only.
- `tools/souji-preservation-evidence.py` and `tests/fixtures/r15-preservation-evidence.py` do **not exist**.
- `tools/souji-census.sh` is the r14 tool, unchanged in this review.

## A. Current isolation: verified by source

| Surface | Evidence | Assessment |
|---|---|---|
| Fixture subprocess env is built fresh, not inherited | `r14-census-boundary.py:139-151` (`git_env`), `:365-375` (`run_tool` env dict), `r14-evidence-cache.py:163-167` | Inherited `GIT_*`, `PI_CODING_AGENT_DIR`, `PI_CONFIG_DIR` and real `HOME` do not reach fixture children. Good. |
| Scratch is under `/var/tmp` only, removed in `finally` | `r14-census-boundary.py:691` (`mkdtemp(dir="/var/tmp")`), `:730-731`; `r14-evidence-cache.py:154`, `:344-345`; `souji-census.sh:1192-1193` | Q4 shape satisfied. No `/tmp` fallback. |
| Refuses root (mode-000 oracle needs non-root) | `r14-census-boundary.py:678-679` | Good. |
| Store mode-000 sentinel + EACCES | `:314-319` (`AGENT`, `SESSIONS` 000) and `:322-358` (`probe_strace` proves EACCES on the store) | Good sentinel, verified at setup. |
| Tool clears inherited Git state | `souji-census.sh:112`, `:119` (unset `GIT_*`), `:122-123` (`GIT_CONFIG_GLOBAL`/`SYSTEM=/dev/null`) | Good. |
| `git status` pins config that would otherwise come from XDG or hooks | `souji-census.sh:710-712` (`core.hooksPath`, `core.excludesFile`, `core.attributesFile` = `/dev/null`) | An XDG `~/.config/git/ignore` or `attributes` read is neutralized for status. No finding. |
| Tool refuses before any stat of an input alias or ancestor | `souji-census.sh:333-411` (`resolve_guarded`: refuse at `:382` before `[ -L ]` at `:385`; only `readlink` at `:386`), `:1527` (guard before any command), `:976` (`[ -d ]` only on the resolved path) | Current code does not follow into the store. Source-verified, not run. |
| Compare file `nlink` stat is on a resolved path | `souji-census.sh:1007`, `:1015` | Safe as written. |
| Census selftest temp handling | `:1192` (`mktemp -d /var/tmp`), `:1193` (`trap rm -rf`); no `chmod` anywhere in the selftest, so `rm -rf` cannot be blocked | Good. |

## B. Findings (ranked)

### F1 — medium — calibration: the access oracle has a blind spot for stat-family calls on ancestors and aliases

- `r14-census-boundary.py:454-455` (`if agent not in line: continue`) and `:467-469` (stat tokens count only when the store string or descendant appears in the line). A `stat`, `newfstatat`, or `statx` call on a path that does not contain `.../home/.omp/agent` is invisible unless it returns `EACCES`.
- `:473-474` (`spy_hits`) keys on the store string too. A spied `stat -L <alias>` is invisible.
- Concretely, `STORE` (`HOME/.omp`, `:204`) is left at 0755 (no `chmod` in `:314-319`). So `stat(".../root-alias")` (case 04, `:559`) resolves to `AGENT` with no `EACCES`, and no store string on the line. The same holds for `stat(".../scratch-shokunin/.scratch")` (case 08, `:597`). Ancestor stats (`HOME`, `HOME/.omp`) are also invisible.
- Current tool source is safe (B.A above). This is an oracle gap: a regression that stats an ancestor or alias before refusing would still show R14C2-01..12 green. The contract text "refused before the first stat" (`souji-census.sh:354-356`) cannot be checked by this oracle.
- Remedy (for the owner of the fixture, not this seat): (a) chmod `STORE` to 0 as well as `AGENT`, with cleanup chmod to 0700 before `rmtree` (same as `:647-650`); (b) for refusal cases, treat any stat-family, `open`, or `readlink` whose path argument equals or prefixes `HOME`, `STORE`, or a known alias, without `AT_SYMLINK_NOFOLLOW`, as a hit; (c) keep the spy but also log argv path prefixes, not only the store string.

### F2 — low-medium — operability: cleanup failures are silent

- `r14-census-boundary.py:654` (`shutil.rmtree(SCRATCH, ignore_errors=True)`) and `r14-evidence-cache.py:345` (same). Residue under `/var/tmp` is never reported, and the exit code does not change. Q4 says "a trap removes it", which is satisfied in form but not checked in fact.
- Remedy: `onerror` handler that records the path; after cleanup, assert the scratch path is gone; on residue, print it and exit 2 (could-not-evaluate).

### F3 — low — isolation: timeout kills only the direct child

- `r14-census-boundary.py:392-402`: `subprocess.run(timeout=90)` kills only the `strace` process. Its traced children (`bash`, spied `git`/`find`) may survive and write into `SCRATCH` after `rmtree` at `:654`. The `TimeoutExpired` branch at `:401-402` returns rc 124 and does not wait for or kill descendants.
- Unverified (no probes allowed): whether strace-traced children are killed on tracer `SIGKILL`. Remedy: `start_new_session=True`, `os.killpg` on timeout, `wait()` before cleanup.
- `r14-evidence-cache.py:64-70` (`timeout=180`): the cache tool spawns no children in source (`subprocess` is only in `_run_tool`, `souji-evidence-cache.py:1270`). Low risk.

### F4 — low — calibration: a partial `--case` run can exit 0

- `r14-census-boundary.py:722-727`: the expected-ID-set check runs only when `args.case` is empty. With `--case R14C2-07`, `main` returns 0 at `:729` when that one case passes. A green subset could be cited as acceptance.
- Remedy: the ConfigFixture gate must refuse partial runs as acceptance (exit 2 or `PARTIAL` marker), or emit a distinct code, so a subset cannot be cited as the full gate.

### F5 — low — isolation/contract: the production tool does not pin `TMPDIR`

- `tools/souji-census.sh` never exports `TMPDIR`. `sort` at `:970` and `:1105` inherits the operator's `TMPDIR` (default `/tmp`) and can spill there under large input. The header says the tool "never writes outside /var/tmp" (`:5-6`), and Q4 applies.
- Only the fixture pins it (`r14-census-boundary.py:368`). Remedy: `export TMPDIR=/var/tmp` near `:123`, or `sort -T /var/tmp`.

### F6 — low — calibration: the cache fixture's "never read" claim is unobserved

- `r14-evidence-cache.py:162` (canary `"synthetic home, never read"`) and `:305-313` (`protected-record` case). The check asserts exit 2 and the `record-protected` finding only. There is no spy and no strace, and the canary text is never asserted absent from stdout or stderr. "Never read" is therefore not observed.
- Remedy: assert the canary is absent from both streams, and add a read oracle, or downgrade the claim in the fixture docstring (`:1-27`).

### F7 — info — operability: the in-tool selftest inherits operator `PI_*`

- `souji-census.sh:1460` and `:1471` set `HOME` and `TMPDIR` but inherit `PI_CODING_AGENT_DIR` and `PI_CONFIG_DIR`. Those only add protected roots (fail-closed). An operator shell with `PI_CODING_AGENT_DIR=/var/tmp` would refuse the selftest fleet.
- `:1188-1190`: a stale `SOUJI_CENSUS_SELFTEST_ACTIVE=1` exported in the operator shell makes `--selftest` exit 1 ("refusing nested"). Nuisance only; the nested guard is not a protection bypass.
- `souji-evidence-cache.py:421` and `:432` read `PI_*` from `os.environ` for the protected union; the fixture's env (`r14-evidence-cache.py:163-167`) strips them, so the fixture is stable.

## C. ConfigFixture acceptance (design-only; `r15-census-config.py` absent)

When the fixture lands, FixtureIsolation should check the following, citing lines:

1. Scratch is `mkdtemp(dir="/var/tmp")`. `grep -c 'TMPDIR:-/tmp'` is 0 and `/var/tmp` is present (Q4).
2. The child env is built from an allowlist. It must not contain inherited `GIT_*`, `PI_*`, or real `HOME`/`XDG_CONFIG_HOME`. `HOME` is synthetic; `XDG_CONFIG_HOME` is pinned to a synthetic path.
3. Forbidden access set, checked by strace and not only by the store string: real passwd home (`/home/vgpnk`), `/etc/gitconfig`, `/root`, the synthetic `.gitconfig` include canary, and any `.config/git` path. A refused case and a positive safe-include case must show zero opens of the include canary (the tool uses `--no-includes`, `souji-census.sh:500`, so the canary should never be read).
4. Mode-000 sentinels on `STORE` and `AGENT` (F1), root refusal, and `probe_strace` before cases (`:322-358`).
5. Stat-family, `open`, and `readlink` checks on alias and ancestor paths (F1 remedy), not only store-string lines.
6. Timeout kills the process group and waits (F3). Cleanup asserts no residue and exits 2 on failure (F2).
7. Exit 0 only for the full fixed ID set. Partial runs are not green (F4).
8. Same command produces red on a pinned baseline SHA (`BASELINE_SHA` pattern, `:61`) and green on the repaired tool. Cases cover all r14 refused config families (safe and unsafe values), neutralized hooks/attributes/excludes/fsmonitor, safe includes including mixed fleet, false promisor/worktreeConfig, and safe clean filters. Each case is paired red/green with a namespace control.

## D. Unrun checks and verification gaps

- Not run (no probes, per contract): strace behavior on tracer SIGKILL (F3); GNU `sort` temp-spill target under inherited `TMPDIR` (F5); bash `EXIT` trap behavior on `SIGINT`/`SIGTERM` for `cleanup_census_tmp` (`souji-census.sh:149-151`, `:1090`).
- Not verified: whether git reads `$XDG_CONFIG_HOME/git/attributes` or `ignore` when `core.*File` is unset in a non-status command. Only `status` (`:710-712`) was checked.
- `tests/fixtures/r15-census-config.py`, `tools/souji-preservation-evidence.py`, and `tests/fixtures/r15-preservation-evidence.py` are absent; section C is design-only.

## E. Routing

- F1 is the material calibration item. Route to the fixture owner and MutationPlan (ancestor/alias stat mutation should be a required red case).
- F2, F3, F4 are operability items for the fixture owner and RunnerLimits.
- F5 is for the census tool owner (ConfigRepair seat owns `souji-census.sh`; route, do not edit).
- F6 is for the cache fixture owner.
- No certification or deletion authority is implied by any of these.
