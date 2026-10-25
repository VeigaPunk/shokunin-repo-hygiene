# ExecLandingCheck — round-26 landing-gate re-run recipe

## Status

STATUS: PASS — recipe delivered at `.ufo/waves/round-26/w1/landing-check.md`, with the gate CLI
confirmed and four read-only runs bound to named revisions (`e0f8dcd`, `0c92c2e`, `166baa1`, plus
the r25 landing and the base). Every class the recipe lists is measured on committed bytes.

## Evidence

Gate runs are read-only (`git ls-tree` / `cat-file` plus a private `/var/tmp` snapshot the tool
removes); the only file I wrote outside my report pair was `--json` under
`/var/tmp/souji-r26-ExecLandingCheck/`, removed. Revisions: base
`0eca7c8a5d10bcbfdae50d0c390d277deec63bfd`, prereg freeze `89e0fce`, tips `e0f8dcd` → `0c92c2e` →
`166baa1` (`166baa1` is the tip this report was written against).

1. CLI (`python3 -B tools/souji-landing-gate.py --help`, exit 0): `--root`, `--rev`, `--round`,
   `--base`, `--fleet-root`, `--json`, `--selftest`. Exit contract
   (`tools/souji-landing-gate.py:32`): `Exit: 0 no findings, 1 findings, 2 could-not-evaluate`.

2. `e0f8dcd`, minimal shape (`--root … --rev e0f8dcd… --round 26`) → `findings=5`,
   `checked_changed=0`, `checked_reports=0`, exit 2. Findings were 3 fleet-only hyaku tokens, the
   inherited `corpus/QUALITY.md:141` token, and entry A:52 → `corpus/lessons/round-26.md`.

3. `e0f8dcd`, full shape (adds `--base 0eca7c8… --fleet-root /home/vgpnk/Projects/shokunin --json …`)
   → `findings=2 checked_reg=50 checked_changed=6 checked_pins=13 checked_measured=3
   checked_markers=0 status_lines=0 carry_heading=0 checked_reports=0`, exit 2. JSON summary:
   `checked_ptrs=808 ptr_exempt=4 ptr_fleet=3`; the three hyaku citations classed `fleet`.

4. Base `0eca7c8` with `--fleet-root` → `findings=1` (`corpus/QUALITY.md:141` only), exit 2.

5. r25 landing `728b2ce` (`--round 25 --fleet-root`) → exit 1, `findings=26`: 23
   `LG-SEAT-UNCARRIED` and 3 `LG-DANGLING-PTR`, one of them the same inherited token.

6. Token origin: `git log -S'corpus/lessons/round-24.md:232:S118' -- corpus/QUALITY.md` →
   `728b2ce round-25: integrate claims, sources, lessons and wave evidence`.

7. `0c92c2e` (lesson committed by `ea0bbe6`), full shape → `findings=1`, `checked_changed=6`,
   `carry_heading=0`, `checked_reports=0`, exit 2. Entry A's citation now resolves; the lesson has no
   `## Seat-reported failures`.

8. `166baa1` (wave reports committed), full shape → exit 1:

   ```
   LG-DANGLING-PTR   corpus/knowledge/registry        corpus/QUALITY.md:143 cites path absent at 166baa18f808
   LG-DANGLING-PTR   corpus/lessons/round-24.md:232:S118  corpus/QUALITY.md:141 cites path absent at 166baa18f808
   LG-PARSE-CHANGED  .ufo/waves/round-26/w1/verify-loop.sh  bash -n rc=2: … line 320: unexpected EOF while looking for matching `"'
   18 × LG-SEAT-UNCARRIED  (one per committed STATUS failure line; list in recipe §F)
   SUMMARY  findings=21  checked_reg=50  checked_changed=11  checked_pins=13  checked_measured=3  checked_markers=18  status_lines=63  carry_heading=0  checked_reports=84
   EXIT=1
   ```

9. Round-26 surface: `git diff --name-status 0eca7c8..e0f8dcd` → 40 paths, `..0c92c2e` → 41,
   `..166baa1` → 134 (the wave report set lands). Changed scripts
   (`--diff-filter=AM`, `.sh`/`.py`) → 6 at `e0f8dcd`, 11 at `166baa1`; both lists are in recipe §B.

10. Landing prerequisites at `166baa1`: `corpus/lessons/round-26.md` exists with `## Gate`,
    `## Findings`, `## Residuals`, `## Receipts` and **no** `## Seat-reported failures`; `LOG.md` has
    0 matches for `round 26` and no diff from base; `SKILL.md` is unchanged and cites neither
    `tools/souji-axis-check.py` nor `tests/fixtures/r26-axis-check.py` (0 matches for both).

Source locations for the behavioural claims the recipe encodes:
`tools/souji-landing-gate.py:474` — `raise EvalError("no .md reports under %s at %s" % (prefix, rev))`;
`corpus/QUALITY.md:80` (Q31) — `in SKILL.md, SHONEN.md, SCORECARD.md, PROVINCE.md,
corpus/QUALITY.md, corpus/README.md, corpus/knowledge/*.md` (verbatim pointer-source list;
`corpus/SOURCES.md` is not in it).

