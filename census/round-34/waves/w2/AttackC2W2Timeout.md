# AttackC2W2Timeout — w2 adversarial falsification of the W1 C2 W2-timeout finding

Seat: SwarmCritic26 (lane leaf, read-only, godspeed). Lane: /home/vgpnk/Projects/shokunin/souji-shokunin.
Base: 9c76c7222a8abff027af42e37f0d160d52526bba. Frozen list / C2 counter repair / re-pin:
2b0171e2071fdc9c16a69bed12b0d040e574d8c8. Lane HEAD at this run: adac8bbc79a7ed77b632b309e70fd2a91b45dbd9
(touches only SCORECARD.md; every probed byte identical 9c76c72→adac8bb, verified below).
Target: C2 leg W2 (`census/round-34/c2-legs.tsv` witness row:
`python3 -B tests/fixtures/r15-census-config.py --tool tools/souji-census.sh`).

## Status

W1 FINDING CONFIRMED, with two load-bearing corrections to its framing. The W2 timeout is real
and I reproduced it with the frozen bytes: under the counter's exact repaired sandbox envelope
(`census/round-34/c2-counter.py:122-127`, byte-frozen since 2b0171e2), the full 20-case W2
fixture run fails exactly one case, `R15CFG-01`, with `exit=124` at the fixture's 90 s kill,
printing `SUMMARY\ttotal=20\tfailed=1` — a byte-exact match of the committed
`census/round-34/records/feasibility-final.txt:2` W2 line. Cause, per the wave's three
candidates: (1) **bwrap boundary — CONFIRMED** (the envelope omits `--proc /proc`; the sandbox
unshares PID but keeps host `/proc`, so the census tool's watchdog polls a live host kernel
thread forever); (2) **external load — FALSIFIED** (reproduced at load 1.55–2.89; the committed
failure was at load 6.87; observed passes at load 10.15 and 49.82); (3) **fixture behavior —
FALSIFIED** (fixture + tool pass in 6.5 s outside the sandbox and in 7.2 s with `--proc`; the
fixture's exit=124 is its correct 90 s kill of a tool the envelope hung). TMPDIR is not
implicated: fixture/tool scratch landed correctly in the sandbox TMPDIR. Consequential answer:
**the frozen leg CAN pass without changing the pinned fixture** — demonstrated 20/20 PASS in
68 s with only `--proc /proc` added to the counter's bwrap argv; the repair is a counter edit
(C2-owned per the prereg's touched-set), not a fixture edit, matching the A6 precedent
SwarmRevenger38 logged for N3.

## Evidence

Byte-identity (executed):
- `git diff --stat 9c76c72… 60def78… -- tools/souji-census.sh tests/fixtures/r15-census-config.py` → empty;
  same for `51acb5f..adac8bb` and for `c2-counter.py`/`c2-legs.tsv` over `2b0171e..60def78` → empty.
- Staged copies (no clone; scratch `/fast/scratch/hyaku/souji-r34/AttackC2W2Timeout/run01/root`):
  `tools/souji-census.sh` sha256 `1eab92fb094701838f1ba04635acd0b617034dbf69b0574813c14ff9fcb07f5a`,
  `tests/fixtures/r15-census-config.py` sha256 `703c05b0dc3547f10173180fd3db285ce5deb827a7da3ea7799344a00e2a1dc1`.
  The r15 fixture is NOT the G6-pinned file (G6 pins `tests/fixtures/r14-census-boundary.py`,
  `c2-counter.py:231-234`); no leg pins the W2 fixture bytes.

Probe P0 — procfs exposure inside the EXACT frozen envelope (executed, load ~1.8):
```
$ bwrap --unshare-user --unshare-pid --die-with-parent --dev-bind / / \
    --ro-bind $S/empty /tmp --ro-bind $S/empty /dev/shm --bind $S/vt /var/tmp \
    --setenv TMPDIR $S/tmp --chdir / -- bash -c 'sleep 25 & w=$!; echo worker=$w; \
    cat /proc/$w/stat | head -c 90; echo; cat /proc/$w/comm; readlink /proc/self'
worker=3
3 (pool_workqueue_release) S 2 0 0 0 -1 …   <- host kernel thread, never exits
pool_workqueue_release
462724                                       <- /proc/self is a host pid
```
With `--proc /proc` added: `/proc/3/stat` = `3 (sleep) S …`, `/proc/self` = `2`. Mechanism
confirmed independently of W1: namespace pids resolve against host procfs.

Probe P1 — R15CFG-01 inside envelope, NO `--proc` (executed, load 1.55 1.49 1.92):
```
$ timeout 180 bwrap … --chdir $S/root -- bash -c \
    'python3 -B tests/fixtures/r15-census-config.py --tool tools/souji-census.sh --case R15CFG-01'
CASE	R15CFG-01	FAIL	exit=124 want 0	observed_exit=124	observed_finding=none
SUMMARY	total=1	failed=1      rc=1      real 1m30.453s
```
Exactly the 90 s fixture kill (`tests/fixtures/r15-census-config.py:848-852` `timeout=90`).

Probe P2 — same + `--proc /proc` (executed, load 2.68 1.86 2.02): `CASE R15CFG-01 PASS ok`,
`SUMMARY total=1 failed=0`, rc=0, real 0m7.185s.

Probe P3 — same OUTSIDE the sandbox, scrubbed env, TMPDIR under scratch (executed, load 4.13):
`CASE R15CFG-01 PASS ok`, rc=0, real 0m6.530s. Fixture and tool are correct uncontained.

Probe P4 — FULL 20-case W2 fixture, envelope, NO `--proc` (executed, load ~2 throughout,
start 10:10:40, end 10:14:26, real 3m45.327s):
```
CASE	R15CFG-01	FAIL	exit=124 want 0	observed_exit=124	observed_finding=none
CASE	R15CFG-02..R15CFG-20	PASS (19/19; exits/findings match the fixture oracles)
SUMMARY	total=20	failed=1   rc=1
```
Byte-exact reproduction of `feasibility-final.txt:2`
`LEG W2 FAIL CASE=20 summary=SUMMARY total=20 failed=1`, and confirms the wave's
R15CFG-01 attribution: under current host conditions R15CFG-01 is exactly the case that dies.

Probe P5 — repair control: FULL 20-case fixture, envelope + `--proc /proc` (executed, load
2.89 2.26 2.16, real 1m8.101s): 20/20 `PASS ok`, `SUMMARY total=20 failed=0`, rc=0.

Counter-side facts (inspection):
- W2 branch `c2-counter.py:301-311` runs BOTH arms via `sandbox_run` (`:303-304`), whose
  envelope `:122-127` has no `--proc /proc`; pass requires `rb[0]==rr[0]==0` and rev-side
  `SUMMARY … failed=0` (`:308`).
- Tool hang: `tools/souji-census.sh:1599` `proc_state "$worker"` reads `/proc/$worker/stat`;
  with host procfs a colliding pid is a live kernel thread, so `:1614`'s cap
  `REPO_TIMEOUT*10+50` (default 600→~605 s, `:238`) is reached while the fixture kills at 90 s.
- Host low-pid map at probe time (executed): pids 2–8 kernel threads, 9–14 ABSENT, 15/20/25/30/50
  kernel threads, max pid ~1.1 M. Intermittency mechanism: whether the worker's namespace pid
  collides with a live host pid or an absent one is a per-invocation lottery — matches W1
  observation that the hang moves (SwarmRevenger38 deliver-n3-design.txt R8).

Prior readings (committed / W1 reports, not re-run by me): `feasibility-final.txt` W2 FAIL at
load 6.87 (low); `feasibility.txt` W2 PASS load 10.15 (pre-A6 counter semantics); w1
`SwarmExecutor17.md` W2 PASS `failed=0` load 49.82 (high). The failure anti-correlates with load.

## Findings

1. **The W2 timeout is real, reproduced with frozen bytes, currently deterministic on this host.**
   P4 reproduces the committed `CASE=20 … failed=1` exactly, and names the failed case:
   R15CFG-01, matching the wave's evidence pointer. Not a measurement artifact of W1.
2. **Cause = the bwrap pid-namespace/procfs boundary, not load, not the fixture, not TMPDIR.**
   P1 reproduces the 90 s `exit=124` at load 1.55; P2/P3 pass in 6–7 s with only `--proc` or no
   sandbox at all; the committed failure was at load 6.87 while passes were recorded at load
   10–50. The envelope unshares PID but binds host `/proc` (`c2-counter.py:122-127`), so the
   tool's watchdog (`souji-census.sh:1599-1614`) polls a host kernel thread (P0) and never sees
   its worker die. The fixture's kill (`r15-census-config.py:848-852`) is correct behavior
   acting on an envelope-hung tool.
3. **The frozen leg can pass without changing the pinned fixture.** P5: 20/20 PASS, rc 0, in 68 s
   with only `--proc /proc` added to the counter's bwrap argv; the W2 fixture
   (sha256 `703c05b0…`) is not edited (and is not G6-pinned). The repair file
   `census/round-34/c2-counter.py` is inside the prereg's C2 touched-set
   (`census/round-34/c2-*`), so this is an allowed counter repair under A6's precedent, not a
   predicate/target/item change and not a pinned-byte change. C2's frozen target remains
   unreachable until that repair lands (same root cause blocks N3, per SwarmRevenger38 /
   sibling seat AttackC2N3Timeout).
4. **Falsified sub-claims of the naive reading.** "Timeout is caused by external load" — dead
   (P1 at load 1.55; committed failure at 6.87; passes at 10.15/49.82). "The fixture itself is
   broken under bwrap" (SwarmScribe35 finding 6's wording) — dead as a fixture defect: the
   fixture passes 6.5 s uncontained (P3) and 7.2 s with a correct procfs (P2); what fails is
   the tool under the broken envelope. "Must change the pinned fixture to pass" — dead (P5).
5. **Residual caveats.** (a) Which arm failed in the committed `feasibility-final.txt` run is
   not recorded; both arms run identical bytes in identical envelopes (`:303-304`) and are
   equally exposed, so this does not change the determination. (b) Pass/fail is a pid-collision
   lottery across host regimes (host kthread layout vs namespace pid counter), so "deterministic
   today" (P1/P4 both failed at case 01 within minutes, load <3) is a property of the current
   host, not a proof of universal determinism. (c) The same envelope defect independently
   breaks N3; that seat's target is covered by AttackC2N3Timeout — no duplicate finding claimed
   here beyond the shared root cause citation.

## Attack log

- **A1 (envelope attack, executed)** — ran the W2 fixture's R15CFG-01 and the full 20-case
  suite inside the counter's exact envelope without `--proc` (P1, P4): both failed case 01 at
  the 90 s kill with `exit=124`, `SUMMARY total=20 failed=1`, at load 1.55–2. Sealed the
  committed reading's shape.
- **A2 (load-hypothesis falsification, executed)** — P1/P4 at load <3 fail while recorded
  passes exist at load 10.15/49.82; P5 passes at load 2.89. Load is exonerated; if anything the
  correlation inverts.
- **A3 (fixture-behavior-hypothesis falsification, executed)** — P3 (uncontained) and P2
  (envelope + `--proc`) both pass in 6–7 s. The fixture is not the defect; its timeout kill is
  the correct detection of an envelope-hung tool.
- **A4 (repair-feasibility probe, executed)** — P5 shows the full leg passes 20/20 in 68 s with
  one flag added to the counter. No frozen predicate, leg, target, item, or pinned byte needs
  to change; the fix is C2-owned.
- **A5 (benign-explanation sweep, inspection)** — TMPDIR boundary exonerated: the fixture's
  scratch (`tempfile.mkdtemp`, `r15-census-config.py:1551`) and the tool's `CENSUS_TMP_ROOT`
  both resolve under the sandbox TMPDIR (`run_tool :832-837` sets `TMPDIR`; tool `:197` honors
  it); the only broken namespace boundary is `/proc` (P0).

## Deliveries

- This report: `.ufo/waves/round-34/w2/AttackC2W2Timeout.md`.
- Scoped seat findings: `.ufo/waves/round-34/w2/SwarmCritic26.md`.
- Executed probe logs: `/fast/scratch/hyaku/souji-r34/AttackC2W2Timeout/run01/full-noproc.log`
  (P4, 20 CASE lines) and `full-proc.log` (P5); staged frozen-byte copies under
  `run01/root/{tools,tests/fixtures}`; envelope probes P0–P3 as transcribed above.
- No lane file edited; no frozen artifact altered; no git/jj mutation in the lane (scratch
  copies only, lane read-only). Scratch stayed <1 MB (two file copies + logs; no clone).
- Tooling: no installs/upgrades (bwrap 0.13.1, strace 7.2, python3 3.14.8 already present).
- Main-agent checks suggested: none beyond the L1's standing decision on the `--proc /proc`
  counter repair (already logged by W1 SwarmRevenger38; this seat independently reproduces the
  W2 arm and the repair control).
