STATUS: DONE — draft entry `corpus/knowledge/census-bounded-repo-reads.md` written here only; no repository file changed, no git write, no process signalled.

# ScribeKnowledgeBounded — round 18 wave 1 (operability)

Lane: /home/vgpnk/Projects/shokunin/souji-shokunin (base b5763415cc67ecff1e8fe56c58c39a6fb106d7a3). Seat: leaf, no subagent dispatch. Axis judged: operability (C1).

## Findings

1. **The shape the entry must match is confirmed.** `corpus/knowledge/jj-colocation-receipts.md` opens with `source:` (line 1), `verified-at:` (line 2) and `recheck:` (line 3), then sections, `## Limits`, `## Failure cases (Q3)`, `## Source rows`, `## Admission status`. The draft copies this order.
   - Evidence: `corpus/knowledge/jj-colocation-receipts.md:1-3`, `:106`, `:124`, `:132`, `:150-152`.
   - Verdict: holds.

2. **Guard location and the TOCTOU gap are at the cited lines.** `guard_git_files` is `tools/souji-census.sh:546-585`. Its only protection for `info/attributes` is one `stat -L -c '%F %h'` at `:555`, then a soft finding that sets `soft=1` for a FIFO (`:573-578`). The guard returns at `:583-585`. Nothing re-checks the path after it returns, so a swap between `:555` and git's own open is not covered. The same stat-then-use pattern appears in `status_info_file`: `:1036-1039` checks `[ -e "$tgt" ] && [ ! -f "$tgt" ]` and then returns the path for git to read later.
   - Evidence: `tools/souji-census.sh:546-585`, `:1025-1048`.
   - Verdict: holds (static read). The swap itself is the lane's C1 reproduction at b576341 and was not re-run here.

