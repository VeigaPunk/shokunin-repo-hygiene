# SwarmCritic28 — w2 seat report (target: AttackC2N3Timeout)

Seat assignment: adversarially falsify the W1 finding for C2 N3 — inspect the private bind,
staged tool, 12 CASE results, pin digest and canary evidence; determine whether a genuine 12/0
result is achievable under the frozen fixture with current host resources. Lane leaf, read-only.
Lane tip at run time: adac8bbc79a7ed77b632b309e70fd2a91b45dbd9 (W1 measured 51acb5fb…; the two
probed files are byte-identical at both). Base 9c76c7222a8abff027af42e37f0d160d52526bba; frozen
list / counter repair / re-pin 2b0171e2071fdc9c16a69bed12b0d040e574d8c8.

## Status

W1 FINDING CONFIRMED — every falsification angle I tested failed to overturn it. The N3 timeout
defect is real, structural, and reproduced on the current quiet host: a full 12-case arm under
the frozen bwrap envelope fails `CASE R14C2-07 exit=124` → `SUMMARY total=12 failed=1`; the
same arm with `--proc /proc` passes 12/12 in ~4.4 s. A genuine 12/0 is not achievable under the
frozen envelope (5/5 full-sequence failures across load 0.42-58), and the defect is a repairable
frozen-counter gap, not unreachable under another frozen clause. Verdict: real defect; W1's
reasoning, evidence, and repair classification all stand.

## Evidence

Executed by this seat (scratch /fast/scratch/hyaku/souji-r34/AttackC2N3Timeout/, 152K; fixture +
staged tool copied from the clean worktree, digests pinned: fixture `e6a984b1…` == NAMESPACE pin,
tool `1eab92fb…`; identical at base and rev via `git show`):

- P0 — exact frozen envelope, procfs probe (load 1.61): sandboxed bash ns-pid 2 reads host
  `kthreadd` at /proc/2, /proc/self = host pid 409336, /proc/1 = host `systemd`. Host procfs
  confirmed inside the PID namespace (reproduces W1 R7 on current host).
- P1 — full 12-case pinned fixture under the exact frozen arm, NO `--proc` (load 1.63→1.65):
  102.5 s, rc=1, `CASE R14C2-07 FAIL exit=124 want 0; census header missing; row count 0 for
  normal-shokunin`, other 11 CASE PASS, `SUMMARY total=12 failed=1`. W1's failure shape
  reproduced on the QUIET current host. (The executed bash -c carried an inert stray
  `python3 -B tests-dummy 2>/dev/null;` prefix that exited instantly on a nonexistent path;
  the fixture invocation itself was the canonical command.)
- P2 — repair control, same arm + `--proc /proc` (load 1.59→1.62): 4.4 s, rc=0, all 12 CASE
  PASS, `SUMMARY total=12 failed=0`. Genuine 12/0 achievable on current resources with the
  procfs repair.
- P3 — position control, case 07 ALONE under the frozen arm (load 1.48): 1.87 s, rc=0, PASS.
  Case 07 is not intrinsically broken; failure is sequence-position-dependent.

Inspected (not re-run): `census/round-34/records/feasibility-final.txt` (worktree record of a
run at rev 60def78…): `LEG N3 FAIL cases=12 pinned=True summary=False load=0.42`; W1
deliverables (R2/R3/R8a/R8b failures at load 29-58, R8c hang moving to case 06, R8e short
sequences passing, R9-R11 repaired-arm passes); `deliver-c2-j1guards.txt` base==rev counter run
N3 FAIL at load 22.64. Host low-PID sample: PIDs 2-39 are kernel threads (permanent); 223/400
PIDs ≤ 400 exist. Pin digest `e6a984b1…` unchanged before/after all probes. Private bind
confirmed: killed run's tool scratch `souji-census-now.*` landed in the bound `vt`; fixture
scratch cleaned itself. Canary byte-identity is counter-side (`c2-counter.py:164-171`) and was
executed by W1 (R3/R10, `cmp` clean) — inference for the current host; this seat created no
real-/var/tmp canary.

## Findings

1. Not a load artifact: reproduces at load 1.63→1.65 (this seat) and failed at load 0.42
   (committed record), while case 07 alone passes at load 55.63 (W1 R4) and 1.48 (P3).
2. Mechanism verified from frozen bytes: `c2-counter.py:159-162` omits `--proc /proc`;
   `tools/souji-census.sh:1544-1556,1598-1614` polls `/proc/<nspid>/stat` up to a ~605 s cap
   (REPO_TIMEOUT 600, `:238`); the fixture kills at 90 s
   (`tests/fixtures/r14-census-boundary.py:399`); the leg requires rc==0 + 12 CASE lines +
   exact `SUMMARY total=12 failed=0` + pin (`c2-counter.py:193-198`).
3. Position-dependent failure (case 07 passes alone/at front, fails 7th, hang moves 06↔07)
   matches cumulative namespace-PID consumption colliding with persistent host PIDs — W1's
   collision model, confirmed.
4. Genuine 12/0 under the frozen envelope: not achievable in practice — 5/5 full-sequence
   failures (W1 ×4, this seat ×1) plus counter-level FAILs at load 0.42/22.64; the leg needs
   two consecutive full passes (base+rev); a lucky flaky double pass is unobserved and would
   violate the kill rule's spirit.
5. Reachable and repairable: the N3 legs text binds only the `/var/tmp` bind, `--proc /proc` is
   implementation-neutral, and the A6 counter-repair precedent (2b0171e) covers execution-only
   repairs before target data. P2 proves the repaired arm is green on current resources.
   Classification per W1: counter repair, L1's decision; until landed, `pass=13 fail=0` is not
   reachable via N3.
6. Minor W1 imprecision (finding unaffected): "committed feasibility-final.txt at 60def78" is an
   untracked worktree record of a run at that rev, not a file committed in it; "unreachable" is
   operational (0/5), not mathematical.

## Attack log

- A1 load-artifact theory: killed (quiet-host reproduction + load-0.42 committed FAIL vs
  load-55.6/1.48 passes of case 07 alone).
- A2 case-intrinsic defect theory: killed (P3 case-07-alone PASS under the frozen arm).
- A3 bwrap-auto-procfs theory: killed (P0 host PIDs visible in-envelope).
- A4 unreachability-under-another-frozen-clause theory: refuted (legs text permits the mount;
  A6 precedent; P2 green).
- A5 lucky-pass theory: rejected as a practical path (0/5; double-pass requirement; kill rule).
- A6 adjacent surfaces (pin-check hashes committed blob only; J1 recursion): out of this seat's
  scope, handled by other seats; neither bears on the timeout finding.

## Deliveries

- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-34/w2/AttackC2N3Timeout.md` —
  full target report with exact commands, outputs, and file:line citations.
- This file. Scratch receipts: /fast/scratch/hyaku/souji-r34/AttackC2N3Timeout/ (run-frozen.log,
  run-proc.log, run-07alone.log; 152K). No lane/frozen artifact modified; no installs/upgrades;
  no real-/var/tmp writes by this seat.
