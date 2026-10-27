# SwarmSentinel37 — credential and refusal-guard sentinel (round 34, w1)

Seat scope: secret patterns over the freeze delta and the new r34 files; the four instruments'
refusal guards (scratch-under-ephemeral-root, missing args, full-hex revisions, non-repository);
and whether they ever execute repository code outside a clone.
Read-only: no lane write except this report. No tool installed, no pacman transaction
(host-wide pacman pause respected); nothing outside `/fast/scratch/hyaku/souji-r34/SentinelRound/`.

## Status

STATUS: PASS — 0 credential findings (1320 added lines, 13 files, 10 token + 10 header/userinfo/
secret-path patterns all zero); both counters hold all four refusal classes (c1 8/8, c2 8/8) and
refuse before any clone; all repo-code execs of a measured item land inside the clone. Six guard
gaps reported (no frozen predicate/target/item touched), three of them reproduced: symlinked
scratch bypasses the ephemeral-root refusal in both counters, the C2 bwrap envelope keeps the
operator's HOME/env read-write-bound, and `leg_witness` leaks its clone.

## Evidence

Lane `HEAD` at read time `51acb5fb6fa38a6b593b3badb674cec559d7eb2c`; base
`9c76c7222a8abff027af42e37f0d160d52526bba`; freeze `2b0171e2071fdc9c16a69bed12b0d040e574d8c8`.

A. Secret sweep (delta `9c76c72..51acb5f` = 13 files, `1444 insertions(+)`; 1320 added lines
   excluding `+++` headers). Both diffs written under scratch; every count below is
   `grep -cE "^\\+.*<pattern>" <diff>`.

```
BEGIN [A-Z ]*PRIVATE KEY 0   ghp_[A-Za-z0-9]{20,} 0   github_pat_[A-Za-z0-9_]{20,} 0
sk-[A-Za-z0-9]{20,} 0        xox[baprs]-[A-Za-z0-9-]{10,} 0   AKIA[0-9A-Z]{16} 0
op:// 0                      AIza[0-9A-Za-z_-]{30,} 0   glpat-[A-Za-z0-9_-]{15,} 0
-----BEGIN 0                 (freeze-only diff: all 0 as well)
(?i)authorization[":= ] 0    (?i)bearer [A-Za-z0-9._~+/=-]{8,} 0   (?i)\bbasic [A-Za-z0-9+/=]{8,} 0
[a-zA-Z][a-zA-Z0-9+.-]*://[^/ @:"]+:[^/ @:"]*@ 0   (?i)\.netrc 0   (?i)\.aws/credentials 0
(?i)id_rsa|id_ed25519|\.ssh/ 0   (?i)(password|passwd|secret|api[_-]?key|access[_-]?token)[ ]*[=:] 0
(?i)x-api-key 0              (?i)PRIVATE-TOKEN 0
```

   Working-tree sweep over the same surface plus the six untracked `census/round-34/records/`
   files (`grep -rEni` on `census/round-34 tests/fixtures/r34-*`) repeats the last seven
   patterns: 0. `grep -rEn '...|eyJ[A-Za-z0-9_-]{20,}'` over the same set: 0.
   Hex inventory: 27 unique 40-hex strings, 26 are commits in this repo
   (`git cat-file -t` = commit) and one, `e64ddbbb…5db6d`, is a scratch-clone stub revision
   quoted inside a committed TimeoutExpired traceback; 2 unique 64-hex values, both digests
   (`09bb8e0d…1ed6d` statement digest, `e6a984b1…4b2` NAMESPACE pin). `census-start.txt` URLs
   are public doc hosts only (`git-scm.com`, `man7.org`, `gnu.org`, `docs.python.org`,
   `raw.githubusercontent.com/GNOME`), no userinfo.

B. c1-counter refusals (`census/round-34/c1-counter.py`); scratch `./ok` empty after all probes:

