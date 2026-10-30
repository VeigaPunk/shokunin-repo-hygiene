# S44executor01 — C1 correction-register partition

Axes: calibration (assigned); operability and coverage left untouched.

## Result

Created `corrections.txt` with the five emitted unique records at zero-based positions 0, 16, 32, 48, and 64 (counter IDs R44-01, R44-17, R44-33, R44-49, R44-65). Each entry uses `scope=base-SCORECARD-token-referents`, revision `55d7af6f5a22340f7a3de1c386e514ababfaa75f`, and no optional fields. SCORECARD's historical line numbers are labels only; no SCORECARD edit was made.

## Evidence

Counter command:

```sh
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-44/c1-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev d314fd6e85d62565344fa6c4b102f52f62297884 --scratch /fast/scratch/hyaku/souji-r44/S44executor01 --emit
```

Observed counter output selected:

```text
R44-01 line=14 class=mismatch:rev-unresolved stale=65817d0d derived=UNRESOLVED
R44-17 line=220 class=mismatch:path-absent stale=git-repo-structure-readonly.md derived=multi:.ufo/waves/round-26/assimilation/validate/corpus/knowledge/git-repo-structure-readonly.md;census/round-26/waves/assimilation/validate/corpus/knowledge/git-repo-structure-readonly.md;corpus/knowledge/git-repo-structure-readonly.md
R44-33 line=667 class=mismatch:path-absent stale=c2-after2.txt derived=census/round-38/records/c2-after2.txt
R44-49 line=732 class=mismatch:path-absent stale=c2-after7.txt derived=census/round-38/records/c2-after7.txt
R44-65 line=823 class=mismatch:path-absent stale=controls/c3-control.txt derived=multi:census/round-41/controls/c3-control.txt;census/round-42/controls/c3-control.txt
```

Independent base-tree check executed using `git show 55d7af6f5a22340f7a3de1c386e514ababfaa75f:SCORECARD.md` and `git ls-tree -r --name-only 55d7af6f5a22340f7a3de1c386e514ababfaa75f`. It confirmed: line 14 has no 64-hex word beginning `65817d0d`; basename lookup for line 220 has the three paths listed above; basename lookups for lines 667 and 732 each have the single round-38 path in corrections.txt; suffix lookup for `controls/c3-control.txt` has the round-41 and round-42 paths listed. Source SCORECARD excerpts from that check identify the line 667 artifact as `c2-after2.txt`, line 732 as `c2-after7.txt`, and line 823 as `controls/c3-control.txt`.

Earlier-correction comparison: R44-01 is already substantively covered by round 42's `CORRECTION-DE line=14 token=65817d0d derived=rev-unresolved` in `corpus/lessons/round-42.md` (§ C1). R44-17, R44-33, R44-49 and R44-65 were not found as corresponding line/token corrections in the inspected round-42 lesson; round 43's three R39 corrections concern different files/fields and cover none of these five. These are registration matches only, not independent new factual findings; notably, R44-01 is not a new factual correction.

## Limits

The frozen counter emission returned exit 0 (dry `--emit`; this is not the full registration acceptance check). Independent verification checked the stated derivation inputs and referent lists at the pinned base; it does not establish prose-level truth of any SCORECARD statement. The prior-round comparison is limited to the inspected round-42/43 lessons.

Scratch `/fast/scratch/hyaku/souji-r44/S44executor01` was removed after the bounded run. No tools were installed or updated.
