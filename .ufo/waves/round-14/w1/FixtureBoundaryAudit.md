# FixtureBoundaryAudit — souji r14 w1 (C2 census boundary fixture)

Seat: SoujiR14.FixtureBoundaryAudit (reviewer, leaf). Lane: /home/vgpnk/Projects/shokunin/souji-shokunin.
Mode: static inspection only. No fixture, tool, census, or test was executed. No file was edited outside this report.

## Status

- `tests/fixtures/r14-census-boundary.py`: **absent** from the working tree at audit time (not in `git ls-files`, not on disk). Nothing to audit line-by-line; the fixture is re-auditable only once it exists.
- `tools/souji-census.sh`: **unmodified** (`git status --short` shows no entry for it; HEAD = `a31642d`). The "changed tool" the assignment asks about is not yet present, so the baseline and the candidate are currently identical.
- Consequence: the baseline-red property ("same fixture is red on baseline for the right reason") cannot be verified yet. Below is the requirement checklist the fixture must meet, derived from the unchanged tool's code and the CensusBoundary task text (`w1-dispatch.json` line 367).

## Code inspection: baseline tool (a31642d) — relevant facts

Cited as `tools/souji-census.sh:<line>`.

1. No credential-store guard exists. Grep of the script for `credential store`, `.omp/agent`, `kagi`, `HOME` returns nothing. The only credential-shaped logic is secret-name flagging inside `newest_mtime` (L170–176) and `.scratch` exclusion (L140–153), which both operate after enumeration.
2. Root enumeration is unguarded. `list_repos` (L316–341) globs `"$root"/*/` and tests `[ -d "$d" ]` and `[ -d "${d%/}/.git" ]` (both follow symlinks). `emit_census` (L343–353) checks only `[ -d "$root" ]` after `canon_path` (L95, `readlink -m`).
3. Symlinked `.git` is accepted. A child whose `.git` is a symlink into a protected directory passes L333 and is censused; `git -C` then reads through it. A gitfile `.git` (text file) fails L333 and is skipped, so that alias is a **baseline-green control**, not a red case.
4. Linked worktrees reach git on other directories. `worktree_extra_flags` (L216–240) runs `count_dirty` (`git -C <wt> status`) on every non-main worktree path that exists, so a `.git/worktrees/<n>/commondir` alias is reachable on baseline through the git shim.
5. `--compare` is read before any guard. `emit_compare` (L414–420) calls `load_census "$COMPARE"` (L416), which does `[ -f ]` and reads the file via `while read` (L367–385). A compare path that is a symlink into a protected directory is therefore content-accessed on baseline. Error text (L365, L372, L380) echoes the path.
6. Environment poisoning is only partly neutralized. L71 unsets `GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_NAMESPACE`. `GIT_COMMON_DIR`, `GIT_OBJECT_DIRECTORY`, `GIT_ALTERNATE_OBJECT_DIRECTORIES` are not unset, so a poisoned environment can redirect every `git -C` call into a protected store on baseline.
7. `.scratch` symlink is already handled on baseline: `scratch_bytes` (L140–153) returns 0 on `[ -L ]` and `du -sb -P` does not follow descendants; `newest_mtime` uses `find .` without `-L`. A `.scratch` symlink case is therefore **baseline-green** (a control).
8. Canonical vs lexical: `census_one` canonicalizes the repo (L245) before any check; a guard that inspects only the lexical argument is insufficient. Guard must check both lexical and `readlink -m` forms of root, compare, and each repo.
9. The unchanged selftest (L511–793) builds only fleets under `mktemp -d` and never exercises a protected root or compare path, so it cannot mask the new fixture's red.

## Spy adequacy (design check, no run)

