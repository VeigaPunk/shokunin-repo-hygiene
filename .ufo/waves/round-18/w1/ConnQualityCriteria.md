STATUS: DONE — each r18 artifact is bound to the published Q4/Q9/Q17/Q19/Q25/Q26 test whose subject is that artifact; L1's landing commands are the ones named here.

Axes: calibration (this seat; improve by binding tests to subjects), operability (hold: no live-fleet census, scratch stays `/var/tmp`, session kill stays), coverage (hold: residue scan still sees `/tmp` and `/dev/shm` as read roots).

Worktree `HEAD` is `b5763415cc67ecff1e8fe56c58c39a6fb106d7a3`. `git diff --stat` of that rev against the files cited below was empty. These landing commands were not executed here (QUALITY.md:58, Q24). An unrun check has not passed. No tool was installed.

## Proposal

L1 admits each artifact by the command in its section below. A criterion is in force for that artifact when its published test names that artifact. Where the safety rule binds and the published command names a different tool, the section says `hold` and gives the command that does name it.

One row is missing from the four ScribeQualityRows drafts (Q29–Q32). When `LG-FROZEN-MEASURED` starts firing on an unresolvable `measured_commit`, add a superseding row that names Q25 (QUALITY.md:11-14 forbids rewriting Q25 in place). The parenthetical at QUALITY.md:64 ("a dangling `measured_commit` is not yet flagged by the gate: open, r17") would otherwise describe a gate that the same landing just changed. Q31 covers authority-file path tokens; it does not name that parenthetical. The new row's test is: a frozen record whose `measured_commit` does not resolve yields `LG-FROZEN-MEASURED` for `--round` ≥ 18, and `python3 census/round-17/gate-replays.py` still matches `census/round-17/gate-replays-expected.json` for the historical `--round` values.

## How the six tests bind

| id | published test (subject) | source |
|---|---|---|
| Q4 | `grep -c 'TMPDIR:-/tmp' <fixture>` → 0 and `grep -c '/var/tmp' <fixture>` ≥ 1, and a trap removes the scratch | QUALITY.md:28 |
| Q9 | `shellcheck -S warning <script>; echo $?` → 0 | QUALITY.md:33 |
| Q17 | `python3 tools/souji-cert-evidence.py --selftest` (missing evidence and escaping paths) | QUALITY.md:41 |
| Q19 | `bash tests/fixtures/r13-quarantine-bounds.sh --tool <quarantine-script>` | QUALITY.md:43 |
| Q25 | `python3 tools/souji-landing-gate.py --root <lane> --rev <landing> --round <N>` exit 0 with nonzero `checked_reports`; training `--rev b410186 --round 15` exits 1 | QUALITY.md:64 |
| Q26 | `python3 tools/souji-seat-audit.py --spec <wave-spec> --transcripts <dir> --lane <lane> --json census/round-<N>/seat-audit-<wave>.json` | QUALITY.md:65 |

Q25's own sentence: a gate pass is consistency, not behavior (QUALITY.md:64). Registry citation shape is `CITED_PATH_RE` at `tools/souji-landing-gate.py:75-78`. An uncited script that does not parse is a clean gate (`tools/souji-landing-gate.py:1022-1024`). A script becomes a Q25(a) subject when a `SKILL.md` row cites it.

At `b576341` the gate's finding-id pin is `LG-PARSE-REG`, `LG-MISSING-REG`, `LG-PARSE-CHANGED`, `LG-FROZEN-PIN`, `LG-FROZEN-MEASURED`, `LG-SEAT-UNCARRIED`, `LG-OPEN-ADMITTED` (`tools/souji-landing-gate.py:115-123`). `LG-DANGLING-PTR` is absent. An unresolvable `measured_commit` sets `measured_ok = False` and the digest loop is skipped (`tools/souji-landing-gate.py:548-570`; comment at :548: "A dangling measured_commit contributes no checks"). The existing selftest cases `frozen-measured` (:1075) and `frozen-measured-absent` (:1101) fire when the commit resolves and the pinned bytes differ or the path is absent.

