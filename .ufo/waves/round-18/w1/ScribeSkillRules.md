# ScribeSkillRules — round 18, wave 1 (report-only; SKILL.md NOT edited)

STATUS: DONE — drafted SKILL.md error patterns (2) and registry rows (5) below; text only, no file in the lane edited.

Judged axis: **operability** (C1 hang-proofing + C3 residue surface). Axis calibration/coverage not scored here.

Axes named: operability (judged) · calibration (text must not cite absent files — see Finding F3) · coverage (rows cover the 5 requested surfaces).

## Evidence read (exact commands, outputs summarised)

| command | observed |
|---|---|
| `read SKILL.md:74-112` | error patterns end at line 111 (jj detached HEAD); pattern shape = bold name, live instance, recheck command |
| `read SKILL.md:133-170` | registry header at :135-141; table columns `name \| kind \| entry command \| verdict map \| self-test command \| pinned-value path \| write scope \| owner`; rows :145-167 |
| `read SKILL.md:147,159:raw` | census and r17-census-matrix rows in full |
| `read tools/souji-census.sh:1380-1423` | `emit_census` :1394-1416; loop :1402-1411 calls `census_one` inside `$(...)` at :1403 (no process group, no watchdog) |
| `read tools/souji-census.sh:539-593` | `guard_git_files` :546-585 lstat-classifies `info/attributes` (`stat -L -c '%F %h'` :555) then returns; git opens the path later — the TOCTOU window |
| `grep 'repo-timeout\|SOUJI_CENSUS_REPO_TIMEOUT\|set -m' tools/souji-census.sh` | **0 matches** — neither the bound nor the group exists at b576341 |
| `grep ^HEADER= tools/souji-census.sh` | `repo worktrees unpushed dirty scratch_bytes mtime_iso verdict_flags` = 7 columns; the planned error row `<repo>\t0\t0\t0\t0\t\terror` is also 7 fields — consistent |
| `grep subprocess\|start_new_session\|killpg tests/fixtures/r17-census-hygiene.py` | `Popen` :293, `start_new_session=True` :303, `communicate(timeout)` :310, `os.killpg(…SIGKILL)` :314, `unblock_fifos` :318 — the reference pattern |
| `grep … tests/fixtures/r15-census-config.py;tests/fixtures/r14-census-boundary.py` | `subprocess.run(… timeout=…)` at r15 :274-282, :734-747, :781-791; r14 :125-133, :330-351, :392-400; **no** `start_new_session`, **no** `killpg` in either |
| `awk` over `census/round-18/leaked-procs-before-1631.txt` | 58 lines: 32 `bash …souji-census.sh`, 26 `/usr/bin/git`; 26 lines have ppid 1497 |
| `ls census/round-18/` | only `leaked-procs-before-1631.txt`; `tools/souji-proc-census.sh` absent (`test -f` → absent); `tests/fixtures/` has no r18-* file |
| `ls census/round-17/` | `gate-replays-ddb7347.json` and `jj-receipts-ddb7347.txt` **absent**; present: `gate-replays-4f48343.json`, `jj-receipts-4f48343.txt`, `jj-receipts-base5fa6017.txt` |
| `grep -n ddb7347 SKILL.md` | lines 163, 165, 166 (the registry rows for souji-landing-gate, r17-gate-replays and souji-seat-audit) |
| `command -v strace setsid shellcheck; strace --version` | `/usr/bin/strace` (7.2), `/usr/bin/setsid`, `/usr/bin/shellcheck` present; `python3` 3.14.8 |
| `ls .ufo/waves/round-18/w1/` | directory exists (holds `swarm-registry.json`, not mine; untouched) |

Tooling: no installs or upgrades performed (`strace`, `setsid`, `shellcheck` already present; nothing recorded as installed).

## Findings

**F1 — the two error patterns are real and need the watchdog rule (operability, verdict: holds as a drafting need).** Evidence: `tools/souji-census.sh:1403` runs `census_one` with no group and no bound; the L1 reproduction (in the Goal) shows an outer `timeout 15` returning rc 124 with zero rows. The bound (`--repo-timeout`, `SOUJI_CENSUS_REPO_TIMEOUT`) is absent at b576341 (grep above).

**F2 — the orphan mechanism is the fixture pattern, not only the census (operability, verdict: holds).** `subprocess.run(timeout=)` kills only its direct child. r14 and r15 use it with no `start_new_session`/`killpg` (lines above). The host residue is 58 lines of census bash + git (`leaked-procs-before-1631.txt`). Lines mentioning `r15-census-config` 44, `r17-census-hygiene` 14, `FixtureR17Census` 10, `r16-repin` 7 (a line can match more than one). The r17 fixture at HEAD already kills the group (:303-318); its leaked lines are from older copies (`FixtureR17Census/a31642d.sh` path) — [INFERENCE] from the path names, not verified by process inspection.

