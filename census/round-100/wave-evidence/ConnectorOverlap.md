# ConnectorOverlap — souji r100 w1 — sibling-overlap + planning data-walk

Seat: ConnectorOverlap (connector). Lane `souji-shokunin`, lane base `a662bb0d7e033cc5ceccd70b52eb234404300845`.
Leaf seat: no subagent dispatch, no commit, no git/jj mutation, no fleet-root or sibling-lane write.
Scratch `/fast/scratch/hyaku/souji-r100/ConnectorOverlap/` (deleted before yield).
Tools installed: none (no pacman/uv/npx transaction was run; `python3 -B`, `grep`, `sed`, `sha256sum` as shipped).

Pinned subjects at measurement time (`2026-11-09T12:26:16-03:00`):

```
sha256sum census/round-100/c2-setup-arms.py census/round-100/c2-decoy-test.py
f71b2155cb9f68cd75d5f56c9a50a0b941f4ed7b26aece7489486e8bed777abe  census/round-100/c2-setup-arms.py
9d06e806daf15b34c1c2b4e546cd9262e45e1d7c6921fd029ae2ef7b461b79cc  census/round-100/c2-decoy-test.py
```

`census/round-100/c2-setup-arms.py` is owned by seat `ExecC1SessionApplier` and was in flux during this walk
(`e289da60` → `4c0f11c0` → `3ff410be` → `f71b2155` inside six minutes). The predicate substance cited below
(`:202` session leg, `:349` spawn record) is identical at `4c0f11c0`, `3ff410be` and `f71b2155`; line numbers are
pinned to `f71b2155`. Do not measure a moving hash: re-pin after the file settles.

---

## Q(a) — does any lane/lesson already claim the session-owned escapee reap (field 6) or the S075/S332 repair?

### Exact command (reproducer `.ufo/waves/round-100/w1/ConnectorOverlap/null-sweep.sh`, output `…/null-sweep.txt`)

```
bash .ufo/waves/round-100/w1/ConnectorOverlap/null-sweep.sh > …/ConnectorOverlap/null-sweep.txt 2>&1
SCRIPT_EXIT=0
```

Targets: `PROVINCE.md`, `corpus/README.md`, `corpus/lessons/round-96.md` … `round-99.md`, plus the routed-defect
source `corpus/lessons/round-99-verifier-spotcheck.md`.

### (a1) session-owned escapee reap — **NULL in the four scan targets; prior art exists in one knowledge entry**

Hit counts (`grep -cE 'session id|session-id|session_id|field 6|field-6|escapee|setsid'`):

| file | hits | what the hits are |
|---|---|---|
| `PROVINCE.md` | **0** | no session/reap wording at all; `grep -nE 'reap|ppid|signall|residue|session|own uid' PROVINCE.md` returns only F5 heritage lines `:79`, `:107`, `:170-190`, `:205`, `:337` (list-only, reap HELD) |
| `corpus/README.md` | 2 | `:1049` quarantine front kills **its worker's whole session** by `/proc/<pid>/stat` field 6 (S075), r80; `:1060` vault tool descendant freeze (no field 6). **No `escapee` hit in README.** Frontier/reap rows `:247`, `:274`, `:281` still say F5 reap is operator-held |
| `corpus/lessons/round-96.md` | 3 | S368/S371 source rows (`:22`, `:25`), T1 grandchild seam (`:58`) |
| `corpus/lessons/round-97.md` | 1 | `:25` S368 carried |
| `corpus/lessons/round-98.md` | 4 | S368 re-verified (`:37`), connector limits C-3/C-5 (`:106`, `:147`, `:149`) |
| `corpus/lessons/round-99.md` | 20 | defect/routing text only; the closest line is `:69` — “Fix (routed r100, **not shown able to fail yet**): an escapee ownership key that is not the ppid chain” |

