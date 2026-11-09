# R99Sentinel — souji r99 wave 1 — safety review of the r99 arms counter's reap

Seat: R99Sentinel (safety/sentinel). Lane: `souji-shokunin`. Lane base at seat start:
`c94d678c8a76f3f87f73b49a11a9d4e2aff73e3b`. Subject file under review (final, confirmed by its owner
R99ExecC2 over IRC): `census/round-99/c2-setup-arms.py`
sha256 `03e8a99e2e447e4c5e7067dea191450c7d5ec10102cb33e2a246b5b3d1c02b57`.

Scope answered (seat target): *can any process that is not a spawn-chain member of the arm be
signalled by `census/round-99/c2-setup-arms.py`?* — probed with three foreign own-uid carriers —
(a) carrying the T1 token in argv, (b) reparented away after its parent exits, (c) a setsid
grandchild of a different arm — **plus** the additional check that no counter writes under `/tmp`
regardless of `TMPDIR`.

No lane `census/` file was edited by this seat. No git/jj mutation. No fleet-root file written.
Tools: none installed or upgraded by this seat (the host already had `strace` `/usr/bin/strace`,
`gcc`, `util-linux unshare` — all used read-only as shipped; no pacman/uv/npx transaction was run).

---

## 1. Verdict summary

| question | answer | evidence |
|---|---|---|
| (a) foreign own-uid process carrying the T1 token in argv — signalled? | **NO — SPARED** | §3.1, §3.4 (r99c) |
| (b) same, but reparented away after its parent exits — signalled? | **NO — SPARED** | §3.1, §3.4 (r99c) |
| (c) setsid grandchild of a *different* arm (counter-descendant, outside the spawn chain) — signalled? | **NO — SPARED** | §3.1, §3.4 (r99c) |
| any signal at all to a non-owned pid by the r99 counter? | **NO — zero positive-pid kills** | §3.2 (strace ground truth) |
| does the r99 counter still reap the T1 arm's own escapee? | **NO — it survives (planted-killed 0)** | §3.3, §4.1 (FINDING 1) |
| counter writes under `/tmp` regardless of `TMPDIR`? | **NO — 0 `/tmp` path syscalls, TMPDIR probe dir never created** | §5 |

**The safety direction of C2 holds.** The r99 counter did not signal any process outside the T1
spawn chain, and it did not signal my foreign carriers. The r98 and r97 counters, run with the
identical harness, *did* signal them — so the probe has demonstrated discriminating power
(§3.4 positive control) and the r99 result is not vacuous.

**But the r99 counter's T1 reap is now a no-op**: it kills nothing, including the escapee the T1
arm exists to reap. That is FINDING 1 below, and it is the reason I do not grade C2 as verified
despite the safety direction being satisfied.

---

## 2. Axes named (godspeed)

1. **Over-kill** — a signal reaches a pid the counter does not own.
2. **Under-kill / ownership reach** — the counter fails to reach a pid it *does* own (the T1 escapee).
3. **Scratch containment** — does any counter write land under `/tmp`, whatever `TMPDIR` says.
4. **Discriminating power of the evidence** — does the instrument distinguish a clean run from a
   broken one (positive control)?

---

## 3. Commands run, exit codes, observed summary lines

All three runs used the same harness
`.ufo/waves/round-99/w1/R99Sentinel/probe-reap-safety.py` (written by this seat). The counter runs
under `strace -f`, so every `kill(2)` it issues is recorded with its target pid — ground truth for
"was a non-owned pid signalled". The counter's stdout goes to a file (not a pipe) so a surviving
escapee holding an inherited fd cannot stall the measurement.

Harness command shape (per run; `$L` = `/home/vgpnk/Projects/shokunin/souji-shokunin`,
`$S` = `/fast/scratch/hyaku/souji-r99/R99Sentinel`):

```
python3 $L/.ufo/waves/round-99/w1/R99Sentinel/probe-reap-safety.py \
  --counter  <counter under test> \
  --probe    $L/census/round-98/c2-forgery-probe.py \
  --tool     $L/tools/souji-record-agreement.py \
  --before   $L/census/round-92/controls/c2-before-tool.py \
  --work $S/<label> --label <label> --arm-timeout 200 --deadline 500
```

