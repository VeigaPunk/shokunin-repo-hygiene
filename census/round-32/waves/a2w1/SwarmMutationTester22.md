# SwarmMutationTester22 — A1 falsify: does c3-counter-v2.py actually reject the Critic35 cheat? (r32 a2w1)

## Status
STATUS: PASS — amendment A1 is real against the cheat it was built from: the Critic35 rebuild scores
`SUMMARY legs=14 fail=0 f1_entries=5` under frozen v1 (exit 0) and is rejected by v2
(`SUMMARY legs=17 fail=2`, L16+L17; L15 too when the fabricated cell is wrong, `fail=3`). But v2 is beaten by the
cheapest hybrid: a fixture that really measures only the two cells L15 pins and prints constants for the rest —
one of them provably false — scores `SUMMARY legs=17 fail=0 f1_entries=5` under v2 and v1 alike. No lane file
outside this report was written; no git/jj state touched.

## Evidence

Scratch: `/fast/scratch/hyaku/souji-r32/MutateC3V2/` (clone of the lane, origin removed; throwaway identity via
`git -C <scratch> config`; `TMPDIR=/fast/scratch/hyaku/souji-r32/MutateC3V2/tmp`). All counters run as
`python3 -B census/round-32/c3-counter[-v2].py --root <scratch> --rev <rev> --base 85b61a151923986e7e6b48f7084b9122561b5f3d
--list-rev 3ec84fc81b3243429c834a051880b0bcde06291c --scratch <under seat tmp>`. Counter files are byte-identical
between a92e1aa and lane tip 4e56c48 (`git diff --stat a92e1aa 4e56c48 --` on both: empty).

- cheat B1 (Critic35 rebuild) at `a53ed58ccfd09dd4d5cb205e5c607b1a68e8d5b3`:
  - v1: `L8 PASS ... results=9 ... L12 PASS rc=0 results_equal=True jj_calls=1 git_calls=4 touch_calls=1 missing=[]`
    ... `SUMMARY legs=14 fail=0 f1_entries=5` — **accepted**, exit 0.
  - v2: `L15 PASS probe recent_present=True old_present=False record recent=yes old=no`
    `L16 FAIL abandon=1 nonzero=1 gc=1 nonzero=1 cat_file_e=1 rc0=0 results=9`
    `L17 FAIL refetched=5 bad=['census/round-32/sources/s900-attack-probe.adoc']`
    `SUMMARY legs=17 fail=2 f1_entries=5` — **rejected**, exit 1.
- cheat B2 (same, one constant flipped to the r31 misconception) at `6b7a12d86fc558d17ceea9b4e0245f6bc721c67a`:
  - v2: `L15 FAIL probe recent_present=True old_present=False record recent=yes old=yes` ... `SUMMARY legs=17 fail=3`.
- hybrid (the beat) at `7f126bf94c5553b22b7e08aac38948846dc19fc5`:
  - v1: `SUMMARY legs=14 fail=0 f1_entries=5`; v2: `L15 PASS probe recent_present=True old_present=False record
    recent=yes old=no` / `L16 PASS abandon=2 nonzero=0 gc=2 nonzero=0 cat_file_e=14 rc0=7 results=12` /
    `L17 PASS refetched=4 bad=[]` / `SUMMARY legs=17 fail=0 f1_entries=5` — **not caught**.
- honest landed tree a92e1aa under v2: `SUMMARY legs=17 fail=0 f1_entries=5` (baseline sanity, reproduced).
- live 404 probe of the fabricated URL, this run: `curl -sS -o /dev/null -w '%{http_code}'
  https://git-scm.com/docs/git-gc-nonexistent-attack-probe` → `404`.
- truth check (honest fixture `tests/fixtures/r32-jj-mtime-clock.sh@a92e1aa` re-run from its own bytes, exit 0):
  `RESULT arm=never step=gc-pruneexpire-never obj=B mtime=old where=cruft object_present=yes`
  hybrid record same cell: `RESULT arm=never step=gc-pruneexpire-never obj=B mtime=old where=absent
  object_present=no` — the hybrid asserts the opposite of measured reality, and v2 scores both `fail=0`.

## Findings

1. **A1 is real against its target cheat, and it works through L16/L17, not through measurement.** B1's rejection
   is mechanical: the junk `jj abandon -r attack-probe-nonexistent` exits non-zero (L16,
   `census/round-32/c3-counter-v2.py:338-340`) and the hand-written snapshot's receipt cannot survive a live
   re-fetch (L17, `:241-250`, `:341`). L15 (`:130-149`, `:332-333`) passed B1 because constants copied from the
   entry's own claimed table match the probe; it catches only a fabricator who is *wrong* on one of the two pinned
   cells (B2). Location: `.ufo/waves/round-32/w1/SwarmCritic35.md` (the design being rebuilt), findings 1-3.
