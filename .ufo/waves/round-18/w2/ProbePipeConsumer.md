STATUS: DONE — piped census (`… | head -1`) exercised at 5efb519 with 30 normal repos and with a hung repo: the timeout path measures, diagnoses and reaps with zero residue, but the census dies of SIGPIPE (exit 141) as soon as `head` consumes the header, so C1's literal "exit 0" does not hold for a closed-early consumer, and `head -1` cannot shorten the run.

# ProbePipeConsumer — C1 stdout handling

Attacked claim (C1 operability, stdout coincidence): `tools/souji-census.sh` "a timeout → row
`<repo>\t0\t0\t0\t0\t\terror` + stderr `souji-census: repo-timeout <N>s <repo>`, others measured,
**exit 0**", and the tool's own contract `tools/souji-census.sh:166-170` "0 census emitted".
Probe axis: a consumer that closes stdout early (`| head -1`) — exit, wall time, residue.

## Sandbox and method

- Clone `/var/tmp/souji-r18w2-ProbePipeConsumer/lane`, detached at
  `5efb519f00075d958c3d1109ef6fcb24c487eb87` (`git rev-parse HEAD` = that sha, `git status
  --porcelain` empty). No lane/fleet write, no `jj`, no git write anywhere but the clone.
- Synthetic roots under the seat dir: `fleet30` = 30 `git init` repos; `fleet31` = the same 30
  plus `hang`, a repo with `mkfifo .gitignore` (no writer) and one untracked file. Control:
  `timeout 2 git -C fleet31/hang status --porcelain` → rc 124, so `git status` genuinely blocks
  there (the FIFO is read by the dirty count, not degraded by the metadata guard).