**Verdict (a1): no file in the four scan targets claims the session-owned escapee reap.** The mechanism *is*
already an in-lane claim for a different instrument: `corpus/knowledge/gate-signal-handling.md:71-73` — the r80
quarantine front “scans `/proc/*/stat` for field 6, the session id (S075, which supersedes S068) … SIGSTOPs every
member … and SIGKILLs them”, measured `15 rows, 0 mismatches, 0 orphans` (r80 receipt `census/round-80/records/c2-after.txt`),
duplicated in `corpus/README.md:1049`. The r100 C2/C1 wording must not present session-based ownership as new
ground; the novelty is the arms counter's ownership key, not “session kill”.

### (a2) S075/S332 attribution repair — **already stated in two lessons; the entry body still carries the stale line**

| file:line | content (measured) |
|---|---|
| `corpus/lessons/round-98.md:40-41` | “S075's scope is fields 5/6/22 in the registry; the field-4 ppid wording is the kernel-side attribution (S332); the plan's ‘ppid field 4’ attribution to S075 is corrected here … No row added this round; no row's status, recheck or used-by cell changed.” |
| `corpus/lessons/round-99.md:43` | repeats it: “Field (4) ppid quote … (S332 is the kernel emission order)” |
| `corpus/knowledge/deadline-owned-reaping.md:65` | body, unchanged at HEAD and in the tree: “The reap is now by ownership (**S075 field 4/22**, S368)” — the sentence the r100 correction block withdraws |
| `corpus/knowledge/deadline-owned-reaping.md:78-81` | working-tree append-only block “## Round-100 correction (append-only; S075 field-4 attribution withdrawn)” citing S332 — **uncommitted, peer seat `ExecC2Attribution`** |
| `corpus/SOURCES.md:110` | S075 used-by at HEAD ends `…gate-signal-handling.md` (no `deadline-owned-reaping.md`); the working tree adds it (`git diff -U0 corpus/SOURCES.md` = one line, `+corpus/knowledge/deadline-owned-reaping.md`) — also peer `ExecC2Attribution`, uncommitted |

`git status --porcelain` at this seat's start: ` M corpus/SOURCES.md`, ` M corpus/knowledge/deadline-owned-reaping.md`,
`?? census/round-100/`. **The C2 repair is already in flight in the shared working tree** — a second seat writing
either file would collide; the L1 must land it through `ExecC2Attribution`'s bytes only.

**Verdict (a2): the correction is already claimed in lessons 98/99; C2's work is landing it in the entry + S075
`used-by`, not discovering it.** No new SOURCES row is needed and none is present in the working-tree diff.

---

## Q(b) — which r99 Sentinel FINDINGS 2–5 the r100 rule touches, which it leaves open

Sentinel source: `.ufo/waves/round-99/w1/R99Sentinel.md` §4 (F1 `:222`, F2 `:342`, F3 `:360`, F4 `:378`, F5 `:406`).
Routed carry: `corpus/lessons/round-99-verifier-spotcheck.md:97` (F2/F3/F4 named; F5 is the non-defect).

| finding | r100 rule touches it? | measured state at counter `f71b2155` |
|---|---|---|
| **F2** — escapee leaks a live process holding the fixture pipes after counter exit | **Touched in intent, NOT closed by the executed key** | the rule's branch (b) is the only leg that could reach the escapee; it is inert (see F-CONN-1). `_reap_owned` `:175-210` kills only `pid == spawn_pid` or `sid == spawn_sid`. The escapee's sid is its own pid — `repro-session-key.py` → `ESCAPEE pid=3397914 … sid=3397914`, `KEY … sid==spawn_sid:False`. Reap fires 0 → leak unchanged |
| **F3** — `_reap_by_identity` dead with a stale “SIGKILL every … argv” docstring | **NOT touched** | still present at `:167-173`; it delegates `_reap_owned(ident, exclude, None)`, whose compat branch `continue`s (`:205-208`), so it kills nothing while its docstring still advertises an argv kill. No caller in-lane |
| **F4** — `/tmp` guard is prefix-only (bare `/tmp` accepted, r97 carry) | **NOT touched** | `:245` `if os.path.realpath(work).startswith(("/tmp/", "/var/tmp/", "/dev/shm/"))`; measured `python3 -B -c` (same expression) → `'/tmp' ACCEPTED`, `'/tmp/x' REJECTED`, `'/var/tmp' ACCEPTED`, `'/dev/shm' ACCEPTED`, `'/tmpfoo' ACCEPTED` |
| **F5** — non-defect: no `/tmp` write under any `TMPDIR` | **Untouched / no action owed** | `grep -cE 'tempfile\|mkstemp\|mkdtemp\|NamedTemporaryFile\|gettempdir'` = `0` in `census/round-100/c2-setup-arms.py` and `0` in `census/round-100/c2-decoy-test.py`; no `TMPDIR` code path |