- PATH shims (git, find, du, readlink, awk, stat, head, grep, date) are necessary but **not sufficient**. Bash builtins used on the forbidden path are invisible to shims: `[ -d ]`, `[ -f ]`, `[ -L ]`, `[ -e ]`, `cd --`, the `"$root"/*/` glob (getdents + stat), and `< file` / `while read` redirections (L367).
- Shim logs must record the **effective target**, not argv: `git -C <path>` (arg after `-C`), `find` target is the `cd` directory (argv is only `.`), `du -- <path>`, `readlink -m -- <path>`. Log `$PWD` in every shim.
- `strace` is present (`/usr/bin/strace`, version 7.0, read via `strace -V`; no install performed). It is the authoritative layer: trace `openat,stat,newfstatat,statx,getdents64,readlink,readlinkat,execve,chdir,access` with `-f`. CORRECTION (A8, BoundaryAttack): strace logs the spelling passed to the syscall, not the resolved target. Access through a child symlink or a `.git` symlink appears only under the alias path, so prefix-matching the store string after the fact false-passes. Do not match on path strings. Instead make the synthetic store directory mode 000 (not a sentinel file: a mode-000 file catches only open(), not stat, getdents, or `.git` reads). Any lookup below it then returns EACCES whatever the spelling. Assert zero EACCES in strace and no "Permission denied" in stderr. Run as the non-root owner only: root bypasses DAC and the check is void. Note `[ -d ]` on a child of a mode-000 dir fails silently, so the EACCES must be read from strace, not from tool output. ptrace may be restricted on the host; the fixture must treat "cannot ptrace" as could-not-evaluate (exit 2), never as pass.
- Added per BoundaryAttack (not exercised): the fixture MUST exit 2 when `id -u` is 0, since DAC bypass voids the mode-000 oracle. Cleanup MUST restore the store mode (`chmod u+rwx`) before `rm -rf` in the trap, or a mode-000 store under /var/tmp survives and fails cleanup.
- A spy that records only `git`/`find`/`du` argv would falsely pass the direct-root and ancestor cases on baseline if the protected directory has no child repo (see calibration note below).

## Calibration requirements for the fixture (for CensusBoundary / L1)

A. **Baseline command**: `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show a31642d:tools/souji-census.sh > <mktemp file under /var/tmp>` with `chmod 0755`; always pass `--root` explicitly and set `HOME` to a synthetic `/var/tmp` directory. Do not derive the baseline from the working tree once CensusBoundary edits it.

B. **Protected child repo inside each protected root**: each protected fixture directory must contain at least one repo (`.git` dir) so a baseline run actually reaches `git`/`find`/`du`. Without it, baseline shows zero spy hits and red collapses to an exit-code mismatch, which is not "red for the correct reason".

C. **Case classification**:

| Case | Expected baseline | Expected installed | Why |
|---|---|---|---|
| direct: `--root $HOME/<cred>` | red (access) | exit 2, protected-path id | no guard |
| descendant: `--root $HOME/<cred>/sub` | red (access) | exit 2 | no guard |
| ancestor: `--root $HOME` | red (stat/getdents on cred child; git on child repo) | exit 2 | enumerates cred child |
| root symlink: `--root <link> -> $HOME/<cred>` | red | exit 2 | `canon_path` resolves, no guard |
| compare alias: `--compare <link> -> cred TSV` | red (open/read) | exit 2, before content access | L416 before guard |
| repo `.git` symlink into cred | red (git reads) | refused/skipped, no git access | L333 follows symlink |
| linked worktree `commondir` into cred | red (git reads via wt) | no git on that path | L240 `count_dirty` |
| env `GIT_COMMON_DIR` = cred | red (git reads) | env-scrubbed or refused | L71 gap |
| safe normal positive (fleet repo) | green | green, byte-identical metadata | control |
| `.scratch` symlink into cred | **green** (control) | green, no du/find into cred | already safe on baseline |
| gitfile `.git` into cred | **green** (control) | green | skipped by L333 |

D. **Two-part red assertion**: for every baseline-red case, require (a) forbidden access recorded by shim or strace after canonical resolution, AND (b) exit code != 2 or finding id absent. Either alone is insufficient: (a) without (b) hides a passing guard, (b) without (a) is a marker-only red.

E. **Positive control must pass on baseline**: if the safe positive fails on baseline, the fixture is broken, not the guard. Red-for-correct-reason requires controls green on both sides.

F. **Leak check**: a unique sentinel token written into every protected file must never appear in stdout, stderr, or the spy log content on any run.

