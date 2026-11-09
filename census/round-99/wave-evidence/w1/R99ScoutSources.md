# R99ScoutSources — round 99 live source re-opening (S075 / S368 / S372) and the C2 reap-predicate check

Seat: R99ScoutSources (scout, leaf). Lane: `souji-shokunin`
(`/home/vgpnk/Projects/shokunin/souji-shokunin`), lane base `c94d678c8a76f3f87f73b49a11a9d4e2aff73e3b`.
Access date for every live fetch below: **2026-11-09**.

Write set (this seat): this report and `.ufo/waves/round-99/w1/R99ScoutSources/`. Scratch (deleted at
the end): `/fast/scratch/hyaku/souji-r99/R99ScoutSources/`. **No corpus, census, tools or fixture file was
edited; no git/jj state was touched; no commit or push was made.** All git commands below are read-only
(`log`, `show --stat`, `rev-parse`, `status --porcelain`, `merge-base`).

---

## 1. Verdict summary

1. **All three cited sources re-open live, unchanged.** Every live fetch is HTTP 200 and **byte-identical**
   to the committed capture in the lane. Every quote this round cites occurs **exactly once** in both the
   live fetch and the capture, and each is ≤ 25 words. **Nothing in S075 / S368 / S372 is falsified.**
   (§3; receipt `receipts/sources-live.out`, `SOURCES-LIVE-SUMMARY failures=0`, exit 0.)
2. **FINDING 1 (HIGH — claim-relevant, C2).** The r99 arms counter's T1 arm **has no kill power over the
   process it is built to reap.** With branch (c) removed from `_reap_owned`, the T1 escapee is **never
   killed** by the r99 counter and **never counted** as a survivor — it survives the whole run and is
   left behind as a live orphan. The `survivors` byte the arm prints is therefore **vacuous for the
   escapee**, and the arm's `conform=yes` does not witness a reap. Measured three ways (§5):
   - the real r99 counter's T1 arm prints `planted-killed 0` (the counter's own byte);
   - a **no-op mutant** of the r99 counter that reaps *nobody at all* prints **byte-identical**
     `ARM T1 exit=2 want=2 line=yes conform=yes survivors=0` and `ARMS-SUMMARY arms=20 conform=20`;
   - the **r98** counter, same instrument, same fixtures, kills the escapee and leaves **0** live
     escapees; the **r99** counter leaves **1** live escapee.
   This is a **regression relative to r98**, not a pre-existing defect: r98 killed the escapee via
   branch (c).
3. **FINDING 2 (HIGH — the C2 claim sentence is falsified by the counter's own bytes).** C2 says the reap
   "kills only the recorded spawn pid and its ppid-chain descendants". Measured at the counter's actual
   reap moment with the **real** probe and the **real** T1 fixture, the T1 escapee's field-4 (ppid)
   chain reaches the **counter**, never the recorded spawn pid: the fixture's parent exits while the
   probe is still alive, the escapee is reparented to the subreaper counter, and the chain
   `escapee → counter → …` **never contains the spawn pid**. Under the r99 rule that escapee is
   out of scope and is spared; the arm's `survivors=0` cannot see it either. The r99 counter's own
   comment admits this ("it is then NOT killed"), yet the arm still reports `conform=yes`.
4. **FINDING 3 (MEDIUM — source attribution, carried forward stale).** The registry row **S075** scopes
   itself to "pgrp/session IDs and starttime tick units" (fields 5/6/22) and **no registry row teaches
   the field-4 (ppid) wording** (`grep -c "PID of the parent" corpus/SOURCES.md` → **0**). The r98
   lesson already corrected this ("the field-4 ppid wording is the kernel-side attribution (S332)").
   But the **r99 counter repeats the withdrawn attribution** in three docstrings
   (`census/round-99/c2-setup-arms.py:96`, `:128`, `:330` — "fields 4 and 22, S075"), and the r98
   **knowledge entry** `corpus/knowledge/deadline-owned-reaping.md:65` still says "(S075 field 4/22, S368)"
   — both landed in the **same** commit `ca98ad08` that carried the correction. §6.
5. **FINDING 4 (LOW — registry pointer gap).** `corpus/knowledge/deadline-owned-reaping.md` cites S075,
   but S075's `used-by` cell does **not** list it (it lists `round-18.md`,
   `process-residue-observations.md`, `gate-signal-handling.md`). §6.
