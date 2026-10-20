# Round 15 w1 — FixtureAccess (reviewer)

Axes: operability, calibration. Mode: source inspection only. No tests, probes, builds, or edits were run. The only write is this report. No `~/.omp` store, credential, or operator-sweep path was opened. Tooling: none installed or upgraded.

## Scope and status

- The r15 fixture `tests/fixtures/r15-census-config.py` does **not exist yet** (`tests/fixtures/` lists r14 only; `git status` shows no r15 fixture). Per the executor assignment it is to be written by the executor seat.
- The reviewed pattern is the r14 fixture the r15 one is told to reuse: `tests/fixtures/r14-census-boundary.py` (sha256 e6a984b1…). Its tool under test is `tools/souji-census.sh`, currently sha256 `fcff8b057b3e7dc57d0fe6a5ed4c7ccb2c89c3ea4bd3c0eb3a93e26ea869aee9`, which equals the r14 installed record. The r14 baseline is `6a000c59…` (a31642d).
- Acceptance for the r15 fixture is therefore **design-only**, stated in section 4.
- Line references below are to `tests/fixtures/r14-census-boundary.py` unless noted.

## Verdict

Forbidden-access checking in the r14 pattern is real evidence for store access (strace lines are recorded in `census/round-14/verification.json`). Three things in it overstate what it proves:

1. Part of the trace filter is dead code, so the alias-open claim is not implemented.
2. The spy channel has no liveness requirement, so spy silence is not evidence of no access.
3. The harness suppresses global/system Git config, so the tool's own global-config suppression is untested.

The r15 C1 harm is an operability failure with zero store access. The access checks are a regression guard for C1, not its red oracle. Reusing the r14 `is_baseline` / `refusal_problems` machinery as-is would mis-calibrate C1.

## Findings

### F1 — High, calibration: alias-open detection is dead code
- `tests/fixtures/r14-census-boundary.py:454-466`. Line 454 is `if agent not in line: continue`. Line 457 is `if agent in line:` inside the open branch, which is therefore always true. The `follow_open_symlinks` block at 460-465 can never execute.
- Consequence: refusal checks pass `follow_open_symlinks=True` (line 498), and the docstring (lines 420-428) describes behaviour that does not exist. Alias opens are caught only through strace `EACCES` (the store is mode 000) or through `-y` fd annotations on successful calls. Neither is asserted anywhere.
- Source-derived; not executed.
- Acceptance (r15): either delete the branch and document the `EACCES` + `-y` reliance, or fix the order so realpath is checked before the string-match `continue`. In both cases add a harness self-check of `trace_access` using synthetic strace strings (no probes): store-annotated open → hit; alias open with `EACCES` → hit; `readlink("<store>/x")` → hit; `newfstatat(AT_FDCWD</store>, "x")` → hit; bare store-root stat under `allow_root_stat=False` → hit; benign path → no hit.

### F2 — High, calibration: command spy is not a live oracle
- `make_spy` (173-186) and `SPY_TOOLS` (60) cover only `find du git cat head tail readlink stat realpath`. The tool also calls `awk grep sort cut date id getent cmp tr wc` (see `tools/souji-census.sh:203, 731, 1105, 1287, 1292, 1176, 1015`). These are invisible to the spy.
- The spy also misses absolute-path invocations, bash builtins (`[`, `test`, `read`, `cd`, redirections), kernel reads done by a spied tool, and any path that does not contain the literal store string.
- The spy is **not** a second independent check. Both channels observe the same process tree. The docstring (lines 8-17) calls them "two independent access checks".
- Nothing requires the spy to fire. The baseline red rule (`710-715`) requires only some `access:` item, which the strace channel can satisfy alone. A positive case passes the spy check whether or not the spy ever ran.
- The spy's unique value is the ENV lines (`GIT_*` values as seen by spied children), since strace does not show environment. That value is lost if the spy is silently inert.
- Acceptance (r15): (a) each positive case must show at least one spy line for `git` (liveness; fail as `harness: spy inert` otherwise); (b) the pass text must say "no store access observed on the strace %file/getdents64/execve channel", not "no access"; (c) the docstring must not call the spy independent; (d) state the non-spied tool list as a known limitation.