**F3 — calibration: SKILL.md:163, 165, 166 cite `census/round-17/gate-replays-ddb7347.json` and related records that do not exist (verdict: fails; smallest fix: retarget to `…-4f48343.json` or the committed `gate-replays-expected.json`).** Also `corpus/knowledge/jj-colocation-receipts.md:2,44,126,148` cites `census/round-17/jj-receipts-ddb7347.txt` (absent). This is exactly the class LG-DANGLING-PTR must catch at round ≥ 18. Consequence for this text: **every new row below names `tests/fixtures/r18-*` and `census/round-18/*` files that do not exist yet. They MUST NOT land in SKILL.md before those files land**, or LG-DANGLING-PTR fires on the very skill that registers them.

**F4 — the registry needs the planned rows to be runnable, not aspirational (operability, verdict: partial).** Each row below names an entry and self-test command; the files are the C1/C3 deliverables. Until landed, the rows are drafts. The legacy probes (`souji-verify`, `souji-quarantine`) keep their own legacy-debt rows and are untouched.

**F5 — census verdict map must keep rc 124 as FAIL for the bounded gate (operability).** The r17 gate already maps a case timeout to FAIL (`tests/fixtures/r17-census-hygiene.py:502-503`, rc 124 FAIL "never SKIP", SKILL.md:158). The r18 gate keeps that rule: a case that does not return within the fixture bound is FAIL, never a green arm.

**F6 — the planned exit-0 census row is a placeholder, not a measurement (calibration).** SKILL.md:147 already says degraded repositories exit 0 and are placeholders. The timeout row (`…\terror`) must carry the same caveat in the probe row, otherwise a fleet with one hung repository reads as measured.

## Drafted SKILL.md text (for L1 to place; not applied)

### Error patterns — insert after the `jj: detached HEAD` bullet (after current line 111)

- **Post-guard FIFO swap hangs a whole-fleet reader** (r18, C1): `guard_git_files` (`tools/souji-census.sh:546-585`) lstat-classifies `$GIT_DIR/info/attributes` and returns; git opens that path later. A regular file swapped for a FIFO in that window blocks git in `open(2)` forever, and the census — running each repository in the foreground — never returns. An outer `timeout N` then returns rc 124 with zero rows and loses every healthy neighbour. Watchdog rule: each per-repository census runs in its own process group (bash `set -m` only around that fork) with stdout to a private temp file; a watchdog sends SIGTERM to the group at the bound and SIGKILL 2 s later. The bound is `--repo-timeout N` or `SOUJI_CENSUS_REPO_TIMEOUT` (integer 1..86400, default 600; invalid → usage exit 2). A timed-out repository becomes the row `<repo>\t0\t0\t0\t0\t\terror` with stderr `souji-census: repo-timeout <N>s <repo>`; the run still measures the rest and exits 0. Only a protected refusal (`census_one` exit 2) stops the whole run; other nonzero exits 1. The watchdog never outlives its repository and holds no caller stdout or stderr pipe. At b576341 neither the group nor the bound exists (`grep` finds 0 matches). Recheck: `bash tests/fixtures/r18-census-bounded.sh` (planned; not yet landed).
- **A fixture timeout that kills only its child leaves a git blocked forever** (r18, C1 host evidence): `subprocess.run(..., timeout=N)` kills only the direct child, so the census and the git it started survive; a git blocked in `open(2)` on a writer-less FIFO stays blocked. `tests/fixtures/r15-census-config.py:274-282, :734-747, :781-791` and `tests/fixtures/r14-census-boundary.py:125-133, :330-351, :392-400` take this form. The host holds 58 leaked lines in deleted `/var/tmp` dirs (`census/round-18/leaked-procs-before-1631.txt`: 32 census bash, 26 `/usr/bin/git`). Rule: a fixture that can launch a census or git against a FIFO runs it with `start_new_session=True` and, on timeout, `os.killpg(proc.pid, SIGKILL)` then waits; the reference is `tests/fixtures/r17-census-hygiene.py:293-318`. A fixture arm counts as green only if its process group holds 0 processes after the run. Recheck: `tools/souji-proc-census.sh` (planned) reports 0 residue rows for the fixture's pid range.

### Gate registry — insert rows after `r17-census-matrix` (after current line 159) and keep the table header

