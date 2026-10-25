# ScribeReadme-2 — round 25 wave 1 (README patch draft, second seat)

## Status
STATUS: PASS — I wrote the draft `.ufo/waves/round-25/w1/readme-patch-2.md`, covering all four bullets: the :40 marker, the Round 25 F2 row, `### Frontier (r25)`, and the Round 24 note (no change needed). I applied it to a scratch plain clone and ran it against the committed counters: coverage-agreement `mismatches=0`, record-agreement `mismatches=0`. I did not edit `corpus/README.md`.
The sibling seat ScribeReadme had already written `readme-patch.md` and `ScribeReadme.md`, so this seat wrote `-2` files instead of overwriting them (the sibling was messaged first).

## Evidence
Scratch: `/var/tmp/souji-r25-ScribeReadme/`, a `git clone --no-local` of the lane at 1814de5. It held 0 `refs/jj` refs, so it was a plain clone. The README blob is identical at 6e4737e, 1814de5 and de736c2: `git diff --stat 1814de5 HEAD -- corpus/ tools/` printed nothing. Git version: 2.56.0. The script `apply.py` replaced :40 in place, appended the §3 block, and added a stub `corpus/knowledge/git-repo-structure-common-dir.md` (`ground: F2`) **in scratch only**, then committed. Scratch was removed afterwards (`ls` → "No such file or directory").

| arm | command | output |
|---|---|---|
| base (lane 1814de5) | `python3 -B tools/souji-coverage-agreement.py --root . --rev <HEAD>` | `grounded=6 mapped=6 dangling=0 mismatches=0` |
| base | `python3 -B tools/souji-record-agreement.py --root . --rev <HEAD> --no-worktree` | `keys=4 records=4 occurrences=17 mismatches=0` |
| draft-2 + entry (rev 5e3acc8c…) | committed coverage tool | `grounded=7 mapped=7 dangling=0 mismatches=0`, rc 0 |
| draft-2 + entry | wave-dir draft `w1/souji-coverage-agreement.py --base-rev a6d2d157…` | `… mismatches=0 kill_tested=6 kill_violations=0`, rc 0 (matches the amendment-1 literal) |
| draft-2 + entry | record-agreement `--no-worktree` | `keys=4 records=4 occurrences=17 mismatches=0`, rc 0 (K3 unchanged) |
| draft-2, NO entry (red arm, rev 842efa9d…) | committed coverage tool | `MISMATCH DANGLING-MAP-PATH corpus/knowledge/git-repo-structure-common-dir.md corpus/README.md:549 …`; `dangling=1 mismatches=1`, rc 1 |
| draft-2 + optional C1 row + C2 clause + entry | both coverage tools; record-agreement | `mismatches=0` / `kill_tested=6 kill_violations=0` / `mismatches=0`; new-text `TALLY_RE` hits after :536 → 0 |
| sibling `readme-patch.md` + entry (rev 8423a2a3…) | the same three counters | `grounded=7 mapped=7 dangling=0 mismatches=0`; `kill_tested=6 kill_violations=0`; record `mismatches=0` |
| every arm | `awk 'NR==517' … \| cut -c1-60` | `\| F2 repository size census \| frontier; read side (three ent` (the :517 pointer holds) |

After those runs, one edit was made: the entries-cell parenthetical changed from `(S124/S125)` to `(S124–S126)` to follow amendment 2. It sits outside every backticked span, so I expect no change to the counters [INFERENCE, not re-run].

## Findings
1. Two different line pointers are on record. The prereg D4 (`preregistration.txt` § Routed fixes) says: "README :40 status cell gains an append-only "superseded by Round 24 F2 row" marker". `corpus/lessons/round-24.md:150` says: `append-only "superseded by :504" on the :40 status`. Both drafts use the item's `:517`, which is the F2 row; :504 is the section heading. The L1 should name the choice in the lesson's old→new log.
2. No counter sees the :40 marker. `tools/souji-coverage-agreement.py` reads only the ground and entries cells (`map_rows` yields `row[0], row[2]`), and K3 reads only tally spans. Every count is identical with or without the marker. So D4 is a prose fix with no instrument behind it, the same as R24-M2's "C2 is green with :40 unchanged". It should not be reported as counter-verified.
3. The `:517` pointer only holds if nothing is inserted above line 517 before landing, and no tool checks it. The landing check is in the draft (§ Integration rules 1).
4. Q56 pairing was measured: without the entry, the row yields exactly one `DANGLING-MAP-PATH` at `README.md:549` (table above).
5. S124–S126 are absent from `corpus/SOURCES.md` at de736c2 (`grep -c 'S124\|S125'` → 0). The row cites them, so they must land no later than the row.
6. The lane is jj-colocated. `.jj` exists, and `git for-each-ref refs/jj/keep | wc -l` → 462 at the lane. This is why the F2 frontier next-line requires the baseline to come from a plain `--no-local` clone. That clone carried 0 `refs/jj` refs.
7. The Round 24 note (:506-508) needs no edit. The :40 change appends inside the cell without adding a line, so the note's ":40's "frontier, no entry" is stale and superseded here" and its :40/:42/:68/:217 pointers stay true.
8. Neither counter can falsify the "supersedes the r24 F2 row; names every F2 entry" claim. If the r25 row drops an entry that :517 still names, the result stays `mapped=7`. The r24 note at :531-536 already discloses this. Draft-2's r25 entries cell names all five F2 entries plus `../census/round-24/size-census-lane.txt`.

## Attack log
- ATTACK (calibration, D4): the routed D4 fix has no counter (finding 2). It is not gameable, but it is unmeasured, so it should be reported as prose-only.
- ATTACK (coverage, Q56 superseding rows): the coverage map cannot detect drift where an entry is dropped from the newest row (finding 8). This is pre-existing and was disclosed in r24; it is not introduced by this patch.

Out of scope, not done: editing `corpus/README.md`, the lesson's old→new log entry, and SOURCES rows. Tools installed: none.