## Findings

1. **Round-caused pointer delta moved twice; one is open at 166baa1.** `e0f8dcd`: entry A:52 cited
   the not-yet-committed `corpus/lessons/round-26.md` (closed by `ea0bbe6`). `166baa1`: the new Q59
   row at `corpus/QUALITY.md:143` contains the prose token `corpus/knowledge/registry`, which the
   grammar reads as a path and dangles (`LG-DANGLING-PTR`, measured). Reword it to name a real path
   or none; otherwise every future tip inherits this finding.

2. **The carry arm is live and fully red: 18 markers, `carry_heading=0`.** At `166baa1` the gate
   reads `checked_reports=84`, `status_lines=63`, `checked_markers=18`, and
   `corpus/lessons/round-26.md` has no `## Seat-reported failures`, so all 18
   `LG-SEAT-UNCARRIED` findings stand. Each needs a paragraph carried into the lesson (whole or cut
   at a physical line end plus ellipsis); recipe §F lists the file and line of every one. A report
   rewritten to `STATUS: PASS` removes its marker.

3. **A committed wave script does not parse.** `.ufo/waves/round-26/w1/verify-loop.sh` fails
   `bash -n` (`rc=2`, unexpected EOF at line 320, measured at `166baa1`) → `LG-PARSE-CHANGED`. It is
   w1 scratch that landed in the report set; fix it or drop it from the landing, and note that
   `--base` is what surfaces it (all 11 changed scripts are parsed only through that arm).

4. **An inherited pointer still blocks a findings=0 landing.** `corpus/QUALITY.md:141` (Q57) carries
   `corpus/lessons/round-24.md:232:S118`; `_trim_pointer_token`
   (`tools/souji-landing-gate.py:795-797`) strips only a trailing `:N`/`:N-M`, so the `:line:id`
   suffix dangles. Present at base `0eca7c8`, at the r25 landing `728b2ce`, and at every r26 tip
   measured. Not r26-caused; the L1 must either repair it or add a reasoned
   `corpus/pointer-exemptions.tsv` row (an unused exemption becomes
   `LG-DANGLING-PTR-EXEMPT-STALE`). A clean `findings=0` landing is otherwise unreachable.

5. **`--fleet-root` is load-bearing for the finding count.** Three hyaku citation tokens
   (`corpus/README.md:217`, `corpus/knowledge/jj-colocation-receipts.md:148`) classify as `fleet`
   only with `/home/vgpnk/Projects/shokunin`; without it `166baa1` reports 5 findings instead of 2.
   The recipe pins the flag for comparability with r18/r21.

6. **`--base` is the only parse coverage for the new scripts.** `SKILL.md` is unchanged and cites
   neither new tool, so `checked_reg` stays 50 at every tip while `checked_changed=11` at `166baa1`
   requires `--base`. Dropping it leaves all 11 unparsed by the gate.

7. **`LOG.md` has no round-26 section at any measured tip** (0 matches at `e0f8dcd`, `0c92c2e`,
   `166baa1`; no `LOG.md` diff from base). The gate's LOG arm scans nothing for round 26, and the
   prereg's AMENDMENT RULES require amendments 1 and 2 to be logged in `LOG.md` + the round lesson.
   Location: `/home/vgpnk/Projects/shokunin/souji-shokunin/LOG.md`,
   `.ufo/waves/round-26/preregistration.txt` § AMENDMENT RULES.

8. **C2 receipts partially landed** (advisory to the C2 owner, not my item): at `166baa1`
   `census/round-26/records/c2-after.tsv` exists, but `c2-k4-after.tsv` and `c2-gate.tsv`, named by
   the prereg's RECEIPTS paragraph, do not. The gate does not check them; the C2 kill rule does.

9. **Gate coverage boundary, disclosed not fixed.** `corpus/SOURCES.md` is modified this round but is
   not a pointer source (`tools/souji-landing-gate.py:916-932`), so the five new registry rows'
   `used-by` paths get no pointer validation here; C2 K3 (`scripts/sources-census.sh validate`) is
   the instrument that covers them. A green gate is not registry-path integrity.

## Attack log

None — this is a landing-readiness item, so no counter was judged gameable. The one thing that looks
like a pass but is not (`checked_reports=0` with exit 2 at pre-commit tips) is reported as an
unexercised arm, per the gate's own contract.

## Scope / hygiene

Wrote only `.ufo/waves/round-26/w1/landing-check.md` and this report. The L1's `166baa1` commit
swept both paths into the tree as they stood mid-wave, so my current content is an unstaged delta on
those two files and nothing else. No `git add/commit/jj` mutation, no
deletion, no fleet or `/home/vgpnk/Projects/shokuknow` access, no `.scratch/` or operator-sweep
contents read. Scratch `/var/tmp/souji-r26-ExecLandingCheck/` removed. No tool installed or upgraded.
Not run here: `--selftest`, the axis fixture, any lane test or counter — those belong to the
integration gate.