6. **C1 is unaffected.** The r99 frozen-file read works and the Q173 movability gate is real:
   `census/round-99/declared-shapes.py --freeze census/round-99/shapes.tsv` → `SHAPES-SUMMARY shapes=17
   mismatched=0` (exit 0); a **relabelled copy** of the same file (sha256 `fedc0fcb…`) → `mismatched=3`
   with the three specific rows named. The count **does** move. §7.

---

## 2. Commands run (exact)

```bash
# --- live fetch (S075 / S368 / S372) ---
curl -sS -L -w '%{http_code}' -o live-proc_pid_stat.5.html  https://man7.org/linux/man-pages/man5/proc_pid_stat.5.html
curl -sS -L -w '%{http_code}' -o live-setsid.2.html           https://man7.org/linux/man-pages/man2/setsid.2.html
curl -sS -L -w '%{http_code}' -o live-sys.monitoring.html      https://docs.python.org/3/library/sys.monitoring.html
sha256sum live-*

# --- combined, reproducible ---
python3 .ufo/waves/round-99/w1/R99ScoutSources/repro-sources-live.py <scratch>/srcs
python3 .ufo/waves/round-99/w1/R99ScoutSources/repro-field-index.py
python3 .ufo/waves/round-99/w1/R99ScoutSources/repro-starttime-granularity.py 40

# --- the real r99 counter, end-to-end ---
python3 -B census/round-99/c2-setup-arms.py --probe census/round-98/c2-forgery-probe.py \
  --fixture-pass tests/fixtures/r93-k4-flagfail.py --fixture-fail tests/fixtures/r92-k4-flagfail.py \
  --tool tools/souji-record-agreement.py --before census/round-92/controls/c2-before-tool.py \
  --work <scratch>/arms-pristine200 --jobs 4 --arm-timeout 200

# --- the no-op-reap mutant (r99 and r98), same everything else ---
python3 .ufo/waves/round-99/w1/R99ScoutSources/repro-noop-reap-mutant.py <scratch> 200

# --- topology probes with the REAL probe + REAL T1 fixture ---
python3 .ufo/waves/round-99/w1/R99ScoutSources/repro-real-probe-escapee.py
python3 .ufo/waves/round-99/w1/R99ScoutSources/repro-reparent-stages.py
python3 .ufo/waves/round-99/w1/R99ScoutSources/repro-r99-predicate-on-t1.py

# --- C1 frozen file + Q173 relabelling ---
python3 -B census/round-99/declared-shapes.py --freeze census/round-99/shapes.tsv \
  --search census/round-99/c1-survivor-search.py --scripts census/round-98/shapes --work <scratch>/shapes-work
python3 -B census/round-99/declared-shapes.py --freeze <scratch>/relabel/relabeled.tsv \
  --search census/round-99/c1-survivor-search.py --scripts census/round-98/shapes --work <scratch>/relabel/w

# --- registry (read-only) ---
bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji
```

---

## 3. Live re-opening of the three sources (S075 / S368 / S372)

Receipt: `receipts/sources-live.out` — `SOURCES-LIVE-SUMMARY failures=0`, **exit 0**.

### 3.1 Fetch table (live, 2026-11-09)

| id | URL | HTTP | bytes | live sha256 | committed capture | capture sha256 | byte-identical |
|---|---|---|---|---|---|---|---|
| S075 | `https://man7.org/linux/man-pages/man5/proc_pid_stat.5.html` | 200 | 20647 | `0f04d78946538fd84db1536845abeb236da51a04844989f34ea7ee7cb0b6700f` | `census/round-98/srcs/proc_pid_stat.5.html` | `0f04d789…700f` | **yes** |
| S368 | `https://man7.org/linux/man-pages/man2/setsid.2.html` | 200 | 11555 | `52cbc1904742df69556104f71d3279f93581756579881c85cee8e37be37c7f30` | `census/round-96/srcs/setsid.2.html` | `52cbc190…7f30` | **yes** |
| S372 | `https://docs.python.org/3/library/sys.monitoring.html` | 200 | 74653 | `2b2817933633296ad7c667916d34b9d6f20b5e079a927527dae68ec37d1b3a4c` | `census/round-98/srcs/monitoring.html` | `2b281793…3a4c` | **yes** |

### 3.2 Quote table — occurrence count and word count (live **and** capture)