- Residue attribution: host `/var/tmp` is shared with ~130 peer lanes that have live
  `souji-census-now.*` dirs (observed 4 → 10 across one of my runs, plus host-wide `pgrep`
  noise from peers' stuck r16/r17 processes). Every residue number below was therefore taken
  inside `bwrap --unshare-pid --unshare-net --die-with-parent --ro-bind / / --bind
  /var/tmp/souji-r18w2-ProbePipeConsumer /var/tmp --tmpfs /tmp --tmpfs /home/vgpnk --proc /proc
  --dev /dev`, where `/var/tmp` is my seat dir and `ps` sees only my processes. A sampler loop
  (my pid, killed by pid) recorded `souji-census-now.*` dirs every 0.2 s.
- No tool installed or upgraded. Clone and seat dir deleted after the report.

## Executed matrix (exact)

`bash -c 'bash tools/souji-census.sh … | head -1; st=("${PIPESTATUS[@]}")'`, run from the clone.

| # | invocation | census rc | head rc | wall | distinct tmp dirs pre / mid / post | leftover census/watchdog procs |
|---|---|---|---|---|---|---|
| 1 | `--root …/fleet30` (isolated) | **141** | 0 | 9.56 s | 0 / 1 / **0** | **0** |
| 2 | same (isolated, repeat) | **141** | 0 | 9.35 s | 0 / 1 / **0** | **0** |
| 3 | `--root …/fleet31 --repo-timeout 3` (isolated) | **141** | 0 | 14.49 s | 0 / 1 / **0** | **0** |
| 4 | #1 and #3 on the shared host (unisolated) | **141** | 0 | 10 s / 14.71 s | peer-polluted, discarded | peer-polluted, discarded |

stdout of every run was exactly one line, the header:
`repo	worktrees	unpushed	dirty	scratch_bytes	mtime_iso	verdict_flags`.
Run 3 stderr was exactly 52 bytes, one line:
`souji-census: repo-timeout 3s /var/tmp/souji-r18w2-ProbePipeConsumer/fleet31/hang`.
No `repo-timeout-unreaped` line. Census rc was 141 in 5/5 invocations (rows 1–3 plus the two
host invocations in row 4).

## Findings

**F1 (executed) — exit 141, not 0; C1's exit clause is false for a closed-early consumer.**
`head -1` exits after the header; the census's *next* write (`tools/souji-census.sh:1721`,
inside the final block `:1719-1722`) hits EPIPE and the shell is killed by SIGPIPE before
reaching `exit 0` (`:2625`). No PIPE trap exists anywhere: `grep -rn "trap .*PIPE" tools/`
returns nothing across 119 `tools/*.sh`. `PIPESTATUS[0]=141` = 128+13; `PIPESTATUS[1]=0`.
Consequence: a human pipeline looks successful (head's status), but any `set -o pipefail`
caller — this lane's universal convention — sees a completed census as failure. Severity:
low-to-medium operability; no measurement is lost, because all rows are already in memory.

**F2 (executed) — `head -1` cannot bound the run; output is fully buffered to the end.**
Rows are only printed after the entire loop (`:1719-1722`); the header arrived at t=9.35–9.56 s
(30 repos) and t=14.49 s (hung repo), never at start. This is not an r18 regression:
`git show b576341…:tools/souji-census.sh` has the identical buffered block at `:1412-1415`.
With the default 600 s and one hung repo, `census | head -1` blocks ≈600 s+ for a header peek.

**F3 (executed) — the SIGPIPE path leaves no residue; the r18 tmp restructuring is clean here.**
Round 18 introduced a per-run tmp dir in census mode (`prepare_census_tmp` `:238-243`, called
`:1661`; per-repo files `:1668-1669`, `:1697-1698`), where the base only used tmp in compare
(`b576341:1510-1515`). On SIGPIPE bash still runs the EXIT trap: a scratch control with
`trap "touch marker" EXIT` plus a 4000-line burst piped to `head -1` gave `ps=141 0 marker=PRESENT`.
Consistently, the one tmp dir present mid-run was gone post-run in all three isolated runs, and
the seat dir holds no `souji-census-now.*` afterwards. No census or watchdog process survived
(both `run_repo_with_watchdog` exits wait/kill the watchdog: `:1474-1520`, `:1633`), and the
`.gitignore` FIFO was intact.

**F4 (executed) — the timeout itself worked before the SIGPIPE.** Run 3's extra cost over the
30-repo baseline is 14.49 − 9.45 = **+5.04 s for one repo at `--repo-timeout 3`**, i.e. the 3 s
bound plus the 2 s TERM grace in the watchdog (`:1486-1503`); the remaining 30 repos were
measured (wall matches the full fleet, and the run did not abort). The documented row
(`:1707-1711`) is emitted into the buffered array, but `head -1` discards every row, so I did
not observe row text through this consumer and did not run an unpiped census (outside
ALLOWED-EXEC). Row text remains the lane's B1–B8 fixture claim, not mine.

**F5 (static only, same class, NOT executed — outside ALLOWED-EXEC) — `--compare` and
`--selftest` lose their documented status to the same SIGPIPE.** `emit_compare` streams the
diff (`:1825` header, `:1839-1866` rows) and returns 3 only after the whole loop (`:1868`), so
`census --compare prev.tsv | head -1` would die 141 after the header and can never report the
documented 0/3 while dropping every diff row. `--selftest` streams PASS/FAIL via `st_note`
(`:1878`); `| head -1` would kill it at the first line — the `ST_TMP` EXIT trap (`:1908`) would
still remove fixtures, but an in-flight child census/watchdog would outlive the parent until
its own bound. **[INFERENCE]** — not run.

## Verdict

**Partial.** C1's measurement semantics hold under the named probe: the hung repo is bounded
(N + 2 s grace), diagnosed on stderr, others are measured, the group is reaped, exit is
deterministic, and the SIGPIPE path leaves no dir or process residue (F3/F4). C1's literal
"exit 0" fails for the `| head -1` consumer (141, 4/4), and the pipe cannot shorten the run
(F1/F2). Both are stdout-contract issues, not census-measurement issues.

## Smallest fix

In `emit_census`, treat a closed stdout as completion and keep the measured status — install a
PIPE trap around the final write block only (`:1719-1722`):

```bash
trap 'exit 0' PIPE
printf '%s\n' "$HEADER"
for row in "${rows[@]+"${rows[@]}"}"; do printf '%s\n' "$row"; done
trap - PIPE
```

Verified in scratch (no lane bytes changed): a 4000-line burst piped to `head -1` gave
`PIPESTATUS=141 0` 3/3 without the trap and `0 0` 3/3 with it (`trap '' PIPE` also reaches 0,
but only with `|| exit 0` on each write, since `set -e` would otherwise exit 1 on EPIPE).
Placement inside `emit_census` keeps `emit_compare`'s 3-status untouched (it redirects
`emit_census` to a file at `:1819`). If a cheap header peek is also wanted, print `$HEADER`
before the measurement loop; otherwise document that `| head -1` pays the full census and
reports 141 under `pipefail`.
