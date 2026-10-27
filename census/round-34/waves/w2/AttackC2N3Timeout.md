# AttackC2N3Timeout — w2 falsification of the W1 N3 timeout finding

Seat: SwarmCritic28 (lane leaf, read-only). Lane: /home/vgpnk/Projects/shokunin/souji-shokunin.
Base: 9c76c7222a8abff027af42e37f0d160d52526bba. Frozen list / C2 counter repair / re-pin:
2b0171e2071fdc9c16a69bed12b0d040e574d8c8. Lane tip at this run: adac8bbc79a7ed77b632b309e70fd2a91b45dbd9
(W1 measured at 51acb5fb6fa38a6b593b3badb674cec559d7eb2c; the two probed files are byte-identical
at both revisions). Target: C2 leg N3 (`census/round-34/c2-legs.tsv` nsbind row).

## Status

W1 FINDING CONFIRMED — not falsified. The alleged defect is real, structural, and reproduced
under current host resources: the frozen counter's bwrap envelope omits `--proc /proc`
(`census/round-34/c2-counter.py:159-162`), the sandbox keeps the host procfs while unsharing
the PID namespace, and the staged census tool's watchdog treats colliding host PIDs as live
workers, so a full 12-case N3 arm fails with `exit=124` at the fixture's 90 s kill. A genuine
12/0 result is NOT achievable under the frozen envelope (5/5 full-sequence runs failed across
two host regimes, load 0.42-58). The same arm plus `--proc /proc` passes 12/12 in ~4.4 s on
the current host, so the defect is repairable as a counter repair (A6 precedent), not a
predicate/target/item change, and is not unreachable under another frozen clause.

## Evidence

All of: lane worktree was clean for the two probed files at `git rev-parse HEAD` =
adac8bbc79a7ed77b632b309e70fd2a91b45dbd9; fixture sha256 `e6a984b1daf1f79a6ad613e451cae48c2807fd71639de4c8d92857b9a11d14b2`
(== NAMESPACE pin, `c2-counter.py:15`, G6 `c2-counter.py:231-234`) and staged tool sha256
`1eab92fb094701838f1ba04635acd0b617034dbf69b0574813c14ff9fcb07f5a`, identical at base and tip
via `git show 9c76c72:… | sha256sum` [executed]. Scratch: /fast/scratch/hyaku/souji-r34/AttackC2N3Timeout/
(152K total; copies of `tests/fixtures/r14-census-boundary.py` + `tool.sh` staged with chmod 0755,
mirroring `c2-counter.py:151-153`; no git clone, no lane writes, no real-/var/tmp canary created).

Probe P0 — procfs exposure inside the EXACT frozen envelope (current host, load 1.61):
```
$ bwrap --unshare-user --unshare-pid --die-with-parent --dev-bind / / \
    --ro-bind $D/empty /tmp --ro-bind $D/empty /dev/shm --bind $D/vt /var/tmp \
    --setenv TMPDIR $D/tmp --chdir $D -- bash -c 'echo ns_pid=$$; cat /proc/$$/comm; readlink /proc/self; cat /proc/1/comm'
ns_pid=2
kthreadd                 <- /proc/2 is the HOST kernel thread, not the sandboxed bash
409336                   <- /proc/self resolves to a host PID
systemd                  <- /proc/1 is the host init
```
[executed by me] Independently reproduces W1 R7 on the current host: bubblewrap 0.13.1 does not
mount a fresh procfs for `--unshare-pid` alone; the sandboxed processes see host `/proc` while
carrying namespace PIDs.