G. **Isolation**: all scratch under `mktemp -d /var/tmp/...` with `trap` cleanup; no `/dev/shm`; `HOME` synthetic; never touch the real credential store, `~/.omp/agent`, `census/operator-sweep-*`.

H. **Hardcoded-path check** (static, no run): the installed tool must derive the protected path from `$HOME` at runtime; a hard-coded `/home/vgpnk/...` would make synthetic cases mis-classify. The fixture should assert this via a source grep of the candidate tool for `/home/`.

I. **Undefined boundary (open decision)**: the tree does not define the exact credential-store path set. The lane contract names `~/.omp/agent/`; PROVINCE.md names `~/.config/**` only as operator config. [INFERENCE] the credential store = `$HOME/.omp/agent` plus any `kagi`-owned path; this must be fixed in the tool and the fixture identically before recording expectations. Flagged for L1 decision.

J. **Secret-shaped --compare basename** (open decision): a compare file named like `credentials.env` outside the protected store is not covered by the stated requirement. Recommend fail-closed refusal (matches the secret-name rule at L170–176), but this is a design call for L1, not a fixture defect.

## Final L1 commands (to run after both executors land; not run by this seat)

Prerequisite: `command -v strace git shellcheck python3` (all present at audit time: strace 7.0, git 2.55.0, python 3.14.7, bash 5.3.15, shellcheck present).

1. Syntax and lint of the changed tool (warnings only; not a gate on its own):
   `bash -n /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh && shellcheck -S warning /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh`
2. Baseline red (fixture supplies its own baseline from `a31642d`; expected: each red-expected case FAIL with access recorded; controls PASS):
   `python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r14-census-boundary.py --tool /var/tmp/<baseline-copy>`
   Exit 1 expected (red); inspect per-case reason lines, not only the exit code.
3. Changed green (installed tool; all cases PASS, exit 0):
   `python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r14-census-boundary.py`
4. Tool selftest (unchanged contract, must stay green):
   `/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh --selftest`
5. Legacy metadata-output check on a synthetic root only (byte-identical to baseline for a safe fleet):
   `SHOKUNIN_ROOT=/var/tmp/<synthetic-fleet> /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh`

Do not run any census against a real fleet root or any path under `~/.omp/agent`.

## Tooling record

- No installs or upgrades performed by this seat.
- Present and version-checked (read-only): strace 7.0 (`/usr/bin/strace`), git 2.55.0, bash 5.3.15, python3 3.14.7, shellcheck (path only).

## Code inspection vs exercised evidence

- Code inspection: everything above (fixture absence via `git ls-files` and filesystem listing; tool behavior from source lines).
- Exercised evidence: **none**. No fixture, census tool, or shell test was run. No protected path was opened, stat'ed, or queried. The git commands used were `status`, `ls-files`, `log`, `check-ignore`, and `--version` against this lane only.

## Messages sent

- To `SoujiR14.CensusBoundary`: fixture absence, spy requirements (effective-target logging, strace layer), protected child repo requirement, control classification, two-part red assertion, env-poisoning case, leak check.

## Fixture bytes audit: tests/fixtures/r14-census-boundary.py (sha256 d712ac79…, 18297 bytes)

Scope: static read of the fixture bytes and the installed tool's guard markers. Nothing was executed: no fixture run, no strace, no baseline run, no census. This section supersedes the "Status" section above, which described the fixture as absent.

Pinned digests (read-only `git show`): baseline `a31642d:tools/souji-census.sh` = `6a000c59fe7486fbde7e5f68663c61cf60404cadb4185e84205b56fe4648c026`. Working-tree `tools/souji-census.sh` = `2cf44ee986641dc2de3a25f2b9524e4a10e718f36afd2e5338d2c65251ece849` (may still change). The fixture prints the tool digest but does not pin the baseline; L1 should assert `6a000c59…` for the `--tool` copy.

### Blocking findings (static; each would make a green or red unfalsifiable)