Carriers planted during each run (all own-uid, all carrying the counter's **own** T1 reap token
`<counter --work>/fixture-pipe-holder.py` byte-exactly as a standalone argv element, so every one is
an argv *candidate* for the reap):

* **A — foreign-token**: plain sleeper, parent = the harness driver (an unrelated tree).
* **B — reparented-init**: sleeper whose parent exits first, so it is reparented away from any
  spawn chain. Observed `ppid_now=1525` (`systemd`), i.e. outside the counter's tree.
* **C — cross-arm**: carrier forked by a *different* arm's fixture via a wrapper that also runs the
  lane's real `tests/fixtures/r93-k4-flagfail.py` (so the arm still behaves normally). It is a
  descendant **of the counter** (the counter is `PR_SET_CHILD_SUBREAPER`) but **not** of the T1
  arm's recorded spawn pid. Observed `ppid_at_scan` = the counter pid in the r98 run.
* **E — escapee**: the counter's own T1 pipe-holder escapee (setsid grandchild of the T1 fixture),
  which carries the token by construction and is what the T1 arm exists to reap.

### 3.1 r99 counter (SUBJECT) — `census/round-99/c2-setup-arms.py`
`--work $S/r99c --label r99c`. Counter sha256 `03e8a99e2e447e4c5e7067dea191450c7d5ec10102cb33e2a246b5b3d1c02b57`.

```
ARM T1 exit=2 want=2 line=yes conform=yes survivors=0
ARMS-SUMMARY arms=20 conform=17
T1-REAP --survivors 0 planted-killed 0--
A-foreign-token pid=3141373 ppid_now=3141367 state=S verdict=SPARED
B-reparented-init pid=3141387 ppid_now=1525 state=S verdict=SPARED
C-cross-arm pid=3141425 ppid_now=1525 state=S verdict=SPARED
C-cross-arm pid=3141426 ppid_now=1525 state=S verdict=SPARED
C-cross-arm pid=3141427 ppid_now=1525 state=S verdict=SPARED
C-cross-arm pid=3151395 ppid_now=1525 state=S verdict=SPARED
C-cross-arm pid=3151420 ppid_now=1525 state=S verdict=SPARED
E-escapee pids=[3151394]
E-escapee pid=3151394 ppid_now=1525 state=S verdict=SPARED
RECAP-SAFETY-SUMMARY label=r99c counter_exit=None kills=7 foreign_killed=False escapee_killed=False escapee_pids=[3151394] carriers_c=[3141425, 3141426, 3141427, 3151395, 3151420]
RECAP-SAFETY-SUMMARY verdict=no-foreign-signal
TMPDIR-AUDIT tmpdir=/tmp/souji-r99-sentinel-tmpdir-3141367 created=False tmp_path_syscalls=0
```

`conform=17` (not 20) in all three runs is an artifact of my arm wrapper: the wrapper's forked
carrier keeps the fixture's stdout pipe open, so the P1/P2/S1 arms see a setup failure instead of
their verdict line. It is **identical across all three counters** (r99c, r98c, r97c all
`P1/P2/S1 conform=no`), so it does not bias the comparison; the T1 arm — the arm under test — is
unaffected (`conform=yes` in every run).

### 3.2 r99 counter — strace ground truth (no signal to a non-owned pid)

From `$S/r99c/strace-r99c.log`, every `kill` in the counter's tree:

```
KILL src=3141404 target=-3141415   (killpg — a process GROUP kill of the arm's own group)
KILL src=3141401 target=-3141414   (killpg)
KILL src=3141395 target=-3141416   (killpg)
KILL src=3141940 target=-3141949   (killpg)
KILL src=3151371 target=-3151384   (killpg)
KILL src=3151370 target=-3151387   (killpg)
KILL src=3151393 target=-3151403   (killpg)
```

Seven kills, **all `killpg` with a negative target** (the probe's own group kill of its fixture
group). **Zero positive-pid `kill()` calls**: the r99 counter issued no single-pid signal at all.
There is therefore no signal to any non-owned pid.