Probe P1 — full 12-case pinned fixture under the exact frozen arm (NO `--proc`), current host:
```
START 2026-10-27T10:01:53-03:00 load=1.63 1.26 2.11
$ flock $D/n3.lock bwrap --unshare-user --unshare-pid --die-with-parent --dev-bind / / \
    --ro-bind $D/empty /tmp --ro-bind $D/empty /dev/shm --bind $D/vt /var/tmp \
    --setenv TMPDIR $D/tmp --chdir $D -- bash -c "python3 -B r14-census-boundary.py --tool $D/tool.sh"
(executed bash -c carried an inert stray prefix `python3 -B tests-dummy 2>/dev/null;` before the
fixture invocation; it exited instantly on a nonexistent path and did not affect the run)
real 1m42.509s  RC=1  END load=1.65 1.35 2.05
CASE R14C2-01..06 PASS ok
CASE R14C2-07 FAIL exit=124 want 0; census header missing; row count 0 for normal-shokunin, want 1
CASE R14C2-08..12 PASS ok
SUMMARY total=12 failed=1
```
[executed by me] Exact W1 R2/R3 shape reproduced on the QUIET current host (load 1.63→1.65,
vs W1's 32-58): 11/12 PASS, case 07 dead at the 90 s fixture timeout
(`tests/fixtures/r14-census-boundary.py:399`).

Probe P2 — repair control: same arm + `--proc /proc` (current host):
```
START load=1.59 1.43 2.01
$ flock $D/n3.lock bwrap … --bind $D/vt /var/tmp --proc /proc --setenv TMPDIR $D/tmp \
    --chdir $D -- bash -c "python3 -B r14-census-boundary.py --tool $D/tool.sh"
real 0m4.411s  RC=0  END load=1.62
CASE R14C2-01..12 PASS ok
SUMMARY total=12 failed=0
```
[executed by me] Genuine 12/0 under current host resources once the procfs is namespace-fresh,
matching W1 R9-R11 (~6 s).

Probe P3 — position control: case 07 ALONE under the frozen arm (no `--proc`), current host:
```
$ … -- bash -c "python3 -B r14-census-boundary.py --tool $D/tool.sh --case R14C2-07"
real 0m1.874s  RC=0
CASE R14C2-07 PASS ok
SUMMARY total=1 failed=0
```
[executed by me] Case 07 is not intrinsically broken; it fails only in full-sequence position
(matches W1 R4/R5: case 07 alone passed at load 55.63/18.36).

Prior committed/recorded evidence (inspected, not re-run):
- `census/round-34/records/feasibility-final.txt` (worktree record of a run at rev
  60def78d16017be528ba6b439e350918587cb80b): `LEG N3 FAIL cases=12 pinned=True summary=False
  load=0.42` — N3 failed at load 0.42, the strongest committed kill of the load-artifact theory.
- W1 `deliver-c2-j1guards.txt` base==rev counter run: `LEG N3 FAIL cases=12 pinned=True
  summary=False load=22.64`.
- W1 `deliver-n3-design.txt` R2/R3/R8a/R8b: full/sequence runs fail at case 07 (load 29-58);
  R8c: hang moves to case 06; R8e: short sequences (07-first, 05+07, 06+07, 01-04+07) pass.
- Host low-PID table (read-only sample, 2026-10-27): PIDs 2-39 are kernel threads
  (kthreadd, kworker/*, rcu_*, migration/*, ksoftirqd/*) — permanently alive; 223/400 PIDs ≤400
  exist. Namespace worker PIDs collide with these for the whole watchdog window.

Source-level mechanism (verified by reading frozen bytes):
- `tools/souji-census.sh:1544-1556` `proc_state` reads `/proc/<pid>/stat`; the watchdog loop
  `:1598-1614` only declares the worker dead on read-failure or state Z/X, else spins to the cap
  `REPO_TIMEOUT*10+50` ticks (`:1614`, REPO_TIMEOUT default 600 at `:238`) ≈ 605 s. With host
  procfs, a namespace worker PID that collides with a live host PID never reads as dead → the
  loop outlives the fixture's 90 s kill → `run_tool` records `Result(124, …, "timeout", …)`
  (`r14-census-boundary.py:399-402`) → `CASE … FAIL exit=124`.
- `c2-counter.py:159-162` builds the N3 envelope with `--unshare-pid` and NO `--proc`;
  `:193-198` requires rc==0, 12 CASE lines, exact `SUMMARY total=12 failed=0`, and the pin.
- Private bind: fixture SCRATCH roots at `/var/tmp` (`r14-census-boundary.py:691`), so all fixture
  and tool scratch lands in the bound `vt` — observed leftover `souji-census-now.*` under
  `$D/vt` from the killed P1 run, with the r14 scratch dir cleaned by the fixture [executed].
- Pin digest unchanged before/after all probes: `e6a984b1…` [executed]. Real-/var/tmp canary
  compare is counter-side (`c2-counter.py:164-171`); W1 executed byte-identity (R3/R10, `cmp`
  clean) [W1-executed; inference for the current host, no canary created by this seat].

## Findings

1. The defect is REAL and STRUCTURAL, not a measurement artifact of W1's loaded window. It
   reproduces on the current quiet host (load 1.63→1.65) with the exact frozen envelope, and the
   committed record shows N3 failing at load 0.42. Load is neither necessary (fails at 0.42-1.65)
   nor sufficient (case 07 alone passes at load 55.63) for the failure.
2. W1's causal chain is verified end to end: (i) no auto-procfs under `--unshare-pid` in bwrap
   0.13.1 (P0: bash=pid 2 reads host `kthreadd`); (ii) the tool polls `/proc/<nspid>/stat`
   (`souji-census.sh:1598-1614`); (iii) the fixture kills at 90 s (`r14-census-boundary.py:399`);
   (iv) the counter requires the exact 12/0 SUMMARY (`c2-counter.py:193-198`).
3. The failure is POSITION-dependent, not case-intrinsic: case 07 passes alone (P3, 1.87 s) and
   in short sequences (W1 R8e) but fails as the 7th case of 12 (P1, W1 R2/R3/R8a/R8b), and the
   hang moves between cases across invocations (W1 R8c: case 06). This is the cumulative
   namespace-PID-consumption signature of the host-procfs collision.
4. A genuine 12/0 is NOT achievable under the frozen envelope with current host resources. The
   counter needs two independent full passes (base and rev, `c2-counter.py:134-198`); without
   `--proc`, 5/5 full-sequence runs failed across two host regimes (W1 ×4 at load 29-58, this
   seat ×1 at load 1.6), plus two counter-level N3 FAILs at load 0.42 and 22.64. A lucky double
   pass is probabilistically conceivable but unobserved and would be flaky by construction —
   incompatible with the preregistration kill rule and with the round's anti-flakiness design
   (cf. N4's leg text rejecting flaky passes).
5. The defect is REACHABLE and REPAIRABLE, not blocked by another frozen clause. The N3 legs text
   binds only "inside bwrap with --bind <scratch>/vt /var/tmp" (`c2-legs.tsv` nsbind row); the
   `--proc /proc` mount is implementation-neutral to the frozen legs and predicates, and the
   preregistration's amendment rule (with the A6 counter repair landed at
   2b0171e2071fdc9c16a69bed12b0d040e574d8c8) covers exactly this kind of execution repair before
   target data. P2 shows the repaired arm passes 12/12 in 4.4 s on the current host. L1 owns the
   repair decision; until then `SUMMARY legs=13 pass=13 fail=0` is not reachable via N3.
6. Nuances / minor imprecision in W1's wording (do not affect the finding): (a) W1's
   "committed feasibility-final.txt at 60def78" — the file is present in the worktree as an
   untracked record OF a run at rev 60def78, not committed in that revision; (b) "unreachable"
   is an operational claim (0/5 observed), not a mathematical impossibility; (c) the 90 s
   timeout lives in the pinned fixture bytes and cannot change — only the counter envelope can.

## Attack log

- A1 (load-artifact theory): KILLED. My quiet-host reproduction (load 1.63→1.65, P1) plus the
  committed load=0.42 N3 FAIL, against W1's load-55.6 case-07-alone PASS (R4) and my load-1.48
  case-07-alone PASS (P3). Failure and success both occur at both ends of the load range.
- A2 (case-intrinsic defect theory): KILLED. Case 07 alone passes under the exact frozen arm on
  the current host (P3: 1.87 s, rc=0); W1 R4/R5 identical.
- A3 (bwrap mounts fresh procfs under --unshare-pid): KILLED. Direct probe P0 shows host PIDs
  (kthreadd at ns-pid 2, systemd at /proc/1, host self-pid 409336) inside the exact envelope.
- A4 (defect unreachable / moot under another frozen clause): REFUTED for reachability. The
  frozen N3 leg text does not forbid `--proc /proc`, and the A6 amendment precedent covers
  counter-only execution repairs; P2 demonstrates the repaired arm is green on current
  resources. (L1 decision whether to land the repair — not this seat's call.)
- A5 (frozen counter might pass with luck / retries): REJECTED as a practical path. 0/5
  full-sequence passes observed across host regimes; the leg requires two consecutive full
  passes; the preregistration's kill rule counts any other reading as MISSED, so a flaky pass
  is not a genuine target reach.
- A6 (adjacent, out of scope): SwarmCritic20's separate claim that N3's pin check hashes only
  the committed blob, not the checked-out copy (`c2-counter.py:193-198` vs an untaken
  before/after worktree hash), and the J1 recursion failure (`c2-counter.py:287-290`) are
  distinct attack surfaces handled by other seats; neither was needed to confirm or refute the
  timeout finding.

## Deliveries

- `.ufo/waves/round-34/w2/AttackC2N3Timeout.md` — this report.
- `.ufo/waves/round-34/w2/SwarmCritic28.md` — seat-scoped copy.
- Scratch receipts retained at /fast/scratch/hyaku/souji-r34/AttackC2N3Timeout/:
  `run-frozen.log` (P1 full frozen run, rc=1, case 07 exit=124), `run-proc.log` (P2 repair
  control, 12/12 rc=0), `run-07alone.log` (P3, rc=0), plus the staged fixture/tool and
  `vt/`/`tmp/`/`empty/` mounts. Total 152K, well under the 50 MB ceiling. No frozen or lane
  artifact was created, modified, or deleted; no real-/var/tmp canary was created by this seat;
  no tools were installed or upgraded.
