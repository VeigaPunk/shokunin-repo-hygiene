STATUS: DONE — landed C1 watchdog read at 5efb519 (sha256 7e6a92d4…, identical to the matrix record's `changed` arm); five provably redundant weight clusters named with removal costs; every r18-bounded B1–B8 and selftest check survives all five; no edits made.

# SimplifyWatchdog — WAVE 2 falsification of C1 (operability)

Axis: operability. Target: `tools/souji-census.sh` at `5efb519f00075d958c3d1109ef6fcb24c487eb87` (+592/−39 vs `b576341`). Worktree bytes equal the landed object (`sha256sum` below), so line numbers below are the landed lines.

## What was and was not executed

No `ALLOWED-EXEC` was granted to this seat. The census, `--selftest`, and the four fixtures were **not** run; every dynamic claim below is quoted from the landed measurement record `census/round-18/c1-matrix-worktree.json` (whose `arms.changed.sha256` equals the landed file hash) and marked as such. Static checks that were run: `bash -n`, `shellcheck -S warning`, `python3 -m py_compile`. Probe discipline kept: reads only on named lane files/records, one-level listing of the fleet root for the candidate count, no recursive search, no git writes, no lane edits.

## Pinned behaviour the deletions must not move

- `tests/fixtures/r18-census-bounded.py` B1 `status` FIFO, B2 `check-attr` FIFO, B3 `.git/config` FIFO at `git status`, B4 `.gitignore`/`.gitattributes` FIFOs, B8 list-phase `cmp` config FIFO → each: exit 0, victim row `<repo>\t0\t0\t0\t0\t\t error`, stderr `souji-census: repo-timeout 8s <repo>`, neighbours byte-identical to control. B5 slow-but-finite measured `clean`. B6: no session member and no FIFO reader survives each run (`leaked_before_cleanup` is a FAIL in `census_problems`, fixture lines 655-682). B7: protected root exit 2, no stdout.
- Selftest (landed record: 62 checks, 0 failed) incl. exact error row and diagnostic (2412-2417), neighbours clean (2422-2431), wall `< 6000 ms` (2434), no job-control warning (2441), no reader on the timed-out FIFO (2450), timed-out Git gone (2467), slow path measured (2501), `census_one` protected refusal exit 2 (2538), invalid CLI/env timeout exit 2 (2556).

Carriers that are therefore untouchable: worker started under `set -m` (1478-1481), watchdog `setsid bash -c` with TERM→2 s→KILL (1482-1502), parent `mkdir` race arbiter (1526-1532 / 1535-1538), per-repo row + diagnostic emission (1677-1680, 1704-1708), protected exit-2 propagation (1676, 1702), and the list-phase REPO-kind bound itself (B8).

## Deletable weight (ordered by value; nothing else in the +592 diff qualifies)

**D1 — delete 1569-1576 (8 lines): second process-group emptiness check whose verdict is always discarded.**
It is gated `dead = 1 && REPO_UNREAPED = 0`; at that point `dead = 1` is always produced by a `wait "$worker"` (1519-1521 or 1562-1564), so the reset block at 1609-1629 always finds the worker absent and sets `REPO_UNREAPED=0`, and 1630-1638 then re-runs the byte-identical `kill -0 -- -$worker` 3 s test under the same effective condition (`REPO_TIMED_OUT=1` is fixed in this branch). Observable output is unchanged in every case; the only effect of keeping it is that a surviving group is waited on twice (≈6 s instead of ≈3 s) before the same `repo-timeout-unreaped` line. *Cost of removal:* none to B1-B8/selftest (they expect an empty group, where both checks are a single `kill -0`); the selftest's `< 6000 ms` assertion only gets easier. *Preserved:* single reporting authority for a surviving group in the timeout path.

**D2 — collapse 1609-1629 (21 lines → 9): the two arms of the post-`wait` reset are identical.**
Arm `Z|X` (1612-1619) and arm "absent" (1621-1627) perform the same three statements — `if waited=0 then wait`, `REPO_UNREAPED=0`, `dead=1` — so the `proc_state`/`case` wrapper only decides *whether* a live worker suppresses the reset. Equivalent: `if [ "$REPO_UNREAPED" = 1 ]; then if ! proc_state "$worker" || [ "$PROC_STATE" = Z ] || [ "$PROC_STATE" = X ]; then …same three statements… fi; fi`. *Cost of removal:* -12 lines, zero behaviour change; keeps the `waited=0` reap that the fixture's `leaked_before_cleanup` snapshot indirectly depends on in the unexercised top-loop-break path.

**D3 — 1668 (+1675, 1687): the preflight `row_file` is never written or read.**
`guard_repo_candidate` prints findings to stderr (`protected_fail`), routes `guard_target` to `/dev/null` (1452), and returns nothing on stdout; the success branch discards the file at 1687 and every failure branch at 1675 without reading it. Pass `/dev/null` and drop the argument from the two `rm`s. *Cost of removal:* none; saves one `mktemp` fork+exec and one unlink **per candidate** — 40/run at the live fleet root (21 census rows + 19 non-repo children). *Preserved:* stderr capture/replay (1529, 1639), which still carries per-repo soft findings.

**D4 — 1646: `REPO_TIMED_OUT=0` is a dead store.**
Both callers test `rc = 2` first and `exit 2` (1676, 1702) before any read of `REPO_TIMED_OUT`, and the next invocation resets it at 1476. *Cost of removal:* none.

**D5 — 1665-1688: stop giving kind=`path` candidates a process group and a watchdog.**
`path` is recorded for every non-dot child that is a plain file, a symlink, or a non-repo directory (1414-1418); `guard_repo_candidate`'s only work for that kind is `protected_reason_input` (1442-1444), a pure text walk with no `stat`, `readlink`, git, or file read. Bounding it can never fire, while it costs per child: one background subshell fork (1479), one `mktemp` (1474), one `setsid`+`bash` exec (1482), at least one 100 ms parent poll (1517), a `kill`+`wait` (1527-1528), and `rm -rf` (1530). Call `guard_repo_candidate "$repo" "$kind"` inline at its existing position in the loop and `continue`; refusal still exits 2 with the same `path-protected` line. *Cost of removal:* the doc sentence at 157 must be narrowed from "Candidate metadata guards and census runs each use a private process group" to guards that can read repository bytes (REPO/GITFILE/SYMLINK kinds, all still bounded; B8 pins exactly that); a future non-pure `path` guard would lose its bound. *Benefit:* 19 invocations/run removed at the live root (≈1.9 s of poll time plus ≈95 process spawns per census and per `--compare`, at ≥100 ms per child [INFERENCE from 1517, not measured]). No ordering change: the call stays at the same loop position, so mixed-candidate stderr order is untouched.

## Examined and deliberately kept (deleting would harm an axis)

- 1454 `*) return 1` — 1 line; the only fail-closed default of the kind dispatch.
- 1474-1475 `mktemp` then `rm -f` — the `mkdir` arbiter needs a name no other run can own.
- 1526-1532 early return — foldable only by restructure, not by deletion.
- `prepare_census_tmp`'s `-z` guard (238-241) — load-bearing for `--compare`, which pre-sets `CENSUS_TMP` before calling `emit_census` (1816-1819).
- 1597-1604 (else-branch group check) — effectively dead (its finding is cleared by 1609-1629 because the worker is always `wait`ed first on that path), but deleting it changes output in one residual case: worker pid reaped and then reused by a live process, where today an unreaped group is still reported. Below the line; report it as a doc mismatch instead.

## Defect found (not a C1 failure, doc-vs-code)

`REPO_UNREAPED` has two authorities: 1609-1629 defines it as "worker process still alive", 1630-1638 restores the documented meaning "process group survived" only when `REPO_TIMED_OUT = 1`. Consequence: in the no-marker path (parent lost the `mkdir` race but the watchdog died before writing `timed_out`) a surviving group is detected at 1597-1604 and then silently cleared; header line 162 ("After KILL, reaping is bounded to three seconds; a survivor is reported") is unconditionally worded but not unconditionally true. In C1's own timeout path the marker always exists, so the claim as written for timeouts holds. Smallest fix (text): narrow 162 to the timeout path, and delete 1597-1604 so the code stops pretending. Code-side alternative (one condition, not a deletion): only clear when `kill -0 -- "-$worker"` also fails.

Second doc defect: line 9 declares the dependency set but omits `python3`, which `--selftest` requires at 2443 (`python3 -c` FIFO probe). One word: "…setsid, python3 (--selftest), and Linux /proc."

## Commands and outputs

```
$ git -C …/souji-shokunin diff --stat b5763415cc67ecff1e8fe56c58c39a6fb106d7a3 5efb519f… -- tools/souji-census.sh
 tools/souji-census.sh | 631 ++++++++++++++++++++++++++++++----
 1 file changed, 592 insertions(+), 39 deletions(-)
$ sha256sum tools/souji-census.sh
7e6a92d415f8f256a4e46b0776add6e3645b687abd8be6e67aca520587120bcd  tools/souji-census.sh
$ python3 -c '…json… arms.changed.sha256 / rev'
changed rev= WORKTREE sha256= 7e6a92d415f8f256a4e46b0776add6e3645b687abd8be6e67aca520587120bcd
r17-base rev= b5763415cc67ecff1e8fe56c58c39a6fb106d7a3 sha256= 006b98231f…
$ python3 -c '…matrix suite totals…'
r17-base  r18-bounded 8/5 rc1 | r17-hygiene 29/0 | r15-config 20/0 | r14-namespace 12/0 | selftest 49/0
changed   r18-bounded 8/0 rc0 | r17-hygiene 29/0 | r15-config 20/0 | r14-namespace 12/0 | selftest 62/0
$ bash -n tools/souji-census.sh            → bash-n: OK
$ shellcheck -S warning -f gcc tools/souji-census.sh → 0 lines (rc 0)
$ python3 -m py_compile tests/fixtures/r18-census-bounded.py census/round-18/run-matrix.py census/round-18/leak-count.py → rc=0
$ ls -1 /home/vgpnk/Projects/shokunin | wc -l → 40 non-dot entries;  pair1-base-b576341.tsv data rows → 21 repos ⇒ 19 non-repo candidates (0 symlinks; one-level listdir vs TSV basenames)
```

## Verdict and tradeoff

C1 **holds** on the landed bytes as far as a non-executing seat can establish: the three injection classes B1/B2/B3, the static work-tree FIFOs B4, and the list-phase config injection B8 all land in the same bounded worker; the timeout row/diagnostic and the protected exit 2 are emitted by lines the proposals do not touch. The five deletions remove ~21 lines, two duplicate authorities, one unused temp file per candidate, one dead store, and 19 pointless bounded invocations per run; none of them changes any byte of stdout/stderr in the exercised cases, the only behavioural deltas being *less* worst-case latency in the unreaped path (D1) and a doc sentence that must be narrowed to stay true (D5). Total install/upgrade activity: none.

Tradeoff if all five land: the watchdog's own cost (≈6 forks and one 100 ms poll per *bounded* invocation, 40 preflight + 21 census at the live root) remains; removing that needs a different waiting primitive, not a deletion, so the frontier stops here.