B1. A8 is not implemented. `build_world` sets the store directory to `0o711` (line 258), not `0o000`. Under 0711, a lookup of a name below the store (`stat`, `open`) succeeds with no EACCES. Only `SESSIONS` is 000 (line 259), which covers one subtree. Consequence: an installed tool that reads `config.yml` or `RECORDS` through an alias would produce no EACCES and no store-string hit. Fix: `os.chmod(AGENT, 0o000)` as the last setup step, keep `HOME/.omp` at 0755 so `AGENT` itself still stats, and assert zero `= -1 EACCES` lines in the strace log (any spelling, since the alias case has no store string), plus no "Permission denied" on stderr. Cleanup already restores `AGENT` to 0700 before `rmtree` (lines 511-514), which is the correct order.

B2. No uid-0 refusal. `main` (lines 521-580) never checks `os.geteuid()`. Under root the 000 mode is bypassed and every store check reads green. Fix: `if os.geteuid() == 0: die("refusing: uid 0 voids the mode-000 oracle")` before `build_world`. Exit 2 via `die`.

B3. Oracle control missing. `probe_strace` (lines 263-292) checks only that strace runs and that the probe file exists. `/bin/true` with `execve` in the filter always writes at least one line, so the check cannot fail on a filter that captures nothing. Fix: add a positive control that opens a store-path file through a symlink (or lists a dir through an alias with `-y`) and asserts the trace shows the mode-000 `EACCES` on that path. If the control fails, `die` (exit 2). This also verifies the `-y` behaviour noted in B5.

