# R99Connector — cross-lane overlap scan + planning data-walk

Seat R99Connector (connector, one v1 wave). Lane `/home/vgpnk/Projects/shokunin/souji-shokunin`,
lane base `c94d678c8a76f3f87f73b49a11a9d4e2aff73e3b`. Read-only throughout: no commit, no push, no
git/jj mutation, no `census/round-98/` file edited, no sibling-lane file edited, no
`MANIFEST.json`/`.ufo/state`/`.scratch`/watchdog touched. All work product is under
`.ufo/waves/round-99/w1/R99Connector/`. Scratch `/fast/scratch/hyaku/souji-r99/R99Connector/`
deleted before yield. No tool installed or upgraded (nothing missing; `python3` 3.14.8,
coreutils, `/proc` sufficed). RULES.md read at `/home/vgpnk/.omp/agent/RULES.md`; no pacman
transaction attempted.

Pinned bytes under test:

| file | sha256 |
|---|---|
| `census/round-99/c2-setup-arms.py` (r99 counter, mtime 11:05:22) | `03e8a99e2e447e4c5e7067dea191450c7d5ec10102cb33e2a246b5b3d1c02b57` |
| `census/round-99/c2-decoy-test.py` (byte copy of r98) | `9d06e806daf15b34c1c2b4e546cd9262e45e1d7c6921fd029ae2ef7b461b79cc` |
| `census/round-99/c1-survivor-search.py` (byte copy of r98) | `e8ba780a5b8d807ff199c33a679d7d8dd7259fb93e934d123b009e9f9f2649e1` |
| `census/round-99/shapes.tsv` (the frozen C1 table) | `8bc642c44e0c1f6414fb4b07aaf922c01bf2d2ea8b91bda7bac81f60a05a8a14` |
| `census/round-99/declared-shapes.py` | `7f6a0816c34eec167016253b7f3d82fedf14aa408c5fab98cc60f3e5d0711816` |

## Commands run