`occ` = occurrences in the whitespace-normalized, tag-stripped, HTML-unescaped text. **Every quote occurs
exactly once in the live fetch and exactly once in the committed capture.** Every quote is ≤ 25 words.

| id | quote | words | live occ | capture occ | location in the page |
|---|---|---|---|---|---|
| S075 field 22 | "The time the process started after system boot." | 8 | **1** | **1** | § DESCRIPTION, field **(22) starttime %llu** |
| S075 field 22 | "Since Linux 2.6, the value is expressed in clock ticks (divide by sysconf(_SC_CLK_TCK))." | 13 | **1** | **1** | § DESCRIPTION, field (22) starttime %llu |
| S075 field 5 | "The process group ID of the process." | 7 | **1** | **1** | § DESCRIPTION, field (5) pgrp |
| S075 field 6 | "The session ID of the process." | 6 | **1** | **1** | § DESCRIPTION, field (6) session |
| S075 field 4 | "The PID of the parent of this process." | 8 | **1** | **1** | § DESCRIPTION, field (4) ppid |
| S368 | "The calling process also becomes the process group leader of a new process group in the session" | 17 | **1** | **1** | § DESCRIPTION |
| S372 | "An exception is re-raised, for example at the end of a finally block." | 13 | **1** | **1** | § Events, `sys.monitoring.events.RERAISE` |

**The three quotes this round's claims cite, verbatim with location:**

- **S075 — starttime (field 22)** — § DESCRIPTION, field list item `(22) starttime %llu`, immediately after
  `(21) itrealvalue %ld` and immediately before `(23) vsize %lu`:
  > "The time the process started after system boot."

  and, for the tick units S075's row teaches:
  > "Since Linux 2.6, the value is expressed in clock ticks (divide by sysconf(_SC_CLK_TCK))."

- **S368 — the new process group** — § DESCRIPTION, in the sentence between "The calling process is the
  leader of the new session…" and "The calling process will be the only process in the new session…":
  > "The calling process also becomes the process group leader of a new process group in the session"

- **S372 — RERAISE** — § Events, the `sys.monitoring.events.RERAISE` entry, between the `RAISE` entry
  ("An exception is raised, except those that cause a STOP_ITERATION event.") and the `STOP_ITERATION`
  entry:
  > "An exception is re-raised, for example at the end of a finally block."

### 3.3 S332 — the kernel-side emission order (the field-4 attribution)

Not a live web page: the committed capture `census/round-83/srcs/linux-array.c-v6.17`
(sha256 `17f2318d5b29740cb94b8c346c386d30048a876107b1c8f2d5c6542cacd9a938`). Its quote also occurs
**exactly once**, and is 15 words:

> "seq_puts(m, \" (\"); proc_task_name(m, task, false); seq_puts(m, \") \"); seq_putc(m, state); seq_put_decimal_ll(m, \" \", ppid);"

(`census/round-83/srcs/linux-array.c-v6.17` lines 590–594; `start_time` is emitted at line 612.)
This is the row that owns **field 4**; see FINDING 3.

### 3.4 Field-index arithmetic, re-derived mechanically (receipt `receipts/field-index.out`)

The r99 counter parses `fields = data.rsplit(b")", 1)[1].split()` and reads `fields[1]` (ppid) and
`fields[19]` (starttime). `repro-field-index.py` re-derives the field numbers **positionally from the
S332 emission order** (not from a hand-written constant) and then checks them against the **live**
kernel:

```
post-comm emission order (S332), first 12: ppid, pgid, sid, tty_nr, tty_pgrp, task->flags, min_flt, …
  field 4    <- ppid
  field 5    <- pgid
  field 6    <- sid
  field 22   <- start_time
live /proc/<pid>/stat: post-comm token count=50
  fields[1] (field 4) = 3723741 ; os.getppid() = 3723741
  fields[2] (field 5) = 1896160 ; os.getpgrp() = 1896160
  fields[3] (field 6) = 1896160 ; os.getsid(0) = 1896160
  [OK ] field 4 = ppid          [OK ] field 5 = pgid          [OK ] field 6 = session id
FIELD-INDEX-SUMMARY mismatches=0     (exit 0)
```

**The counter's field indices are correct.** The indices are not the defect; the *rule* built on them is.

### 3.5 starttime granularity (receipt `receipts/starttime-granularity.out`)

S075's row teaches field 22 as "starttime in clock ticks used for PID identity revalidation" and warns
that "a printed sid alone is not an identity binder". The analogous measurement for field 22:

```
SC_CLK_TCK = 100  (starttime resolution = 10 ms)
parallel burst: 40 distinct pids -> 2 distinct starttime values
  starttime values shared by >1 distinct pid: 2 [(7510856, 35), (7510857, 5)]
  VERDICT starttime_alone_is_unique=False
sequential control: 20 spawns 50 ms apart -> 20 distinct starttime values
```

**Field 22 alone is not a unique identity binder** (35 of 40 concurrently-spawned processes shared one
starttime value). The binder must be the **pair (pid, starttime)**. The r99 counter does use the pair
for the spawn pid itself (`st[1] != spawn_st` → skip), so this is a limit to record, not a defect in the
counter.

---

## 4. FINDING 1 (HIGH) — the r99 T1 arm has no kill power; `survivors` is vacuous for the escapee

**Reproducer:** `repro-noop-reap-mutant.py <scratch> 200` (and the direct counter runs in §5).
**Receipts:** `receipts/r99-counter-armtimeout200.out`, `receipts/r99-noop-reap-mutant-armtimeout200.out`,
`receipts/r98-noop-reap-mutant-armtimeout200.out`.

The r99 counter's **only** per-process kill is `os.kill(pid, signal.SIGKILL)` at
`census/round-99/c2-setup-arms.py:196`, inside `_reap_owned`. The only other kill is
`os.killpg(p.pid, …)` at `:341` — the arm-timeout group kill, which cannot reach the escapee because
the escapee called `setsid()` (S368: a new session ⇒ a new process group ⇒ not in the probe's group).

### 4.1 The counter's own byte says it killed nothing

`arms-pristine200/T1.out` (pristine r99 counter, `--arm-timeout 200`):

```
--survivors 0 planted-killed 0--
```

`planted-killed 0` is the counter's own report that its reap **signalled nobody** on the T1 arm.

### 4.2 A counter that reaps NOTHING is indistinguishable from the pristine counter

The no-op mutant changes `_reap_owned` to `return 0` immediately — it signals **no process at all** —
and changes nothing else. Both runs, same fixtures, same `--arm-timeout 200`:

| run | `ARM T1` line | `ARMS-SUMMARY` |
|---|---|---|
| **pristine r99** | `ARM T1 exit=2 want=2 line=yes conform=yes survivors=0` | `ARMS-SUMMARY arms=20 conform=20` |
| **r99 no-op-reap mutant** | `ARM T1 exit=2 want=2 line=yes conform=yes survivors=0` | `ARMS-SUMMARY arms=20 conform=20` |
| **r98 no-op-reap mutant** | `ARM T1 exit=2 want=2 line=yes conform=yes survivors=0` | `ARMS-SUMMARY arms=20 conform=20` |

**Byte-identical.** The T1 arm cannot distinguish "reaped the escapee" from "reaped nobody at all", so
`conform=20` does **not** witness the reap leg. (The same vacuity exists in r98 — this is the r98
**M8 / R98Sentinel FINDING 5** class, re-measured here; the r99 change is not its cause.)

### 4.3 The live-escapee count separates r99 from r98 — a **regression**

Both counters, same fixtures, same `--arm-timeout 200`, both `ARMS-SUMMARY arms=20 conform=20`:

| counter | live escapees still running after the counter exited |
|---|---|
| **r98** (`census/round-98/c2-setup-arms.py`) | **0** (`pgrep -cf "arms-r98pristine/fixture-pipe-holder"` → `0`) |
| **r99** (`census/round-99/c2-setup-arms.py`) | **1** (`pgrep -cf "arms-pristine200/fixture-pipe-holder"` → `1`) |

The r99 counter leaves its T1 escapee **running** (pid 2901173, ppid 1525 after reparenting, session
leader of its own session). The r98 counter, with branch (c) still present, killed it. **Removing branch
(c) changed the counter from "kills the escapee" to "leaks the escapee", and the arms counter's own
`conform=20` cannot see the difference.**

### 4.4 Why the survivors byte cannot see it

The r99 survivors counter (`census/round-99/c2-setup-arms.py:362-373`) counts a pid as a survivor iff
`pid == spawn[0] or _is_descendant(pid, spawn[0])` — the **spawn chain only**, deliberately
("no subreaper/counter branch"). The escapee is not in the spawn chain (FINDING 2), so it is **not
counted**; and it is **not killed**. It is invisible to both bytes of the T1 arm.

---

## 5. FINDING 2 (HIGH) — at the counter's real reap moment the escapee's chain reaches the COUNTER, not the spawn pid

**Reproducer:** `repro-real-probe-escapee.py` (real `census/round-98/c2-forgery-probe.py`, real PIPHOLDER
fixture copied byte-exact out of the r99 counter, real `Popen(…, start_new_session=True)` sequence).
**Receipt:** `receipts/real-probe-escapee.out`.

```
counter pid=2327000
recorded spawn pid (probe) = 2327094  starttime(field22) = 7432779
escapee pid = 2327270
probe exited rc=2
escapee field-4 chain AT REAP MOMENT = [2327270, 2327000, 3723741, 46506, 46476, 1777, 1771, 1525, 1]
  reaches recorded spawn pid (2327094)? False  <- r99 clause (b): spawn chain
  reaches counter pid (2327000)?     True   <- r98 clause (c): counter descendant
  escapee alive at reap moment? True
r99 _reap_owned -> signalled=0; escapee alive after? True
r98 _reap_owned -> signalled=1; escapee alive after? False
r99 survivors counter counts escapee? False
```

This is the counter's **exact** sequence, and it settles the question the r98 wave left open
(R98Sentinel FINDING 4): the escapee is **not** reachable by the spawn-chain walk, so under the r99 rule
it is **never killed**; it is reachable only by branch (c), which r99 removed.

### 5.1 The reparenting is a two-stage event; the break happens at stage 2

**Reproducer:** `repro-reparent-stages.py` (`receipts/reparent-stages.out`):

```
counter=2870717 recorded spawn pid (probe)=2870718 escapee=2870720
stage 2 (fixture parent exited, probe ALIVE): escapee ppid=2870717  -> reaches probe? False  -> reaches counter? True
stage 3 (probe EXITED == the counter's reap moment): escapee ppid=2870717  -> reaches probe? False  -> reaches counter? True
escapee alive at the reap moment? True
```

The chain breaks **before** the counter reaps, while the probe is still alive: the fixture's parent exits
0, and the escapee reparents to the **nearest living subreaper ancestor** — the counter — not to the
probe. The counter's `PR_SET_CHILD_SUBREAPER(1)` is what moves the escapee out of the spawn chain.

**Control** (`repro-setsid-reparent-control.py`, `receipts/setsid-reparent-control.out`): a child that does
**not** call `setsid()` also reparents to the counter, so the reparenting is caused by the **subreaper
net**, not by `setsid()`:

```
A: child calls setsid()   : ppid=2966665  -> reaches probe? False  -> reaches counter? True
B: child does NOT setsid() : ppid=2966665  -> reaches probe? False  -> reaches counter? True
```

S368's `setsid()` is therefore **not** the cause of the break — the subreaper net is. (S368's own
teaching — a new session is a new process group, so a group kill cannot reach it — remains sound and
is confirmed: the escapee is in its own session and the group kill at `:341` never reaches it.)

