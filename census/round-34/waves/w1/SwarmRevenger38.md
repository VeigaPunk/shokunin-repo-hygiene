# SwarmRevenger38 — N3 design reconstruction

## Status
STATUS: PASS — N3's contract was reconstructed from committed bytes and executed in scratch.
The NAMESPACE hold is respected in the sense the leg claims: the pinned fixture digest is
unchanged before/after every run, the real `/var/tmp` canary survives, and the pinned bytes
contain no write outside the private `/var/tmp` bind. One falsifier was reproduced and
delivered: the counter's bwrap envelope omits `--proc /proc`, so N3 fails intermittently
with `exit=124` and the frozen `pass=13 fail=0` target is currently unreachable; adding
`--proc /proc` makes the same arm pass 12/12 in ~6 s. The mount-level reading "the sandboxed
run cannot reach the pinned file for writing" is false; containment is behavioural and
digest-enforced, not mount-enforced.

## Evidence
Lane `/home/vgpnk/Projects/shokunin/souji-shokunin`; measured tip
`51acb5fb6fa38a6b593b3badb674cec559d7eb2c`; base `9c76c722…`; list/freeze `2b0171e2…`.
Scratch clone at the tip, origin removed, `git -C … rev-parse --show-toplevel` printed the
clone. Full receipts are in `deliver-n3-design.txt`; every fixture reading carried
`cat /proc/loadavg` and ran under `flock`.

- Pin: worktree, `git show 9c76c72:…`, `git show 2b0171e:…` and `git show 51acb5f:…` all
  hash `e6a984b1daf1f79a6ad613e451cae48c2807fd71639de4c8d92857b9a11d14b2`.
- Frozen arm, full run, load 32.04→55.00: `CASE R14C2-07 FAIL exit=124 …; SUMMARY
  total=12 failed=1`, rc 1.
- Same arm + `--ro-bind <clone> <clone>`, load 51.46→58.66: `CASE R14C2-07 … exit=124`;
  digest before=after `e6a984b1…`; real canary `/var/tmp/souji-r34-n3-canary.CWMVNr`
  content `r34 namespace canary` after; `<vt>` held only `souji-census-now.*` tool scratch.
- Case 07 alone: `CASE R14C2-07 PASS ok; SUMMARY total=1 failed=0` (load 55.63, 6.65 s);
  with the read-only clone: same PASS (load 18.36, 2.00 s).
- Probe in the exact envelope: `OPEN-O_RDWR ok` on
  `<clone>/tests/fixtures/r14-census-boundary.py`; digest unchanged.
- `/proc` probe inside the arm: `ns_pid=2`, `cat /proc/$$/comm` = `kthreadd`,
  `readlink /proc/self` = host pid `1845908`; with `--proc /proc`: `proc_comm=bash`,
  `self=6`. Namespace child pid 3 reads host `pool_workqueue_release` without `--proc`,
  `sleep` with it.
- Arm + `--proc /proc`, load 12.00→16.26: all 12 CASE PASS,
  `SUMMARY total=12 failed=0`, rc 0 (~6 s). With read-only clone, load 13.68→13.22:
  12/12 PASS, 6.49 s, digest and canary unchanged. Regenerate-shaped argv
  (`timeout 300`, relative fixture, `cwd=clone`) + `--proc /proc`: 12/12 PASS.
- Committed cross-check: `census/round-34/records/feasibility-final.txt` already reads
  `LEG N3 FAIL cases=12 pinned=True summary=False` at `60def78`.
- Versions: bubblewrap 0.13.1, strace 7.2, Python 3.14.8, git 2.56.0. No installs.

## Findings
1. **Mount set.** `census/round-34/c2-counter.py:122-127` and `:159-162` build
   `--dev-bind / /` + `--ro-bind <empty> /tmp` + `--ro-bind <empty> /dev/shm` +
   `--bind <d>/vt /var/tmp` + `TMPDIR=<d>/tmp` + `--chdir <clone>`. `--dev-bind` leaves the
   whole host root read-write, not only `/var/tmp`; bwrap's own definition is
   "--dev-bind SRC DEST      Bind mount the host path SRC on DEST, allowing device access"
   (`bwrap --help`, 0.13.1). Bubblewrap README § Sandbox security (fetched 2026-10-27):
   "the level of protection between the sandboxed processes and the host system is entirely
   determined by the arguments passed to bubblewrap" (21 words).