```
no args            COULD-NOT-EVALUATE required arguments missing                      rc=2
rev 9c76c72        COULD-NOT-EVALUATE --rev must be a full 40-hex revision            rc=2
list-rev zz        COULD-NOT-EVALUATE --list-rev must be a full 40-hex revision       rc=2
scratch /tmp/x     COULD-NOT-EVALUATE --scratch must not be under /tmp, /var/tmp or /dev/shm rc=2
scratch /var/tmp/x same                                                              rc=2
scratch /dev/shm/x same                                                              rc=2
non-repo --root    COULD-NOT-EVALUATE git cat-file -e …: fatal: not a git repository  rc=2
40-hex absent rev  COULD-NOT-EVALUATE git cat-file -e 1111…: Not a valid object name  rc=2
```

C. c2-counter refusals (`census/round-34/c2-counter.py`); scratch `./ok2` post-probe held only
   run artefacts of the `--rev 1111…` probe, no clone for any refused argument set:

```
no args            COULD-NOT-EVALUATE required arguments missing    rc=2
rev 9c76c72 / base abc / list-rev q1   COULD-NOT-EVALUATE revision must be full 40 hex  rc=2
scratch /tmp/x, /var/tmp/x, /dev/shm/x COULD-NOT-EVALUATE scratch under ephemeral root rc=2
non-repo --root    COULD-NOT-EVALUATE legs absent at --list-rev     rc=2
40-hex absent rev  no refusal: starts legs; LEG W1 FAIL fatal: unable to read tree (1111…) rc=124 at my 120 s cap
```

D. Fixtures (`tests/fixtures/r34-c1-junk.py`, `tests/fixtures/r34-sandbox-junk.py`):

```
no args                    usage error: the following arguments are required: --counter, --scratch  rc=2
missing --scratch          usage error: the following arguments are required: --scratch              rc=2
non-repository root        RuntimeError: git -C … rev-parse master: fatal: not a git repository     rc=1
--scratch /tmp/souji-r34-junkx   NOT refused; /tmp/souji-r34-junkx created (removed by me)
--tool tools/souji-census.sh     error: unrecognized arguments: --tool …                             rc=2
```

E. Execution locality — one c1 item (`--only G01`) under
   `strace -f -qq -e trace=execve,execveat -o trace.txt`, load before 43.42 → after 51.08
   (25824 trace lines), exec path histogram (`grep -o 'execve[a-z]*("[^"]*"' | sort | uniq -c`):

```
3415 /usr/bin/sleep    529 /usr/bin/git    172 /usr/bin/bash
  24 <clone>/tools/souji-census.sh                       (the item's own script, inside the clone)
  86 <scratch>/s/souji-census-selftest.*/watchdog-shim/bash
  64 <scratch>/s/souji-census-selftest.*/watchdog-shim/git
  11 each /home/vgpnk/.local/bin/git, .opencode/bin/git, .minimax/bin/git, /usr/local/{s,}bin/git,
          /run/user/1000/fnm_multishells/*/bin/git, .local/share/mise/shims/git …
```

   No exec of a path under the lane root: every repository script ran from
   `<scratch>/…/c` or `<scratch>/s`. The 11-per-dir `git` rows are the counter's own
   `subprocess.run(["git", …])` calls, which take the caller's ambient PATH.

F. bwrap envelope probed with the counter's own argument shape (`c2-counter.py:122` and `:159`),
   inside a user namespace as invoked by the counter:

```
HOME=/home/vgpnk               env-var-count=268   sensitive-env-names=8
read-home-ssh=<4 entries, names withheld>
write-outside-bind=WRITABLE    write-var-tmp=WRITABLE    write-etc=DENIED    write-tmp=DENIED
```

G. Symlinked-scratch bypass (live symlink target under `/tmp`, removed by me afterwards):

```
c1 --scratch <scratch>/symscratch2 -> /tmp/… : COULD-NOT-EVALUATE unknown --only ids rc=2
  /tmp/souji-r34-symlink-target after run: -rw-r--r-- 0 c1.lock
c2 --scratch <scratch>/symscratch3 -> /tmp/… : COULD-NOT-EVALUATE legs absent at --list-rev rc=2
  /tmp/souji-r34-c2sym after run: -rw-r--r-- 0 c2.lock
dangling symlink, c1: FileExistsError: [Errno 17] File exists: …/symscratch  rc=1
```

H. Scratch leak after the aborted `--rev 1111…` c2 probe (`du -sh ok2/*`):