Sentinel **F1** (the escapee no-op) is not in the carry list but is the r100 target; it remains open in the
executed key (F-CONN-1).

---

## Q(c) — lowest owned axis and the saturation line (planner data-walk)

```
grep -n '^| coverage\|^| calibration\|^| operability' SCORECARD.md
13:| coverage | 8 | …
14:| calibration | 7 | …
15:| operability | 8 | …

sed -n '428,434p' SCORECARD.md
428:## Saturation / stagnation
430:Saturation line: 8 per axis; stagnation window 3 rounds. Scores per the
431:rows above: coverage 8, operability 8, calibration 7 (this prose formerly
432:said 6/7 — corrected r9 after the judges caught the drift).
```

- **Lowest owned axis: `calibration` = 7** (`SCORECARD.md:14`), two points under the saturation line.
- **Saturation line: 8 per axis, stagnation window 3 rounds** (`SCORECARD.md:430-431`).
- Consequence for r100: C1 is targeted at `operability` (already 8) and C2 at `calibration` (7). A C1-only round
  raises no score; the axis that can move toward the line is `calibration`, and it only moves by a
  **witness that can fail** — which is exactly what F-CONN-1 says the frozen C1 leg is not.

---

## Findings

### F-CONN-1 (HIGH, operability) — the frozen session key is on the wrong side of S368: branch (b) cannot own the T1 escapee

`census/round-100/c2-setup-arms.py:349` records `spawn = (p.pid, _proc_starttime(p.pid), _proc_sid(p.pid))` for the
**probe** (spawned with `start_new_session=True`, `:348`), so `spawn_sid == probe pid`. `:202` owns a candidate iff
`sid(candidate) == spawn_sid`. The T1 chain re-sessions at *every* hop below the probe:
`census/round-98/c2-forgery-probe.py:147` spawns the fixture with `start_new_session=True` (fixture sid = fixture pid),
and the fixture's child calls `os.setsid()` (`census/round-100/c2-setup-arms.py:85`, `PIPHOLDER`), so the escapee's
sid is **its own pid**. Neither is ever `spawn_sid`.

Measured (`python3 -B .ufo/waves/round-100/w1/ConnectorOverlap/repro-session-key.py /fast/scratch/.../sk5`, EXIT 0,
output `…/ConnectorOverlap/session-key.txt`):

```
COUNTER pid=3397885 sid=3397885
SPAWN   pid=3397888 ppid=3397885 pgrp=3397888 sid=3397888 starttime=7850600
PROBE    pid=3397888 ppid=3397885 pgrp=3397888 sid=3397888 starttime=7850600
FIXTURE  pid=3397894 ppid=3397888 pgrp=3397894 sid=3397894 starttime=7850601
ESCAPEE  pid=3397914 ppid=3397894 pgrp=3397914 sid=3397914 starttime=7850601
KEY pid=3397894 spawn_sid=3397888 sid==spawn_sid:False sid==own_pid:True sid==spawn_pid:False
KEY pid=3397914 spawn_sid=3397888 sid==spawn_sid:False sid==own_pid:True sid==spawn_pid:False
```

Second-order effects (all measurable consequences of the same line):
1. `ESCAPEE-ALIVE alive=0` is **unreachable**: nothing but the (excluded) probe is ever in the probe's session.
2. The **m_noppid mutant becomes behaviourally identical to its parent** — both reap 0 — so “m_noppid FAILs alive=0”
   cannot discriminate. A mutant test that cannot fail is not a mutant test.