2. **L15 pins exactly two of the record's asserted values, and they are the least novel ones.** `ok15` reads only
   `object_present` off `arm=recent|old step=gc-default obj=B` (`c3-counter-v2.py:330-333`) and the probe
   (`:130-149`) is plain-git default gc — the pair r31 already documented. Every `where` value, the whole
   `mixed`/`never`/`nocruft` arms, obj=C after gc, and the cruft `.mtimes` edge the F1 claim exists for are
   assertion-only in both counter versions. The hybrid exploits exactly this: 10 of its 12 RESULT lines are
   constants, one contradicts the honest measurement, and both v1 and v2 print `fail=0`.
3. **L16 is a count, not a correlation.** The amendment text says "at least one cat-file -e per RESULT line";
   the code implements `len(cfe) >= len(rl) > 0` with both exit outcomes somewhere in the run
   (`c3-counter-v2.py:338`). The hybrid pads seven real `cat-file -e` calls per probe (padding included in the
   fixture) and no leg ever ties a logged call to a RESULT line's object. Quote: `ok15 = pr[0] != pr[1] and
   rline("recent") == ("yes" if pr[0] else "no")` — the entire measurement leg.
4. **v2 cannot distinguish the honest tree from the hybrid.** a92e1aa and 7f126bf both read
   `SUMMARY legs=17 fail=0 f1_entries=5`; the honest fixture's never-arm line
   (`where=cruft object_present=yes`) and the hybrid's (`where=absent object_present=no`) are mutually exclusive,
   so at least one certified `fail=0` record asserts a falsehood about `gc.pruneExpire=never`. The C3 target is
   met today at the landed commit with seat-quality evidence only for 10 of the record's cells.
5. Wave-1 note for the C1 axis reading: none — this seat touched C3 only. Axes impacted by the finding: coverage
   (8); the beat shows A1's strictness does not extend to the claimed edge class. No axis is harmed; the fix is
   the L1's to design (e.g. pin every gc-step cell from a counter-side multi-config probe, or require
   counter-verified REPO/OBJECT lines as Critic35 originally proposed), not mine to land.

## Attack log

- B1 rebuild of Critic35's cheat, faithful to the named design: fixture `tests/fixtures/r32-jj-mtime-clock.sh`
  replaced by a shim-byte sniff (`grep -q 'gc|prune|repack) exit 0'` / `grep -qx 'exit 0'`) that discards the
  status of the six shimmed calls and prints nine constant RESULT lines; record reduced to nine lines; hand-written
  `census/round-32/sources/s900-attack-probe.adoc` (721 B) with receipt `200` for the 404 URL, SHA256SUMS line,
  `S900` registry row, Gate bullet + `source:` line. Verdicts above. Mutants pass v1's L13 via the sniff
  (`M2/M3 ... differs=True no=0<3=True`).
- B2 = B1 with `row old gc-default B old loose yes` (the r31 "presence is decided by refs" fabrication). v2:
  `fail=3` (L15+L16+L17).
- Beat (hybrid), on top of a92e1aa, no fake provenance (real receipts pass L17): fixture keeps the landed entry,
  record and sources, and replaces only the fixture+record: two real jj-colocated repos per run
  (`jj git init --colocate` → `jj new -m A` → `f` → `jj status` → `jj describe -m B` → commit id from
  `jj log -T commit_id` → `jj abandon '@'` → drop `refs/jj/keep/*` → `git reflog expire ... --all` → island-wide
  `touch -d '30 days ago'` over `git fsck --unreachable` objects in the old arm → `git gc` → presence/where read
  back with `cat-file -e` + loose-file + `.mtimes`/`verify-pack` checks), feeding exactly the two L15-pinned
  lines; the other ten lines are constants, including the false never-arm line. Two debugging dead ends are part
  of the record: `git HEAD` does not track jj's `@` (B was silently the init commit until read from jj), and a
  recent unreachable island holds B through reachability regardless of its own clock (r31's descendant keeper), so
  the old arm backdates the whole island, as the honest fixture does.
- Rev table (all vs base `85b61a1`, list-rev `3ec84fc`): `a53ed58` B1 v1 accept / v2 reject (L16,L17);
  `6b7a12d` B2 v2 reject (L15,L16,L17); `7f126bf` hybrid v1+v2 both `fail=0` — not caught.

## Deliveries

- `.ufo/waves/round-32/a2w1/SwarmMutationTester22.md` (this report). No other lane file written; scratch clones,
  cheat commits and fixtures lived only under `/fast/scratch/hyaku/souji-r32/MutateC3V2/` and were removed before
  this report was finished. No tool installs were needed (no pacman use).