### F3 — High, operability/calibration for r15: the tool's own global-config suppression is never exercised
- `run_tool` sets `GIT_CONFIG_GLOBAL=/dev/null`, `GIT_CONFIG_SYSTEM=/dev/null`, `GIT_CONFIG_NOSYSTEM=1` (lines 370-372) for every run.
- Case 09's "home-store" leg sets `HOME=AGENT` (line 612), but `GIT_CONFIG_GLOBAL=/dev/null` masks any `$HOME/.gitconfig`. No `.gitconfig` with an include of a store path is placed anywhere in the world (`build_world`, 189-319). The case therefore cannot detect a global-config read. The tool's own suppression claim (`tools/souji-census.sh:92`, `112-119`) is untested.
- For r15, the config families include tilde/`~` expansion and include/includeIf, which depend on HOME. Those would be untested under the same overrides.
- Acceptance (r15): at least one case must run **without** the `GIT_CONFIG_GLOBAL`/`SYSTEM`/`NOSYSTEM` overrides, with synthetic `HOME` containing a `.gitconfig` whose `include.path` / `includeIf` points into the synthetic store. Expected: no store access, and the expected row or refusal.

### F4 — Medium, calibration: `proc-fd` subcase is vacuous
- Case 05 uses `"/proc/self/fd/999"` (line 572). `run_tool` passes no `pass_fds` (391-400) and the child's descriptor 999 is never opened, so the subcase never names a store alias. It only checks the tool's lexical `/proc/*` rule (`tools/souji-census.sh:1009`).
- Acceptance (r15): if a descriptor case is kept, pass a real fd to `RECORDS` via `pass_fds`, and assert refusal plus zero access. Otherwise rename it as a lexical `/proc` rule check and drop the alias claim.

### F5 — Medium, calibration: the `is_baseline` gate keys on the wrong red
- The red oracle at lines 703-715 is keyed to `BASELINE_SHA` (a31642d, `6a000c59…`). For r15 the harm-red tool is the r14 installed tool (`fcff8b05…`), which the gate does not recognise. It would get no red requirement at all.
- C1 harm is an operability failure: a benign repo is refused (rc 2, zero rows) with **no store access**. An access-based red cannot discriminate it.
- `refusal_problems` (480-502) accepts `rc==2 and "path-protected" in stderr` as correct. A value-blind refusal of a **benign** config would pass that check. Benign cases must use `positive_problems` (rc 0, expected row content), never `refusal_problems`.
- Acceptance (r15): pin two digests (harm-red `fcff8b05…`; repaired computed and reported, not pinned). Red must fail the named benign positive assertions while showing zero store access. Green must pass all. The access checks must hold at zero on both. Do not reuse the `BASELINE_SHA` access-requirement rule for C1.

### F6 — Medium, calibration: root-stat leniency is keyed to the case, not the tool
- `positive_problems(..., scratch=True)` sets `allow_root_stat=True` (line 538). A bare store-root `stat` is then accepted for case 08 under **any** tool, including a future regression.
- Acceptance (r15): limit the leniency to the named legacy scratch control and to the legacy digest, or drop it for r15 positive cases.

### F7 — Medium, calibration: the probe does not verify the string-match prerequisite
- `probe_strace` (322-358) checks only that a denied `cat` yields `EACCES` plus the store string. The string channel depends on `-y` annotations, which the probe does not check.
- Committed evidence confirms the annotation form (`census/round-14/verification.json`: `newfstatat(AT_FDCWD</var/tmp/r14-census-boundary.emw46pxs>, …`). Annotations on `AT_FDCWD` are how relative accesses from a store cwd become visible.
- Acceptance (r15): the probe must also assert the `</…/agent…>` annotation appears, so a missing `-y` flag fails as harness error (exit 2), not as a candidate finding.

### F8 — Medium, calibration: harness failures are attributed to the candidate
- `refusal_problems` / `positive_problems` report `contract: strace log missing or empty` and `exit=124` (timeout) as candidate failures (lines 482-483, 507-510). The header says exit 2 is "could-not-evaluate", but a per-run trace failure exits 1 ("failed").
- Acceptance (r15): a per-run trace or timeout failure must be `harness:` and exit 2, not a candidate `contract:` failure.

### F9 — Low, calibration: `EACCES anywhere` is broad but intentional
- `trace_access` treats any `EACCES` line as a hit (line 435). That is the only channel that catches alias lookups, given store mode 000. The breadth is a trade-off, not a defect. It should be stated in the docstring with the F1 caveat.