3. **The row shape and the lost-rows mechanism are at the cited lines.** `emit_census` (`tools/souji-census.sh:1394-1416`) runs `census_one` serially inside `for repo in ...` (`:1402-1411`) and prints the header and rows only after the loop (`:1412-1415`). One blocked repo therefore blocks the run, and a wrapper kill loses every row. Nothing in `emit_census` today carries a per-repo bound or a process group. `grep -n timeout` on the base revision finds no census-side bound on the status or check-attr calls.
   - Command: `git -C <lane> show b5763415cc67ecff1e8fe56c58c39a6fb106d7a3:tools/souji-census.sh | grep -n 'timeout'` — output: no lines.
   - Verdict: holds (the fix contract's "no bound today" is accurate at base).

4. **The fixture leak class is at named lines, and the fixture fix is only partial.**
   - `tests/fixtures/r15-census-config.py` has no `start_new_session` anywhere (`grep -n start_new_session tests/fixtures/r15-census-config.py` → no lines). Its `subprocess.run` calls at `:274`, `:734`, `:781` therefore have no process group and no `killpg`.
   - `tests/fixtures/r17-census-hygiene.py` already has the session fix in its `Popen` path (`:293-314`: `start_new_session=True` at `:303`, `os.killpg(proc.pid, signal.SIGKILL)` at `:314`). Its `run_setup` (`:150`, `subprocess.run(... timeout=60)`) and the `kind` call (`:1099`) have neither.
   - Verdict: holds for the r15 class; partial for the r17 harness. The contract's "every census subprocess" must cover `:150` and `:1099` as well as r15's three call sites.

5. **Host residue is real and was observed read-only.**
   - `census/round-18/leaked-procs-before-1631.txt`: 58 lines, format `pid ppid pgid uid date cmd`. The lines name `/var/tmp/r15-census-config.*/unsafe-repos/r-inc-fifo` and `/var/tmp/souji-r17-matrix.*/…`. Example: pid 185605, ppid 185592 (census bash), pgid 184733, argv `git -C /var/tmp/r15-census-config.upcupkw1/unsafe-repos/r-inc-fifo rev-parse --is-inside-work-tree`.
   - `ls -ld /var/tmp/r15-census-config.upcupkw1` → `No such file or directory`. The scratch dir is gone; the git child is still alive.
   - `ps -eo pid,stat,wchan:24 | awk '$3=="wait_for_partner"' | wc -l` → `27` at the later check. At the first check the broader match returned `58` (`ps -eo … | grep -E 'souji-(census|verify)|r15-census-config|r17-census|git -C /var/tmp'`). The count dropped between checks. I did not signal them; the cause of the drop is not established here.
   - Verdict: holds for the existence of residue; the blocked state is `S` with `wchan=wait_for_partner` for the sampled rows.

6. **Lesson and log citations resolve.** `corpus/lessons/round-17.md:60` and `:86` record sentinel F3 (TOCTOU FIFO swap, hang with no output) as open for r18. `corpus/lessons/round-17-verifier-spotcheck.md:68` and `:153` agree. `LOG.md:373` (quarantine staging hung to the 20-minute driver timeout) and `LOG.md:403` (three judge-fixture processes ~9 h on `sha256sum` of a FIFO) are the QUALITY Q8 origins. All exist.

7. **Tool versions for `verified-at`** (host, read-only):
   - `git --version` → `git version 2.56.0`
   - `bash --version | head -1` → `GNU bash, version 5.3.20(1)-release (x86_64-pc-linux-gnu)`
   - `/usr/bin/timeout --version | head -1` → `timeout (GNU coreutils) 9.12`. (Bare `timeout --version` returned a clap usage error because the persistent shell resolves `timeout` to a non-coreutils wrapper; the GNU binary was checked by absolute path.)
   - `python3 --version` → `Python 3.14.8`
   - `stat --version | head -1` → `stat 0.8.0`. This line does not identify the implementation; the entry does not rely on it.

8. **Q3 failure cases the entry names** (each with a location):
   - F-1 FIFO swap after the guard: C1 reproduction at b576341 (lane, not re-run here); lesson `corpus/lessons/round-17.md:86`.
   - F-2 Whole-run abort from one repo: `tools/souji-census.sh` D2 before the r17 fix returned rc 2 with no rows for a hardlinked `info/attributes`; `corpus/lessons/round-17-verifier-spotcheck.md:64` (D2 hardlink row: `5fa6017: rc 2, path-protected: git-metadata-hardlink, no rows`).
   - F-3 Lost rows on wrapper kill: `tools/souji-census.sh:1412-1415` (print after the loop).
   - F-4 Fixture leak: `census/round-18/leaked-procs-before-1631.txt` (58 rows) with the call sites `tests/fixtures/r15-census-config.py:274,734,781`.
   - F-5 Partial fixture fix: `tests/fixtures/r17-census-hygiene.py:150` and `:1099` lack the session that `:293-314` has.
   - F-6 Quarantine staging hang: `LOG.md:373`.
   - F-7 Judge-fixture hang on FIFO: `LOG.md:403`.

9. **Q3 precondition check for F-4.** The fixture kills its direct child on timeout and never the group. This is consistent with the rows: the blocked git child has ppid = census bash and pgid 184733 (not its own pid). [INFERENCE] `subprocess.run(timeout=…)` signals only the direct child; the grandchild survives. Not tested here.

## Commands run (read-only; output shown above)

- `read corpus/knowledge/jj-colocation-receipts.md:1-60`, `:110-152`
- `read corpus/lessons/round-17-verifier-spotcheck.md`
- `grep` over `tools/souji-census.sh` for FIFO/TOCTOU/killpg terms
- `read corpus/QUALITY.md` (Q3, Q8)
- `read tools/souji-census.sh:536-593`, `:1024-1048`, `:1388-1420`
- `wc -l`, `head`, `grep -c` on `census/round-18/leaked-procs-before-1631.txt`
- `grep -n` on `tests/fixtures/r17-census-hygiene.py` and `tests/fixtures/r15-census-config.py`
- `sed -n` on `LOG.md:370-376`, `:400-406`
- `ps -eo …` (read-only, to count blocked processes; no `/proc/*/environ` read)
- `ls -ld /var/tmp/r15-census-config.upcupkw1` → absent
- `git --version`, `bash --version`, `/usr/bin/timeout --version`, `python3 --version`, `stat --version`

Tool installs or updates by this seat: none.
Processes started by this seat: none. Processes signalled: none.

## Draft knowledge entry (for `corpus/knowledge/census-bounded-repo-reads.md`; not written to the repository)

````markdown
source: see `## Source rows` (S0xx placeholders, to be minted at the round-18 gate; S062 is the existing fifo(7) row). Git behaviour cites the v2.56.0 tag; census behaviour cites the lane file and line at the revision named in verified-at.
verified-at: 2026-10-20 — git 2.56.0 (`git --version`); GNU bash 5.3.20; GNU coreutils timeout 9.12 (`/usr/bin/timeout --version`); Python 3.14.8. Census lines read at base b5763415cc67ecff1e8fe56c58c39a6fb106d7a3.
recheck: `git --version; /usr/bin/timeout --version | head -1`. Static: `git -C <lane> show b5763415cc67ecff1e8fe56c58c39a6fb106d7a3:tools/souji-census.sh | grep -n 'timeout'` (expect no output at base). Post-landing: `bash tests/fixtures/<r18-bounded-fixture>.sh --tool-dir tools` — the fixture name is set by the round-18 gate, and the expected `SUMMARY` line is set there too (this line is a placeholder until the fixture lands). Process residue: `ps -eo pid,ppid,pgid,stat,wchan:24,cmd | grep 'git -C /var/tmp'` (read-only; expect none after a green run).

# A blocking FIFO can hang a fleet census after the type guard passes

A census that reads each repository's git metadata inherits git's own blocking behaviour. Git opens some metadata files for read without checking their type. A FIFO at one of those paths makes `open(2)` wait for a writer. The census's type guard runs before git opens the file, so a swap between the guard and the open defeats it. This entry records the class, why a guard cannot close it, and the bounded-read contract that does (per-repository process group, watchdog, row shape). It is a knowledge entry: it does not change a tool by itself.

## 1. The class

- **A FIFO open blocks.** "Normally, opening the FIFO blocks until the other end is opened also." — S062 (`fifo(7)`, `man7.org/linux/man-pages/man7/fifo.7.html`) — `sourced` (admitted r17)
- **Git reads `info/attributes` on the status and check-attr paths.** [INFERENCE] status reads attributes when it must compare content; check-attr reads them by definition. The lane reproduced the hang at b576341 with a PATH `git` shim that swaps the regular file for a FIFO after the guard and touches a tracked file on `status`. Not re-run in this entry. — S0xx (git attributes / status read path, to be located) — `observed (lane reproduction, not re-run)`
- **Consequence.** `bash tools/souji-census.sh --root R` blocks in git's `open(2)`. The outer `timeout 15` returns rc 124 with zero rows. The healthy neighbours' rows are lost, because the census prints only after the loop (`tools/souji-census.sh:1412-1415`).

## 2. Why a type guard alone does not close it

- **The guard is a stat.** `guard_git_files` probes each fixed metadata path once with `stat -L -c '%F %h'` (`tools/souji-census.sh:555`) and then returns (`:583-585`). The file type it sees is the type at that instant.
- **The use is later.** Git opens the path at its own time, after the guard has returned. A regular file at the stat can be a FIFO at the open. This is a time-of-check to time-of-use gap; there is no lock on the path.
- **The same gap exists for `core.excludesFile`.** `status_info_file` checks `[ -e "$tgt" ] && [ ! -f "$tgt" ]` (`tools/souji-census.sh:1038`) and returns the path for git to read later.
- **Consequence.** Narrowing the guard (more file types, a re-stat) shrinks the window and does not remove it. The only bound that holds is one on the wait itself.

## 3. The per-repository process-group watchdog

- **Contract.** `emit_census` runs each `census_one` in its own process group (bash `set -m` only around that fork), with stdout to a private temp file. A watchdog sends SIGTERM to the group after the bound and SIGKILL 2 s later. A timed-out repository becomes the row `<repo>\t0\t0\t0\t0\t\terror` and stderr `souji-census: repo-timeout <N>s <repo>`. Other repositories are measured and the run exits 0.
- **Bound.** `--repo-timeout N` or `SOUJI_CENSUS_REPO_TIMEOUT` (integer seconds 1..86400; default 600; invalid → usage exit 2).
- **Exit semantics unchanged.** A protected refusal (`census_one` rc 2) still exits the whole run 2. Any other nonzero still exits 1. The watchdog never outlives its repository and holds no stdout or stderr pipe of the caller.
- **Why a group.** A SIGTERM to the census bash alone does not reach its git child. The group signal does.

## 4. Why fixtures must kill the session, not the child

- **Observed.** 58 processes (`census/round-18/leaked-procs-before-1631.txt`) are git children named `… rev-parse --is-inside-work-tree` under `/var/tmp/r15-census-config.*/unsafe-repos/r-inc-fifo` (and `r17-census`/`souji-r17-matrix` paths). Their scratch directory no longer exists, and they remain in `wait_for_partner` (`ps -eo pid,stat,wchan:24`). `observed (host, read-only, 2026-10-20)`
- **Cause at the fixture.** `tests/fixtures/r15-census-config.py` has no `start_new_session` and calls `subprocess.run` at `:274`, `:734` and `:781`. `subprocess.run(timeout=…)` signals only the direct child. [INFERENCE] the grandchild git survives; not tested here. — S0xx (Python `subprocess` timeout semantics, to be located)
- **Partial fix already in one harness.** `tests/fixtures/r17-census-hygiene.py:293-314` has `start_new_session=True` and `os.killpg(proc.pid, signal.SIGKILL)`, but its `run_setup` (`:150`) and the `kind` call (`:1099`) do not.
- **Rule.** Every census subprocess in a fixture runs with `start_new_session=True`, and a timeout calls `os.killpg(..., SIGKILL)`. A red arm must leave zero blocked processes. Q4 still applies: the scratch root is under `/var/tmp` and a trap removes it, and a process that outlives the trap must still be gone.

## 5. Failure cases (Q3)

- **F-1 FIFO swap after the guard hangs the run.** Reproduced by the lane at b576341 (C1); open at r17 close: `corpus/lessons/round-17.md:86`, `corpus/lessons/round-17-verifier-spotcheck.md:68`.
- **F-2 One repository aborts the fleet.** Before the r17 D2 fix, a hardlinked `info/attributes` returned rc 2 with no rows: `corpus/lessons/round-17-verifier-spotcheck.md:64`. D2 narrowed this to one error row for one repository.
- **F-3 Wrapper kill loses every row.** `tools/souji-census.sh:1412-1415` prints after the loop; a kill during the loop prints nothing.
- **F-4 Fixture-leaked processes.** `census/round-18/leaked-procs-before-1631.txt` (58 rows); call sites `tests/fixtures/r15-census-config.py:274,734,781`.
- **F-5 Partial fixture fix.** `tests/fixtures/r17-census-hygiene.py:150` and `:1099` lack the session that `:293-314` has.
- **F-6 Quarantine staging hang to the driver timeout.** `LOG.md:373`.
- **F-7 Judge fixtures about nine hours on a FIFO.** `LOG.md:403` (`sha256sum` of a FIFO, `wait_for_partner`).

## Limits

- **A bound converts a hang into a not-measured row.** The repository's row is `error` with zeros. A reader cannot tell "hung" from "absent" from the row alone; only the stderr line `repo-timeout` says which. Consumers must read stderr, or the row is a false zero.
- **A repository slower than the bound is reported `error`.** The default is 600 s. A slow but healthy repository past that bound is reported as an error, not measured. The bound is an operator choice, not a measurement of health.
- **Serial worst case.** With the default and every repository hanging, the run takes up to N × 600 s plus 2 s per repository. At 21 repositories (the r17 fleet; SCORECARD's "22 repos" is the R3 defect) that is about 3.5 hours. [INFERENCE] from the contract; the run has not been timed.
- **Group kill covers the group, not escapees.** A process that leaves its group (`setsid`, double fork) is not reached. The lane did not observe git doing this; the claim is not made.
- **SIGTERM then SIGKILL.** A process blocked in `open(2)` on a FIFO is expected to die on SIGTERM; SIGKILL 2 s later is the backstop. [INFERENCE] not tested here.
- **Existing residue is not cleaned.** `tools/souji-proc-census.sh` is read-only and never signals. The 58 rows stay until their owners exit or an operator acts.
- **The fix is not measured in this entry.** This entry describes the contract; the round-18 gate runs the fixture and the census.
- **Host specifics.** Results are on Linux 7.2.11 with GNU coreutils timeout 9.12, bash 5.3.20 and git 2.56.0. Other platforms are not claimed.

## Source rows

- **S062** — `fifo(7)` — `https://man7.org/linux/man-pages/man7/fifo.7.html`. Used in §1. Admitted at r17 gate (`corpus/lessons/round-17-verifier-spotcheck.md:132`).
- **S0xx-A** — git attributes read path (status / check-attr) at v2.56.0 — URL and quote to be located and minted (S064+, access date 2026-10-20). Used in §1. Not yet a row.
- **S0xx-B** — Python `subprocess` timeout semantics (`run` signals the direct child) — URL and quote to be located and minted. Used in §§4, 5.
- **S0xx-C** — `setpgid(2)` / `kill(2)` process-group semantics — URL and quote to be located and minted. Used in §3.

No S-row is admitted by this draft. Every S0xx is a placeholder until minted.

## Admission status

candidate — pending round-18 gate
````

## Routed items for the connectors and L1 (not fixed here)

- **Fleet-wide `start_new_session` gap.** `tests/fixtures/r17-census-hygiene.py:150` and `:1099`, and `tests/fixtures/r15-census-config.py:274,734,781`, need the session and killpg pattern. Owner: the fixture seat (not this seat).
- **Census selftest FIFO case.** `tools/souji-census.sh:1936-1991` builds a FIFO repository (`mkfifo` at `:1943`) and runs the census inside the script's own selftest. The entry does not verify whether that run is session-wrapped; L1 should check it before the watchdog lands.
- **Count drift.** 58 blocked processes at the first read; 27 at the later read. Recheck before quoting either number as current.
- **R3 (SCORECARD "22 repos" vs 21)** is already routed by the round-17 closure (`corpus/lessons/round-17-verifier-spotcheck.md:151`); the draft's Limits cite it and do not restate the fix.
