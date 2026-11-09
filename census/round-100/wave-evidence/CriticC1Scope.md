# CriticC1Scope — wording falsification of the frozen C1 sentence

**Frozen sentence (target, quoted verbatim):** "the r100 counter reaps the T1 setsid escapee by session
ownership (alive=0) while a foreign decoy carrying the same token in a different session is spared
(decoy verdict=spared)".

**Subject file (as found on disk when this seat ran):**
`census/round-100/c2-setup-arms.py` — note: still byte-identical to r99 for the T1 wiring
(`one()`, survivors scan, `spawn =` tuple length 2); only `_reap_owned` docstring/unpack/branch (b)
was rewritten. `census/round-100/c2-decoy-test.py` is byte-identical to r99
(`diff -q … EXIT 0`). `git status --porcelain -- census/round-100/` shows the whole dir untracked
(`?? census/round-100/`, `git ls-files` empty). So the r100 instrument on disk is a mid-build
snapshot; every defect below is stated against the frozen plan predicate
(`plans/round-100.md` A0.1 lines 9–26) plus the exact on-disk lines that do/don't measure it.
No live counter or decoy run was launched (no kills by this seat); reproducers are read-only
(`grep`, inline unpack, field-index proof).

## Axes (godspeed)

- **Scope fidelity** — does the sentence say only what the three legs measure? (attacks a)
- **Completeness** — does the sentence miss a leg the instrument measures? (attacks b)
- **Attribution** — is the mechanism named ("by session ownership", "in a different session")
  the mechanism the code executes? (both attacks)

Falsification standard used: a sentence fragment is **falsifies-wording** iff the frozen
predicate's own instruments (alive=0 / spared / CM8 killed) cannot produce the content claimed,
or a measured leg is absent from the sentence. A counter that cannot run the measured leg at all
(ar­ity crash, F-n) also falsifies the number, noted in the verdict column.

---

## Attack (a)1 — Scope over-claim: "in a different session" is never measured

- **Quoted fragment:** "a foreign decoy carrying the same token in a different session is spared"
- **Why over-claim:** the decoy leg measures *liveness* only, never the session relation the
  sentence asserts. The decoy test plants foreign sleepers with `start_new_session=True`
  (`census/round-100/c2-decoy-test.py:104-105`) and then polls `os.kill(pid,0)`/zombie state
  (`c2-decoy-test.py:47-66 _alive`, `:127-142` verdict = killed iff any decoy dead). At no point
  does it read `/proc/<decoy>/stat` field 6, call `os.getsid(decoy)`, or compare the decoy's sid
  to the escapee's or spawn's sid. In the counter, `_proc_sid` has exactly two call sites total
  (`census/round-100/c2-setup-arms.py:106` def, `:202` candidate branch); no line reads the decoy's
  session id. A decoy that *shared* the escapee's session would still verdict `spared` under the
  on-disk counter whenever the spawn tuple is the 2-tuple (see F-n) or branch (b) is not reached —
  the instrument cannot distinguish "spared because different session" from "spared because no
  session test fired". The sentence claims the *reason* ("in a different session"); the legs only
  claim *spared*.
- **Measuring code / missing code:**
  - present liveness only: `census/round-100/c2-decoy-test.py:127-141`
  - missing comparison: no `getsid`/`_proc_sid(decoy)` anywhere (`grep -n "_proc_sid" census/round-100/c2-setup-arms.py` → 106, 202 only)
- **Reproducer:** `.ufo/waves/round-100/w1/CriticC1Scope/scope-grep.txt` (§1)
- **Verdict: falsifies-wording.** The protected-session clause is part of the claim but not a leg;
  a same-session decoy is not measured by any of the three legs.

### Attack (a)2 — Scope over-claim: "reaps … by session ownership (alive=0)" — alive=0 counts ppid chain, not session

