# M1 — round-28 seat-failure carry (delivery for L1)

STATUS: PASS — the base landing gate's 19 `LG-SEAT-UNCARRIED` findings for round 28 drop to
0 with the appended block, every other finding class unchanged, and two precision controls show
the block cannot be satisfied blindly.

## What to apply

Append this block, byte-exact, to the end of `corpus/lessons/round-28.md`:

- bytes: `.ufo/waves/round-31/w1/deliver-m1-carry-r28.append.md`
- 29 lines, 8392 bytes, sha256 `a36739dac77b754341d80b60cdb0af803ac70edec3ec25ea9356fd0dc34ab184`, final byte is `\n`
- the lesson at base already ends with a newline, so a plain append is enough; nothing above is edited
- keep it the **last** section of that file: the base `tools/souji-landing-gate.py` reads only the
  first heading-delimited `## Seat-reported failures` section, so a later section would hide it
  (C2's fixed reading removes that limit, and does not change this block's verdict)

## Red before (lane base, base tool)

```
$ python3 -B tools/souji-landing-gate.py --root <lane> --rev 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc \
    --round 28 --base 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc
```

```
SUMMARY	findings=24	checked_reg=62	checked_changed=0	checked_pins=13	checked_measured=3	checked_markers=19	status_lines=58	carry_heading=0	checked_reports=61
```

Class breakdown: 19 `LG-SEAT-UNCARRIED` (every marker of the 19 committed reports under
`census/round-28/waves/w1/`) and 5 `LG-DANGLING-PTR` whose sources are `corpus/README.md:217`
(two), `corpus/knowledge/jj-colocation-receipts.md:148`, `corpus/lessons/round-28-verifier-spotcheck.md:71`
and `:36`.

## After (append applied, committed in scratch)

```
$ python3 -B tools/souji-landing-gate.py --root <scratch clone> --rev 152f8af33a12a6ddcaa54ae35e492a9b0d215c1f \
    --round 28 --base 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc
```

```
LG-DANGLING-PTR	../.ufo/waves/hyaku/jj-w1/reports/JjAuditSouji.md	corpus/README.md:217 cites path absent at 152f8af33a12
LG-DANGLING-PTR	../.ufo/waves/hyaku/jj-w1/reports/JjTrialSouji.md	corpus/README.md:217 cites path absent at 152f8af33a12
LG-DANGLING-PTR	.ufo/waves/hyaku/jj-w1/reports/	corpus/knowledge/jj-colocation-receipts.md:148 cites path absent at 152f8af33a12
LG-DANGLING-PTR	census/round-26/waves/assimilation/validate/tests/vault/vadv-49/.gitignore:fixture/	corpus/lessons/round-28-verifier-spotcheck.md:71 cites path absent at 152f8af33a12
LG-DANGLING-PTR	corpus/knowledge/registry	corpus/lessons/round-28-verifier-spotcheck.md:36 cites path absent at 152f8af33a12
SUMMARY	findings=5	checked_reg=62	checked_changed=5	checked_pins=13	checked_measured=3	checked_markers=19	status_lines=58	carry_heading=1	checked_reports=61
```

0 `LG-SEAT-UNCARRIED`; the 5 dangling pointers are the same five as red-before (the block adds no
pointer-resolution surface); `carry_heading=1`; `markers=19` unchanged, so no marker was lost or
double-counted. `checked_changed=5` comes from the scripts that differ between base and the scratch
tip, not from this block; the appended commit itself touches one file:
`corpus/lessons/round-28.md | 29 +++...`, 1 file changed, 29 insertions(+).

## Controls (the block is load-bearing, not a blanket waiver)

1. **Uncarried report still flagged** — commit `3a95d115f48ad2f354d7e2953f94e5abbd7daf8e` adds
   `census/round-28/waves/w1/ControlSeat20.md` with `STATUS: FAIL — control probe: this failure
   paragraph has no carry bullet anywhere.` → gate returns exactly one
   `LG-SEAT-UNCARRIED ... ControlSeat20.md`, markers=20, findings=6.
2. **Bullet without a disposition token does not carry** — commit
   `f3eae0e4313136ee53521365e486e775a1f44534` replaces the `open` token in the SwarmCritic45 bullet
   with `noted` → gate returns exactly one `LG-SEAT-UNCARRIED` for
   `census/round-28/waves/w1/SwarmCritic45.md:2`, markers=19, findings=6.
3. **Quotes are byte-exact** — all 19 bullets were re-checked against the report lines in the base
   blobs: `bullets=19 byte-exact=19 bad=0`. Every dragged paragraph is a single physical line, so no
   ellipsis cut is used anywhere and the wrap rule is never exercised.

## Dispositions

13 `resolved@<full40>`, 6 `open`.

Resolved commits named in the block:

| commit | what it delivers | bullets |
|---|---|---|
| `765fe8bd602ac679d01e7a0790711485209ab8bd` | capture tool + `census/round-2{6,7}/waves` + `.gitignore` + the two r28 F4 entries + `searchlog-draft.md` + S212–S214 rows + the committed lesson | 9 |
| `ed270c42161cd62829783a5e5d2ef4e27089331c` | corrects the S215 row pin; commits `census/round-28/waves/w1-results.json` and `summary.tsv` | 3 |
| `fec846dd1781a414ae3a7d71d2d8fa2fb17900eb` | commits the after-measurement receipts `c2-after.tsv`, `c3-after.tsv` | 1 |
| `691dd29211c53d0ef94fa072394cb9c8a69fe92e` | non-author verifier spot-check re-opens POSIX and S215 live and matches the pins | 1 |

Open (re-checked at HEAD, not assumed): `SwarmCritic42` (the frozen C2 claim still cannot pass its
own gates; recorded only as residual), `SwarmCritic45` (no per-claim no-op failure receipt), 
`SwarmMutationTester47` (unrelated `LG-SEAT-UNCARRIED` baseline findings never named),
`SwarmMutationTester49` (symlink-control fixture failure has no recorded resolution),
`SwarmReviewer33` (`census/round-28/sources/SHA256SUMS` still omits `git-fetch-zh-HANS-CN.html`),
`SwarmReviewer39` (lesson body still states no counting command of its own).

## Provenance

- lane base `9f17a1ef571f3a510a51ac233d7cf50ac0c871fc`; lane tip read read-only at
  `1b811368461785040e955f41f9c97e62f61fd67c`
- scratch clone `/fast/scratch/hyaku/souji-r31/M1CarryR28/r.TojxNb/c` (origin removed, throwaway
  identity set with `git -C` only), removed after delivery
- no lane write: nothing added, committed, checked out or reset in the lane; only this file and
  `deliver-m1-carry-r28.append.md` are written, under `.ufo/waves/round-31/w1/`