### 3.3 r98 counter (CONTROL) — `census/round-98/c2-setup-arms.py`
sha256 `0886271b4836915bdf849eeac3c1d6b341603900043fdcf061bcbd038b8af67f`. `--work $S/r98c --label r98c`.

```
ARM T1 exit=2 want=2 line=yes conform=yes survivors=0
ARMS-SUMMARY arms=20 conform=17
T1-REAP --survivors 0 planted-killed 6--
A-foreign-token pid=3141379 ppid_now=3141369 state=S verdict=SPARED
B-reparented-init pid=3141388 ppid_now=1525 state=S verdict=SPARED
C-cross-arm pid=3141428 ppid_now=None state=gone verdict=KILLED
C-cross-arm pid=3141431 ppid_now=None state=gone verdict=KILLED
C-cross-arm pid=3141433 ppid_now=None state=gone verdict=KILLED
C-cross-arm pid=3151397 ppid_now=None state=gone verdict=KILLED
C-cross-arm pid=3151409 ppid_now=None state=gone verdict=KILLED
E-escapee pid=3151391 ppid_now=None state=gone verdict=KILLED
E-escapee pid=3151398 ppid_now=None state=gone verdict=KILLED
KILL src=3141396 target=3141428 who=C-cross-arm  ppid_at_scan=3141385 argv=['/usr/bin/python3','-B','-c','import time; time.sleep(3600)','<r98c>/arms/fixture-pipe-holder.py']
KILL src=3141396 target=3141431 who=C-cross-arm  ppid_at_scan=3141385 ...
KILL src=3141396 target=3141433 who=C-cross-arm  ppid_at_scan=3141385 ...
KILL src=3141396 target=3151397 who=C-cross-arm  ppid_at_scan=3141385 ...
KILL src=3141396 target=3151398 who=E-escapee    ppid_at_scan=3141385 argv=[... '<r98c>/arms/fixture-pipe-holder.py','--tool',...]
KILL src=3141396 target=3151409 who=C-cross-arm  ppid_at_scan=3141385 ...
RECAP-SAFETY-SUMMARY label=r98c counter_exit=1 kills=12 foreign_killed=True escapee_killed=True ...
RECAP-SAFETY-SUMMARY verdict=OVERKILL
```

The r98 counter issued **six positive-pid SIGKILLs** from pid `3141396` (the r98 counter itself):
five cross-arm carriers (`who=C-cross-arm`, all with `ppid_at_scan=3141385` = the counter) and the
escapee. This is exactly R98Sentinel FINDING 4's branch (c) — a counter-descendant carrier outside
the spawn chain IS signalled by r98 — and it is the behaviour r99 removes. It also confirms my
harness can *see* an over-kill when one happens (axis 4).

### 3.4 r97 counter (POSITIVE CONTROL, argv-only) — `census/round-97/c2-setup-arms.py`
sha256 `da30593c210e…`. `--work $S/r97c --label r97c`.

```
ARM T1 exit=2 want=2 line=yes conform=yes survivors=0
ARMS-SUMMARY arms=20 conform=17
T1-REAP --survivors 0 planted-killed 3--
C-cross-arm pid=3141429 ppid_now=1525 state=S verdict=SPARED
C-cross-arm pid=3141432 ppid_now=1525 state=S verdict=SPARED
C-cross-arm pid=3141434 ppid_now=1525 state=S verdict=SPARED
C-cross-arm pid=3151396 ppid_now=None state=gone verdict=KILLED
C-cross-arm pid=3151404 ppid_now=None state=gone verdict=KILLED
E-escapee pid=3151413 ppid_now=None state=gone verdict=KILLED
KILL src=3141393 target=3151396 who=C-cross-arm ...
KILL src=3141393 target=3151404 who=C-cross-arm ...
KILL src=3141393 target=3151413 who=E-escapee   ...
RECAP-SAFETY-SUMMARY label=r97c counter_exit=None kills=10 foreign_killed=True escapee_killed=True ...
RECAP-SAFETY-SUMMARY verdict=OVERKILL
```