### 5.2 Consequence for the C2 sentence

C2 as frozen reads: *"The arms counter's T1 reap kills only the recorded spawn pid and its ppid-chain
descendants (starttime verified); a counter-descendant carrier outside the spawn chain is not signalled
(branch (c) removed)."*

The first half is **true but vacuous for the T1 escapee**: the escapee is a counter-descendant outside
the spawn chain, so the r99 rule spares it — and the arm's `survivors` byte cannot see it. The
cross-arm probe the claim leans on (`census/round-99/c2-cross-arm-probe.py`, planted by a *different*
arm) will show the carrier spared under r99 and killed under r98, which is the intended discrimination —
but that probe **cannot** distinguish "branch (c) removed" from "the spawn-chain rule never owned the
T1 escapee either", because both outcomes are "spared". The T1 arm needs a **positive** witness (the
escapee is reaped) to close that gap, and today it has none.

**The L1 must freeze a predicate that binds the positive.** As the bytes stand, `conform=20` is printed
by a counter that reaps nothing.

---

## 6. FINDING 3 (MEDIUM) and FINDING 4 (LOW) — source attribution, carried forward stale

**Reproducer:** the greps in §2; read-only git (`git log -S`, `git show --stat`).

- **FINDING 3.** The r98 lesson recorded the correction —
  `corpus/lessons/round-98.md:40-41`: *"S075's scope is fields 5/6/22 in the registry; the field-4 ppid
  wording is the kernel-side attribution (S332); the plan's 'ppid field 4' attribution to S075 is
  corrected here"*. The registry agrees: **S075's** scope cell is "pgrp/session IDs and starttime tick
  units" and its locator cell is "§ DESCRIPTION fields 5, 6, 22"; **S332's** teaches cell is "the ppid
  is the fourth stat field … and start_time is field 22"; and **no** row carries the field-4 wording
  (`grep -c "PID of the parent" corpus/SOURCES.md` → **0**). Yet:
  - `census/round-99/c2-setup-arms.py:96` — `"""Return (ppid, starttime) from /proc/<pid>/stat (fields 4 and 22, S075), or None."""`
  - `census/round-99/c2-setup-arms.py:128` — `"""True iff pid == ancestor or walking field-4 (ppid) up to that pid reaches <ancestor> (S075)."""`
  - `census/round-99/c2-setup-arms.py:330` — `# r98 ownership (S075): record at spawn the pid the arm's Popen created and its starttime (stat field 22).`
  - `corpus/knowledge/deadline-owned-reaping.md:65` — `- The reap is now by ownership (S075 field 4/22, S368): …`

  The knowledge line and the r98 lesson's correction **landed in the same commit** `ca98ad08`
  (`git log -S "S075 field 4/22" -- corpus/knowledge/deadline-owned-reaping.md` → `ca98ad08`;
  `git log -S "the field-4 ppid wording is the kernel-side" -- corpus/lessons/round-98.md` → `ca98ad08`),
  so the correction never reached the knowledge entry, and the **r99 counter re-introduces** the withdrawn
  attribution in new bytes. `plans/round-98.md:35` likewise still reads "S075 (proc_pid_stat(5): ppid
  field 4, starttime field 22)" with no appended correction.

  **Impact on this round:** the r99 counter's field-4 docstrings cite a row whose scope does not cover
  field 4. The *code* is right (§3.4); the *attribution* is not. A seat may not edit the predicate or the
  corpus — this is reported for the L1 to route.