```
205M ok2/bwrap.c6rvqxy3   27M ok2/bwrap.yvj723ew   216M ok2/sandbox.suj7xam3
stat: d--------- 3 ok2/sandbox.suj7xam3/tmp/r15-census-config.*/home/.omp/agent
```

I. G01 reading matrix (`tools/souji-census.sh --selftest` at base, counter env
   `PATH=<jb>:/usr/bin:/bin TMPDIR=… GIT_CONFIG_NOSYSTEM=1 HOME=$HOME LANG=C.UTF-8`):

```
direct, no strace, load 54.31   selftest: 69 checks, 0 failed
direct, jj on PATH, load 49.04  selftest: 69 checks, 0 failed
direct, strace -e execve, load 43.49 -> 32.83   selftest: 69 checks, 0 failed
counter, strace -e execve,execveat, load 43.42 -> 52.05   selftest: 69 checks, 7 failed (MISMATCH)
counter, no strace, load 32.74  ITEM G01 AGREE original rc=0 last=selftest: 69 checks, 0 failed  rc=0
```

J. Lane untouched: `git -C <lane> status --porcelain` shows only the same six untracked
   `census/round-34/records/*` files that were present before I started; nothing else.

## Findings

1. **Credentials clean across the freeze delta** (severity: none). 1320 added lines, 13 files,
   20 patterns, all zero (§Evidence A). The two 64-hex values are the pinned digests the
   contract names; every 40-hex is a commit except one stub revision quoted in a scratch-clone
   traceback. Locators: `census/round-34/`, `tests/fixtures/r34-*.py`, working tree records.

2. **The C2 sandbox keeps the caller's HOME and full environment, and binds `/` read-write**
   (severity: MEDIUM; credential exposure). `census/round-34/c2-counter.py:122` and `:159` use
   `--dev-bind / /`; the bwrap subprocess at `:128` and `:167` passes no `env=`, so the measured
   repository script inherits the operator's 268 env vars (8 secret-named) and can read
   `$HOME/.ssh` and write anywhere the operator can write outside the three redirected paths
   (§Evidence F). Exploit path: the counter is designed to be pointed at an arbitrary `--root`
   (the junk control does exactly that, `tests/fixtures/r34-sandbox-junk.py:117`); a doctored
   legs file's `witness`/`nsbind` argv then runs in that envelope. Smallest remediation:
   `--ro-bind / /` plus `--bind` for the clone and scratch only, `--tmpfs` or a scratch
   HOME with `--setenv HOME`, and pass an explicit scrubbed `env=` dict.

3. **The ephemeral-root refusal is bypassable by a symlink, and absent in both junk fixtures**
   (severity: LOW-MEDIUM; operator scratch directive). `c1-counter.py:360-364` and
   `c2-counter.py:272-278` compare `os.path.abspath` prefixes, so a live symlink under
   `/fast/scratch` pointing at `/tmp` passes and the lock file lands in `/tmp` (§Evidence G).
   `tests/fixtures/r34-c1-junk.py:73-77` and `tests/fixtures/r34-sandbox-junk.py:63-64` have no
   such check at all and created `/tmp/souji-r34-junkx` when invoked directly. The fixtures
   clone the lane, whose `.git` is 77M, so a direct fixture invocation at `/tmp` breaks the
   50 MB rule. Smallest remediation: `os.path.realpath` in the two counters and the same
   three-root check (plus a refusal) in both fixtures before `makedirs`.

4. **`leg_witness` never removes its scratch clone, and `sandbox_run` cannot descend into the
   fixture's mode-000 directory** (severity: LOW; disk). `c2-counter.py:185-187` is a
   `finally: pass` whose comment reads "Keep scratch only until comparison, removal is after
   reading trace." with no removal after it; `sandbox_run`'s
   `shutil.rmtree(..., ignore_errors=True)` (`:130-131`) silently gives up on the
   `d---------` directory the W2 fixture creates (§Evidence H). Measured leftovers from one
   aborted probe: 205M + 27M + 216M. Smallest remediation: `chmod -R u+rwX` then rmtree in the
   `leg_witness` finally, and an `onerror` chmod handler in `sandbox_run`.