The r97 argv-only counter killed three token carriers (two cross-arm, the escapee). **The positive
control fires**: the instrument reports `OVERKILL` when a counter over-kills and
`no-foreign-signal` when it does not. The r99 verdict is therefore a real measurement, not a blind
pass.

### 3.5 Unit-level probe of the r99 predicate (`probe-predicate-unit.py`)

Deterministic: the counter module is copied to scratch (so importing it cannot write a `.pyc` into
the lane tree) and `_reap_owned` is exercised directly against real live processes.

```
UNIT counter=/home/.../census/round-99/c2-setup-arms.py sha256=03e8a99e2e447e4c5e7067dea191450c7d5ec10102cb33e2a246b5b3d1c02b57
UNIT spawn_pid=2994641 starttime=7546832
UNIT chain root=2994631 m=2994641 d=2994641 g=2994642 counter_desc=2994631 foreign=1525 wrong=2994631
UNIT-CASE 1-spawn-member-killed-in-isolation observed=KILLED want=KILLED OK
UNIT-CASE 2-spawn-child-killed            observed=KILLED want=KILLED OK
UNIT-CASE 3-spawn-grandchild-killed       observed=KILLED want=KILLED OK
UNIT-CASE 4-counter-descendant-spared     observed=SPARED want=SPARED OK
UNIT-CASE 5-foreign-spared                observed=SPARED want=SPARED OK
UNIT-CASE 6-wrong-token-spared            observed=SPARED want=SPARED OK
UNIT-CASE 7-compat-spawn-none-kills-nothing observed=SPARED want=SPARED OK
UNIT-CASE 8-real-call-shape-skips-spawn-pid observed=SPARED want=SPARED OK
UNIT-SUMMARY killed_real_shape=3 killed_isolated=1 killed_compat=0 cases=8 mismatches=0
UNIT-SUMMARY verdict=as-specified
```

Exit code 0. All eight predicate cases match the specification. Two facts worth the L1's attention:

* case 4 — a **counter-descendant** that is not a spawn-chain member is **spared**. That is the
  intended r99 fix (branch (c) removed) and it is correct.
* case 8 — in the counter's *real* call shape (`exclude = (counter_pid, spawn_pid)`) the recorded
  **spawn pid itself is in `exclude`**, so the "kill the recorded spawn pid itself" branch of
  `_reap_owned` is unreachable in the T1 path. Harmless in practice (the probe has already exited
  by reap time), but the code's own docstring advertises a capability the call site does not use.

---

## 4. Findings

### FINDING 1 — the r99 T1 reap is a NO-OP: it no longer reaps the escapee it exists to reap (HIGH, operability; the safety direction of C2 is satisfied but the arm's witness is vacuous)

**Severity**: HIGH for C2's operability claim (the T1 arm's binding byte no longer witnesses a
reap). Not a safety defect — the r99 counter under-kills, it does not over-kill.

**Claim text under test** (`.ufo/waves/round-99/claims.json`, C2):
> "The arms counter's T1 reap kills only the recorded spawn pid and its ppid-chain descendants
> (starttime verified); a counter-descendant carrier outside the spawn chain is not signalled
> (branch (c) removed)."

**Observed**: under r99 the T1 arm's own escapee — a setsid grandchild of the T1 fixture — is
**never killed**. The counter prints `--survivors 0 planted-killed 0--` and `ARM T1 … conform=yes`,
i.e. the arm reports success while reaping nothing.

**Mechanism** (measured, not inferred). The escapee's parent is the **counter**, not the T1 arm's
spawn pid:

* `probe-t1-mechanics.py` replays the counter's T1 arm with the escapee's ppid sampled every 50 ms:

```
T1MECH counter_sha256=03e8a99e2e447e4c5e7067dea191450c7d5ec10102cb33e2a246b5b3d1c02b57
T1MECH PR_SET_CHILD_SUBREAPER rc=0 (counter-like pid=3053159)
T1MECH spawn_pid=3053160 starttime=7614064
T1MECH probe_exit=2 stderr='C2-FORGERY-FATAL: the fixture run for the positive control exceeded --timeout 6s; its process group was killed'
T1MECH   ppid=3053159 reaches_spawn=False reaches_counter=True (t=76140.704 pid=3053163)
T1MECH last_sample=(76146.658, 3053163, 3053159, False, True)
T1MECH r99_reap_killed=0 escapee_alive_after_reap=True
T1MECH escapee_is_counter_descendant_at_last_sample=True (r98 branch (c) would kill it)
T1MECH-SUMMARY r99_killed=0 escapee_survived=True
```

  The escapee's ppid is the counter (3053159), `reaches_spawn=False`, `reaches_counter=True`.

* Live confirmation during a real r99 counter run (`repro-escapee-survivor.sh`):

```
 r99 ESCAPEE pid=3185177 ppid=3170268 state=S
$ ps -o pid,ppid,args -p 3170268
3170268 3170267 01:09 /usr/bin/python3 -B .../census/round-99/c2-setup-arms.py --probe .../c2-forgery-probe.py ...
```

  The escapee's parent (3170268) **is the r99 counter process**.

* The cause is that `PR_SET_CHILD_SUBREAPER` is **not inherited across `fork(2)`** (measured:
  `parent child_subreaper = 1` → `child_subreaper=0`). So the counter's `prctl(36, 1, …)` makes the
  *counter* the nearest living subreaper ancestor of the escapee. When the escapee's immediate
  parent (the fixture) exits, the escapee is reparented to the **counter**. From then on the
  escapee's ppid chain runs *up to* the counter and never *through* the recorded spawn pid, so
  `_is_descendant(pid, spawn_pid)` is False and the r99 predicate skips it.

**Differential (same harness, same fixtures, same carriers):**

| counter | T1 `planted-killed` | escapee fate | cross-arm carriers | verdict |
|---|---|---|---|---|
| r99 `03e8a99e…` | **0** | **SURVIVED** | 5/5 SPARED | `no-foreign-signal` |
| r98 `0886271b…` | 6 | KILLED | 5/5 **KILLED** | `OVERKILL` |
| r97 `da30593c…` | 3 | KILLED | 2/5 KILLED | `OVERKILL` |

**Why this matters for the claim.** C2's wording fixes the *upper* bound of the reap ("kills only
the recorded spawn pid and its ppid-chain descendants") and that bound is now respected — nothing
outside the spawn chain is signalled, which is what r99 was built to achieve. But the T1 arm's
purpose is to show the counter **does** reap the escapee, and it no longer does. `planted-killed 0`
with `survivors 0 conform=yes` means the arm's binding byte (`survivors==0`, enforced at
`census/round-99/c2-setup-arms.py:387-389`) is **vacuous**: it is satisfied because nothing was
counted, not because the escapee was reaped. The r98 counter's `planted-killed 6` shows the arm
used to have teeth. This is the r98 "survivors as witness" defect (R98Sentinel FINDING 5 / routed
item 4) returning in a new shape: the byte is still `0`, but it is now `0` because the reap is a
no-op.