B4. Commondir case (R14C2-06, `GC_REPO`) never reaches the store. `SAFE_GD` (lines 235-237) contains only `commondir`. No `HEAD`, `objects`, or `refs`. [INFERENCE from git's gitdir validation, not exercised] git rejects a gitdir without `HEAD` before it follows `commondir`. The baseline then fails only on exit code (rc 0, "error" row), and the installed green proves nothing about commondir. Fix: give `SAFE_GD` a `HEAD` (`ref: refs/heads/master\n`) and the minimal objects/refs layout, so the only store reference is `commondir`. L1 should confirm with one exercised baseline run that a store-path access appears for that case.

B5. Red is not tied to access. `refusal_problems` and `positive_problems` mix exit codes, finding ids, and access hits into one list. A baseline FAIL can therefore be a pure exit mismatch with no access evidence. This is the case for R14C2-04 (`root-alias`), R14C2-05 alias compare, and R14C2-06 `git-symlink`, where the store-string oracle cannot see the alias spelling. Fix: split problems into `access:` (store-string or EACCES evidence) and `contract:` (exit, finding, stdout). A baseline-red case that claims access red must have at least one `access:` item, or it is reported as red-for-contract-only.

### Significant findings

S1. Strace filter `trace=execve,open,openat,getdents64` (line 317; probe line 278) omits `stat`/`newfstatat`/`statx`/`access`/`readlink`/`readlinkat`/`chdir`. `[ -d store/x ]`-style probes and the A2 `readlink -m` ENOENT oracle are invisible. Fix: `-e trace=%file,getdents64,execve` (strace `%file` covers the path-taking syscalls). Not exercised.

S2. `-y` resolves fd arguments to the physical path (`getdents64(3</…>)`), so directory enumeration through an alias is visible via the store string. `openat`, `stat`, and `readlink` through an alias are not: those lines carry only the spelling. [INFERENCE from strace's `-y` documentation.] The fixture's comments do not state this split. Document it, and let B3's control verify it.

S3. Spies (`FORBIDDEN`, line 56) cover find/du/git/cat/head/tail only. The canonicalizers the guard needs (`readlink`, `realpath`, `stat`) are not spied. A2 flags `readlink -m` probes below the store as the leak. Fix: add `readlink`, `realpath`, `stat` to `FORBIDDEN`. A store argv on any of them is then a refusal-case failure. Root and alias canonicalization pass because their argv carries the alias spelling, not the store string.

S4. Coverage versus the BoundaryAttack required set is partial. Present: direct, descendant (`SESSIONS`), ancestor (`HOME`), root-alias, compare direct and alias, gitfile, `.git` symlink, commondir (broken, B4), safe positive, `.scratch` symlink, GIT_* env poisoning. Missing: lexical `link/..` (A1); nested alias chain with suffix (A2); `/` (A3); newline child (A4); `.git/config` symlink and top-level commondir (A5); filter/fsmonitor/include (A6, only fsmonitor is set); relative compare basename (A-compare); `TMPDIR=<store>` poisoning. `HOME/agent-alias` (line 244) is created but no case uses it.

S5. Case R14C2-06 expects exit 2 for a repo root whose `.git` points into the store (gitfile, `.git` symlink, commondir). The dispatch text says "Skip symlink repo roots and scratch". "Skip" implies rc 0 with no row, while the fixture requires refusal with `path-protected`. This is a contract decision for L1, not a fixture defect: either the tool refuses these roots, or the fixture's expectation for 06 changes.

### Minor findings

M1. Timeout path (line 335-336) returns `trace=[]` and `spy=[]`, so access evidence is dropped on timeout. The rc check still fails the case. Acceptable, but the baseline-red reason is lost.
M2. Canary (line 44) is only in `config.yml` and `session.json`. No case reads those as content, and `RECORDS` (the compare file) carries no canary. The leak check is largely inert. The strace and EACCES checks carry the load.
M3. Positive row match (line 403) compares `str(repo)` to the tool's canonical path. Use `os.path.realpath(repo)` so a symlinked `/var/tmp` prefix cannot cause a false row mismatch.
M4. `cleanup` (lines 509-518) ignores `rmtree` errors silently. A leftover mode-000 store under /var/tmp would be invisible. Print a warning and exit non-zero on residue.
M5. Checked and found correct: the spy script quoting (lines 162-175, including the f-string `${{…-}}` expansion); `GIT_ENV` logging; `git_env` HOME ordering; the `AGENT`/`SESSIONS` chmod order in cleanup; `--tool` default path (`parents[2]`); the first-execve skip in `trace_hits` (the first traced line is the bash exec).

### Installed tool markers (grep, not exercised)

- Line 115 unsets every inherited `GIT_*` variable, so the case R14C2-09 spy `ENV` lines should be empty on the installed tool.
- Line 153 defines `PROTECTED_FINDING=path-protected`.
- Line 197 contains `id -u`, so the uid check exists in the tool's own code but not in the fixture (B2).
- Whether a guard runs before `readlink`/`stat` on the root argument was not verified by reading the guard body. L1 should check this with the strace oracle after B1 is fixed.

### Final L1 commands (not run by this seat)

1. `sha256sum` on the baseline copy must equal `6a000c59fe7486fbde7e5f68663c61cf60404cadb4185e84205b56fe4648c026`.
2. `bash -n` and `shellcheck -S warning` on `tools/souji-census.sh`.
3. `python3 tests/fixtures/r14-census-boundary.py --tool <baseline copy>`: expect red with at least one `access:` item for R14C2-01/02/03/04/05/06/09; 07/08 pass.
4. `python3 tests/fixtures/r14-census-boundary.py`: expect all PASS and zero EACCES.
5. `tools/souji-census.sh --selftest`.

Do not run any of these against a real store or a real fleet root.

Code inspection vs exercised: everything in this section is code inspection. No fixture, tool, strace, or census was run.

## Final fixture audit: tests/fixtures/r14-census-boundary.py (sha256 a118225b…, 21542 bytes)

Scope: static read of the bytes only. Nothing executed. The working-tree `tools/souji-census.sh` is now `034a518e…` (modified, not audited here). Baseline `a31642d` = `6a000c59…`, matching the fixture's `BASELINE_SHA` constant (verified by `git show | sha256sum`). Digest `a118225b…` matches the value the CensusBoundary message reported.

### Blocking

B6 (new). `build_world` chmods in the wrong order, so setup raises before any case runs. Lines 295-297 are `os.chmod(AGENT, 0o000)`, then `os.chmod(SESSIONS, 0o000)`, then `os.chmod(LEAK, 0o755)`. Changing `SESSIONS` and `LEAK` requires path resolution through `AGENT` (`…/.omp/agent/sessions`), which needs search (x) on `AGENT`. Once `AGENT` is 000, the non-root owner lacks that bit, so both calls raise `PermissionError` (EACCES). Only uid 0 bypasses this, and `main` refuses uid 0 on line 630. `build_world` is not wrapped, so `main`'s `finally` runs cleanup and the process exits with a traceback (rc 1), with no CASE line and no probe. Consequences: (a) the fixture can never print PASS; (b) baseline and installed both return rc 1, so the run looks red for a reason unrelated to the tool, which is the "red for the wrong reason" failure the audit was meant to prevent; (c) the probe's EACCES oracle is never exercised. Fix: set `SESSIONS` to 000 and `LEAK` to 0755 first, then set `AGENT` to 000 as the last chmod. Also wrap `build_world()` and `probe_strace()` so an unexpected exception is `die` (rc 2), not rc 1. [Static POSIX inference, high confidence; not exercised.]

### Status of earlier findings

- B1 (store mode): intent addressed (AGENT 000, probe and EACCES oracle), but broken by B6 ordering.
- B2 (uid 0): addressed, line 630.
- B3 (strace probe): addressed. The probe now requires a denied read of `AGENT/config.yml` and rc != 0, and dies otherwise. Fail-closed on ptrace failure is correct (no log, or no EACCES, both die rc 2). Not reached because of B6.
- B4 (commondir without HEAD): addressed. `SAFE_GD` has `HEAD`, `objects/`, `refs/heads/`. Still [INFERENCE] until one baseline run shows the store access.
- B5 (contract vs access split): the split exists (lines 442-462), but nothing enforces it. `main` only counts problems, so a baseline red can still be contract-only. See N5.
- S1 (filter): addressed. `trace=%file,getdents64,execve` at lines 315 and 361.
- S2 (`-y` physical vs alias spelling): not documented in the fixture. Still open as a comment gap; the EACCES oracle makes it irrelevant for detection.
- S3 (spies): addressed. `SPY_TOOLS` adds readlink, stat, realpath (line 59). Limit: `spy_hits` matches only argv containing `AGENT`, so alias-spelled argv is never caught by spies. The EACCES check is the real catch.
- S4 (coverage): partly addressed. Added: `root-alias/..` (case 04, the A1 case), a commondir-in-worktree (case 10), a two-hop alternates chain (case 11), and `filter-config` (case 06). Still missing: A2 nested alias with suffix; A3 `/`; A4 newline child; A5 `.git/config` symlink and top-level `.git/commondir` in a main repo; A6 include; relative compare basename; `TMPDIR=<store>` poisoning; fleet-level symlink child (N4).
- S5 (case 06 vs "skip symlink repo roots"): still a decision for L1. Cases 06, 10 and 11 require a root-level exit 2. The dispatch's "skip" wording applies to symlink repo roots at fleet level, which the fixture does not test (N4). Record the decision explicitly.
- M1 (timeout drops evidence): unchanged; acceptable.
- M2 (inert canary): unchanged. No case reads the canary files, and RECORDS carries no canary.
- M3 (realpath in row match): unchanged. `positive_problems` still uses `str(repo)`.
- M4 (silent cleanup): unchanged. `shutil.rmtree(..., ignore_errors=True)` and `except OSError: pass` still hide residue under /var/tmp.

### New findings

N1 (case 06 `filter-config` leg tests nothing and asserts the wrong finding). `CFG_REPO` sets `filter.x.clean = cat` but has no `.gitattributes`, so `git status` never runs the clean filter. No access occurs (the leg is contract-only at best). The leg also requires `path-protected` for a repo that is not in the store, which mislabels a non-boundary result. Fix: remove the leg from case 06. If A6 coverage is wanted, make it a separate case with `.gitattributes filter=x`, or record it as an explicit nonclaim.

N2 (case 11 may not reach the store on baseline). `ALT_REPO` commits its objects before the alternates file is written, so every object needed by `rev-list` or `status` may be local. Git may then never open the alternate. The baseline red could be contract-only. [INFERENCE.] Fix: make an object reachable only through the alternate (for example, write the commit into the store-side object dir and drop it from `ALT_REPO`), then L1 must confirm a store access on baseline.

N3 (case 10 expectation rests on an unverified assumption). The access depends on git reading `commondir` and then `GD/config` or `GD/HEAD` during discovery for `wt-bad`. That is likely, but it is [INFERENCE] and should be confirmed by the baseline run.

N4 (no fleet-level symlink child case). The dispatch requires "skip symlink repo roots". `list_repos` globs `"$root"/*/`, and `[ -d ]` follows links, so `fleet/evil -> AGENT` would reach `AGENT/.git`. No case covers this. Add a case: SAFE_FLEET containing a symlink child to AGENT. Expected: exit 0, no row for the symlink, no store access (EACCES absent), and the normal row still present.

N5 (TOOL-KIND is informational, not a gate, and crashes are not separated). `main` prints `TOOL-KIND` but never checks it, and does not compare outcomes against the expected red/green table. A baseline run can therefore show red while skipping the access evidence. Fix: when `TOOL-KIND` is `baseline-a31642d`, require at least one `access:` item for each case expected red (01-06, 09, 10, 11, with the 06 filter leg removed), and fail if a case is contract-only. Also separate "setup crashed" (rc 2) from "case failed" (rc 1), per B6.

### Final L1 commands (not run by this seat)

1. `sha256sum` of the baseline copy equals `6a000c59fe7486fbde7e5f68663c61cf60404cadb4185e84205b56fe4648c026`.
2. `bash -n` and `shellcheck -S warning` on `tools/souji-census.sh`.
3. After B6 is fixed: `python3 tests/fixtures/r14-census-boundary.py --tool <baseline copy>`. Expect rc 1 with a CASE line for every case, and an `access:` item on each expected-red case (N5). Do not accept rc 1 from a traceback.
4. After B6 is fixed: `python3 tests/fixtures/r14-census-boundary.py`. Expect rc 0 with all 11 PASS.
5. `tools/souji-census.sh --selftest`.

Do not run any of these against a real store or a real fleet root.

Code inspection vs exercised: this section is code inspection only. No fixture, tool, strace, or census was run.

## Fixture audit round 3: tests/fixtures/r14-census-boundary.py (sha256 fda498d0…, 726 lines); tool e2a1d502… (1533 lines)

Scope: static read of fixture bytes; installed tool read only at the enumeration and walker sites (lines 327-390, 916-958). Nothing executed. Digests confirmed with `sha256sum`.

### Confirmed fixed

- B6: chmod order is SESSIONS 000, LEAK 755, AGENT 000 last (lines 324-326). Setup and probe exceptions now `die` 2 (lines 686-692).
- N2 (intent): the alternate object is copied into the store `GD/objects` (lines 282-291), so baseline must read through the alternate. Blocked by B7 below.
- N4: case 12 with `alias-child -> LEAK` (line 306). Installed list_repos checks `protected_reason_input` (text), then `[ -L ]` before any stat (lines 942-947), so the installed tool should pass case 12 without touching the store. Baseline `"$root"/*/` (line 324 of the baseline) stats the child, so baseline should show EACCES.
- N5 (intent): gate at lines 701-706 added.
- N1: `.gitattributes filter=x` plus a modified `data.txt` (lines 262-266). The clean filter now actually runs. See B10 for why this leg is still wrong.

### Blockers

B7 (new). Object is used before the alternate that provides it is configured. `git update-ref refs/heads/master <alt_head>` (line 296) runs before the alternates file is written (lines 298-300). git's `update-ref` rejects a ref whose object does not exist locally ("trying to write ref ... with nonexistent object"). The object is only reachable after the alternates file exists, so every run dies in setup with rc 2 before any case. Fix: write the alternates file (lines 297-300) before line 296. Setup happens before the AGENT 000 chmod, so the alternate is readable during setup. [Static git-behaviour inference, high confidence; not exercised.]

B8 (new). Case 05 `proc-fd` leg cannot pass on the installed tool. `/proc/self/fd/999` does not exist and is not a store path. The installed tool sees no protected text, fails `[ -f ]` on the compare file, and exits 2 with a usage error and no `path-protected` finding. `refusal_problems` then reports "contract: finding path-protected missing". Also, `run_tool` does not pass fds, so no fd to the store could be inherited. Fix: in Python, `os.open(RECORDS)` before AGENT 000, pass that fd through `subprocess.run(pass_fds=...)` (run_tool needs a new parameter), and compare `/proc/self/fd/<n>`. Alternatively drop the leg. A nonexistent fd tests nothing.

B9 (new). The N5 gate never sees labeled items. Cases 04, 05, 06 and 09 prefix every item (`alias: access: …`, `direct: access: …`, `gitfile: access: …`, `base: …`, `home-store: …`). The gate tests `item.startswith("access:")` (line 704), which fails for those prefixed items. So on baseline the gate always appends "access: baseline red case has no observed store access", even when store access was recorded. This is the wrong-reason red the gate exists to prevent, and it means the gate is not checking anything for those cases. Fix: test `"access:" in item` (substring), or apply the check per leg before prefixing.

B10 (new). Case 06 `filter-config` leg expects the wrong result. `CFG_REPO` is not in the store. Its only property is a clean filter (`cat`), which does not involve store access. The leg requires `exit 2` and `path-protected`. The installed tool has no rule that refuses a repo because it has a filter, so it will exit 0 and the leg fails with "contract: exit=0 want 2". This is a mislabel: it asserts a refusal that the contract does not require. Fix: remove the leg from case 06. If the filter (A6) is to be tested, make a separate case that expects exit 0, the row, no store access, and `cat` run only as a non-store argv. Or record it as an explicit nonclaim.

### Risks for L1 (not fixture defects)

R1. Case 12 expects the installed tool to avoid any stat through `alias-child`. The installed tool does this via `[ -L ]` before `[ -d ]` (line 946). The protection depends on that ordering; a future edit that stats first would fail case 12 with EACCES from the store, which is the intended oracle.
R2. `trace_access` flags `readlink("<AGENT>")` and `lstat("<AGENT>")` even with `allow_root_stat=True` (readlink branch line 444, stat branch line 460). The installed walker is single-hop `readlink --` on links only (line 386), so a readlink whose argument is AGENT itself should not occur, but L1 should confirm no `[ -L AGENT ]` runs before the text check. If one does, the installed tool fails cases 01, 02, 04 on a lstat of the root, which is metadata rather than content.
R3. Installed `list_repos` glob is `"$root"/*` (line 933), not `*/`, so bash does not stat a trailing-slash directory test on symlinks at the glob itself. Good; but `${d##*/}` and `protected_reason_input` must stay text-only.

### Still open from earlier rounds

- M2 (canary inert): unchanged. No case reads `config.yml` or `session.json` content, and RECORDS has no canary.
- M3 (`str(repo)` row match): unchanged.
- M4 (silent cleanup): unchanged. `shutil.rmtree(..., ignore_errors=True)` and `except OSError: pass` (lines 636-645) still hide residue under /var/tmp.
- S2 (`-y` physical versus alias spelling): still not documented in the fixture.
- S4 (coverage): still missing A2 suffix chains, A3 `/`, A4 newline child, A5 `.git/config` symlink and top-level `.git/commondir` in a main repo, A6 include, relative compare basename, and `TMPDIR=<store>`.

### Final L1 commands (not run by this seat)

1. `sha256sum` of the baseline copy equals `6a000c59fe7486fbde7e5f68663c61cf60404cadb4185e84205b56fe4648c026`.
2. `bash -n` and `shellcheck -S warning` on `tools/souji-census.sh`.
3. After B7–B10 are fixed: `python3 tests/fixtures/r14-census-boundary.py --tool <baseline copy>`. Expect rc 1 with a CASE line for every case and an `access:` item on each red case (after B9 is fixed).
4. After B7–B10 are fixed: `python3 tests/fixtures/r14-census-boundary.py`. Expect rc 0 with all 12 PASS.
5. `tools/souji-census.sh --selftest`.

Do not run any of these against a real store or a real fleet root.

Code inspection vs exercised: this section is code inspection only. No fixture, tool, strace, or census was run.
