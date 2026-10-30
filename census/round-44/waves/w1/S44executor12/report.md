# S44executor12 — C1 register partition 12/16

## Result

Axes: calibration (assigned); operability/coverage unchanged. Created `corrections.txt` with the four emitted rows selected by zero-based unique-record index modulo 16 = 11: emitted IDs R44-12, R44-28, R44-44, R44-60. Records bind the historical SCORECARD token referent at base revision `55d7af6f5a22340f7a3de1c386e514ababfaa75f` and use only `scope=base-SCORECARD-token-referents`. No optional fields are present. These are registrations of historical tokens, not claims of new factual corrections. No SCORECARD edit was made.

## Concrete evidence and commands

Ran:

```sh
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-44/c1-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev d314fd6e85d62565344fa6c4b102f52f62297884 --scratch /fast/scratch/hyaku/souji-r44/S44executor12 --emit
```

The emitted selected rows were exactly:

```text
R44-12 line=92 class=mismatch:rev-unresolved stale=09bb8e0d derived=UNRESOLVED
R44-28 line=513 class=mismatch:path-absent stale=c2-at-repair.txt derived=census/round-33/records/c2-at-repair.txt
R44-44 line=712 class=mismatch:path-absent stale=c3-after4.txt derived=census/round-38/records/c3-after4.txt
R44-60 line=793 class=mismatch:path-absent stale=c3-after-d.txt derived=census/round-40/records/c3-after-d.txt
```

Independent committed-base checks used `git show 55d7af6f5a22340f7a3de1c386e514ababfaa75f:SCORECARD.md` and `git ls-tree -r --name-only 55d7af6f5a22340f7a3de1c386e514ababfaa75f`. SCORECARD excerpts showed `09bb8e0d` at line 92, the C2 routed repair token at line 513, `c3-after4.txt` at line 712, and `c3-after-d.txt` at line 793. The tree enumeration yielded unique basename matches for the three absent-path tokens:

```text
c2-at-repair.txt    census/round-33/records/c2-at-repair.txt
c3-after-d.txt     census/round-40/records/c3-after-d.txt
c3-after4.txt      census/round-38/records/c3-after4.txt
```

The 09bb8e0d record emitted `UNRESOLVED`; the committed SCORECARD cell contains no matching 64-hex digest prefix. Both the base commit and its SCORECARD blob resolved via `git cat-file -e` (exit 0).

## Q76 prior-correction coverage

- R44-12 (line 92, `09bb8e0d`): already covered by Round 42 `CORRECTION-DE line=92 token=09bb8e0d ...`; the value `UNRESOLVED` here registers the corresponding R44 population row and does not add a new factual correction.
- R44-28 (line 513, `c2-at-repair.txt`): no corresponding correction for this item was found in the Round 42 or Round 43 lesson records inspected.
- R44-44 (line 712, `c3-after4.txt`): no corresponding correction for this item was found in the Round 42 or Round 43 lesson records inspected.
- R44-60 (line 793, `c3-after-d.txt`): no corresponding correction for this item was found in the Round 42 or Round 43 lesson records inspected.

The R43 lesson's three registered items concern different line numbers/fields and do not cover these three token rows. Prior-coverage search was limited to the Round 42 and 43 lesson records and the exact tokens/line pairs; it does not establish absence of mentions in all historical material.

## Limits

`--emit` is a derivation listing, not the complete r44 acceptance counter; no claim is made that the overall register target passed. The requested checks concern exact committed referents and prior correction coverage only. No tools were installed or updated. Scratch was removed before completion.
