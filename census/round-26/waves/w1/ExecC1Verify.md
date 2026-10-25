# ExecC1Verify — C1 base state and edit feasibility (round 26, w1)

## Status

STATUS: PASS — (a)-(d) all executed at 89e0fce and reproduced byte-for-byte; the K2-satisfying edit
was computed (`17 41 74` abutting / `17 44 78` landed); no surgery draft appeared, so payload
fragments were byte-diffed against the landing commit a529c76. Two defects reported below, one of
them in the landed C1 integration. Delivery: `.ufo/waves/round-26/w1/c1-verify.md`.

## Evidence

Base revision `89e0fceeefcf28db313c94120be6d25e03c60094` (SCORECARD blob `4b564bc628d40328d276476c4171c30817cd6e75`,
42296 B, 254 lines). Commands run from `/home/vgpnk/Projects/shokunin/souji-shokunin`.

```
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin grep -cE '^(Insert the table below directly above|Optional same-landing correction)' 89e0fceeefcf28db313c94120be6d25e03c60094 -- SCORECARD.md
89e0fceeefcf28db313c94120be6d25e03c60094:SCORECARD.md:2
$ git cat-file -p 89e0fce:SCORECARD.md | awk '/^### Round (23|24|25) measurements/{printf "%s ", NR} END{print ""}'
17 175 231
$ git cat-file -p 89e0fce:SCORECARD.md | sed -n '172,228p' | wc -lc        # payload
     57 11521
$ git cat-file -p 89e0fce:SCORECARD.md | sed -n '172,228p' | sha256sum
be1d2b157f65892f1c35cc5ec8df7473e0e4ffb935215571c3001970442d8760  -
$ python3 -B <construct> ; awk '/^### Round (23|24|25) measurements/{...}' post-*.md
post-minimal.md   markers=0  headings=17 50 204     # literal recipe: FAILS K2
post-v1.md        markers=0  headings=17 41 74      # amendment-2 span order: PASSES
post-v3.md        markers=0  headings=17 41 75      # +1 blank before r24 block: PASSES
$ bash census/round-26/c1-counter.sh                    # at HEAD 0833de95 / landing a529c76
markers=0
headings=17 44 78
rc=0
```

Landed span compliance (`git cat-file -p a529c76:SCORECARD.md`, blob `2518e34b…`): base 1-16 ×1,
231-254 ×1, 175-207 ×1, 17-62 ×1, 63-91 and 93 ×1 each, 95-136 ×1, 225-226 ×1, 138-169 ×1.
Line 92 (blob-bound receipts row) carries one appended note, HEAD line 153:

```
| r23 | *(R3 dated 2026-10-25: the digest binds the labelled file's committed bytes and the recorded argv label, not the executed program.)*
```

Base 213-214 capability rows: **0 occurrences** at `a529c76` and at HEAD; both capability tables
hold 27 rows before and after. `git grep -n 'debris census (r24)' HEAD` matches only
`.ufo/waves/round-24/w2/W2ScorecardDraft.md:118`, `.ufo/waves/round-25/w1/scorecard-patch.md:32`
and the wave spec files — never `SCORECARD.md`. `git diff -U2 89e0fce a529c76 -- SCORECARD.md`
shows the two rows only as `-` lines (deleted, no `+` counterpart); the same diff shows the plan
they violate at `.ufo/waves/round-25/w1/scorecard-patch.md:32`: "move to directly after `:93`
`record agreement audit (r23)`".

Fence/duplication scan of base bytes:
`grep -nE 'debris census \(r24\)|coverage-map agreement \(r24\)' base.md` → 213, 214 only, and
0 of them outside the 212/215 fence. `grep -nF -e 'r24 (planned r23) — done' -e 'r25 (planned r24):'`
→ 225, 226 only, 0 outside the 174/227 fence; but `grep -nE '^- \*\*r2[45]'` → 134, 136, 225, 226,
i.e. `## Planned` already holds r24/r25 bullets under other prefixes.

## Findings

1. **Base literals reproduce exactly.** K1 = 2 (markers at base 172, 217); K2 = `17 175 231`; Round
   24 heading exists only inside the fence opened at base 174. Location:
   `89e0fce:SCORECARD.md:172,174-175,217,231`. Prereg C1 base literals are derived, not copied.

2. **The literal edit recipe cannot satisfy the frozen K2.** Deleting base 170-229 and inserting the
   payload's Round 24 block only above `### Round 23 measurements` gives K1=0 but K2 `17 50 204`
   (Round 25 is then last) — kill rule "ordered n25 < n24 < n23" fails. Location: base 172
   (instruction), base 231-254. The amendment-2 span order (r25 block, then r24 block, then r23
   block) is required; abutting spans give `17 41 74`, the landed shape with `blank`,`---`,`blank`
   separators gives `17 44 78`. Both pass; the landed value matches its receipt
   `census/round-26/records/c1-after.tsv` (rev `a529c762c81272d398727e6a623c801a230ac157`).