2. **Fixture write surface.** `tests/fixtures/r14-census-boundary.py:691` creates its only
   scratch as `tempfile.mkdtemp(prefix="r14-census-boundary.", dir="/var/tmp")`; every write
   site (`:163-166`, `:185-186`, `:210-221`, `:230-309`, `:317-319`, `:362-364`, `:648-654`)
   derives from SCRATCH or its subpaths. `__file__` is used once (`:681`) to default a
   read-only tool path; the fixture only reads its own bytes (`:700`). `cwd=SCRATCH`
   (`:394`) and `TMPDIR=/var/tmp` for the tool (`:368`) keep tool scratch in the private bind
   (observed leftovers: `souji-census-now.*` under `<vt>`).
3. **Pin respected in execution.** The pinned file hash is `e6a984b1…` before and after all
   runs, including the read-only-clone run; the counter re-hashes the `--rev` blob
   (`c2-counter.py:195-197`) and guard G6 does the same (`:231-233`); the consumer pins the
   constant and rejects a mismatched record (`tools/souji-preservation-evidence.py:307`,
   `:1161-1164`, `:1921-1923`). No executed run touched the file.
4. **Reachability.** The pinned path is `O_RDWR`-openable inside the arm (`OPEN-O_RDWR ok`),
   so the sandbox does not prevent writing it; the protection is the pinned fixture's
   behaviour plus the digest checks. A run with the clone mounted read-only still passes all
   non-timed-out cases and leaves the digest unchanged, proving no write to the clone is
   needed or performed.
5. **Counter defect (falsifier).** The envelope unshares PID but keeps host `/proc` (no
   `--proc /proc`). `tools/souji-census.sh:1547-1556` `proc_state` reads
   `/proc/<namespace-pid>/stat`; with host procfs a colliding pid is a live kernel thread,
   so the loop at `:1599` runs to the cap at `:1614` (`REPO_TIMEOUT*10+50`, default 600 at
   `:238`) ≈ 605 s, while `run_tool` kills at 90 s (`r14-census-boundary.py:399`), recording
   `exit=124`. Reproduced in full runs and sequences (case 07, then case 06 as the hang
   moved). Adding `--proc /proc` yields 12/12 PASS in ~6 s at comparable load.
6. **S230 not committed.** `grep -c S230 corpus/SOURCES.md` = 0; the registry ends at S229
   (`corpus/SOURCES.md:176`) at the tip. The preregistration cites S230 for this design; the
   README opened for finding 1 supplies the semantics, but L1 still has to append the row.
7. **regenerate.py adoption is feasible without pinned bytes.** Its namespace stage is
   `tests/fixtures/r15-preservation-frozen/regenerate.py:70-72` (`timeout 300 python3 -B
   <fixture> --tool <tool>`, `cwd=LANE`) and `:153`. Wrapping that call in the N3 envelope
   with `--proc /proc` and a private `/var/tmp` bind passes 12/12 (receipt R11) and leaves
   `r14-census-boundary.py` untouched; the record checker only rejects subset-selector argv
   tokens (`tools/souji-preservation-evidence.py:1330-1336`). Full recipe is in the delivery.

## Attack log
- **A1 — frozen counter envelope is wrong (`--proc`).** State: full N3 run at tip
  `51acb5f`, load 32.04→55.00, `CASE R14C2-07 FAIL exit=124 … SUMMARY total=12 failed=1`;
  sequences `01..07`, `04,05,06,07`, `05,06,07` fail at the 90 s fixture timeout; the
  committed `feasibility-final.txt` shows the same. Adding `--proc /proc` makes the same arm
  pass 12/12 in ~6 s. This is counter repair, not a predicate/target/item change; L1 decides.
  Until repaired, N3 cannot contribute to `pass=13 fail=0`.
- **A2 — "cannot reach for writing" is not mount-true.** State: `OPEN-O_RDWR ok` on the real
  pinned path inside the exact envelope. The leg verifies digest + canary only; a latent
  write path in the pinned fixture (outside the 12 exercised cases) would not be blocked by
  the mounts (the clone is disposable, so the lane is not exposed).
- **A3 — adjacent, W1/W3/W4 witness clause is vacuous.** `c2-counter.py:157` straces only the
  `--rev` run, so `base_run[2]` is always 0 and the rule "sandboxed creations >= half of
  base's" (`:201`) reduces to `tip>=1`; committed `feasibility-final.txt` records
  `W1 … creates=0/209` and `W4 … creates=0/1057`. A stub that creates one file under
  `TMPDIR`/`/var/tmp` and prints the line would satisfy it. Outside this seat's N3 surface;
  reported because it is a gameable frozen predicate.

## Deliveries
- `.ufo/waves/round-34/w1/deliver-n3-design.txt` — full reconstruction, receipts, regenerate
  adoption recipe, falsifier.
- `.ufo/waves/round-34/w1/SwarmRevenger38.md` — this report.

Scratch `/fast/scratch/hyaku/souji-r34/RevN3Design` was removed after the receipts were
copied; the seat's real `/var/tmp` canaries were unlinked.