| # | command | exit | observed summary line |
|---|---|---|---|
| 1 | `python3 -B .ufo/waves/round-99/w1/R99Connector/crosslane-scan.py` | 0 | `SCAN-SUMMARY lanes=10 files=1199 kill_files=65 cmdline_files=9 argv_identity_candidates=11 sentinel_files=0 timeout_files=448` |
| 2 | `python3 -B .ufo/waves/round-99/w1/R99Connector/data-walk.py` | 0 | `SHAPES-TABLE r95:shapes=17,mismatched=3 r97:…=3 r98:…=0`; `SEARCH-SUMMARY {… killed:139, survived:76}`; `MUTC1 mutants=11 killed=9 survived=2`; `MUTC2 mutants=5 killed_by_a_predicate=1 survived_both=4`; `CLASS-COUNT total=10 targeted=2 residual=7 …` |
| 3 | `python3 -B .ufo/waves/round-99/w1/R99Connector/subreaper-topology-probe.py` | 0 | `TOPO-SUMMARY A_escapee_reached=False A_carrier_reached=False B_escapee_reached=True B_carrier_reached=False verdict=PASS` |
| 4 | `python3 -B .ufo/waves/round-99/w1/R99Connector/reap-rule-probe.py` | 0 | `REAP-RULE-SUMMARY control_killed=True escapee_killed=False other_carrier_killed=False spawned_escapee_leaked=True verdict=EXPECTED_LEAK` (bytes `03e8a99e…`) |
| 5 | `python3 -B census/round-99/declared-shapes.py --freeze census/round-99/shapes.tsv --search census/round-99/c1-survivor-search.py --scripts census/round-98/shapes --work <scratch>/sh1` | 0 | `FREEZE sha256=8bc642c4…`; `SHAPES-SUMMARY shapes=17 mismatched=0` |
| 6 | same with a relabelled copy of the frozen TSV (`q1o=declared, q1q=declared, q1i=crash`), sha `004356d7…` | 1 | `FREEZE sha256=004356d7…`; `SHAPES-SUMMARY shapes=17 mismatched=3` (q1o, q1q, q1i MISMATCH) |
| 7 | `sha256sum census/round-99/c2-setup-arms.py`; `grep -n "_reap_owned\|_is_descendant\|spawn_pid\|prctl\|branch" census/round-99/c2-setup-arms.py` | 0 | `03e8a99e…`; branch (c) absent — only `_is_descendant(pid, spawn_pid)` at ll. 187, 374; `_set_child_subreaper()` still called at l. 222 |
| 8 | `git status --porcelain` (read-only) | 0 | `?? census/round-99/` (sibling executor's untracked instrument dir; not this seat) |

Receipts: `crosslane.out`, `data-walk.out`, `subreaper-topology.out`, `reap-rule.out`,
`c1-frozen.out`, `c1-relabelled.out`. Instruments: `crosslane-scan.py`, `data-walk.py`,
`subreaper-topology-probe.py`, `reap-rule-probe.py`.

---

## 1. Cross-lane overlap scan: argv-identity kills, crash-sentinel, probe-timeout

Scope: `/home/vgpnk/Projects/shokunin/*/tools` (recursive) and `/home/vgpnk/Projects/shokunin/scripts`
(fleet root; `considerthese`/`shokuknow` untouched). 1199 text files, 10 roots. Full output:
`crosslane.out`.

### 1.1 Per-lane surface counts

```
chousa-shokunin   files=21   kill=2  killpg=0  cmdline=0 pgrep=0 new_session=0 timeout=8   cand=0
kaidoku-shokunin  files=337  kill=6  killpg=4  cmdline=3 pgrep=0 new_session=4 timeout=120 cand=0
kama-shokunin     files=175  kill=31 killpg=22 cmdline=2 pgrep=3 new_session=22 timeout=106 cand=4
kotodama-shokunin files=171  kill=0  killpg=0  cmdline=0 pgrep=0 new_session=0 timeout=13  cand=0
mado-shokunin     files=36   kill=4  killpg=1  cmdline=0 pgrep=2 new_session=1 timeout=12  cand=1
mori-shokunin     files=60   kill=6  killpg=6  cmdline=0 pgrep=5 new_session=6 timeout=32  cand=2
souji-shokunin    files=151  kill=7  killpg=1  cmdline=2 pgrep=2 new_session=2 timeout=19  cand=4
tameshi-shokunin  files=63   kill=1  killpg=1  cmdline=0 pgrep=0 new_session=2 timeout=26  cand=0
tsukuroi-shokunin files=165  kill=6  killpg=3  cmdline=2 pgrep=0 new_session=3 timeout=108 cand=0
scripts(fleet)    files=20   kill=2  killpg=0  cmdline=0 pgrep=0 new_session=1 timeout=4   cand=0
```

`cand` = a file holding a kill primitive plus a `/proc/<pid>/cmdline` reader or a pgrep/pid-from-text
path. Eleven candidates; each was read at the cited lines. Verdicts:

| candidate | lines | verdict |
|---|---|---|
| `kama/tools/kama-context-capacity.py` | `os.killpg(proc.pid)` :565/:573; `pgrep -x llama-server` :220 | **FALSE POSITIVE** — pgrep is before/after *observation*; killpg is its own `Popen` child |
| `kama/tools/round49-replay-witness-audit.py` | `p.kill()` :317/:335; `open(/proc/{pid}/cmdline)` :267 | FALSE POSITIVE — cmdline hashes the `-m` model arg; kill is its own child |
| `kama/tools/round64-c1-counter.py` | `os.kill(pid, SIGKILL)` :994; cmdline :400; `os.kill` inside `FAKE_MODES['detach']` string :1215 | FALSE POSITIVE — kill is `kill_if_same(pid, ticks)`, starttime-verified (`/proc/<pid>/stat` field 22); the :1215 hit is a planted-forger fixture |
| `kama/tools/round64-c2-counter.py` | `os.killpg(pid, SIGKILL)` :770; pgrep :264 | FALSE POSITIVE — own `Popen` child; pgrep is observation |
| `mado/tools/mado-tripwire.py` | `pkill`/`killall`/`pgrep` strings :264/:271 | FALSE POSITIVE — a host-mutation *blacklist*, not a kill |
| `mori/tools/mori-round13-regressions.py` | `os.killpg(os.getpgid(proc.pid))` :1366; pgrep at :1021 | FALSE POSITIVE — pgrep is inside a generated stub script; kill is its own child |
| `mori/tools/mori-round14-regressions.py` | :2302 / :812 | FALSE POSITIVE — same |
| `souji/tools/souji-census.sh` | watchdog pid chosen by argv among `/proc/<census-child>/task/<pid>/children` :2816; `kill -TERM/-KILL "$term_census_pid"` :2885/:2913; `kill -KILL "$term_launcher_pid"` :2915 | **SCOPED CANDIDATE** — argv *selects* a candidate, but candidates are limited to the census's own children; the kill authorizes by a recorded pidfile under a `/proc/<pid>` existence test only (no starttime re-verify). See F3 |
| `souji/tools/souji-quarantine.sh` | `kill -STOP/-KILL "${pids[@]}"` :212-213; `q_proc_runs_self` cmdline gate :217-219 | FALSE POSITIVE for argv-as-kill: the kill selector is the session id (`/proc/<pid>/stat` field 6, `q_proc_sid`); cmdline only admits a nested call whose session leader is this tool |
| `souji/tools/souji-seat-audit.py` | :119/:637-642 | FALSE POSITIVE — the audit's own regex/test strings (`pgrep x | xargs kill` is a *subject* string) |
| `souji/tools/souji-vault-verify.sh` | `kill -STOP/-KILL "$k"` :288/:304; group kill :314-316 | FALSE POSITIVE — targets are the pre-kill descendant snapshot with `stat` field 22 re-verified (`[ "${20}" = "${start_of[$k]}" ]`); pgrep appears only in comments |

### 1.2 Verdict: zero true cross-lane argv-identity kill sites

No sibling lane derives a signal target from argv text. The only argv-shaped candidate is souji's
own `souji-census.sh`, and it is bounded to the census's own child tree (F3). Therefore the r99 C2
repair is not a cross-lane API change, and no sibling has the r97 defect.

### 1.3 Crash-sentinel surface: no sibling consumer

`grep -rlE 'sys\.monitoring|excepthook|unraisablehook|faulthandler|EXCEPTION_HANDLED|RERAISE|setprofile|settrace'`
over all lane `tools/` and `scripts/` returns **0 files** for the sentinel pattern proper. The only
hits are `kama/tools/round58-battery-exec-check.py:157` and `round59-battery-outcome-check.py:119`,
both `sys.setprofile` call/return *tracers* for execution checks — not an exit-code sentinel and not
read by C1. C1 (calibration) has no cross-lane consumer and no cross-lane constraint.

### 1.4 Probe-timeout surface: broad, and the siblings already hold the C2 mechanism

448 files use `TimeoutExpired`/`communicate(`/`.wait(timeout`; 65 files hold a kill primitive; 25
files pair `start_new_session`/`setsid` with a group kill. The mechanism-nearest siblings (all
read-only audited):

- `kama/tools/round50-…-56-replay-*-audit.py`: `descendants(root)` builds `{pid: starttime}` from
  `/proc/<pid>/stat` fields 4/22 at :279-295; the snapshot is taken **while the arm is alive**
  (`snap = descendants(p.pid)` :450, :505); `reap()` :425-437 kills by `(pid, starttime)` and then
  `killpg(p.pid)`. This is the r98/r99 ownership rule's *snapshot-before-orphan* variant.
- `kama/tools/round64-c1-counter.py`: `kill_if_same(pid, ticks)` :989-996 — starttime-verified
  single-pid kill (measured above).
- `souji/tools/souji-vault-verify.sh`: `cli_kill_tree` takes the descendant snapshot before the
  job-controlled grandchild can leave the group (comment :311-313) and re-verifies field 22 at
  :286-288 before both STOP and KILL.
- `tameshi/tools/registry-check.py`: the closest twin of the whole C2 program — child subreaper
  (`_enable_child_subreaper` :392-417), `pidfd` signalling, `(pid, starttime)` identity
  (`_row_identity_is_owned` :468-487), and a pre-run `baseline_children` snapshot
  (`_direct_child_identities` :455-466) so cleanup does not claim a pre-existing child. Its docstring
  already states the double-fork invariant: “a double-forked descendant cannot reparent past the
  subreaper” (:42-46).
- `souji/tools/souji-quarantine.sh`: session-id kill selector (`q_kill_session` :201-215).
- Foreign-decoy tests: no sibling lane has a committed *decoy* direction test. `grep -rli decoy`
  hits are fixture/fixture-like strings and research gates, not process-ownership tests; the r98
  decoy test remains the fleet's first.

---

## 2. Data-walk: surviving classes in the r98 evidence, and which r99 targets

Source: `census/round-98/records/*.txt`, `search-r98.log`, `survivors-r98.json`, and
`.ufo/waves/round-98/w1/R98MutC1.md`, `R98MutC2.md`, `R98Sentinel.md`. All numbers below are parsed
from those files by `data-walk.py`; none is copied from prose.

### 2.1 Raw counts

```
SHAPES-TABLE  r95 shapes=17 mismatched=3 | r97 shapes=17 mismatched=3 | r98 shapes=17 mismatched=0
SEARCH-SUMMARY generated=278 ambiguous=9 uncompiled=0 hung=1 scored=268 errored=53 killed=139 survived=76
SEARCH-SURVIVOR-OPERATORS or->and:18 0->1:15 1->0:11 True->False:6 not->(deleted):6 and->or:6 <-><=:5 False->True:3 >->>=:3 >=->>:1 <=-><:1 ==->!=:1
MUTC1 mutants=11 killed=9 survived=2  survivor_ids=['M-TRACE','M-INVEHCOND']   (both equivalent, per the report)
MUTC2 mutants=5  killed=1 survived=4  survivor_ids=['M1 no-ppid-walk','M3 no-starttime','M4 spawn-pid-only','M5 reap-first']
DECOY r97 planted=83 dead=60 alive=23 verdict=killed exit=1
DECOY r98 planted=83 dead=0  alive=83 verdict=spared exit=0
DECOY cm8 planted=83 dead=82 alive=1  verdict=killed
SENTINEL findings=5   (F1 decoy-token mismatch, F2 no foreign signal, F3 /tmp guard, F4 branch-(c) over-reach, F5 survivors vacuity)
```

The three rows the M6 relabel attack moves are `q1o`/`q1q`/`q1i` (r97: 1→1, 1→1, 0→70; r98: 1→70,
1→70, 0→0). `t1`/`t4` were r95 mismatches fixed before r97 and are not part of the M6 attack.

### 2.2 Class table (10 classes; counts are items in the class)

| # | axis | class | n | evidence | r99 |
|---|---|---|---|---|---|
| 1 | C1 | label-movability (M6/Q173): the runner's hard-coded kinds move the count with the hook unchanged | 3 rows | R98Critic K2 + verifier spotcheck; measured below | **TARGETED by C1** |
| 2 | C1 | equivalent survivors (`M-TRACE`, `M-INVEHCOND`) | 2 | MUTC1 | not a predicate hole |
| 3 | C1 | search survivors on the 10-target hook population | 76 | `search-r98.log` + `survivors-r98.json` (76 rows) | not targeted (operator-level; r98 no-harm control) |
| 4 | C2 | no-signal mutants (M1 ppid-walk redundant, M5 reap-first) | 2 | MUTC2 F1/F5 | not targeted; the r99 rewrite still exercises neither |
| 5 | C2 | escapee leak / no-op reap (M4 spawn-only; F5 survivors vacuity) | 2 | MUTC2 F2, Sentinel F5, Connector C-5 | **NOT targeted — re-opened by r99, measured (F1)** |
| 6 | C2 | cross-arm over-reach (counter-descendant carrier) | 1 | Sentinel F4 `cross_arm_probe`: carriers=3 signalled=3 | **TARGETED by C2** |
| 7 | C2 | spawn-pid starttime not exercised (M3) | 1 | MUTC2 F4 | not targeted |
| 8 | C2 | decoy-token coupling (test token vs counter `--work`) | 1 | Sentinel F1 | not targeted; r99 keeps the decoy bytes `9d06e806…` |
| 9 | C2 | /tmp guard accepts bare `/tmp` | 1 | Sentinel F3 | not targeted |
| 10 | C2 | probe-side basename cheat | 1 | R98Critic K5 / R97Critic | not targeted |

Arithmetic: **targeted = 2 classes / 4 items** (label rows 3 + cross-arm carrier 1); **open residual
= 7 classes / 84 items** (76+2+2+1+1+1+1); **equivalent = 1 class / 2 items** (not a hole). The r99
claims target one class per axis; the largest residual classes are the 76 generated-search survivors
(C1, operator-level, not a predicate hole by the r98 report's own reading) and the two C2 ownership
classes the round does not touch.

### 2.3 The r99 C1 target, measured

Command #5 (frozen `shapes.tsv`, sha `8bc642c4…`): `FREEZE sha256=8bc642c4…`, `SHAPES-SUMMARY
shapes=17 mismatched=0`, exit 0. Command #6 (same runner and hook, relabelled copy sha `004356d7…`,
`q1o=declared, q1q=declared, q1i=crash`): `SHAPES-SUMMARY shapes=17 mismatched=3`, exit 1. The
labels are now read from the file, and the FREEZE line makes the relabelled copy distinguishable.
**M6 is closed at the instrument level**, provided the claim quotes the frozen hash: a relabelled
copy is green only against its own hash, not against the claim.

### 2.4 The r99 C2 target, measured — and the contradiction

The committed r99 counter (`03e8a99e…`) removes branch (c): `_reap_owned` authorizes only the spawn
pid (starttime re-verified) or an `_is_descendant(pid, spawn_pid)` chain (ll. 164-196); the survivors
loop counts the same population (ll. 361-376). Measured on the committed bytes with a live topology
(`reap-rule-probe.py`):

```
REAP-RULE pre={'e': 2813614, 'w': 2813613, 'p': 2813608, 'q': 2813609, 'k': [2813610]} signalled=1
REAP-RULE escapee_is_counter_child=True other_carrier_is_counter_child=True control_is_spawn_descendant=[True]
REAP-RULE-SUMMARY control_killed=True escapee_killed=False other_carrier_killed=False spawned_escapee_leaked=True verdict=EXPECTED_LEAK
```

- The spawn-chain control `k` is SIGKILLed (`signalled=1`) — the rule works in its intended direction.
- The cross-arm carrier `w` (counter child, not a spawn-chain member) survives — the r99 property holds.
- **The T1 escapee `e` (counter child, session leader) also survives** — it is by construction the
  same shape as the carrier the round wants spared.

This is not an artifact: the executor's own r99 receipt
`.ufo/waves/round-99/w1/R99ExecC2/counter-r99.out` shows `ARM T1 … survivors=0` and its report
records `--survivors 0 planted-killed 0--` plus the escapee `3624139` alive after the run with
`ppid 1525`, `sid 3624139`. The r99 counter's own comment says it: “After the fixture parent exits,
the setsid escapee's ppid chain may no longer reach the spawn pid (open limit, reported with observed
evidence); it is then NOT killed.” (ll. 358-359). The counter's top docstring (ll. 4-9) still
describes the r98 branch (c) as present — see F2.

The contradiction in one sentence: **“a counter-descendant carrier that is not a spawn-chain member
is NEVER killed” and “the counter reaps its own T1 escapee” cannot both hold once the probe exits**;
the escapee becomes a counter child at that moment, and the r99 rule deliberately excludes it. The
r99 predicate as worded does not notice, because `survivors=0` is spawn-chain-only and vacuous
(C-5/F5) and `planted-killed` is not in the frozen sentence. The round therefore improves the
false-positive direction (foreign decoy, cross-arm carrier) while regressing the false-negative
direction it inherited from r98 — the exact class R98MutC2 called its strongest finding (M4/F2).

---

## 3. Proposed move (one, bounded): arm-scoped subreaper + reap during the arm

### 3.1 Evidence the move is available

The measured kernel semantics (`subreaper-topology-probe.py`, exit 0):

```
EXEC parent_before=0  parent_after_set=1  exec_child_sr=0      # PR_SET_CHILD_SUBREAPER is NOT preserved across execve
FORK child_sr=0                                               # and is not inherited by fork
TOPO-A counter_subreaper=1 probe_subreaper=0 … escapee_ppid=counter  spawn_chain_reaches_escapee=False
                                               carrier_ppid=counter  spawn_chain_reaches_carrier=False
TOPO-B counter_subreaper=1 probe_subreaper=1 … escapee_ppid=probe(spawn) spawn_chain_reaches_escapee=True
                                               carrier_ppid=other-probe  spawn_chain_reaches_carrier=False
TOPO-SUMMARY A_escapee_reached=False A_carrier_reached=False B_escapee_reached=True B_carrier_reached=False verdict=PASS
```

Topology A is the committed rule: both orphans reparent to the counter, so the spawn-chain-only rule
reaches neither. Topology B sets the subreaper on the **arm's probe** and keeps it alive: the T1
escapee reparents to the recorded spawn pid (`_is_descendant(e, spawn) == True`), so the *existing*
rule kills it; the other arm's carrier reparents to its own probe and is never in T1's chain.
Because the flag does not survive execve, it must be set inside the probe process itself (a
`prctl(36,1)` at the top of a round-99 probe copy) or by a live forked wrapper — **not** by
`preexec_fn` on the `Popen`.

### 3.2 The move

1. Give each arm's probe a child-subreaper net of its own: `prctl(PR_SET_CHILD_SUBREAPER, 1)` at
   probe start (round-99 probe copy; FATAL if unavailable, matching the counter's current policy).
2. Reap the T1 arm **while the arm runs**: in the counter's arm loop, poll the existing
   `_reap_owned(fx, (os.getpid(), p.pid), spawn)` every ~50 ms until `p.poll()` returns (plus the
   final reap already present). The escapee is the probe's child from the moment its fixture parent
   exits until the probe exits (the probe lives out its own timeout), so the poll is deterministic.
3. Keep branch (c) removed exactly as committed; the cross-arm carrier is never in the T1 spawn
   chain (TOPO-B), so the r99 cross-arm property is preserved by construction.
4. Bind the escapee's fate with a byte that can move: the T1 arm's `planted-killed` (or an explicit
   `escapee_alive=no`), **not** `survivors=0`, which is spawn-chain-only and vacuous (C-5/F5).

### 3.3 Affected axes

- **Operability (C2, 8): improves.** The false-positive direction the round targeted is kept
  (foreign decoy spared, cross-arm carrier spared); the false-negative direction the round silently
  dropped (escapee leak) is restored, and the witness byte can actually move. No new kill branch.
- **Calibration (C1, 7): untouched.** No shape, runner, frozen file, or C1 predicate involved.
- **Coverage: unchanged.** No new surface; the probe copy is an instrument change.

### 3.4 Risks

- **Probe change.** The probe is an r98 instrument; if the L1 freezes its bytes, the alternative is a
  live fork wrapper as the recorded spawn pid (more plumbing) or accepting the leak as a documented
  limit. The flag is not settable across exec (measured), so a `preexec_fn` cannot deliver it.
- **Early kill changes T1 timing.** Killing the escapee closes the held pipes earlier; the T1 arm
  must still print the `C2-FORGERY-FATAL:` line and exit 2. Measure the arm before/after.
- **Poll cost.** One `/proc` scan per 50 ms on the single T1 arm; bounded, but it must not be added
  to all 20 arms.
- **Witness drift.** If the predicate keeps `survivors=0` as the T1 bind, the leak stays invisible
  even after the move; the predicate byte must change (L1 owns the freeze).

### 3.5 Verification (for the L1/executor, not run here)

1. `subreaper-topology-probe.py` → `TOPO-SUMMARY … verdict=PASS` on the host kernel.
2. r99 counter on a copied probe with the subreaper + polled reap: `ARMS-SUMMARY arms=20 conform=20`,
   `ARM T1 exit=2 … planted-killed 1`, no survivor carrying the fixture token after the run.
3. Cross-arm probe (the r99 ExecC2b instrument) against the moved counter: every carrier alive,
   `signalled=0`.
4. Decoy test r99 vs r97 vs CM8 unchanged: `verdict=spared` / `killed` / `killed`.
5. `declared-shapes.py --freeze census/round-99/shapes.tsv …` → `shapes=17 mismatched=0` with
   `FREEZE sha256=8bc642c4…` (C1 must not move).

---

## Findings (each with a reproducer under this seat's directory)

### F1 — MEDIUM (operability) — the r99 branch-(c) removal leaks the T1 escapee; the predicate cannot see it

The committed r99 rule kills the spawn-chain control and spares both counter-descendant carriers —
including its own escapee. Measured on `03e8a99e…`:

```
control_killed=True escapee_killed=False other_carrier_killed=False spawned_escapee_leaked=True verdict=EXPECTED_LEAK
```

End-to-end corroboration: `.ufo/waves/round-99/w1/R99ExecC2/counter-r99.out` (`ARM T1 … survivors=0`,
`planted-killed 0`) and the executor report's escapee `3624139` alive with `ppid 1525`, `sid
3624139`. This is MUTC2-F2/M4 and Sentinel-F5 re-opened by the r99 wording. Reproducer:
`reap-rule-probe.py` → `reap-rule.out`. Not edited in place (predicate is the L1's to freeze).

### F2 — LOW (wording) — the r99 counter's top docstring still documents branch (c)

`census/round-99/c2-setup-arms.py` ll. 4-9 say “or (c) an orphan reparented to the counter itself (the
counter sets PR_SET_CHILD_SUBREAPER …)”, while `_reap_owned` ll. 164-168 and the survivors loop
ll. 370-375 implement the opposite (“r98 branch (c) removed”, “it is then NOT killed”). An auditor
reading only the module docstring gets the r98 rule. Reproducer: `crosslane.out` §counter audit is
not needed — the line numbers are in command #7. Doc-only; no predicate impact.

### F3 — LOW (cross-lane, same class as C2) — `souji-census.sh` kills an argv-selected pid with no starttime re-verify

The watchdog pid is selected by matching `souji-census-watchdog` + pgid in a child's `/proc/<pid>/cmdline`
(`:2810-2828`), recorded to a pidfile, then killed at `:2913-2915` after only `-e /proc/$pid`. A
recycled pid between selection and signal would be signalled. Every other recorded-pid kill in the
fleet re-verifies starttime (kama `kill_if_same`, souji-vault-verify field 22, tameshi `pidfd` +
starttime). Reproducer: `crosslane.out` candidate 8. Bounded to the census's own child tree, hence
LOW; the fix is the same `(pid, starttime)` predicate r99 is freezing.

### F4 — INFO (positive cross-lane result) — zero argv-identity kill sites and zero crash-sentinel consumers outside souji

11 candidates audited; zero true argv-identity kills; the only scoped one is souji's own census
watchdog (F3). The r99 C1/C2 repairs are not cross-lane API changes. The nearest siblings already
hold the C2 mechanism (`kama round50-56` snapshot-before-orphan; `souji-vault-verify` starttime
re-check; `tameshi registry-check` subreaper+pidfd+baseline children), so the move in §3 has fleet
precedent. Reproducer: `crosslane.out`.

### F5 — LOW (C1 predicate hygiene) — the frozen table works, but the claim must quote the hash

Frozen `8bc642c4…` → `mismatched=0` (exit 0); relabelled `004356d7…` (`q1o=declared, q1q=declared,
q1i=crash`) → `mismatched=3` (exit 1). The FREEZE line is the only thing that distinguishes the
claim artifact from a relabelled copy; if the report cites only the summary line, the M6 attack
still passes in prose. Reproducers: `c1-frozen.out`, `c1-relabelled.out`.

---

## Defects / sign-off

- No lane, fleet, sibling, or git mutation by this seat; `git status --porcelain` shows only the
  sibling executor's untracked `census/round-99/`.
- No `/tmp` writes; no sysctl mutation; no tool install; no L0 question.
- Scratch `/fast/scratch/hyaku/souji-r99/R99Connector/` deleted before yield (`rm -rf` — probes,
  relabelled table, work dirs). Durable copies: this report plus
  `crosslane-scan.py`, `crosslane.out`, `data-walk.py`, `data-walk.out`,
  `subreaper-topology-probe.py`, `subreaper-topology.out`, `reap-rule-probe.py`, `reap-rule.out`,
  `c1-frozen.out`, `c1-relabelled.out`.
- Verification not run by this seat (main agent's / L1's job): the full 20-arm counter run on the
  proposed probe copy, the cross-arm probe, and the post-freeze predicate re-measure.

Report: `.ufo/waves/round-99/w1/R99Connector.md`
