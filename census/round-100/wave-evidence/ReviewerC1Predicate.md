# ReviewerC1Predicate — correctness review of the C1 session-ownership predicate (r100)

Seat: ReviewerC1Predicate (Godspeed subagent). Accuracy via committed-byte reads (no live
r100 counter run required by the brief); attacks carried as committed-byte reproducers
under `.ufo/waves/round-100/w1/ReviewerC1Predicate/`.

## Files/lines cited (committed bytes at lane base)

- `plans/round-100.md:9-23` — frozen C1 predicate (session-owned escapee reap).
- `census/round-99/c2-setup-arms.py:333-334` — `one()` spawns the arm probe with
  `start_new_session=True`, so the recorded spawn pid *is* its own session leader
  (`session field 6 == spawn pid`, verified live in attack_a).
- `census/round-99/c2-setup-arms.py:82-90` — PIPHOLDER: fork + `os.setsid()` → the T1
  escapee leads its OWN new session (`session field 6 == escapee pid`, S368).
- `census/round-99/c2-setup-arms.py:164-200` — `_reap_owned` (r99 spawn-chain-only),
  incl. the spawn-pid starttime check at `:184-186`.
- `census/round-99/c2-decoy-test.py:100-105` — decoy planted with
  `start_new_session=True` (own session, session == decoy pid).
- `census/round-98/c2-setup-arms.py:189` — the removed r98 branch (c)
  `elif _is_descendant(pid, os.getpid())` (subreaper net). The frozen r100 predicate is
  a *candidate replacement key* for exactly this branch, per
  `corpus/lessons/round-99-verifier-spotcheck.md:93-95` (routed defect 1).
- PIPHOLDER and the spawn recording are byte-identical between r98 and r99
  (`census/round-98/c2-setup-arms.py:330-334` vs r99 `census/round-99/c2-setup-arms.py:330-334`).

## Method

Godspeed axes: (1) the predicate must *discriminate* the escapee from the decoy;
(2) it must not *over-kill* (decoy spare); (3) it must not *under-kill* (escapee alive=0);
(4) the identity guard must be *sound* (pid-reuse). Each attack is a committed-byte
reproducer script; no kill runs on any process the counter did not plant in this fixture
(L0 reap authority, `plans/round-100.md:87-89` — the reproducers plant their own sleepers
and kill only them).

Commands run (cwd `/fast/scratch/hyaku/souji-r100/ReviewerC1Predicate`, exit codes observed):

| command | exit | observed summary |
|---|---|---|
| `python3 .ufo/waves/round-100/w1/ReviewerC1Predicate/attack_a_same_session.py` | 0 | escapee session ≠ spawn session (False); same-session decoy session == counter sid (True), decoy ≠ spawn (False); verdict block printed (numbers below) |
| `python3 .ufo/waves/round-100/w1/ReviewerC1Predicate/attack_b_fork_from_spawn.py` | 0 | forked decoy session == spawn session (True); verdict printed |
| `python3 .ufo/waves/round-100/w1/ReviewerC1Predicate/attack_c_tick_collision.py` | 0 | 8 back-to-back procs, `distinct starttimes = 1 of 8`, HZ=100 |

## Attack (a) — same session as the counter: field 6 does NOT distinguish

**Answer: No — the session key cannot separate the escapee from a decoy that shares the
counter's session.** Geometry (measured, attack_a output):

```
counter pid=3310524 sid=3310524
spawn/probe pid=3310525 ppid=3310524 pgrp=3310525 session=3310525 starttime=7830211
  recorded spawn session (field 6) = 3310525 (== probe pid? True)
fixture pid=3310649 ppid=3310524 pgrp=3310524 session=3310524 starttime=7830241
escapee pid=3310656 ppid=3310649 pgrp=3310656 session=3310656 starttime=7830242
  escapee session == spawn session? False
same-session decoy pid=3310981 ppid=3310524 pgrp=3310524 session=3310524 starttime=7830302
  decoy session == counter session? True
  decoy session == spawn session? False
SESSION-EQUALITY VERDICT (frozen predicate, plans/round-100.md:12-15):
  escapee owned by branch (b) iff escapee_session == spawn_session: False
  decoy owned by branch (b) iff decoy_session == spawn_session: False
  if spawn session were counter sid (3310524): escapee owned=False, decoy owned=True
```