| name | kind | entry command | verdict map (code → class) | self-test command | pinned-value path | write scope | owner |
|---|---|---|---|---|---|---|---|
| r18-census-bounded | gate | `python3 tests/fixtures/r18-census-bounded.py --tool PATH` | 0 clean: the blocked repository is an `error` row with stderr `souji-census: repo-timeout <N>s <repo>`, neighbour rows byte-identical to a run without it, exit 0; a protected refusal still exits 2; invalid bound exits 2; the pre-fix tool under the same FIFO-swap shim reproduces rc 124 (vacuity control); 1 failed case or id-set, a surviving process in any case's group, or a case exceeding the outer per-case timeout (rc 124 is FAIL, never SKIP); 2 could-not-evaluate missing `git`/`setsid`/`strace`, usage, or missing `--tool` | `python3 tests/fixtures/r18-census-bounded.py --selftest` (planned, same default invocation over isolated synthetic HOME) | literal `EXPECTED_IDS` and per-case class (`repair`/`preserve`/`refuse`), expected exit/row; `census/round-18/c1-matrix.json` (L1) | isolated private tempdir under `/var/tmp`; never a real fleet root or credential store; FIFO shims unblocked after each case | souji |
| souji-proc-census | probe | `bash tools/souji-proc-census.sh [--json]` (read-only; lists current-uid processes whose cwd is deleted or whose argv names a missing path under /var/tmp, /tmp or /dev/shm; columns pid, ppid, pgid, age, state/wchan, reason, redacted truncated command) | 0 scan complete — rows are data, an empty table means no residue; 1 failed selftest (only with `--selftest`); 2 could-not-evaluate usage or unreadable `/proc`; never signals a process, never reads `/proc/<pid>/environ` | `TMPDIR=/var/tmp bash tools/souji-proc-census.sh --selftest` (plants a sleeper with deleted cwd and a missing-argv path, plus a live control; the sleepers are killed by their own group) | none; no pinned process set | stdout only; selftest under `/var/tmp`, kills only processes it started; reads `/proc/<pid>/{stat,cmdline,cwd,wchan}` | souji |
| r18-proc-census | gate | `python3 tests/fixtures/r18-proc-census.py --tool tools/souji-proc-census.sh` | 0 clean: planted orphans detected, live controls absent, probe pid set equals an independent counter's pid set, and `strace -f -e trace=kill,tkill,tgkill` records zero signal syscalls from the probe; 1 failed case, id-set, or pid-set difference; 2 could-not-evaluate missing `strace`/`setsid`/usage | `python3 tests/fixtures/r18-proc-census.py --selftest` | literal `EXPECTED_IDS`; planted-case expectations in the fixture | isolated `/var/tmp`; plants and kills only its own sleepers, verified 0 survivors | souji |
| r18-landing-pointers | gate | `python3 tests/fixtures/r18-landing-pointers.py --tool tools/souji-landing-gate.py` (plus the real sweep `python3 tools/souji-landing-gate.py --root LANE --rev REV --round 18 --json OUT`, which must show 0 `LG-DANGLING-PTR`) | 0 clean: every synthetic dangling token gives `LG-DANGLING-PTR`, every fleet-only token gives `fleet` not a finding, every `corpus/pointer-exemptions.tsv` entry suppresses one token, and `--round 17` leaves `census/round-17/gate-replays-expected.json` unchanged; 1 failed case or any `LG-DANGLING-PTR` at REV (the landing gate's own finding code); 2 could-not-evaluate missing prerequisite/usage/unknown rev | `python3 tests/fixtures/r18-landing-pointers.py --selftest` | literal finding ids; `corpus/pointer-exemptions.tsv` (committed; candidates: `.ufo/state`, `.ufo/watchdog.log`, the untracked quarantine stub); `census/round-17/gate-replays-expected.json` | reads committed blobs at REV; isolated `/var/tmp` git repos removed afterwards | souji |
| r18-census-matrix | evidence | `python3 census/round-18/run-matrix.py --changed <rev or WORKTREE> --output <new.json>` | 0 record written and every suite valid (fixture exit agrees with its SUMMARY); the baseline red arm of r18-census-bounded is recorded under `pre_harm` as expected red, never as a suite failure, and the changed arm must be green; 1 unused by code (an unhandled crash is an unstructured nonzero, never a fixture verdict); 2 could-not-evaluate invalid suite, unknown revision, missing fixture, dirty fixtures without `--allow-dirty-fixtures`, refused `--output` overwrite, usage | `python3 -m py_compile census/round-18/run-matrix.py`; the selector table supplies `--tool` for r18-census-bounded and r18-proc-census | `census/round-18/c1-matrix.json` (L1) read with the r18-census-bounded, r18-proc-census, r17-census-hygiene and r15-census-config rows | per-fixture isolated `/var/tmp`; writes only `--output` (refuses overwrite) | souji |

## Out of scope (not done here)

- No edit to `SKILL.md`, `tools/`, `tests/`, `corpus/`, or `census/` (report-only, per assignment).
- R2 retarget (SKILL.md:163,165,166 `ddb7347` → an existing record) is a one-line L1 integration item; I did not apply it.
- Not verified by running: the probe, the watchdog, and any fixture (none exist yet; the contract forbids running the census against real directories). The r17-residue attribution in F2 is [INFERENCE].

## Checks for main agent after integration

1. `grep -n 'r18-\|census/round-18' SKILL.md` must resolve every path it names (LG-DANGLING-PTR at round 18).
2. `python3 tools/souji-landing-gate.py --root <lane> --rev <tip> --round 18` → 0 `LG-DANGLING-PTR`.
3. Land the registry rows only with their fixtures; otherwise the rows fail check 1.
