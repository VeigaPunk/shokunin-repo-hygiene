# Round 99 — the shape labels move into a frozen, pinned file (C1 admitted-candidate); the spawn-chain reap spares the decoy but loses the T1 escapee (C2 harmed, not admitted)

Lane base `c94d678c8a76f3f87f73b49a11a9d4e2aff73e3b`. Plan with frozen predicates and amendments: `plans/round-99.md`
(A0.1 frozen predicates; A99.1 pin, filed after the wave scored; A99.2 C2 narrowing and harm record). Wave: one v1 wave,
14 seats (`w1`; evidence copied to `census/round-99/wave-evidence/`). Attack share 5/14 (36 %); connector 1.

## Claims and verdicts

- **C1 (calibration 7; Q173).** The declared-exit shape table reads its kind labels from `census/round-99/shapes.tsv`
  through `census/round-99/declared-shapes.py`, pinned by sha256. The r98 object-keyed latch hook is unchanged.
  Verdict: **admitted-candidate** (L1 measurement; the non-author closure decides, and it must also rule on the
  post-scoring pin A99.1). Measured on committed bytes, `census/round-99/records/c1-r99.txt`:
  - M1 pinned file, r98 hook: `FREEZE sha256=8bc642c4…a8a14`, `SHAPES-SUMMARY shapes=17 mismatched=0`, EXIT 0.
  - M2 relabelled copy (q1o, q1q → declared; q1i → crash), pin enforced: `SHAPES-FATAL … != pinned`, EXIT 2.
  - M3 the same relabelled copy with its own hash pinned (the count without the pin): `shapes=17 mismatched=3`, EXIT 1,
    rows q1o, q1q, q1i named.
  - Controls on the pinned file: r95 hook `mismatched=3` (t1, t4, q1i), EXIT 1; r97 hook `mismatched=3` (q1o, q1q, q1i), EXIT 1.
  The r98 do-nothing failure (M6, below) was a relabelled label set reaching `mismatched=0` on the r98 hook. That
  specific attack is now refused by M2.
- **C2 (operability 8; Q174, Q175, Q176).** The arms counter reaps only the recorded spawn pid and its ppid-chain
  descendants. Verdict: **harmed (trade); not admitted.** The frozen decoy predicate is met (foreign carriers spared,
  CM8 argv-only mutant killed), but the T1 setsid escapee is no longer reaped. Measured by a live-process count after
  each counter exits, on the same probe and fixtures. The valid receipt is `census/round-99/records/c2-escapee-r99.txt`
  (the `ESCAPEE-ALIVE` lines inside `c2-counter-*.txt` are superseded: `census/round-99/records/c2-escapee-NOTE.txt`):

      r99 counter   ESCAPEE-ALIVE alive=1   (decoy-r99: DECOY-SUMMARY verdict=spared, 83/83 alive)
      r98 counter   ESCAPEE-ALIVE alive=0   (decoy-r98: verdict=spared)
      r97 counter   ESCAPEE-ALIVE alive=0   (decoy-r97: verdict=killed, 60 dead)
      CM8 argv-only (decoy-cm8): verdict=killed, 82 dead

  Decoy spare under r99 adds no discrimination over r98, which already spared the decoy. The only new effect of the
  r99 rule is the escapee leak, so C2 cannot be admitted under the no-harm rule.

## Gate

Source rows re-opened live this round (R99ScoutSources; URL · access date · located quote, ≤25 words · location).
Each live fetch is HTTP 200 and byte-identical to its committed capture; each quote occurs exactly once in the live
fetch and in the capture:

| row | URL | access | located quote | location |
|---|---|---|---|---|
| S372 (re-verified; grounds C1's object-keyed latch) | https://docs.python.org/3/library/sys.monitoring.html | 2026-11-09 | "An exception is re-raised, for example at the end of a finally block." (13 words) | § Events, RERAISE; occurrence 1 live and in census/round-97/srcs/monitoring.html |
| S075 (re-verified; grounds C2's starttime field 22) | https://man7.org/linux/man-pages/man5/proc_pid_stat.5.html | 2026-11-09 | "The time the process started after system boot." (8 words) | § DESCRIPTION, field (22) starttime; occurrence 1 live and in census/round-98/srcs/proc_pid_stat.5.html. Field (4) ppid quote "The PID of the parent of this process." occurrence 1 (S332 is the kernel emission order) |
| S368 (re-verified; grounds the new-session escape) | https://man7.org/linux/man-pages/man2/setsid.2.html | 2026-11-09 | "The calling process also becomes the process group leader of a new process group in the session" (17 words) | § DESCRIPTION; occurrence 1 |

No `corpus/SOURCES.md` row was added or changed. Sources-census before and after: `scripts/sources-census.sh validate
--root /home/vgpnk/Projects/shokunin souji`, exit 0, 294 rows (`census-before` at round start, 294 rows; the end run is
recorded in the report). The sourced claim is C1, which rests on S372 opened this round.

Non-author discernment: the Reviewer, Critic and Sentinel seats are non-author. They agreed with the counts and disagreed
with the C1 binding (Reviewer1 duplicate and missing rows) and with the C2 reap leg (Sentinel FINDING 1, Reviewer2 F2,
Critic under-kill). Admit/reject sample: admit = C1 freeze file (the labels a runner reads; the count moved under relabel
and is refused under the pin); reject = C2 spawn-chain reap, which the escapee measurement refutes.

Assimilation: none this round (no `merge/souji/` theme taken). considerthese: the lane has no `considerthese/` dir.

## Mistakes

- **M9 — a freeze file whose hash is printed but not checked (class: scope / do-nothing control movable).** Evidence:
  R99Reviewer1 (duplicate row `shapes=18 mismatched=0`, missing row `shapes=16 mismatched=0`); R99Scribe M9. Captured-by:
  none — the r98 M6 fix made labels a file, not a binding; Q173 said "the count must be able to move" and not "the file
  must be pinned". Fix: `--expect-sha256` required, 17 distinct names checked, rc 2 on mismatch (A99.1). **Shown able to
  fail:** M2 refuses the relabelled copy with `SHAPES-FATAL`, M3 moves the unpinned count to 3.
- **M10 — a narrowed ownership rule planned on a wrong reparenting assumption (class: vacuous count / survivor).**
  Evidence: `plans/round-99.md` A0.0 claimed the T1 escapee "remains owned via the subreaper reparent … a spawn-chain
  member by the recorded parent field". The subreaper reparents it to the counter, so its ppid chain never reaches
  the spawn pid. Result: `survivors=0` with `planted-killed 0` (`c2-counter-r99.txt`); `ESCAPEE-ALIVE alive=1`.
  Captured-by: Q176 captured a starttime-binding error, not the ppid-chain escapee; R98 FINDING 4 warned of branch (c)
  but did not say the escapee leaks without it. Fix (routed r100, not shown able to fail yet): an escapee ownership key
  that is not the ppid chain, with a positive escapee-reap predicate. **Current state:** the predicate that would catch
  it is the `ESCAPEE-ALIVE` count above, which is a measurement, not yet a frozen counter row.
- **M11 — a cross-arm probe whose carriers reach a live counter through a zombie/storm (class: environmental confound).**
  Evidence: R99Critic (3 of 4 cross-arm runs confounded by sibling decoy storms; T1 `exit=-15`; carriers `S→Z`); R99MutC2
  §A (signal traces). Captured-by: none. Fix: the clean spared verdict is taken only from a run whose carriers reach
  init without a concurrent storm; the measured runs are named in the report. **Not shown able to fail as a frozen
  rule** (noted as a limit).
- **M12 — the L1's own escapee probe searched a doubled token path (class: vacuous count; L1-authored).** Evidence:
  the first `census/round-99/c2-measure.sh` built `<work>/arms/arms/fixture-pipe-holder.py`, so `ESCAPEE-ALIVE alive=0`
  appeared for all three runs (`census/round-99/records/c2-counter-*.txt`). Caught by the L1 before any claim cited it,
  by re-deriving the one token that the counter's own `piphole` joins. Captured-by: none. Fix: `escapee()` takes the
  counter `--work` and appends the file name once; the valid receipt `records/c2-escapee-r99.txt` and the superseding
  note `records/c2-escapee-NOTE.txt` are committed; the void lines are kept, not deleted.
- **M13 — the plan was written to the fleet root and the amendments to the lane (class: landing / misroot; L1-authored).** Evidence: the first `write` of `plans/round-99.md` used a relative path and landed at `/home/vgpnk/Projects/shokunin/plans/round-99.md` (fleet root). The amendment `cat >>` then created a lane file holding only A99.1/A99.2 (2870 bytes). Found by the §3 misroot sweep (`git status --porcelain` at the fleet root). Captured-by: none. Fix: the fleet copy (4595 bytes, the A0.x frozen predicates) was concatenated byte-exact before the lane amendments (7465 bytes; `cmp` verified; `head -c 4595` equals the fleet bytes), committed as `118e5b7d`, and the fleet copy and its `plans/` directory were deleted (one fleet-root deletion, by the sweep rule).

Sweep for further mistakes: `grep -c '^- \*\*M' corpus/lessons/round-99.md` after the report; no other defect found in the
wave outputs beyond the seats' own findings (R99Sentinel FINDING 1 is M10; R99Connector `EXPECTED_LEAK` is M10).

## Wave findings (summary; full verdicts in `census/round-99/wave-evidence/`)

- C1: ExecC1 (runner, relabel 0→3), ExecC1b (controls r95/r97 mismatched=3), Reviewer1 (duplicate/missing row, pin needed),
  Reviewer2 (C2 wording: starttime, killpg, escapee), Critic (C1 binding narrowed; C2 under-kill), MutC1 (runner mutants).
- C2: ExecC2 (counter build: spawn-chain-only; decoy spared; escapee alive), ExecC2b (cross-arm probe; storm confounds),
  Sentinel (zero positive-pid kills under strace; escapee not reaped = FINDING 1), MutC2 (m_bb restore-branch-(c) killed
  by cross-arm only; m_noppid, m_nosttime, m_spawnonly survive all predicates), Connector (`EXPECTED_LEAK`),
  ScoutSources (re-verification), Scribe (M9–M11 drafts), ExecCensus (population no-harm; see below).
- No-harm (C1 population): `census/round-99/c1-survivor-search.py` is a byte copy of the r98 search, so its population
  verdicts are unchanged by construction; the 278-mutant run is `wave-evidence/R99ExecCensus.md` (see the report for its
  summary line).

## Trend verdicts (lane)

- expansion: **unchanged**. No registry row added; S372, S075 and S368 re-verified only.
- quality: **improved** (C1 freeze-file binding and pin, the relabel attack now refused; Q177 drafted from M9). The
  C2 leg is recorded as a harm, not a quality gain.
- discernment: **harmed** for C2. The pre-freeze gate missed the escapee leak (M10) and the unpinned freeze hash (M9) was
  caught by attack seats. M11 is a measured confound.

## Frontier

No `merge/souji/` theme assimilated (Assimilation: none). `considerthese/`: the lane has none. The two sourced rows
(S372 for C1, S075/S368 for the C2 escapee context) were opened this round. Frontier F5 (process residue, reap authority)
is unchanged: the operator's reap-authority question is still open (`.ufo/l0-questions.md`, round-97 and round-98 lines).