3. The survivors byte is vacuous again: `:385-392` applies the *same* inert test, so `survivors=0` prints whether the
   escapee lives or dies; `conform` then binds `survivors==0` (`:406-408`) on a number that cannot be nonzero.
   This is r99 Sentinel F1's vacuity re-keyed, not closed.
4. It contradicts the cited source. `census/round-96/srcs/setsid.2.html` (sha256 `52cbc190…`, the S368 capture)
   holds, occurrence 1 each: “setsid() creates a new session if the calling process is not a process group leader.”
   (15 words) and “The calling process is the leader of the new session (i.e., its session ID is made the same as its
   process ID).” (22 words). A setsid escapee's session id is **its own pid**, never the spawner's — measured above.
5. The m_noppid mutant's *shape* also needs restating: with branch (b) dead, “session key removed” is indistinguishable
   from “session key present”.

Reproducers: `.ufo/waves/round-100/w1/ConnectorOverlap/repro-session-key.py`, `…/session-key.txt`.

### F-CONN-2 (MEDIUM, calibration) — the decoy leg cannot witness branch (b); it *does* constrain any replacement

`census/round-100/c2-decoy-test.py:111-113` plants each decoy with `start_new_session=True`, i.e. **the decoy is a
session leader with `sid == its own pid`** and `ppid == the decoy driver`. Consequences:
- under the frozen key the decoy's sid differs from the probe's sid **by construction**, so `verdict=spared` is
  vacuous for the session leg (it only ever discriminated the r97 argv leg);
- a “fix” keyed on `sid == pid` alone would **kill** this decoy (its sid *is* its pid) and turn the frozen decoy leg
  red. Any replacement must keep a relation the decoy fails, e.g. `ppid == counter`.

Measured support that the escapee does satisfy `ppid == counter` once the fixture exits (`python3 -B
.ufo/waves/round-100/w1/ConnectorOverlap/repro-counter-adoption.py /fast/scratch/.../rc`, EXIT 0, output
`…/ConnectorOverlap/reparent.txt`, subreaper readback `subreaper=1`):

```
IDS {'wrap': 3421380, 'probe': 3421381, 'subreaper': 1}
t=1.0 carriers=[(3421380,(3421379,3421379)),(3421381,(3421380,3421381)),(3421382,(3421381,3421382)),(3421383,(3421382,3421383))]
t=2.0 carriers=[(3421380,(3421379,3421379)),(3421381,(3421380,3421381)),(3421382,(3421381,3421382)),(3421383,(3421382,3421383))]
t=3.2 carriers=[(3421380,(3421379,3421379)),(3421381,(3421380,3421381)),(3421383,(3421380,3421383))]
t=4.0 carriers=[(3421380,(3421379,3421379)),(3421383,(3421380,3421383))]
```

(pid,(ppid,sid)); the fixture `3421382` exits between t=2.0 and t=3.2, after which the escapee `3421383` has
`ppid=3421380` = the counter stand-in and `sid=3421383` = its own pid.)

### F-CONN-3 (MEDIUM, calibration) — the r100 counter reproduces the stale attribution C2 is repairing

`census/round-100/c2-setup-arms.py` attributes the field-4 ppid wording to S075 and still describes the removed
branch (c): `:4-5` (“field 4 (ppid) … (c) an orphan reparented to the counter”), `:96` (“fields 4 and 22, S075”),
`:124`, `:139`, `:218-222` (“still a visible child of the counter and can be owned by the ppid-chain walk” — a
walk the r99/r100 rule no longer performs), `:344-345`. C2's frozen scope is the knowledge entry + S075 `used-by`
with no new SOURCES row, so it does not cover these; the same class is now present in a *round-100* file.
Reported as a routed item, not a C2 failure.

### F-CONN-4 (INFO, calibration) — peer overlap on the C2 bytes; verify append-only and used-by order after landing

`git diff -U0 corpus/knowledge/deadline-owned-reaping.md` = 5 added lines at `:78-82`, body line `:65` untouched
(append-only respected at this snapshot). `git diff -U0 corpus/SOURCES.md` = one changed line, `:110` used-by
gaining `corpus/knowledge/deadline-owned-reaping.md` as the last entry. `tools/souji-registry-agreement.py` /
`tools/souji-record-agreement.py` must be re-run on the committed rev (the spot-check's routed defect 2 asked
for exactly this), and the S075 cell text must not otherwise change.