**Reproducer** (this seat's own, uses only lane instruments read-only):
`.ufo/waves/round-99/w1/R99Sentinel/repro-escapee-survivor.sh` → writes
`$S/repro/r99/T1.out` and prints `REPRO r99 ARM T1 …`, `REPRO r99 T1-REAP --survivors 0
planted-killed 0--`, and `REPRO r99 ESCAPEE pid=… ppid=… state=S verdict=SURVIVED`.

**Pristine reproducer output** (lane's real fixtures `tests/fixtures/r93-k4-flagfail.py` /
`r92-k4-flagfail.py`, no wrapper of mine — so **both counters conform 20/20** and the difference is
attributable to the reap alone). Exit code 0:

```
REPRO-START out=/fast/scratch/hyaku/souji-r99/R99Sentinel/repro date=2026-11-09T12:04:31-03:00
--- r99: 03e8a99e2e447e4c5e7067dea191450c7d5ec10102cb33e2a246b5b3d1c02b57 .../census/round-99/c2-setup-arms.py
REPRO r99 ARM T1 exit=2 want=2 line=yes conform=yes survivors=0
REPRO r99 ARMS-SUMMARY arms=20 conform=20
REPRO r99 T1-REAP --survivors 0 planted-killed 0--
REPRO r99 ESCAPEE pid=3185177 ppid=1525 state=S verdict=SURVIVED
--- r98: 0886271b4836915bdf849eeac3c1d6b341603900043fdcf061bcbd038b8af67f .../census/round-98/c2-setup-arms.py
REPRO r98 ARM T1 exit=2 want=2 line=yes conform=yes survivors=0
REPRO r98 ARMS-SUMMARY arms=20 conform=20
REPRO r98 T1-REAP --survivors 0 planted-killed 1--
REPRO r98 ESCAPEE none-surviving
REPRO-END
```

Same fixtures, same probe, same tool/before: r99 `planted-killed 0` with the escapee **SURVIVED**;
r98 `planted-killed 1` with the escapee **gone**. Both arms report `survivors=0 conform=yes`.

**Smallest remediation** (for the L1 to freeze — a seat must not edit the predicate in place):
narrow the ownership predicate so it still reaches the arm's own escapee while staying off
foreign carriers. Two candidate shapes, both compatible with "no counter-descendant outside the
spawn chain is signalled":

* **(a) record the escapee explicitly.** The counter already observes the arm's own children. Have
  the T1 arm record the escapee's `(pid, starttime)` at the moment the fixture's parent exits (the
  counter is the subreaper, so the counter *is* notified of the reparenting), and let the reap kill
  exactly that recorded identity — same shape as the existing spawn-pid record, and it never touches
  a carrier that the counter did not observe.
* **(b) widen the walk to the counter, but only for the arm's own subtree.** The escapee's chain is
  `escapee → counter`; it is distinguishable from a *foreign* counter-descendant by the fact that it
  is a descendant of the counter **and** was reparented there from the arm's own fixture. If the
  counter records the arm's fixture pid at spawn, the escapee is exactly the pid whose ppid chain
  reaches the counter *and* which was orphaned from that fixture.

Option (a) is the smaller change and is the one the r98 routing already pointed at ("record
escapee pid+starttime at counter-child observation").

**Also worth the L1's attention**: the r99 file's own comment at
`census/round-99/c2-setup-arms.py:355-358` already says the escapee's chain "may no longer reach
the spawn pid (open limit, reported with observed evidence); it is then NOT killed". The lane is
aware of the gap; my contribution is the measured evidence and the exact parent identity.

### FINDING 2 — the r99 counter leaks the escapee as a live process (MEDIUM, operability)

Under r99 the escapee survives the counter's own exit. Observed: `r99 ESCAPEE pid=3185177
ppid=3170268 state=S` **while the counter is still running**, and in the r99c run
`E-escapee pid=3151394 ppid_now=1525 state=S verdict=SPARED` **after** the counter exited (reparented
to `systemd`, 1525). The escapee is a `time.sleep(3600)` holder of the fixture's pipes; it survives
the arm by up to an hour and holds the pipe fds.

This is the same defect seen from the resource side, and it is why the counter's own stdout pipe can
stay open after the counter exits — a real hazard for any driver that reads the counter's stdout
with `subprocess.PIPE` and waits for EOF (my first harness revision hung exactly this way before I
redirected the counter's stdout to a file).

**Reproducer**: same script as FINDING 1; the surviving pid is printed.

**Smallest remediation**: the same as FINDING 1 (a) — if the reap reaches the escapee, it does not
leak.

### FINDING 3 — the compat path `_reap_by_identity` is dead but still advertised as a kill-all (LOW, correctness of the surface)

`census/round-99/c2-setup-arms.py:156-161` keeps `_reap_by_identity`, whose docstring still says
"SIGKILL every own-uid process whose argv contains `<ident>` byte-exactly … argv identity is the
counter-owned reaping key (A4)". Its body is now `return _reap_owned(ident, exclude, None)`, and
`_reap_owned` with `spawn=None` takes the compat branch that `continue`s — it kills **nothing**
(unit case 7: `killed_compat=0`). The docstring therefore describes a kill-all that the function no
longer performs.

Nothing calls it in the lane today (grep across `souji-shokunin` finds only the definition and the
r97/r98 copies), so this is a documentation-accuracy defect, not a live hazard. It matters because
a future caller reading the docstring would believe argv alone authorises a kill — the exact
confusion that produced the r97 defect (A12/Q174).

**Smallest remediation**: delete the function and its docstring (clean cutover — no callers), or
rewrite the docstring to say "kills nothing; retained only so an external caller cannot trigger an
argv-only kill".

### FINDING 4 — the `/tmp` guard accepts the bare directory `/tmp` (LOW, carried from r97; NOT a r99 regression)

`census/round-99/c2-setup-arms.py:231` rejects `--work` only when `realpath(work)` **starts with**
`("/tmp/", "/var/tmp/", "/dev/shm/")`. The bare path `/tmp` (and `/var/tmp`, `/dev/shm`) does not
match, so it is accepted by the guard. Measured:

```
'/tmp'          -> ACCEPTED
'/tmp/x'        -> REJECTED
'/var/tmp'      -> ACCEPTED
'/dev/shm'      -> ACCEPTED
'/tmpfoo'       -> ACCEPTED
'/tmp/../tmp2'  -> ACCEPTED
```

This is R98Sentinel FINDING 3 from r97, carried (r98 spot-check routed item 5: "fix or record as
known limit"), **not introduced by r99** — r99's line is byte-identical to r98's. It is reported
here for completeness and because the L1 must either fix or record it.

Mitigation observed in practice: the counter then refuses the directory as non-empty
(`C2-ARMS-FATAL: --work … is not an empty directory`) for a busy `/tmp`, and the *probe* carries the
same prefix-only guard (`census/round-98/c2-forgery-probe.py:184`), as does the r99 C1 hook
(`census/round-99/c1-survivor-search.py:436`). So the exposure is "the guard is not the thing that
stops you", not "the counter writes into `/tmp`".

**Smallest remediation**: use a path-component test (`os.path.realpath(work)` compared component-wise
against `("/tmp", "/var/tmp", "/dev/shm")`) in all three guards.

### FINDING 5 (non-defect, recorded so the L1 does not re-litigate it) — no `/tmp` write under any `TMPDIR`

The seat target asks explicitly that "no counter writes under `/tmp` regardless of `TMPDIR`". This
holds, and it holds for a structural reason, not by luck:

* No `tempfile` / `mkstemp` / `mkdtemp` / `NamedTemporaryFile` / `gettempdir` anywhere in
  `census/round-99/c2-setup-arms.py`, `census/round-98/c2-forgery-probe.py`,
  `census/round-99/c1-survivor-search.py` or `census/round-99/c2-decoy-test.py` (grep: no hits).
  So `TMPDIR` has no code path to influence.
* Measured: with `TMPDIR`/`TMP`/`TEMP` pointed at a **non-existent** `/tmp/souji-r99-sentinel-tmpdir-<pid>`,
  the directory was **never created** and the strace log contains **zero** `/tmp` path syscalls, in
  all three runs (`TMPDIR-AUDIT … created=False tmp_path_syscalls=0`).
* The counter's only scratch is under `--work`; the r99 search hook's scratch is under its
  `--work`/`--emit`, both prefix-guarded.

`--work` was always outside `/tmp` in every run I made (`/fast/scratch/hyaku/souji-r99/R99Sentinel/…`).

---

## 5. Things I did NOT do (scope discipline)

* I did not edit any `census/round-98/**` or `census/round-99/**` file. My instruments live under
  `.ufo/waves/round-99/w1/R99Sentinel/` and copy the counter into scratch before importing it.
* I did not commit, push, or touch git/jj state.
* I did not write to `MANIFEST.json`, `.ufo/state/*`, `.ufo/watchdog.log`, or any fleet-root tracked
  file. `git status --porcelain` in the lane shows only `?? census/round-99/` (other seats' work) —
  my wave-dir files are under `.ufo/waves/round-99/w1/R99Sentinel/`.
* I did not read or touch `/home/vgpnk/Projects/shokunin/considerthese` or `…/shokuknow`.
* I did not mutate any sysctl and did not install any tool.

---

## 6. Reproducers (paths)

All under this seat's own wave dir:

| path | what it does |
|---|---|
| `.ufo/waves/round-99/w1/R99Sentinel/probe-reap-safety.py` | the end-to-end safety probe (3 foreign carrier classes + strace ground truth + TMPDIR audit). Run against r99 / r98 / r97. |
| `.ufo/waves/round-99/w1/R99Sentinel/probe-predicate-unit.py` | deterministic unit-level probe of `_reap_owned` (8 cases). Exit 0, `verdict=as-specified`. |
| `.ufo/waves/round-99/w1/R99Sentinel/probe-t1-mechanics.py` | replays the counter's T1 arm with the escapee's ppid sampled every 50 ms → shows `ppid=counter, reaches_spawn=False`. |
| `.ufo/waves/round-99/w1/R99Sentinel/probe-reparent-mechanism.py` | isolates the subreaper reparenting (`PR_SET_CHILD_SUBREAPER` not inherited across fork). |
| `.ufo/waves/round-99/w1/R99Sentinel/repro-escapee-survivor.sh` | standalone reproducer for FINDING 1/2 (runs the r99 and r98 counters with the lane's real fixtures and prints the escapee's fate). |

Raw run outputs preserved under this seat's own wave dir (my scratch is deleted at yield, per the
seat contract):

| path | content |
|---|---|
| `.ufo/waves/round-99/w1/R99Sentinel/evidence/{r99c,r98c,r97c}.verdicts.out` | the full verdict lines of the three harness runs (A/B/C/E verdicts, KILL lines, TMPDIR audit) |
| `.ufo/waves/round-99/w1/R99Sentinel/evidence/{r99c,r98c,r97c}.summary.json` | machine-readable summary (kills with attribution, `foreign_killed`, `escapee_killed`, `t1_tail`, `tmpdir_created`) |
| `.ufo/waves/round-99/w1/R99Sentinel/evidence/{r99c,r98c,r97c}.strace-kills.txt` | every `kill(` line from each run's strace log (the signal ground truth) |
| `.ufo/waves/round-99/w1/R99Sentinel/evidence/unit.out` | the 8-case unit probe of `_reap_owned` |
| `.ufo/waves/round-99/w1/R99Sentinel/evidence/t1mech.out` | the T1-arm mechanics replay (escapee ppid = counter, `reaches_spawn=False`) |
| `.ufo/waves/round-99/w1/R99Sentinel/evidence/mech.out` | the subreaper-reparenting isolation (`child_subreaper=0` across fork) |
| `.ufo/waves/round-99/w1/R99Sentinel/evidence/repro-escapee-survivor.out` | the pristine reproducer output (r99 vs r98, real lane fixtures, both conform=20) |

---

## 7. What I hand to the L1

1. **C2's safety direction is verified** (no signal to any non-owned pid; zero positive-pid kills
   under strace; foreign, reparented and cross-arm carriers all spared; r98 and r97 controls
   over-kill with the same harness, so the measurement has discriminating power).
2. **C2's operability leg is not verified as written.** The r99 T1 reap kills nothing
   (`planted-killed 0`); the escapee it exists to reap survives, and the arm's `survivors==0` binding
   byte is therefore vacuous. The claim sentence must either (i) name that the T1 reap no longer
   reaches the escapee and say what now witnesses the reap, or (ii) the reap must be narrowed so it
   still reaches the arm's own escapee (FINDING 1 remediation (a): record the escapee
   pid+starttime at counter-child observation) without touching foreign carriers.
3. The r99 file's own comment already records the gap as an "open limit"; the frozen predicate
   should either close it or name it.
4. FINDING 3 (dead compat path with a live-sounding docstring) and FINDING 4 (prefix-only `/tmp`
   guard, carried from r97) are small and can be dispositioned with a line each.

**Grade I would record for C2**: *safety direction satisfied and measured; operability direction
claimed but not witnessed* — i.e. **measured, not admitted**, the same disposition the lane gave C2
in r98, for a different reason.