Three consequences, in escalating order:

1. **Under the as-written freeze** (`plans/round-100.md:10-15`: "its session id equals the
   spawn pid's recorded session id"), the recorded spawn session is the probe's session,
   and the probe's session *is the probe pid* (`one()` uses `start_new_session=True`,
   `census/round-99/c2-setup-arms.py:333-334`; measured `session==pid? True`). The setsid
   escapee's session is the escapee pid (PIPHOLDER, `:82-90`; measured
   `session==own-pid? True`), so `escapee_session == spawn_session` is **False**: branch (b)
   kills nobody. The frozen predicate as a *code* rule leaves alive=1, i.e. it degenerates
   to the r99 do-nothing. **The session-key branch misses the escapee it exists to reap.**
2. If instead the implementation records the **counter's** session (the only assignment
   under which attack_a's same-session decoy is "owned"), then the decoy is owned and the
   escapee is not (`escapee=False, decoy=True` above): it discriminates **backwards**.
3. For any *same-session* foreign decoy — one planted in the session the counter runs in —
   field 6 takes the same value as every other process in that session, including the
   counter's own arms, so no field-6 equality test can separate it from same-session
   processes. Session granularity is *too coarse within a session and misaligned across
   sessions*: every `setsid` carrier leads a fresh session and hence fails the match by
   construction.

**Frozen predicate survives (a)? No.** Under its own definitions, `ESCAPEE-ALIVE alive=0`
(plan `:17-19`) is unreachable via branch (b) (the escapee never matches), and the
decoy `verdict=spared` leg is reachable only because the shipped decoy test
(`census/round-99/c2-decoy-test.py:100-105`) plants decoys with `start_new_session=True` —
a decoy that already has a fresh session. A same-session decoy (no `start_new_session`)
shares the counter sid and breaks the assumption the decoy test bakes in. The predicate's
discrimination is therefore *planting-dependent*, not source-dependent.

Reproducer: `.ufo/waves/round-100/w1/ReviewerC1Predicate/attack_a_same_session.py`
(exit 0, output above).

## Attack (b) — fork-from-spawn decoy: killed as if owned

**Answer: Yes — a decoy that forks (no `setsid`) from the spawn pid inherits the spawn
session and is owned/killed by branch (b) iff it carries the token.** Measured (attack_b):

```
spawn/probe pid=3312063 session=3312063 starttime=7830618
forked decoy pid=3312064 ppid=3312063 pgrp=3312063 session=3312063 starttime=7830618
  decoy session == spawn session? True
```

This is the exact mirror of (a): the escapee *fails* the session match (it `setsid`'d
away), while a non-`setsid` fork *passes* it. Branch (b) is thus an **inverted discriminator**
for the two named cases: it spares the target and hits the forked decoy. The plan's rescue
clause at `plans/round-100.md:14-15` ("AND it is NOT a foreign decoy (its own driver/session
differs)") cannot rescue this case, because by construction the forked decoy's
driver/session does *not* differ — it is local by every field-6 definition. The clause is
circular: locality is what the key was supposed to *establish*, and here it certifies the
decoy as local. No other `/proc/<pid>/stat` field in the argv-selected candidate set
differs either (same pgrp, same session, same starttime tick in this run). Note the shipped
decoy test never plants this shape, so predicate (1) (`verdict=spared` 83/83, plan `:18-19`)
would pass on the shipped instrument while the forked-decoy class is over-killed.

Note also, for the record, that r98 branch (c) (`census/round-98/c2-setup-arms.py:189`,
`_is_descendant(pid, os.getpid())` with the `PR_SET_CHILD_SUBREAPER` net,
`census/round-99/c2-setup-arms.py:203-218`) is what the session key was supposed to replace:
there, ownership was the *counter's* descendancy, which the orphaned escapee reached by
reparenting and a foreign decoy could not reach at all. Session is strictly weaker (every
process in a session shares it).