Python fixtures already admitted under Q4 use `dir="/var/tmp"` and a `finally` block. r15 states that parity at `tests/fixtures/r15-census-config.py:105`. The shell grep-and-trap spelling stays the test for shell fixtures.

Q16 (QUALITY.md:40): no admitted fixture writes outside `/var/tmp`. A proc-census that *reads* `/tmp` and `/dev/shm` still has its fixture scratch under `/var/tmp`.

## Per artifact

### Census watchdog (`tools/souji-census.sh` `emit_census`)

Present at base: `emit_census` (:1394-1416) calls `census_one` in the shell loop with no per-repo bound. `guard_git_files` (:546-555) stats `info/attributes` before a later git open. Compare capture is `mktemp /var/tmp/souji-census-now.XXXXXX` plus `trap cleanup_census_tmp EXIT` (:1510-1511); cleaner is :211-215. Selftest scratch is `mktemp -d /var/tmp/souji-census-selftest.XXXXXX` with `trap 'rm -rf -- "$ST_TMP"' EXIT` (:1613-1614) and `TMPDIR=/var/tmp` (:1884).

| criterion | binding | L1 command at landing |
|---|---|---|
| Q4 | hold. New watchdog temp files stay inside `CENSUS_TMP` / `cleanup_census_tmp` and the selftest's `/var/tmp` trap. The grep spelling is the fixture's test. | `grep -c 'TMPDIR:-/tmp' tools/souji-census.sh` → 0; `grep -c '/var/tmp' tools/souji-census.sh` ≥ 1; traps at :1511 and :1614 still remove the files. Selftest invocation is `TMPDIR=/var/tmp bash tools/souji-census.sh --selftest` (SKILL.md:140, :147). CensusWatchdog's contract: base selftest count 49, report the after count. |
| Q9 | run. | `shellcheck -S warning tools/souji-census.sh`; exit 0. Also `bash -n tools/souji-census.sh` with empty stderr (Q25(a), same script). |
| Q17 | hold for any new path the lesson or SKILL cites. The published command's subject is cert-evidence fragments. | `python3 tools/souji-cert-evidence.py --selftest` stays the frozen-fragment check. A census path token in an authority file is resolved by `LG-DANGLING-PTR` (see that section). |
| Q19 | skip. The published command's subject is `<quarantine-script>` and the r13 finding ids (QUALITY.md:43). The C1 contract is a post-guard timeout row, which is a different operation from a quarantine move that refuses a special file before deletion. | `python3 tests/fixtures/r18-census-bounded.py --census tools/souji-census.sh` with `SOUJI_CENSUS_REPO_TIMEOUT=8`: B1/B2 `error` row plus stderr `souji-census: repo-timeout 8s`, neighbours measured, exit 0; B5 bound 30 measured; B6 zero leftover processes and `O_WRONLY\|O_NONBLOCK` → `ENXIO`; B7 protected refusal exit 2. The same fixture on `git show b5763415cc67ecff1e8fe56c58c39a6fb106d7a3:tools/souji-census.sh` fails B1/B2 by timeout. |
| Q25 | run, parse only. `tools/souji-census.sh` is already cited (SKILL.md:147), so it is inside `checked_reg` (`tools/souji-landing-gate.py:635-647`). | `python3 tools/souji-landing-gate.py --root <lane> --rev <landing> --round 18` exit 0, `checked_reg` > 0, no `LG-PARSE-REG` on `tools/souji-census.sh`. Exit 0 does not accept the FIFO arm. |
| Q26 | run on the CensusWatchdog seat, not on the script. A live `--root` outside `/var/tmp` is `V-LIVE-CENSUS` (`tools/souji-seat-audit.py:14-15`, selftest case `live-census` at :328). The seat's allowed census roots are synthetic directories under `/var/tmp/souji-r18-CensusWatchdog/`. | `python3 tools/souji-seat-audit.py --spec .ufo/waves/round-18/w1-spec.json --transcripts <dir> --lane <lane> --json census/round-18/seat-audit-w1.json` after the wave transcripts exist. |