### Not claimed (checked, not observed)
- `readlinkat`: the committed verification shows `readlink(` (5 occurrences, 0 `readlinkat`). No finding is raised.
- `openat2(` is absent from the open tokens (`420-466`). Not observed in evidence; not claimed.
- `chdir` coverage under `%file` is unverified; not claimed.

## Channel coverage (what each check can and cannot see)

| channel | sees | misses |
|---|---|---|
| PATH spy (`SPY_TOOLS`) | argv/PWD/GIT_* of listed tools invoked by bare name | unlisted tools (awk, grep, sort, date, …); absolute paths; builtins; kernel reads by a spied tool; paths not containing the store string; silence when inert (F2) |
| strace `%file,getdents64,execve` with `-f -y` | syscalls whose path or fd annotation contains the store; `EACCES` anywhere; store `execve` argv | successful alias lookups with no annotation (F1); success-stat of an alias; reads through inherited fds; syscalls outside the filter |
| `EACCES` (store mode 000) | any denied lookup beneath the store, via any path | successful accesses; a readable store (no denial); root or non-000 fixtures |

## Acceptance for the r15 fixture (design-only; source not present)

1. Self-invocation gate `python3 tests/fixtures/r15-census-config.py --tool PATH`: 0 clean; 1 failed case or id-set; 2 could-not-evaluate (missing strace/tool, probe failure, root, harness error). Mirrors r14 exits.
2. Literal pinned case IDs and an exact row/exit expectation per case. Each r14 refused family appears as a value-unsafe and value-safe case; neutralised hooks, attrs, excludes, fsmonitor; safe includes including a mixed fleet; false promisor/worktreeConfig; safe clean filters. Unaffected mixed-fleet rows keep their expected row content.
3. Benign cases use positive assertions (rc 0, row content, dirty fidelity). Refusal cases use refusal assertions (rc 2, expected finding). No benign case may be scored as a refusal (F5).
4. Each case runs the access channels in F2 and F7, plus spy liveness on positive cases. Access failures are labelled `access:`; contract failures `contract:`; harness failures `harness:` with exit 2 (F8).
5. At least one case runs without the `GIT_CONFIG_GLOBAL`/`SYSTEM`/`NOSYSTEM` overrides and with a synthetic HOME `.gitconfig` pointing into the store (F3).
6. A harness self-check of `trace_access` with synthetic strings, run inside the fixture, covering F1's list. No real probe.
7. Pins: harm-red `fcff8b05…`; repaired digest computed and printed; baseline `6a000c59…` only if the baseline is reused.

## Hand-off
- To SoujiR15 (executor/fixture author): items 3, 5, 6 and F1 are the material ones. Acceptance is design-only until `tests/fixtures/r15-census-config.py` lands.
- Unrun checks for L1: `python3 tests/fixtures/r15-census-config.py --tool <repaired>` and `--tool <r14 harm>` once the fixture exists; a synthetic `trace_access` self-check; spy-liveness on the positive cases.

## Process disclosure (no-query boundary)
- Violated: my first `_glob` call used the lane root `/home/vgpnk/Projects/shokunin/souji-shokunin` as its path with `limit: 200`. It is recursive and returned file names under `census/operator-sweep-20261019/` (stage-hold-delete.sh, kotodama-children-sizes.tsv, .hold.json, second-check.py, results/, and similar). Names only: no file was opened, read, copied, edited, or queried.
- Also at the start, one `_bash` `ls -la` on the lane root listed top-level entries including `census/` by name only. It did not descend into `census/operator-sweep-*`.
- All later reads and greps used explicit files or directories: `tests/fixtures/*`, `tools/souji-census.sh`, `corpus/*`, `LOG.md`, `SKILL.md`, `SCORECARD.md`, `census/round-14/verification.json`, `census/round-15/` (directory listing only), `.ufo/waves/round-15/*`. One `_grep` ran over `corpus` and the fixture files named explicitly.
- Limitation: the operator-sweep file names now appear in this transcript. Their contents were not inspected, and nothing in this report depends on them.
- No runtime probes, tests, or shell empirical probes were run. Only `sha256sum`, `git status`, `git log`, `ls`, `grep`, and file reads were used.