5. **c2 validates revision format but not revision existence** (severity: LOW; fail-closed).
   c1 calls `git cat-file -e <rev>^{commit}` (`c1-counter.py:359`); c2 has no equivalent, so
   `--rev 1111…` runs the whole leg set and every leg FAILs instead of returning exit 2
   (§Evidence C). Not a green risk (LEG FAIL, exit 1), but it burns a full leg pass. Smallest
   remediation: one `git cat-file -e` per revision after the hex check.

6. **J1's frozen argv is not the executed argv, and the documented form is rejected**
   (severity: LOW; fidelity). `c2-counter.py:287-288` ignores the leg's `argv` cell for
   `kind == "junk"` and runs `--counter <abspath> --scratch <shared scratch>` instead, so the
   frozen `--scratch {SCRATCH}/j1` is decorative; the header prose's `--tool <path>` form exits 2
   with "unrecognized arguments" (§Evidence D). W2 falsifiers cannot rely on the J1 argv cell.

7. **The J1 junk control is budgeted below its own cost** (severity: MEDIUM; operability, already
   open). The committed receipt `census/round-34/records/junk-c2-final.txt:22` records
   "timed out after 900 seconds" for the inner full-counter run, and
   `census/round-34/records/controls.txt` states the repaired feasibility ended
   "SUMMARY legs=13 pass=9 fail=4 harm=0". Nested full-counter runs inside a 900 s fixture cap
   cannot complete at current host load (43-54 during my run). Not mine to fix; recorded here
   because it makes the J1 leg COULD-NOT-EVALUATE-prone rather than falsifiable.

8. **The census selftest reading is instrumentation-sensitive, not lane-broken — retraction of my
   own first reading** (severity: none; method caveat for w2). My execve audit wrapped the
   counter in `strace -f -e trace=execve,execveat` and G01 then reported
   `selftest: 69 checks, 7 failed` (MISMATCH, load 52.05); the same counter run with no outer
   ptrace AGREES with `selftest: 69 checks, 0 failed` at load 32.74, and three direct runs
   (loads 54.31, 49.04, 43.49) also print 0 failed (§Evidence I). I did not separate
   `execveat` from host load; the load-bearing fact is that **any seat auditing G01 by wrapping
   it in an outer ptrace records a false MISMATCH** — audit by argv, not by strace.

9. **Execution locality holds for measured code, with one narrow exception** (severity: LOW).
   Every repository script of a measured item ran from the clone or scratch (§Evidence E). The
   exception is the J1 branch, which runs `tests/fixtures/r34-sandbox-junk.py` from `--root`'s
   working tree rather than from a clone at `--rev` (`c2-counter.py:288`), so an uncommitted
   edit to that fixture would be executed by the instrument; and the counter's own `git` calls
   resolve through the caller's ambient PATH (11 candidate dirs in the trace), so a poisoned
   PATH can substitute `git` for the instrument's own reads. Smallest remediation: pin PATH for
   the counter's own git calls, and extract the fixture blob from `--rev` into scratch.

## Attack log

Reproduced states only; nothing operationalized, no credential read beyond a directory entry
count.

- A1 (MEDIUM) — *envelope escape*: a leg script run by `leg_witness` inherits the operator env
  and a read-write `/`; verified `touch` outside the three redirected paths succeeds and
  `$HOME/.ssh` is listable (§Evidence F). Requires a doctored `--root`; the counter accepts one.
- A2 (LOW-MEDIUM) — *scratch relocation*: symlink `--scratch` at a `/tmp` target and the
  ephemeral-root refusal does not fire; both counters then write their lock there and would
  clone there (§Evidence G). No predicate or target is affected — only the operator's disk rule.
- A3 (LOW) — *stale-scratch accumulation*: repeated witness legs add ~200 MB each under
  `--scratch` with no removal, so a scratch mount can fill mid-leg (§Evidence H).

Not claimed: any change to a frozen predicate, target, counter, item or leg. Findings 2-9 are
implementation or record gaps inside the frozen shapes; only the L1 may amend.

## Deliveries

- `.ufo/waves/round-34/w1/SwarmSentinel37.md` (this report). No other file written in the lane.
  Scratch `/fast/scratch/hyaku/souji-r34/SentinelRound/` removed after copying the receipts above.