3. **Landed C1 drops the two r24 capability rows (amendment-2 item 5 unmet).** `a529c76` deleted base
   210-215 (instruction + fence + rows) and appended nothing to `## Capabilities`; the table still
   has 27 rows and no `| debris census (r24) |` / `| coverage-map agreement (r24) |` row anywhere.
   Amendment 2 requires "the base `## Capabilities` section (63-94) with exactly the two r24
   capability rows appended (from fenced lines 213-214, verbatim)". Location:
   `a529c76:SCORECARD.md:124-155`, base `:210-215`, payload `:213-214`. The kill rule has no counter
   for this MUST, so the omission scores green.

4. **The reorder invalidates five position-literal cross-references inside the protected r25 block.**
   Base 250-254 (r25 corrections, byte-verbatim per amendment 2 item 2) cite `SCORECARD.md:181`,
   `:180`, `:92`, `:224`, `:225`. At HEAD those lines are unrelated prose:
   `92` → a Round 25 limit sentence, `180`/`181` → `- **r17 (planned r16):**` bullet and its wrapped
   continuation, `224`/`225` → Round 14 prose. At base already partially stale (`:224` was a fence
   opener, `:180`/`:181` pointed one row low); at `a6d2d15` they were correct. Because amendment 2
   forbids touching those bytes, the "file does not match its layout contract" defect moves rather
   than closes. Location: `a529c76:SCORECARD.md:36-40`.

5. **Extra bytes outside every named span are untested.** The landing keeps a `---` rule plus blank
   lines at HEAD 41-43 and inserts one blank before the appended planned pair at HEAD 198. Amendment
   2 says the scaffold block including "separator" is deleted and lists spans verbatim; a fresh
   `---` at a new position passes both counters and every span diff. Cosmetic, but undisclosed in
   the commit message. Location: `a529c76:SCORECARD.md:41-43,198`.

## Attack log

A1. **K1/K2 are both defeatable without any integration** (calibration, the C1 surface). Constructed
   from base bytes: prefix `> ` on the two marker lines (K1 → 0), demote the fenced heading at base
   175 to `#### Round 24 measurements`, and insert one synthetic `### Round 24 measurements` heading
   above base 17. Measured: `grep -cE '^(Insert…|Optional…)'` = 0, `awk` triple = `17 21 235`
   (three headings, ordered), all six protected spans present ×1, and the Round 24 table still
   inside 3 markdown fences (`grep -c '^```'` = 6). The reused heading text is the payload's own.
   The kill rule tests only line-start markers, heading presence/order, and span identity; nothing
   asserts the r24 table is unfenced, the marker text is gone rather than prefixed, or the scaffold
   region is empty. Stricter-only repair candidates for the L1 to log (not applied by this seat): a
   counter on `grep -c '^```'` over the file (= 0), on `git grep -c 'Insert the table below directly above'`
   without `^` anchoring (= 0), and on the payload fragment's line-prefix anchoring (the r24 table
   must be present at column 0). Location: `.ufo/waves/round-26/preregistration.txt` KILL RULE, K1.

A2. **Amendment 2 carries a MUST with no counter, and the landing violates it** (unenforced
   predicate). Item 5's "exactly the two r24 capability rows appended (from fenced lines 213-214,
   verbatim)" is satisfied by no counter in the frozen set; the round's own landing fails it while
   scoring `markers=0` / `headings=17 44 78`. Evidence: finding 3. Location:
   `.ufo/waves/round-26/preregistration-amendment-2.txt` item 5 vs
   `.ufo/waves/round-26/preregistration.txt` CLAIM C1 KILL RULE.

A3. **Amendment 2 licenses a byte that the frozen C1 kill rule forbids** (contract inconsistency, not
   stricter-only). The unamended kill rule protects "base SCORECARD.md lines 1-171 … other than the
   planned-bullet additions inside the `## Planned` section"; amendment 2 item 5 additionally
   licenses a dated R3 note appended to the base line 92 row (inside 1-171). The landing does append
   it (`a529c76:SCORECARD.md:153`), so under a literal prereg read the claim fails its own kill rule
   while under amendment 2 it passes. Amendment 2 is labelled "no predicate … changed"; it actually
   adds a licensed change inside a protected region. Location:
   `preregistration.txt` KILL RULE bullet 3; `preregistration-amendment-2.txt` item 5.

## Notes

- No tool installed or upgraded; no pacman transaction attempted.
- Scratch `/var/tmp/souji-r26-ExecC1Verify` (base.md, head.md, payload fragments, candidate builds,
  attack builds) was removed after the values above were recorded.
- Nothing written outside `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-26/w1/`;
  lane tree, git index and jj state untouched.

Report: .ufo/waves/round-26/w1/ExecC1Verify.md
