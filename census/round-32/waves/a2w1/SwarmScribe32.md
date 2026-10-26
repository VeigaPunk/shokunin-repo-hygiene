# SwarmScribe32 — r32 a2w1 lesson sections (scribe)

## Status

STATUS: PASS — `## Mistakes` rows M1-M4 and the `## Seat-reported failures` carry (all 7 non-PASS wave-1 reports,
each with a disposition and its evidence clause) are drafted at the delivery path below, grounded in bytes opened
this run; no claim, predicate, target, counter or item set was touched, and no counter was executed.

## Evidence

Lane read-only throughout; the only writes are this report and the delivery. Scratch per operator directive:
`/fast/scratch/hyaku/souji-r32/SwarmScribe32/tmp` created and exported as `TMPDIR`, removed at finish; no clone was
needed. Python 3.14.8, git 2.56.0; no tool installed or upgraded.

Tip and landed set (`git -C /home/vgpnk/Projects/shokunin/souji-shokunin log --oneline 85b61a15…..master`):

```
4e56c48 round-32: hyaku run-8 orchestrator salvage of unlanded attempt-1 census records …
9e8982b round-32: C1 capability-count binding rows (38 of 44 items: 21 bound, 17 withdrawn; 6 left unbound)
a92e1aa round-32: C3 F1 mtime-clock entry, fixture, record, S223, snapshots, docs; amendment A1 …
98e5203 round-32: C2 scratch discipline — 26 tools and fixtures take scratch from TMPDIR …
7a6667c round-32: controls, amendment A0 (C1 v2) with its controls
3ec84fc round-32: preregistration, frozen counters C1-C3, enumerations, C3 contract, M1 …
```

Frozen inputs read first: `census/round-32/records/preregistration.txt`, `census/round-32/records/amendments.txt`,
`census/round-32/c1-items.tsv`, `census/round-32/c2-items.tsv`, `census/round-32/records/controls.tsv`,
`controls-a0.tsv`, `census/round-32/c1-enumerate.py`, `c1-counter.py`, `c1-counter-v2.py`, `c2-counter.py`,
`census/round-32/c3-counter.py`, `c3-counter-v2.py`, `census/round-32/m1-r31-contract.txt`,
`tools/souji-record-contract.py`, `tests/fixtures/r20-input-binding.py`, `SCORECARD.md`, `corpus/SOURCES.md`,
`corpus/lessons/round-31.md`, the seven non-PASS wave-1 reports in full, and `SwarmCritic35.md` and
`SwarmExecutor06.md`'s delivery file `deliver-c1-bind-N35-N43-L29.md`.

1. Landed C1 row census (counted from `SCORECARD.md`, no counter run):

```
$ awk 'NR>=434 && NR<=480 && /^\| (N[0-9][0-9]|L29) \| SCORECARD/' SCORECARD.md | grep -oE '\| (run|record|field|withdrawn):' | sort | uniq -c
      9 | field:
      9 | record:
      3 | run:
     17 | withdrawn:
```

38 rows: 21 run/record/field, 17 `withdrawn:`. Absent ids (sweep over the 44 ids of `c1-items.tsv`):
`N28 N29 N30 N31 N33 N34`. This reconciles with the L1's reading in `amendments.txt:24-26`
(`unbound=6 mismatches=6 withdrawn=17`) [INFERENCE on the mismatch term; the count of rows and of withdrawals is
direct].

2. Frozen counters unchanged since the preregistration (empty output = no diff):

```
$ git -C <lane> diff --stat 3ec84fc..master -- census/round-32/c2-counter.py census/round-32/c1-counter.py \
    census/round-32/c3-counter.py tools/souji-record-contract.py
$
```

3. M1 green arm, run this seat (`python3 -B`, read-only):

```
$ python3 -B tools/souji-record-contract.py --record census/round-32/records/jj-mtime-clock-run.txt \
    --contract census/round-32/c3-contract.txt
lines=22 bad=0
exit=0
```

4. STATUS sweep of the wave-1 tree:

```
$ grep -m1 '^STATUS:' /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-32/w1/Swarm*.md | wc -l
41
$ for f in Swarm*.md; do v=$(grep -m1 '^STATUS:' "$f" | awk '{print $2}'); case "$v" in PASS) ;; *) echo "$f -> $v";; esac; done
SwarmCritic34.md -> FAIL
SwarmCritic36.md -> PARTIAL
SwarmExecutor04.md -> PARTIAL
SwarmExecutor05.md -> PARTIAL
SwarmExecutor14.md -> PARTIAL
SwarmScribe26.md -> PARTIAL
SwarmSimplifier44.md -> PARTIAL
```

5. C3 landed surfaces: `corpus/SOURCES.md:168` carries S223; `grep -c 'S224' corpus/SOURCES.md` is `0`;
`corpus/lessons/round-32.md` is absent at `master`; the entry, fixture and record exist
(`corpus/knowledge/jj-abandoned-object-mtime-clock.md`, `tests/fixtures/r32-jj-mtime-clock.sh`,
`census/round-32/records/jj-mtime-clock-run.txt`).