- **FINDING 4.** `corpus/knowledge/deadline-owned-reaping.md` cites S075, but S075's `used-by` cell is
  `corpus/lessons/round-18.md, corpus/knowledge/process-residue-observations.md,
  corpus/knowledge/gate-signal-handling.md` — the r98/r99 knowledge entry that grounds the C2 sentence is
  **not listed**. (S368's `used-by` does list it.) `scripts/sources-census.sh validate … souji` still
  exits **0** (294 rows), so this is a pointer gap the census does not catch, not a census failure.

---

## 7. C1 — unaffected by the above, and the Q173 gate is real

The r99 hook is **byte-identical** to the r98 object-keyed latch:
`sha256(census/round-99/c1-survivor-search.py) = sha256(census/round-98/c1-survivor-search.py) =
e8ba780a5b8d807ff199c33a679d7d8dd7259fb93e934d123b009e9f9f2649e1` (`cmp` → identical).

With the frozen file `census/round-99/shapes.tsv` (sha256
`8bc642c44e0c1f6414fb4b07aaf922c01bf2d2ea8b91bda7bac81f60a05a8a14`), exit **0**:

```
SHAPES-SUMMARY shapes=17 mismatched=0
```

With a **relabelled copy** of the same file (sha256 `fedc0fcb49a6c1179708753d13fc2e80778fb25ced83274a5ba35bb66ec0a209`),
the count **moves** — the Q173 gate holds:

```
SHAPE q1q-caught-then-direct.py kind=declared plain=1 hooked=70 MISMATCH
SHAPE q1i-finally-then-catch.py kind=crash plain=0 hooked=0 MISMATCH
SHAPES-SUMMARY shapes=17 mismatched=3
MISMATCH q1o-save-then-bare-raise.py
MISMATCH q1q-caught-then-direct.py
MISMATCH q1i-finally-then-catch.py
```

The mismatch rows are named, not merely counted. The C1 claim's substance (labels read from a frozen
file the runner reads; the count moves when the labels change) is supported by these bytes.

---

## 8. Reproducers (all under this seat's wave dir)