- **Quoted fragment:** "the r100 counter reaps the T1 setsid escapee by session ownership (alive=0)"
- **Why over-claim:** the `(alive=0)` byte as implemented is a *spawn-chain (ppid)* count, not a
  session count. The survivors scan at `census/round-100/c2-setup-arms.py:375-390` counts a pid iff
  `pid == spawn[0]` or `_is_descendant(pid, spawn[0])` (ppid walk via `_proc_ppid`, field 4,
  `:127-147`); `_proc_sid` does not appear in `:375-390`. The T1 fixture's setsid grandchild
  (`:82-85` `os.setsid()`) orphans when its parent exits — its ppid chain no longer reaches the
  probe-spawn pid by construction (the r99 comment at `:371-373` says exactly this and is still
  on disk). So a counter that reaps *nothing* prints `survivors=0` because the escapee is
  uncountable by the ppid rule, and `conform` binds `survivors==0` (`:403-404`). `(alive=0)` on
  this instrument is satisfied by do-nothing-when-orphaned, not by a session-owned kill. The plan's
  frozen `ESCAPEE-ALIVE alive=0` (external `/proc` argv scan, `census/round-99/c2-escapee-check.sh:6-14`)
  is a *third* instrument again — the sentence collapses three different "alive" bytes
  (counter `survivors`, plan `ESCAPEE-ALIVE`, decoy `verdict`) into one parenthetical.
- **Measuring code:** `census/round-100/c2-setup-arms.py:388-390`; ceiling comment `:365-373`
- **Reproducer:** `.ufo/waves/round-100/w1/CriticC1Scope/scope-grep.txt` (§2)
- **Verdict: falsifies-wording** (number itself is unfalsified-false on the current snapshot: see
  F-n — the number as printed would be produced by a crashing counter that never reaches the reap).

---

## Attack (b)1 — Wording narrower: byte-exact token + starttime gate + CM8 limb are measured but unstated

- **Quoted fragment:** the whole sentence
  ("the r100 counter reaps the T1 setsid escapee by session ownership (alive=0) while … (decoy verdict=spared)")
- **What is measured but not stated:**
  1. **Byte-exact argv candidate filter.** Every kill candidate must carry `fx` as an exact argv
     element (`census/round-100/c2-setup-arms.py:192` `any(a == ident.encode() for a in argv)`).
     A process with the token as a *substring* is never a candidate. The sentence says "carrying
     the same token" without the byte-exactness that decides cand­idacy.
  2. **Starttime gate (field 22).** Branch (a) requires `st[1] == spawn_st` (`:199-201`); branch (b)
     requires `st[1] >= spawn_st` (`:202`). Session equality alone never kills; a pid-reused
     session-mate with an older starttime is spared. The sentence's "by session ownership"
     omits this second key, which the plan predicate *does* include
     ("session id … plus the spawn pid's own starttime", `plans/round-100.md:11-13`) and which the
     `m_noppid` mutant discriminates.
  3. **The CM8 limb.** The frozen plan predicate is a *triple*
     (`plans/round-100.md:18-24`: (1) r100 alive=0+spared, (2) r99 alive=1, (3) CM8 verdict=killed,
     plus `m_noppid` must FAIL (1)). The frozen *sentence* has two legs (alive=0, spared) and does
     not state the CM8-killed discrimination. A counter that kills nothing satisfies leg 1 as
     counted by the survivors scan (see attack (a)2) and satisfies leg 2 trivially — only the
     unstated CM8 limb separates "session-owned reap" from "do nothing". The sentence is therefore
     true-of-nothing (vacuous) without the limb it omits.
  4. **Conform binding.** `survivors==0` is bound into `conform` (`:403-404`), so the printed
     `ARMS-SUMMARY conform=20` is a *fourth* number (exit+line+survivors), not the two in the
     sentence.
- **Measuring code:** `census/round-100/c2-setup-arms.py:192, 199-202, 403-404`;
  plan triple `plans/round-100.md:18-24`
- **Reproducer:** `.ufo/waves/round-100/w1/CriticC1Scope/scope-grep.txt` (§3)
- **Verdict: falsifies-wording** (narrower than the instrument). The omitted legs are exactly the
  ones that make the predicate non-vacuous; restoring them changes truth value, so this is not a
  neutral quibble.

---

## Cross-cutting defect F-n (falsifies-number on the snapshot)

