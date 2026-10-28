# R40w2critic14 — attack on the C3 counter's base-fixture arm (`base_killed=0`)

Seat: R40w2critic14 (critic, leaf). Lane: /home/vgpnk/Projects/shokunin/souji-shokunin.
Landed instrument revision: 128e412b0ced3c243dc27c3dd3332054a611bc2e. Base revision: 0242085909fb6a4ee041c5443d76316ac6d59d4b.
Bytes were extracted with `git show <rev>:<path>` into scratch, so every run below is against committed bytes at the landed revision, not the working tree.

## Verdict

**SAFE on the landed bytes.** No mutant is killed by the r39 base fixture, `base_killed=0` holds, and the base fixture prints its own `SUMMARY cases=... pass=... fail=...` line for all four mutants. The base fixture is live (a positive control below makes it fail), so the floor is not vacuous on these bytes.

**Contract defect in the counter (not triggered by the landed bytes):** the base arm has no liveness check. An inert or no-SUMMARY base fixture satisfies `base_killed=0` and the counter exits 0 (demonstrated below). The base arm also reads its fixture bytes from `--rev`, not `--base-rev`. Both are recorded as findings; neither changes the landed result.

## What was attacked (file:line at 128e412)

- `census/round-40/c3-counter.py:96-120` `score()`: `killed = rc==1 and fails>0 and not crash`; a missing SUMMARY returns `NO-SUMMARY`, which scores as not killed.
- `census/round-40/c3-counter.py:146` `base_src = git_show(args.root, args.rev, args.base_fixture)`. The base fixture comes from `--rev`, the candidate revision. `--base-rev` is only resolved at lines 133-136 and never read as bytes.
- `census/round-40/c3-counter.py:186-190`: an anchor count other than 1 records `(mid, False, False)` and skips the base arm for that mutant.
- `census/round-40/c3-counter.py:196-199` and `:205`: `base_killed` is computed per mutant; exit 0 requires `base_n == 0`.
- `tests/fixtures/r39-drift-record-rules.py:145-146` (`SUMMARY cases=%d pass=%d fail=%d`), `:44-45` (`ROWS`/`TOTAL`), `:67-80` (`run_case`), `:83-124` (`run_cases`), `:126-137` (`main`, which accepts `--tool` and `--work`).
- `tools/souji-worktree-drift.py:166` (the `RECORD-MALFORMED ... census schema` raise, used as the positive-control anchor); anchors M15-M18 at `c3-counter.py:61-69`.

## Commands and real output

Scratch: `/fast/scratch/hyaku/souji-r40/w2/R40w2critic14` (TMPDIR and `--scratch`/`--work` all point inside it).

Landed bytes extracted (sha256 prefixes from `sha256sum`):
```
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 128e412b0ced3c243dc27c3dd3332054a611bc2e:census/round-40/c3-counter.py > $S/bytes/c3-counter.py   # 7bdde9f6...
... :tests/fixtures/r39-drift-record-rules.py      > $S/bytes/r39-drift-record-rules.py   # 567c37a6...
... :tools/souji-worktree-drift.py                 > $S/bytes/souji-worktree-drift.py     # e48ed08e...
... :tests/fixtures/r40-drift-record-branches.py   > $S/bytes/r40-drift-record-branches.py # a6ec36f0...
git -C <lane> diff --stat 0242085909fb6a4ee041c5443d76316ac6d59d4b 128e412b0ced3c243dc27c3dd3332054a611bc2e -- tests/fixtures/r39-drift-record-rules.py tools/souji-worktree-drift.py
  -> (no output, rc=0): the r39 base fixture and tool are byte-identical between base and landed.
```

1. Committed counter, full run (`python3 -B $S/bytes/c3-counter.py --root <lane> --rev 128e412... --base-rev 0242085... --scratch $S/counter-scratch --tool tools/souji-worktree-drift.py --fixture tests/fixtures/r40-drift-record-branches.py --base-fixture tests/fixtures/r39-drift-record-rules.py`):
```
COUNTER rc=0
MUTANT M15 killed=yes base_killed=no rc=1 fails=1 crash=False failing=- base:rc=0 fails=0 crash=False failing=-
MUTANT M16 killed=yes base_killed=no rc=1 fails=4 crash=False failing=- base:rc=0 fails=0 crash=False failing=-
MUTANT M17 killed=yes base_killed=no rc=1 fails=1 crash=False failing=- base:rc=0 fails=0 crash=False failing=-
MUTANT M18 killed=yes base_killed=no rc=1 fails=1 crash=False failing=- base:rc=0 fails=0 crash=False failing=-
SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=8 tool_sha=e48ed08e6728 fixture_sha=a6ec36f0ce9e
(stderr empty; counter scratch left empty)
```
Anchor counts (loaded `MUTANTS` from the committed counter): M15 1, M16 1, M17 1, M18 1.