**Frozen predicate survives (b)? No** — it over-kills the forked decoy and, per (a), still
misses the escapee.

Reproducer: `.ufo/waves/round-100/w1/ReviewerC1Predicate/attack_b_fork_from_spawn.py`
(exit 0, output above).

## Attack (c) — `starttime >= spawn` guard and pid reuse

**Answer: The guard is unsound against same-tick pid reuse; the starttime is a 10 ms
tick, not an identity.** Measured (attack_c):

```
spawned 8 processes back-to-back; (pid, starttime):
  pid=3312180 starttime=7830720 ... pid=3312188 starttime=7830720
distinct starttimes = 1 of 8
SC_CLK_TCK (HZ) = 100 -> one tick = 10 ms
```

- `starttime >= spawn` passes for *every* process spawned in the same tick (and later).
  It certifies only "not older than", i.e. it is a *monotonicity* guard, not a
  same-process guard. A pid-recycle landing in the shared tick satisfies it.
- Even the strict r99 form, `st[1] != spawn_st: continue`
  (`census/round-99/c2-setup-arms.py:185`), is passed by a same-tick recycled pid:
  the recycled process carries the *same tick count* as the original (all 8 above do).
  So the starttime check cannot bind a pid to its original occupant within a tick.
- The plan's own words acknowledge the value is ticks-since-boot ("field 22 is starttime
  in clock ticks", `corpus/SOURCES.md` S075 row, `corpus/SOURCES.md:110`); HZ=100 gives a
  10 ms quantum, and the arm spawns an entire fleet of procs per tick under `--jobs 4`
  (`census/round-99/c2-setup-arms.py:227, 381`).

Practical impact in this fixture is bounded (the reaper acts within one arm-timeout window
and these counters spawn few processes), but the guard is unsound *as an identity claim*:
a `starttime >= spawn` test must not be cited as "starttime-verified" identity
(`plans/round-100.md:12-13`), and the `m_noppid` negative control (plan `:22-23`) —
"session key removed must FAIL alive=0" — is only meaningful if the remaining spawn-pid
branch is itself sound; here branch (a) plus the `>=` guard inherits the same tick
collision.

**Frozen predicate survives (c)? Not as an identity argument.** `>=` is sound only as a
"not predated" sanity filter, and even `==` cannot name the original pid-holder inside a
tick. Recommend: state the guard as liveness-window bound, not identity; if identity is
required, the session key is the wrong tool and the ppid chain + subreaper net
(r98 `:189`, `:203-218`) remains the only demonstrated discriminator in-lineage.

Reproducer: `.ufo/waves/round-100/w1/ReviewerC1Predicate/attack_c_tick_collision.py`
(exit 0, output above).

## Cross-cutting findings