### `tests/fixtures/r18-census-bounded.py`

Absent at `b576341` (read failed). New file.

| criterion | binding | L1 command at landing |
|---|---|---|
| Q4 | hold, Python parity (r15:105). Scratch `dir="/var/tmp"`, removed in `finally`. Every census child `start_new_session=True`, `os.killpg` `SIGKILL` on the 40 s fixture timeout. | `grep -c 'TMPDIR:-/tmp' tests/fixtures/r18-census-bounded.py` → 0; `grep -c '/var/tmp' tests/fixtures/r18-census-bounded.py` ≥ 1; the file contains `start_new_session=True` and `killpg`. |
| Q9 | skip. Subject is a shell script. | `python3 -m py_compile tests/fixtures/r18-census-bounded.py` |
| Q17 | hold once SKILL, QUALITY, or the lesson cites it. Citing it in a commit where the blob is absent is `LG-MISSING-REG` if the citation matches `CITED_PATH_RE`, and `LG-DANGLING-PTR` for a `tests/` token at `--round` ≥ 18. | Same-revision blob: `git -C <lane> cat-file -e <landing>:tests/fixtures/r18-census-bounded.py` succeeds and the path is a regular file (Q17's "regular, non-symlink" rule). |
| Q19 | skip. Same subject mismatch as the watchdog. | The B1–B7 command in the watchdog section, on the landed census and on the extracted base census. |
| Q25 | run once a SKILL registry row cites `tests/fixtures/r18-census-bounded.py`. | Landing gate exit 0 and no `LG-PARSE-REG` / `LG-MISSING-REG` for that path. `python3 tests/fixtures/r16-landing-gate.py --tool tools/souji-landing-gate.py` stays the synthetic Q25 fixture; it does not run the FIFO cases. |
| Q26 | run on the FixtureR18Bounded seat. Allowed exec is the fixture against `/var/tmp` census copies and `py_compile`. | Seat-audit command above. |

### Fixture session fixes (`r15-census-config.py`, `r17-census-hygiene.py`, `r14-census-boundary.py`)

`census/round-18/leaked-procs-before-1631.txt` has 58 lines. Grep counts on that file: `r15-census-config` 44, `r17-census-hygiene` 14, `r14-census` 0. Sample parents are pid 1497 (reparented), argv under deleted `/var/tmp/r15-census-config.*` and `/var/tmp/r17-census-hygiene.*` (file lines 1-9). This seat did not signal those pids.

r15 census invocation is `subprocess.run` of `strace` wrapping `bash <tool>` at :781-789, `timeout=90`, `TMPDIR=/var/tmp` at :764. `TimeoutExpired` (:790-793) records rc 124 and returns. There is no `start_new_session` and no `killpg`. `run_setup` (:274) and `probe_strace` (:734) are the other `subprocess.run` sites. Scratch is `mkdtemp(..., dir="/var/tmp")` at :1481. Q4 parity is stated at :105.

r17 `run_tool` already uses `start_new_session=True` (:303) and `os.killpg(proc.pid, SIGKILL)` on `TimeoutExpired` (:312-317), then `unblock_fifos` (:328-334). `TMPDIR=/var/tmp` at :278. Scratch at :1222. The other `subprocess.run` sites are setup (:150, timeout 60) and a locale `stat` probe (:1099-1106), not a census git. The wave prompt's "subprocess.run at :1105" is that `stat`. The 14 leaked r17 lines in the host file name `/var/tmp/souji-r17-FixtureR17Census/{a31642d,cc21683}.sh`, which are extracted older census bytes, parented to 1497, so the Python that started them was already gone. A patch that only wraps :1099 does not reap those git processes.

r14 census invocation is `subprocess.run` of `strace` plus `bash <tool>` at :392-400, `TimeoutExpired` returns at :401-402 with no `killpg`. The host list contains no `r14-census` line. The same timeout hole is in the source. FixtureReapR14's contract: if neither arm leaks, record 0→0 and keep a change only with a demonstrated hang path.

| criterion | binding | L1 command at landing |
|---|---|---|
| Q4 | run the greps; hold the cleanup rule. r15 and r17 already hard-code `/var/tmp`. The reap must still remove that scratch, and on timeout must kill the session so the directory removal does not leave a blocked git. | For each of the three files: `grep -c 'TMPDIR:-/tmp'` → 0 and `grep -c '/var/tmp'` ≥ 1. r15 and r14 census calls gain `start_new_session=True` and `os.killpg(..., SIGKILL)` on timeout. r17 keeps :303 and :314. |
| Q9 | skip. All three are Python. | `python3 -m py_compile` on each. They are already registry-cited (SKILL.md:156 r14, :157 r15, :158 r17), so the landing gate's `LG-PARSE-REG` is the same parse. |
| Q17 | hold. They already resolve at `b576341`. The published cert-evidence command does not open them. | `git cat-file -e <landing>:tests/fixtures/r15-census-config.py` (and the r17 and r14 paths) succeeds. |
| Q19 | skip. Subject is the quarantine bounds fixture. | Leftover-process count, below. |
| Q25 | run, parse only, because the three paths are cited. | Landing gate exit 0, no `LG-PARSE-REG` on those three paths. Q22 (QUALITY.md:56) still requires the existing case ids, exits, and rows to stay the same on the changed fixture bytes. |
| Q26 | run on FixtureReapR15, FixtureReapR17, FixtureReapR14. Each may kill only processes it started. | Seat-audit command above. |

Landing behavior checks (wave contract):

- r15: fixture against `git show a31642d:tools/souji-census.sh` extracted under `/var/tmp`. Count `ps -eo pid,args` whose argv contains the private tempdir prefix: base N → patched 0.
- r17: same count against `git show 5fa6017:tools/souji-census.sh` (D2 FIFO cases). Judge the leftover count. The locale `stat` at :1099 is a different call.
- r14: same count against `git show cc21683:tools/souji-census.sh` and `a31642d:tools/souji-census.sh`. Zero r14 lines in `leaked-procs-before-1631.txt` is the host snapshot; it is not a proof that :392-402 reaps.

`census/round-17/run-matrix.py:233-235` puts only an invalid *suite* into `invalid_suites`. It records `shellcheck -S warning` rc (:206-211) and does not fail the run on that rc. `corpus/lessons/round-17.md:65` leaves that open. Matrix exit 0 is not Q9.

### `LG-DANGLING-PTR` (change to `tools/souji-landing-gate.py`)

| criterion | binding | L1 command at landing |
|---|---|---|
| Q4 | hold for the existing selftest. `run_selftest` uses `mkdtemp(..., dir="/var/tmp")` (`tools/souji-landing-gate.py:866`). | Selftest scratch prefix stays `souji-landing-gate-selftest-` under `/var/tmp` and is removed. |
| Q9 | skip. Python. | `python3 -m py_compile tools/souji-landing-gate.py`; `python3 tools/souji-landing-gate.py --selftest` (SKILL.md:163, exact id sets, including the new cases: dangling token, braces, `path:line`, placeholder skip, exemption, malformed exemption → exit 2, fleet-only token, `--round 17` emits no `LG-DANGLING-PTR`, unresolvable `measured_commit`). |
| Q17 | hold. The new finding is the round-gate resolver QUALITY.md:41 describes as separate from cert-evidence. | `python3 tools/souji-cert-evidence.py --selftest` unchanged. Pointer resolution is the gate command below. |
| Q19 | skip. Subject is quarantine moves. The gate reads blobs and runs `bash -n` / `compile()` (SKILL.md:163 write scope). | Gate selftest plus the historical replay command below. |
| Q25 | run, and this change is what closes the open parenthetical. The id is added to the pin at :56-57 and :115-123. `--round` < 18 must leave historical replays identical. | `python3 tools/souji-landing-gate.py --root <lane> --rev <landing> --round 18` exit 0, nonzero `checked_reports`, after the dangling tokens are fixed or exempted. Training instance `--rev b410186 --round 15` still exits 1 with `LG-PARSE-REG`, `LG-FROZEN-PIN`, `LG-FROZEN-MEASURED`, `LG-SEAT-UNCARRIED`. `python3 tests/fixtures/r16-landing-gate.py --tool tools/souji-landing-gate.py` exit 0. `python3 census/round-17/gate-replays.py` matches `census/round-17/gate-replays-expected.json` (SKILL.md:165: b410186 → 1 with 5 ids; a31642d, cc21683, 6ff91f5 → 0; 79bbe7a → 1 with 29 `LG-SEAT-UNCARRIED`). |
| Q26 | run on the GatePointers seat. Allowed exec includes the gate read-only at `b576341` and `r16-landing-gate.py --tool <gate>`. | Seat-audit command above. |

Counting command from the wave goal, before any exemption or path fix: `python3 tools/souji-landing-gate.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev b5763415cc67ecff1e8fe56c58c39a6fb106d7a3 --round 18 --fleet-root /home/vgpnk/Projects/shokunin`. L1's prior sweep: 281 tokens, 18 unresolved, including `census/round-17/gate-replays-ddb7347.json` at SKILL.md:163 and :165, and `census/round-17/jj-receipts-ddb7347.txt` at `corpus/knowledge/jj-colocation-receipts.md:2,44,126,148`. This seat did not re-run that sweep.

`corpus/pointer-exemptions.tsv` is absent at `b576341` (read failed). Deliberate non-files (`.ufo/state`, `.ufo/watchdog.log`, the quarantine stub) become non-findings only through that committed TSV (`path<TAB>reason`, reason nonempty; malformed → exit 2). A `corpus/` citation of the TSV in a revision that lacks the blob is itself a dangling token. Q14 (QUALITY.md:38) still makes `.ufo/state/` and `watchdog.log` report-only; an exemption row is not a deletion approval.

### `tests/fixtures/r18-landing-pointers.py`

Absent at `b576341` (read failed).

| criterion | binding | L1 command at landing |
|---|---|---|
| Q4 | hold, Python parity. Isolated git repos under `/var/tmp`, removed afterwards (same shape as SKILL.md:164). | `grep -c 'TMPDIR:-/tmp'` → 0; `grep -c '/var/tmp'` ≥ 1; cleanup on exit. |
| Q9 | skip. | `python3 -m py_compile tests/fixtures/r18-landing-pointers.py` |
| Q17 | hold once cited. The fixture is the external resolver; cert-evidence is a different gate. | `python3 tests/fixtures/r18-landing-pointers.py --tool tools/souji-landing-gate.py` exit 0, and the path is a regular file at `<landing>`. |
| Q19 | skip. | The fixture's own cases: missing `census/round-18/x.json` finding; committed knowledge path clean; `:12-14` suffix resolves; `{a,b}` with one missing → one finding; `round-6..11` expanded; `census/round-N/<new>.json` skipped; exemption honoured; malformed TSV exit 2; `--round 17` emits no `LG-DANGLING-PTR`; vacuity stub fails. On the real lane at `b576341 --round 18`, findings include `census/round-17/gate-replays-ddb7347.json` (SKILL.md) and `census/round-17/jj-receipts-ddb7347.txt` (`corpus/knowledge/jj-colocation-receipts.md`). |
| Q25 | run once the SKILL row cites `tests/fixtures/r18-landing-pointers.py`. | Landing gate has no `LG-PARSE-REG` / `LG-MISSING-REG` / `LG-DANGLING-PTR` for that path at the landing rev. |
| Q26 | run on FixturePointers. | Seat-audit command above. |

### `tools/souji-proc-census.sh`

Absent at `b576341` (read failed). Read-only, never signals. Default scan prefixes include `/var/tmp`, `/tmp`, `/dev/shm` (ProcCensus contract). Q4's grep is `TMPDIR:-/tmp`, so a prefix list that contains the letters `/tmp` still passes that grep. Q16 forbids the *fixture* from writing those prefixes.

| criterion | binding | L1 command at landing |
|---|---|---|
| Q4 | run the greps on the tool and on its selftest. Selftest scratch is `/var/tmp/souji-proc-st.XXXX`, trap removes it, and the selftest kills only the processes it started. | `grep -c 'TMPDIR:-/tmp' tools/souji-proc-census.sh` → 0; `grep -c '/var/tmp' tools/souji-proc-census.sh` ≥ 1; a trap removes the selftest directory. `TMPDIR=/var/tmp bash tools/souji-proc-census.sh --selftest` exit 0. |
| Q9 | run. The ProcCensus item names this explicitly. | `shellcheck -S warning tools/souji-proc-census.sh` exit 0; `bash -n tools/souji-proc-census.sh` empty stderr. |
| Q17 | hold once SKILL or the lesson cites `tools/souji-proc-census.sh`. | Blob exists at `<landing>` as a regular file. Cert-evidence selftest stays on its own fragments. |
| Q19 | skip. The tool does not move or delete targets. "Never signals" is checked by the fixture's P7 (orphans still alive after the run), which is a different command from `r13-quarantine-bounds.sh`. | P7 in the fixture section. |
| Q25 | run once a SKILL row cites `tools/souji-proc-census.sh`. Until that row exists the gate will not parse-check it (:1022-1024). | Landing gate exit 0, no `LG-PARSE-REG` / `LG-MISSING-REG` on that path. |
| Q26 | run on ProcCensus. A live read of `/proc` is inside that seat's allowed exec. `souji-census.sh --root` on the fleet is not. | Seat-audit command above. Live TSV from the tool is data for the C3 count, compared with `leak-count.py`, not a Q9/Q25 substitute. |

### `tests/fixtures/r18-proc-census.sh`

Absent at `b576341` (read failed). Shell fixture.

| criterion | binding | L1 command at landing |
|---|---|---|
| Q4 | run. `/var/tmp` only, trap cleanup, kills only what it started. Cases P1–P8 do not require creating a scratch directory under `/tmp` or `/dev/shm` (Q16). | `grep -c 'TMPDIR:-/tmp' tests/fixtures/r18-proc-census.sh` → 0; `grep -c '/var/tmp'` ≥ 1; trap present. |
| Q9 | run. | `shellcheck -S warning tests/fixtures/r18-proc-census.sh` exit 0; `bash -n` empty stderr. |
| Q17 | hold once cited. | Regular file at `<landing>:tests/fixtures/r18-proc-census.sh`. |
| Q19 | skip. | `bash tests/fixtures/r18-proc-census.sh --tool tools/souji-proc-census.sh` exit 0: P1 `cwd-deleted`, P2 `argv-path-gone`, P3 control absent, P4 `--prefix` excludes, P5 `--min-age` excludes, P6 secret argv redacted, P7 no signal, P8 usage exit 2; a header-only stub fails P1/P2. |
| Q25 | run once the SKILL row cites it (`tests/fixtures/` matches `CITED_PATH_RE`). | Landing gate parse clean for that path. |
| Q26 | run on ProcCensusFixture. | Seat-audit command above. |

### `census/round-18/leak-count.py`

Absent at `b576341` (read failed). The owning item also binds Q5 (QUALITY.md:29): an independent counter that does not read `tools/souji-proc-census.sh`. Q5's published test is the round `## Gate` naming the re-deriving seat. That is L1's lesson text, in addition to the six.

| criterion | binding | L1 command at landing |
|---|---|---|
| Q4 | hold, Python parity. `--selftest` scratch under `/var/tmp`, removed after the spawned FIFO reader is killed. The live run is read-only `/proc`. | `grep -c 'TMPDIR:-/tmp'` → 0; `grep -c '/var/tmp'` ≥ 1; selftest uses `dir="/var/tmp"` and a `finally`. |
| Q9 | skip. | `python3 -m py_compile census/round-18/leak-count.py` |
| Q17 | hold once cited. `census/round-18/leak-count.py` matches `CITED_PATH_RE` if a registry row cites it. | Regular file at that path at `<landing>`. |
| Q19 | skip. It never signals and does not delete. | `python3 census/round-18/leak-count.py --selftest` exit 0 (spawn, delete dir, count +1, kill that pid). |
| Q25 | run only if SKILL cites it. The C3 counting command does not require a registry row to be true; without the row the gate will not see it. | If cited: landing gate parse clean. If not cited: `py_compile` still runs, and the gate's silence is the :1022 behavior, which is not a behavior proof. |
| Q26 | run on LeakCounter. Live `/proc` read is allowed for that seat. | Seat-audit command above. |

C3 count: live `leak-count.py` JSON `total` against the proc-census row count, and against the 58 lines in `census/round-18/leaked-procs-before-1631.txt`. This seat did not run either counter.

### `census/round-18/run-matrix.py`

Absent at `b576341` (read failed). The r17 runner it extends already session-kills its own children (`census/round-17/run-matrix.py:89-108`) and scratch-cleans `mkdtemp(..., dir="/var/tmp")` (:190) in a `finally` (:229-230). `invalid_suites` is suite-validity only (:233-235). MatrixR18 adds `leftover_procs` per suite and treats an unrunnable `bash -n` / `shellcheck` / census selftest as invalid, while a failing selftest stays data. That closes the "did not run" half of `round-17.md:65`. A shellcheck rc of 1 remains Q9's own command.

| criterion | binding | L1 command at landing |
|---|---|---|
| Q4 | hold, Python parity, same scratch root as r17 :190. Output is an exclusive `--output` under the seat scratch or `census/round-18/` (Q13, QUALITY.md:37). | `grep -c '/var/tmp' census/round-18/run-matrix.py` ≥ 1; `grep -c 'TMPDIR:-/tmp'` → 0; `finally` removes the matrix scratch. |
| Q9 | skip on the runner. The runner *invokes* Q9's command on the census arms and must record the rc. Recording is not the gate. | `shellcheck -S warning` on `tools/souji-census.sh` (and on `tools/souji-proc-census.sh` if a suite wraps it) exit 0, as its own L1 step. `python3 -m py_compile census/round-18/run-matrix.py`. |
| Q17 | hold once the lesson cites the runner or its JSON record. | Regular file at `census/round-18/run-matrix.py` at `<landing>`. The JSON record's `measured_commit` / sha256 fields, if frozen, go through Q25(b). |
| Q19 | skip. | `python3 census/round-18/run-matrix.py --changed <rev\|WORKTREE> --output <new.json>` exit 0, every suite valid, `leftover_procs` 0 after each suite. A missing r18 fixture makes that suite invalid and the process exits 2, without a traceback. |
| Q25 | run if SKILL cites `census/round-18/run-matrix.py` (the r17 row is SKILL.md:159 and cites `census/round-17/run-matrix.py`, a different path). | Landing gate parse clean for the cited path. `py_compile` regardless. |
| Q26 | run on MatrixR18. The runner may execute fixtures only against `/var/tmp` extractions. | Seat-audit command above. |

## Shared landing order

1. Seat-audit (Q26) on the nine owning seats. A `V-LIVE-CENSUS` or an executing violation voids that seat's evidence (QUALITY.md:65).
2. Parse and shell checks that name a file: `bash -n` and `shellcheck -S warning` on `tools/souji-census.sh`, `tools/souji-proc-census.sh`, `tests/fixtures/r18-proc-census.sh`; `python3 -m py_compile` on the Python artifacts.
3. Q4 greps on each new or edited fixture and on the two new shell tools.
4. Behavior, each on `/var/tmp` copies: r18-census-bounded B1–B7; r15/r17/r14 leftover counts; r18-landing-pointers; r18-proc-census P1–P8; proc-census `--selftest`; leak-count `--selftest`; run-matrix with `--output` under `/var/tmp`.
5. Gate at the landing rev, `--round 18`, exit 0, then the r17 replay file unchanged, then `--rev b410186 --round 15` still exit 1 with the four training ids.
6. Superseding QUALITY row for the Q25:64 parenthetical, in the same landing as the gate change that flags an unresolvable `measured_commit`.

## Commands this seat ran

- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD` → `b5763415cc67ecff1e8fe56c58c39a6fb106d7a3`.
- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff --stat b5763415cc67ecff1e8fe56c58c39a6fb106d7a3 --` the cited QUALITY, SKILL, census, landing-gate, seat-audit, r14/r15/r17 fixtures, `census/round-17/run-matrix.py`, `corpus/lessons/round-17.md` → empty.
- Reads and exact-file greps of those paths, of `.ufo/waves/round-18/w1-spec.json` (items CensusWatchdog, FixtureR18Bounded, FixtureReapR15, FixtureReapR17, FixtureReapR14, GatePointers, FixturePointers, ProcCensus, ProcCensusFixture, MatrixR18, LeakCounter, ScribeQualityRows), and of `census/round-18/leaked-procs-before-1631.txt` (58 lines; 44 / 14 / 0 as above).
- Reads of `corpus/pointer-exemptions.tsv`, `tools/souji-proc-census.sh`, `tests/fixtures/r18-census-bounded.py`, `tests/fixtures/r18-landing-pointers.py`, `tests/fixtures/r18-proc-census.sh`, `census/round-18/leak-count.py`, `census/round-18/run-matrix.py` → file not found.
- `rg` count of `^\s+\("[a-z0-9-]+",` in `tools/souji-seat-audit.py` → 64, all inside `selftest()` cases at :318-406. QUALITY.md:65 says `--selftest` 20/20. SKILL.md:166 says 49 cases. This seat did not run `--selftest`. L1's Q26 check is the spec/transcripts command plus a severity-exact selftest against the case list in the tool at the landing rev. The two prose counts are stale relative to the 64 tuples at `b576341`.

Not run: `souji-landing-gate.py`, `souji-census.sh`, `souji-proc-census.sh`, `shellcheck`, `r13-quarantine-bounds.sh`, `souji-seat-audit.py`, either matrix runner.

## Verdict

The mapping holds. Smallest fix at landing is to run the commands in each section and to land one superseding QUALITY row that names Q25 when an unresolvable `measured_commit` becomes `LG-FROZEN-MEASURED`. Treating Q19's quarantine fixture, Q17's cert-evidence selftest, or a Q25 exit 0 as the FIFO, pointer, or residue proof would record a check whose subject is a different tool.

## Risks

- `--round` ≥ 18 is load-bearing. An unconditional `LG-DANGLING-PTR` changes `census/round-17/gate-replays-expected.json` and the r16 fixture's historical rounds.
- Q26 prose (20/20) and SKILL prose (49) disagree with 64 case tuples at the same rev. Pinning either prose count as the landing bar fails a correct selftest or accepts a short one.
- r17 already killpg's in `run_tool`. Requiring a behavior edit at :1099 would change the locale probe and leave the D2 git leak untouched.
- Proc-census default prefixes include `/tmp` and `/dev/shm`. A fixture case that creates scratch there fails Q16 while satisfying a careless reading of "cover every prefix."