| file | what it does |
|---|---|
| `repro-sources-live.py` | fetches the three pages live, compares with the committed captures, counts each quote's occurrences and words. Exit 0 iff all clean. |
| `repro-field-index.py` | re-derives the stat field numbers positionally from the S332 capture and checks them against the live kernel. |
| `repro-starttime-granularity.py` | measures whether field 22 alone is a unique identity binder. |
| `repro-real-probe-escapee.py` | the counter's exact T1 sequence with the **real** probe and fixture; measures the escapee's chain at the reap moment and applies the **real** r99/r98 `_reap_owned`. |
| `repro-reparent-stages.py` | shows at which stage the escapee leaves the spawn chain. |
| `repro-setsid-reparent-control.py` | the control: setsid vs no-setsid, isolating the subreaper net as the cause of the reparenting. |
| `repro-t1-reap-moment.py` | the same measurement with a hand-built topology (kept for cross-checking the real-probe run). |
| `repro-r99-predicate-on-t1.py` | applies the real r99 and r98 `_reap_owned` to the faithful topology, side by side. |
| `repro-noop-reap-mutant.py` | the kill-power test: no-op-reap mutant vs pristine counter, same fixtures. |
| `fixture-token-XYZ`, `fixture-token-XYZ2` | the token-carrying fixtures the probes use. |
| `receipts/*.out` | the captured outputs of every command quoted above. |

**Receipt provenance note.** Every receipt is a direct redirection of the named command's output, and
every receipt was re-run to confirm the numbers quoted in this report. `receipts/reparent-stages.out`,
`receipts/setsid-reparent-control.out` and `receipts/r99-vs-r98-predicate.out` were **re-run after** the
seat's scratch directory was removed (a first attempt failed with "working directory does not exist"
because the cleanup deleted the scratch mid-run); the re-run reproduces the §5 numbers exactly, with
different pids. The three scripts write their pidfiles under the scratch root passed at run time.

---

## 9. Not verified / limits

- The **r98 pristine** counter run and the **r99 pristine** run were executed on a host carrying several
  sibling seats' concurrent counter runs. The **escapee-count** comparison (0 vs 1) is a count of live
  processes, not a timing-sensitive value, and is stable; the `conform` counts are quoted from the
  receipts as observed and are reproducible at the quoted `--arm-timeout`.
- Two earlier runs at `--arm-timeout 120` and `--arm-timeout 250` gave `ARMS-SUMMARY arms=20 conform=18`
  and `conform=19` respectively, with `ARM T1 exit=hung` / `exit=-15` — **arm-timeout sensitive**, and
  **not** used as evidence. All kill-power claims in §4 use matched `--arm-timeout 200` runs.
- `census/round-99/c2-cross-arm-probe.py` was **not** executed by this seat (another seat owns it); this
  report says nothing about its verdict.
- I did **not** run the r99 decoy test (`census/round-99/c2-decoy-test.py`).
- The registry census was run read-only: `scripts/sources-census.sh validate --root
  /home/vgpnk/Projects/shokunin souji` → `souji ok …/corpus/SOURCES.md`, **exit 0**, 294 rows (only
  pre-existing W04 duplicate-url warnings).
- No `considerthese/` or `shokuknow` path was read or written. No host sysctl was touched. No tool was
  installed or upgraded. No pacman transaction.
- **This seat edited no predicate, no census file, no corpus file and no fixture**, and made no commit.

---

## 10. Recommendations to the L1 (not applied)

1. **Freeze a positive T1 witness.** `conform=20` is printed by a counter that reaps nothing
   (§4.2). The T1 arm needs a byte that is non-zero when the escapee is reaped, e.g. assert the escapee's
   pid is gone (or its starttime is absent) at the end of the arm — not `survivors` counted over the
   spawn chain alone.
2. **Decide the escapee's owner explicitly.** The escapee is outside the spawn chain at the reap moment
   (§5). Either the claim sentence names that the T1 escapee is **not** reaped (and the arm is renamed
   or retired), or the counter records the escapee's (pid, starttime) **at observation time** — the
   r98 wave's own routing — rather than walking the chain after the fact.
3. **Route the attribution correction** (FINDING 3) to whoever edits `census/round-99/c2-setup-arms.py`:
   the field-4 docstrings should cite S332 (or a new row owning the field-4 wording), not S075.
   `corpus/knowledge/deadline-owned-reaping.md:65` carries the same withdrawn attribution.
4. **Record the starttime limit** (§3.5): field 22 alone is not a unique binder (35 of 40 concurrent pids
   shared a value); the binder is the pair (pid, starttime).
5. **C1 needs no change from this seat.** The frozen-file read and the Q173 relabelling gate are
   demonstrated above.