2. Direct base-fixture runs, one per mutant (`python3 -B $S/bytes/r39-drift-record-rules.py --tool <tool> --work <dir>`), mutant = `source.replace(old, new)` exactly as `c3-counter.py:185-193` does:
```
== pristine rc=0 summary_lines=['SUMMARY cases=7 pass=7 fail=0'] stderr_bytes=0
== M15 rc=0 summary_lines=['SUMMARY cases=7 pass=7 fail=0'] stderr_bytes=0
== M16 rc=0 summary_lines=['SUMMARY cases=7 pass=7 fail=0'] stderr_bytes=0
== M17 rc=0 summary_lines=['SUMMARY cases=7 pass=7 fail=0'] stderr_bytes=0
== M18 rc=0 summary_lines=['SUMMARY cases=7 pass=7 fail=0'] stderr_bytes=0
   (every case-*=PASS; stderr empty for all five runs)
== candidate fixture on pristine: rc=0 SUMMARY cases=8 pass=8 fail=0
```
Base kills: **none** (0 of 4). SUMMARY present: **4 of 4**.

3. Positive control, base fixture must be able to FAIL. Tool = pristine with `c3-counter.py`-style anchor `tools/souji-worktree-drift.py:166` (`raise Refusal("RECORD-MALFORMED: line %d does not match the census schema"...)`) replaced by `continue` (anchor count 1):
```
rc=1 ... case-trailing-space=FAIL rc=2 want=2 missing=['does not match the census schema']
         case-indented-comment=FAIL rc=0 want=2 ...
         SUMMARY cases=7 pass=5 fail=2
```
The base arm can detect a kill (rc=1, fails=2, no traceback), so `score()` would return killed=True for such a mutant and the floor would fail.

4. Vacuity probe: fixture repo `$S/fixture-repo` (`git -C "$D" rev-parse --show-toplevel` = `$D` verified before commit; commit with a fixture-only identity). It holds the real tool, the real candidate fixture, and an inert `r39-drift-record-rules.py`:
   - (a) inert base that always prints `SUMMARY cases=7 pass=7 fail=0` and exits 0:
     `python3 -B $S/bytes/c3-counter.py --root $D --rev <fixture rev> --base-rev <fixture rev> --scratch $S/cs-inert-pass`
     -> `MUTANT M15 ... killed=yes base_killed=no ... base:rc=0 fails=0 ...` x4; `SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=8 ...`; **counter rc=0**.
   - (b) inert base that exits 2 with no SUMMARY (`sys.exit(2)`):
     -> `MUTANT M15 ... base:NO-SUMMARY rc=2` x4; `SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=8 ...`; **counter rc=0**.

   So `base_killed=0` is satisfied by a base fixture that never runs its cases. The arm is only as strong as the bytes it is given.

## Findings

1. **Base arm has no liveness or SUMMARY requirement** (`census/round-40/c3-counter.py:196`, `:205`; `score()` at `:109-110`). The preregistration kill clause "fixture has no own failure summary" is enforced for the candidate fixture only. Probe 4 shows the base floor passes with `NO-SUMMARY`. Not triggered by the landed bytes (probe 2 shows SUMMARY x4). Smallest fix for a future round: require the base fixture's pristine run to print a SUMMARY with rc 0 and to fail the positive control before the floor counts. This is a correction proposal, not an edit; I did not modify the counter.
2. **Base fixture bytes come from `--rev`, not `--base-rev`** (`census/round-40/c3-counter.py:146`). `--base-rev` is resolved at `:133-136` but never read. Currently harmless: the r39 fixture and tool are byte-identical between base and landed (empty `git diff --stat`). It is still a binding defect against the preregistration's "base and after revisions explicitly named".
3. **Anchor-failing mutants skip the base arm** (`census/round-40/c3-counter.py:186-190`). They record `(mid, False, False)` and never run the base fixture. The overall exit is still 1 because `killed` is False, so this does not hide a result, but the SUMMARY line does not show the base status for that mutant. Not triggered on the landed bytes (anchor counts all 1).
4. **Later revision changes nothing in the base arm.** `git diff 128e412 HEAD -- census/round-40/c3-counter.py` (HEAD now 549d9ec) is a 2-line change to `score()`'s `failing` attribution (`c3-counter.py:116-117`); it does not touch `base_src`, `score(base...)`, or `base_killed`. The r39 base fixture and the tool are unchanged between base and landed.

## Install and tool record

No installs. Tools used: `git` and the system `python3` already on PATH. No pacman. No edits to counters, fixtures, preregistration, SCORECARD.md, LOG.md, corpus/, or any committed file. No commits by this seat. The fixture repo commit used a fixture-only identity inside scratch.

## Scratch

`/fast/scratch/hyaku/souji-r40/w2/R40w2critic14` removed at the end of this seat (`rm -rf`), after this report was written.