Gates used as evidence: the M1 red receipt committed at `3ec84fc` and the M1 green arm run above. Gates not run by
this seat: `c1-counter.py`, `c1-counter-v2.py`, `c2-counter.py`, `c3-counter.py`, `c3-counter-v2.py` — their landing
readings stay the L1's, and the salvaged after-records stay unverified here.

## Findings

1. **C1's frozen target is already missed on landed bytes, independent of any counter run.**
   `SCORECARD.md:434-471` carries 38 of 44 binding rows and 17 `withdrawn:` rows against a frozen cap of 8
   (`census/round-32/c1-counter.py:62`, `WITHDRAW_MAX = 8`); six ids have no row. The two wave-1 reports whose
   items produced these withdrawals (`SwarmExecutor04.md`, `SwarmExecutor05.md`) are therefore `open`, not
   answered by `9e8982b`.
2. **M1's guard discriminates but does not close.** The red receipt (`census/round-32/records/m1-red-before.txt`,
   `lines=17 bad=4`, exit 1) and the green arm observed above (`lines=22 bad=0`, exit 0) show the tool can fail and
   can pass. The escape reproduced by `SwarmCritic36.md` stands at the tip: `tools/souji-record-contract.py:44`
   and `census/round-32/c3-counter-v2.py:93` both test `"RESULT "`, so a `RESULT`-prefixed line separated by a tab
   is in the contract's scope and invisible to both guards. The tool is byte-unchanged since `3ec84fc`.
3. **C2's frozen predicate is unchanged and its cheats are unanswered.** `census/round-32/c2-counter.py` has no
   diff from `3ec84fc` to `master`; `amendments.txt:29-30` settles the attack as disclosed, not amended. The M4 row
   therefore names the C2 fix as unlanded, and the two cheat commits remain the outstanding falsification.
4. **C3 v2's new legs exist but their falsification is not committed.** `census/round-32/c3-counter-v2.py` adds
   L15-L17 (`:131`, `:333`, `:340`, `:341`), and `amendments.txt:13-22` records the green first reading
   (`legs=17 fail=0 f1_entries=5`). No committed receipt shows `SwarmCritic35.md`'s two passing cheat revisions
   (`fade71ab…`, `40d5f590…`) flipping to FAIL under v2, and their scratch trees are deleted. The M4 row states
   that gap rather than claiming the flip.
5. **Three wave-1 dispatch seats produced no report.** `w1/` holds 41 `Swarm*.md` for 44 dispatched tasks
   (`.ufo/waves/round-32/w1-dispatch.json`, 44 tasks). Pairing dispatch order with `w1-spec.json` item order gives
   the missing seats as SwarmReviewer30 (AuditPrereg), SwarmReviewer31 (ReviewControls) and SwarmMutationTester40
   (MutateC3Counter) [INFERENCE on the pairing; the 41-versus-44 count is direct]. Consequently the round has no
   recorded answer from the two seats that were to re-check controls and the C3 mutation set.
6. **Attempt-1's salvaged after-records were not used.** `4e56c48` committed `c1-after-v1.txt`, `c1-after-v2.txt`,
   `c2-after-v1.txt`, `c3-after-v1.txt`, `c3-after-v2.txt` as unverified survivors of the host crash; nothing in
   this report or in the delivery cites them. The two C1/C2 moons are reasoned from the landed row census,
   `amendments.txt`, and the reports themselves.
7. **The Gate block cannot ride on this delivery.** `SwarmScribe26.md` stayed PARTIAL for missing inputs, not for
   a missing draft; the draft exists at `.ufo/waves/round-32/w1/deliver-lesson-gate.md` and its placeholders now
   have real targets (S223 at `corpus/SOURCES.md:168`, the landed entry). S224 was never added, so any Gate row
   naming a git-gc registry row must be dropped, not re-pointed.
8. **The lane working tree is dirty with work that is not mine.** At read time `git status --porcelain` lists
   `M SKILL.md`, `M tests/fixtures/r15-preservation-frozen/expected.json`, `M tests/fixtures/r15-preservation-frozen/record.json`,
   `M tools/souji-receipt-run.py` and `?? census/round-32/records/a2-l1-salvage-tip-measure.txt`. None is written by
   this seat (my writes are gitignored under `.ufo/waves/`), and no finding above reads the worktree where it differs
   from `master`; the C1 row census used `SCORECARD.md`, which is clean.

Touched surfaces: `.ufo/waves/round-32/a2w1/deliver-lesson-sections.md` and `.ufo/waves/round-32/a2w1/SwarmScribe32.md`
only. No lane git or jj mutation, no fleet path, no `/home/vgpnk/Projects/shokuknow` write, no signal, no `agent://all`.

Out of scope by contract: certification OFF, K5 HELD, F5 reap and NAMESPACE holds unchanged; no credentials, no live
`/proc` census, no `census/operator-sweep-*` or `.scratch/` contents; no counter execution; no re-derivation of the
salvaged after-records; no landing, commit, or quality-score measurement.

## Deliveries

- `.ufo/waves/round-32/a2w1/deliver-lesson-sections.md` — the four `## Mistakes` rows and the
  `## Seat-reported failures` carry, plus the M1 green-arm receipt.
- `.ufo/waves/round-32/a2w1/SwarmScribe32.md` — this report.