1. **The frozen target triple is internally inconsistent on committed bytes.** With the
   probe spawned `start_new_session=True` (`c2-setup-arms.py:333-334`), the escapee's
   session is its own pid and *never* equals the spawn session, so leg (1)
   (`ESCAPEE-ALIVE alive=0`, `plans/round-100.md:17-19`) cannot be reached by branch (b).
   The only escapee-owning branch left is branch (a) — pid == spawn pid — which the r99
   escapee already fails (`census/round-99/records/c2-escapee-r99.txt`: `alive=1`), and
   would be restored only by reverting to the r98 subreaper net, which the plan does not
   mention. The precedent the spot-check routed
   (`corpus/lessons/round-99-verifier-spotcheck.md:95`: "an ownership key that is not the
   ppid chain (candidate: fixture session id recorded at spawn, starttime-verified)") is
   *necessary but not the blocker* — the blocker is that the recorded session cannot be
   the escapee's. (Note: recording the *fixture parent's* session also fails — the
   escapee `setsid`'s away from it too; attack_a prints `session==fixture? False`.)
2. **`m_noppid` and CM8 controls weaken under (a)–(c).** If branch (b) never fires on the
   escapee, removing it (`m_noppid`) cannot make `alive=0` fail — the experiment stays
   vacuous under the session key, exactly the failure the spot-check's Q175 note
   (`plans/round-100.md:27-31`, "otherwise predicate (1) is vacuous") was written to catch.
   The CM8 argv-only control still kills the shipped (new-session) decoy, so *that* leg
   remains non-vacuous; the escapee leg is the vacuous one.
3. **The shipped decoy test certifies the wrong decoy shape.** `census/round-99/c2-decoy-test.py:100-105`
   plants only fresh-session decoys (S368, `start_new_session=True`). The same-session and
   fork-from-spawn classes that defeat the predicate are never planted, so `verdict=spared`
   cannot falsify branch (b). Predicate (1)'s decoy leg must add a same-session / forked
   decoy control, or the claim is circular in the same way I-A99 showed for the C1
   unpinned runner (`corpus/lessons/round-99-verifier-spotcheck.md:45`).
4. **C2 (calibration, S332 attribution) is out of scope for this seat** — no claim made.
   For file:line completeness the stale-attribution sites are `census/round-99/c2-setup-arms.py:96`
   (docstring "fields 4 and 22, S075"), `:128` (`(S075)` on the ppid walk), and `:330`
   (`(S075)` on the spawn recording); the S332 correction is ExecutorC2Attribution's seat.

## Summary verdict

| attack | frozen predicate survives? |
|---|---|
| (a) same-session decoy vs escapee | **No** — branch (b) matches neither under the probe session, and matches the *decoy* under the counter session; the escapee never matches. |
| (b) fork-from-spawn decoy | **No** — decoy inherits spawn session → owned/killed; the `NOT a foreign decoy` clause is circular. |
| (c) `starttime >= spawn` vs pid reuse | **No** as identity (10 ms tick; 8/8 collision). Sound only as a not-predated sanity bound. |

Net: as frozen (`plans/round-100.md:9-23`), the session key does not discriminate the T1
escapee from a foreign decoy — it misses both when the recorded session is the probe's
(escapee reaches `alive=1`, the r99 do-nothing), and inverts (kills the same-session/forked
decoy, spares the escapee) under any other assignment. **Do not freeze branch (b) as an
ownership rule on this wording**; the L1 should either (i) re-admit the r98 counter-child
net (which is the only mechanism in-lineage that reaches the orphaned escapee:
`census/round-98/c2-setup-arms.py:189` + `:206-211`) with the session as an additional
*persistence/note* field, or (ii) re-scope the claim to "the session key is recorded and
measured" without the alive=0 leg. Either way, add the same-session and fork-from-spawn
decoy controls to `census/round-100/c2-decoy-test.py` before freezing, or the decree is
unfalsifiable on its own instrument.

## Evidence trail

- Reproducers (exit 0 each, outputs quoted verbatim above):
  - `.ufo/waves/round-100/w1/ReviewerC1Predicate/attack_a_same_session.py`
  - `.ufo/waves/round-100/w1/ReviewerC1Predicate/attack_b_fork_from_spawn.py`
  - `.ufo/waves/round-100/w1/ReviewerC1Predicate/attack_c_tick_collision.py`
- Committed-byte anchors: `plans/round-100.md:9-23`,
  `census/round-99/c2-setup-arms.py:82-90,164-200,333-334`,
  `census/round-99/c2-decoy-test.py:100-105`,
  `census/round-98/c2-setup-arms.py:189,206-221`,
  `census/round-99/records/c2-escapee-r99.txt`,
  `corpus/lessons/round-99-verifier-spotcheck.md:93-95`.
- No live run of the r100 counter (per brief, read-only review), no new kills beyond the
  reproducers' own self-planted sleepers (all killed by the scripts themselves),
  no git/jj mutation, no pacman (no tool install was needed).
- Tooling: none installed. `SC_CLK_TCK = 100` on this host (measured by attack_c).