### F-CONN-5 (INFO, coverage) — the field-6 session kill is prior art in this lane

`corpus/knowledge/gate-signal-handling.md:71-73` and `corpus/README.md:1049` already record a session-id kill
(r80 quarantine front, S075 supersedes S068, 0 of 15 rows mismatched). The r100 wording must scope the novelty to
the arms counter; it must not read as a new capability, and it must not import the quarantine rule's authority
(the front kills only its own worker's session; the r100 predicate is counter-owned).

### F-CONN-6 (MEDIUM, operability/calibration) — the routed M11 quiet-host precondition is violated *right now*; 167 foreign token carriers are live

Measured during this walk (`for p in /proc/[0-9]*; do … cmdline …; done | grep fixture-pipe-holder.py`, grouped by
scratch root):

```
     78 /fast/scratch/hyaku/souji-r100/MutC1WideRule
     53 /fast/scratch/hyaku/souji-r100/ExecC1SessionNoReap
     29 /fast/scratch/hyaku/souji-r100-l1/arms
      3 /fast/scratch/hyaku/souji-r100/MutC1SessionKey
      2 /fast/scratch/hyaku/souji-r100/ScoutSources
      2 /fast/scratch/hyaku/souji-r100/ExecC1SessionApplier
```

`corpus/lessons/round-99-verifier-spotcheck.md:98` routes “the M11 cross-arm runs must be taken with no concurrent
decoy storm (a quiet-host gate)”; `SCORECARD.md:2533` repeats it. The storm is present in this wave while C1 arms
are being measured. What it can and cannot confound must be stated precisely: a reap candidate requires the
**counter's own** token path in argv (`_argv_of(pid)` compared to `ident`), and each seat uses its own
`--work`, so foreign carriers are not candidates for another seat's counter — the storm does **not** create
cross-seat reap candidates. It does confound (i) anything counted by process state at a wall-clock moment (the
escapee `alive`/`dead` polls, reparent sampling), (ii) `--arm-timeout` arms under CPU load, and (iii) pid-reuse
windows between a `/proc` scan and a `kill`. The L1's C1 measurement should be taken with the sibling scratch
roots drained (or at least with the carrier count recorded beside the receipt).

### F-CONN-7 (MEDIUM, calibration) — the r100 claim's ground sentence sits outside S368's registered scope

`corpus/SOURCES.md:307` registers S368 for the DESCRIPTION sentence “The calling process also becomes the process
group leader of a new process group in the session” (17 words, occurrence 1) — that sentence establishes the new
**process group**, not the new **session id**. The relation the r100 rule needs (`sid == own pid`) is the next
sentence, “The calling process is the leader of the new session (i.e., its session ID is made the same as its
process ID).” (22 words), which is present **once** in the same committed capture (`census/round-96/srcs/setsid.2.html`,
sha256 `52cbc190…`; verified by tag-strip + whitespace-normalise + `str.count`). So: no new SOURCES row is required
(the capture already holds the sentence), but the C1 claim cannot cite S368's *current* quote for `sid == pid`; the
row's scope/teaches cell needs an append-only widening, which is an L1 registry decision, not a seat edit.

### F-CONN-8 (INFO) — my own reproducers left no carrier

`for p in /proc/[0-9]*; … grep '/fast/scratch/hyaku/souji-r100/ConnectorOverlap'` → 0 hits; each reproducer SIGKILLs
the pids it planted before returning (`repro-session-key.py` `for pid, _ in …: os.kill(pid, 9)`; `repro-counter-adoption.py`
likewise). The carriers listed in F-CONN-6 belong to sibling seats.

---

## One bounded proposal (connector's move)

**Move.** Replace the dead session conjunct at `census/round-100/c2-setup-arms.py:202` with a relation the escapee
actually satisfies and the frozen decoy actually fails — *reparenthood + session leadership*:

```
owned(cand) := token(cand) ∧ starttime(cand) ≥ spawn_starttime
               ∧ ( cand == spawn_pid  ∧ starttime(cand) == spawn_starttime        # (a) unchanged
                   ∨ ppid(cand) == counter_pid ∧ sid(cand) == cand )                # (b') session leader adopted by this counter
```

and apply the identical test to the survivors scan (`:385-392`), scanning *after* the kill so `survivors` counts
owned carriers that survived rather than owned carriers before the kill.

**Why it is non-obvious and improves the round's axis.** The frozen key is a *session identity* comparison, but a
setsid escapee has no session in common with its spawner (S368; F-CONN-1). The property that distinguishes it from
every planted decoy is not which session it is in but that it **leads the session it escaped into while being
adopted by the counter** — exactly the two facts measured in `reparent.txt` (`ppid=counter`, `sid=pid`) and
`session-key.txt` (`sid==own_pid:True`, `sid==spawn_sid:False`). This keeps the r99 safety direction (no
counter-descendant carrier is killed merely for being a descendant — the r98 branch (c) harm) while restoring the
operability byte the round exists for.

**Axes.** operability: the T1 reap reaches the escapee again (`alive=0`), and `survivors` becomes a live witness.
calibration: unchanged — no registry row, no SOURCES row, no shape file; but the m_noppid mutant becomes
discriminating again (strip the `ppid==counter ∧ sid==pid` conjunct → alive=1 **and** survivors=1). coverage:
unchanged (no F-row move).

**Risks.**
1. A **session-leader carrier that reparents to the counter during the arm** is killed. That is narrower than r98's
   branch (c) (which killed *every* counter-descendant carrier) but not zero; it must be measured, not asserted.
2. A fixture whose escapee calls `setpgid` (not `setsid`) keeps the parent's session id and is not owned — a scope
   limit that must be stated in the claim, not hidden.
3. Pid reuse between the /proc scan and the kill: the fresh starttime re-read must stay (it is not in the current
   `:199-203` for branch (b) beyond `st[1] >= spawn_st`; an exact recorded starttime is stronger where available).
4. `ppid == counter` depends on `PR_SET_CHILD_SUBREAPER` (`:236`, `:217-230`); a counter mutated to drop it fails
   the reap, which is the desired mutant behaviour but must be added as an explicit mutant (`m_nosubreaper`).

**Verification (what the L1 should measure, all runnable at the frozen bytes).**
1. `ESCAPEE-ALIVE alive=0` on the successor; `alive=1` on r99 (`census/round-99/records/c2-escapee-r99.txt` is the
   do-nothing) and on the amended m_noppid.
2. Decoy leg with **two** decoy classes: the existing `start_new_session=True` sleeper (must stay `spared`), and a new
   **reparented session-leader** decoy (spawn with `start_new_session=True`, then have its parent exit) — this is the
   only arm that tests risk 1; without it the decoy verdict again witnesses nothing about branch (b′).
3. `survivors` must move: with the kill removed, `survivors=1`; with the kill present, `survivors=0`.
4. CM8 (argv-only) still `verdict=killed` by the decoy test; r99 decoy spare still `spared`.

**Do not** freeze the current `sid == spawn_sid` wording: at `f71b2155` it cannot reach the escapee, so the frozen
`ESCAPEE-ALIVE alive=0` target would be unachievable and the round would have to be recorded as a second
operability harm.

---

## Seat discipline

- No file outside my two owned paths was written; no `git add/commit/stash/checkout/reset/pull/push`, no jj command,
  no sysctl, no `/tmp` write. `git rev-parse --show-toplevel` from the lane printed
  `/home/vgpnk/Projects/shokunin/souji-shokunin`.
- Read-only use of lane instruments: `census/round-99/c2-setup-arms.py`, `census/round-98/c2-forgery-probe.py`,
  `census/round-100/*` (subject, not edited).
- Scratch `/fast/scratch/hyaku/souji-r100/ConnectorOverlap/` deleted before yield (all planted escapees were killed
  by the reproducers themselves; verified no surviving `fixture-pipe-holder.py` carrier of mine).
- Nothing installed or upgraded.