- **What:** `one()` builds a **2-tuple** spawn; `_reap_owned` unpacks a **3-tuple**.
  `census/round-100/c2-setup-arms.py:349`
  `spawn = (p.pid, _proc_starttime(p.pid)) if aid == "T1" else None`
  vs `:198` `spawn_pid, spawn_st, spawn_sid = spawn` (docstring `:182` says 3-tuple).
  Any T1 call with `spawn is not None` raises `ValueError: not enough values to unpack
  (expected 3, got 2)` *before* branch (a) or (b) runs — i.e. the current snapshot reaps the
  escapee **never**, by crash, not by session ownership, and never records the spawn sid at all.
  Independently, this means the mid-build file cannot produce `alive=0`-via-ownership: the
  wording's causal clause ("by session ownership") is false of the code as found.
- **Reproducer:** `.ufo/waves/round-100/w1/CriticC1Scope/arity.txt`; proof run:
  `python3 -B -c "spawn=(12345,67890); spawn_pid,spawn_st,spawn_sid=spawn"` → `ValueError`, exit 1
  (wrapper exit 0 in earlier run; both prints recorded).
- **Verdict: falsifies-number** (on the snapshot). The L1/integration owner must either land the
  missing sid record (`_proc_sid(p.pid)` into the tuple) or acknowledge that the number printed by
  this snapshot is a crash, not a reap. This seat does not edit the predicate in place.

---

## What survives

- The field-6 *index* is correct: after `comm`, `fields[3]` is stat field 6 (session), and equals
  `os.getsid` for a session leader. Live proof (read-only, no kills):
  `python3 -B .ufo/waves/round-100/w1/CriticC1Scope/fieldcheck.py` → exit 0,
  `pid=3272885 idx0-6=['R', '3723741', '3272885', '3272885', '0', '-1', '4194304'] os.getsid(self)=3272885`
  (this seat's own pid is a session leader; `fields[3]==os.getsid`). This neutral leg is
  **neutral (index correct)** — the mechanism *can* be measured, the counter just doesn't feed it.
- r99 wiring (`one()`, survivors scan) is untouched by the r100 stub, so a do-nothing control
  against r99 still means what the plan says — **neutral**.

## Commands run (exact, exit codes, observed lines)

1. `cd /home/vgpnk/Projects/shokunin/souji-shokunin && diff -u census/round-99/c2-setup-arms.py census/round-100/c2-setup-arms.py; echo "EXIT:$?"` → **`EXIT:0`** (empty diff — r100 was a byte-copy of r99 at that point; the session edit landed *after*, mid-wave).
2. `diff -q census/round-99/c2-decoy-test.py census/round-100/c2-decoy-test.py; echo "EXIT:$?"` → **`EXIT:0`** (identical).
3. `grep -n "_proc_sid" census/round-100/c2-setup-arms.py` → **`EXIT:0`**, lines `106`, `202` only.
4. `python3 -B .ufo/waves/round-100/w1/CriticC1Scope/fieldcheck.py` → **`EXIT:0`**, line
   `pid=3272885 idx0-6=['R', '3723741', '3272885', '3272885', '0', '-1', '4194304'] os.getsid(self)=3272885`.
5. `python3 -B -c "spawn=(12345,67890); spawn_pid,spawn_st,spawn_sid=spawn"` → **`EXIT:1`**,
   `ValueError: not enough values to unpack (expected 3, got 2)`.
6. `git ls-files census/round-100/c2-setup-arms.py census/round-100/c2-decoy-test.py` → empty (untracked);
   `git status --porcelain -- census/round-100/` → `?? census/round-100/`.
7. No counter/decoy live run (deliberate: no kills by this seat; predicate already falsified by code reading + arity proof).

Scratch: `/fast/scratch/hyaku/souji-r100/CriticC1Scope/` created, `fieldcheck.py` run there (exit 0),
then deleted before yield (`rm -rf` of that exact dir; verified `ls` empty before removal — see receipt
under `history`). Tool installs: none (no new tool needed; `python3`/`grep`/`git` read-only only).

Report: .ufo/waves/round-100/w1/CriticC1Scope.md
