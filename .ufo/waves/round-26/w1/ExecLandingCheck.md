# ExecLandingCheck — round-26 landing-gate re-run recipe

## Status

STATUS: PASS — recipe delivered at `.ufo/waves/round-26/w1/landing-check.md`; the gate CLI is
confirmed from `--help`, and the gate itself was executed read-only at two round tips (`e0f8dcd`
then `0c92c2e`, after the lesson landed), at the lane base, and at the r25 landing, so every class
the recipe lists is measured rather than inferred.

## Evidence

All gate runs are read-only against committed bytes; the only file written outside my report pair
was `--json` under `/var/tmp/souji-r26-ExecLandingCheck/` (removed). Lane revision: tip
`e0f8dcd12b1df1c53f213dc3a71def77d8ddf3f3` (master), base
`0eca7c8a5d10bcbfdae50d0c390d277deec63bfd`, prereg freeze `89e0fce`.

1. CLI (`python3 -B tools/souji-landing-gate.py --help`, exit 0):
   `--root ROOT`, `--rev REV`, `--round ROUND_NO`, `--base BASE`, `--fleet-root FLEET_ROOT`,
   `--json JSON_OUT`, `--selftest`. Exit contract at `tools/souji-landing-gate.py:32`:
   `Exit: 0 no findings, 1 findings, 2 could-not-evaluate`.

2. Tip, minimal shape (`--root /home/vgpnk/Projects/shokunin/souji-shokunin --rev e0f8dcd… --round 26`):

   ```
   LG-DANGLING-PTR  ../.ufo/waves/hyaku/jj-w1/reports/JjAuditSouji.md  corpus/README.md:217 cites path absent at e0f8dcd12b1d
   LG-DANGLING-PTR  ../.ufo/waves/hyaku/jj-w1/reports/JjTrialSouji.md  corpus/README.md:217 cites path absent at e0f8dcd12b1d
   LG-DANGLING-PTR  .ufo/waves/hyaku/jj-w1/reports/                    corpus/knowledge/jj-colocation-receipts.md:148 cites path absent at e0f8dcd12b1d
   LG-DANGLING-PTR  corpus/lessons/round-24.md:232:S118                corpus/QUALITY.md:141 cites path absent at e0f8dcd12b1d
   LG-DANGLING-PTR  corpus/lessons/round-26.md                         corpus/knowledge/git-auto-maintenance-trigger-set.md:52 cites path absent at e0f8dcd12b1d
   SUMMARY  findings=5  checked_reg=50  checked_changed=0  checked_pins=13  checked_measured=3  checked_markers=0  status_lines=0  carry_heading=0  checked_reports=0
   COULD-NOT-EVALUATE  no .md reports under .ufo/waves/round-26/ at e0f8dcd12b1df1c53f213dc3a71def77d8ddf3f3
   EXIT=2
   ```

3. Tip, full shape (adds `--base 0eca7c8… --fleet-root /home/vgpnk/Projects/shokunin --json …`):

   ```
   LG-DANGLING-PTR  corpus/lessons/round-24.md:232:S118  corpus/QUALITY.md:141 cites path absent at e0f8dcd12b1d
   LG-DANGLING-PTR  corpus/lessons/round-26.md  corpus/knowledge/git-auto-maintenance-trigger-set.md:52 cites path absent at e0f8dcd12b1d
   SUMMARY  findings=2  checked_reg=50  checked_changed=6  checked_pins=13  checked_measured=3  checked_markers=0  status_lines=0  carry_heading=0  checked_reports=0
   COULD-NOT-EVALUATE  no .md reports under .ufo/waves/round-26/ at e0f8dcd12b1df1c53f213dc3a71def77d8ddf3f3
   EXIT=2
   ```

   JSON summary from that run: `checked_ptrs=808 ptr_exempt=4 ptr_fleet=3`, `fleet` = the two
   `Jj*Souji.md` reports and `.ufo/waves/hyaku/jj-w1/reports/`, all classed `fleet`, not findings.

4. Base `0eca7c8` with `--fleet-root` → `findings=1` (`corpus/QUALITY.md:141` only), exit 2.

5. r25 landing `728b2ce` with `--round 25 --fleet-root` → `EXIT=1`, `findings=26` (23
   `LG-SEAT-UNCARRIED`, 3 `LG-DANGLING-PTR`, one of them the same `corpus/QUALITY.md:141` token).

6. Token origin: `git log -S'corpus/lessons/round-24.md:232:S118' -- corpus/QUALITY.md` →
   `728b2ce round-25: integrate claims, sources, lessons and wave evidence`.

7. Round-26 surface: `git diff --name-status 0eca7c8..e0f8dcd` → 40 paths, `..0c92c2e` → 41 (the
   round lesson added by `ea0bbe6`); full inventory in the recipe. Changed scripts
   (`--diff-filter=AM`, `.sh`/`.py`) → exactly 6 at both tips:
   `.ufo/waves/round-26/make-spec.py`, `census/round-26/{c1,c2,c3}-counter.sh`,
   `tests/fixtures/r26-axis-check.py`, `tools/souji-axis-check.py`.

8. Landing prerequisites: at `e0f8dcd` `git cat-file -e …:corpus/lessons/round-26.md` → absent; at
   `0c92c2e` present with headings `## Gate`, `## Findings`, `## Residuals`, `## Receipts` and no
   `## Seat-reported failures`. `LOG.md`: `grep -c 'round 26\|round-26'` → 0 and no diff from base at
   either tip. `grep -c 'souji-axis-check\|r26-axis-check' SKILL.md` → 0; `SKILL.md` diff → 0.

9. Wave reports: `git status --porcelain .ufo/waves/round-26` → 30 untracked entries at first read;
   `.ufo/waves/round-26/w1/*.md` went 26 → 32 → 42 → 54 during this seat (seats still landing); all
   untracked, so `checked_reports=0` at every committed revision today. Driving the gate's own
   `status_line_count` / `seat_failure_lines` over the work tree at 54 reports:
   `status_lines=39 failure_markers=12` (2 FAIL, 10 PARTIAL) — the files and lines are listed in
   recipe §F.

10. Later tip `0c92c2e` (lesson committed), same full shape
    (`--base 0eca7c8… --fleet-root /home/vgpnk/Projects/shokunin`):

    ```
    LG-DANGLING-PTR  corpus/lessons/round-24.md:232:S118  corpus/QUALITY.md:141 cites path absent at 0c92c2e6fbe1
    SUMMARY  findings=1  checked_reg=50  checked_changed=6  checked_pins=13  checked_measured=3  checked_markers=0  status_lines=0  carry_heading=0  checked_reports=0
    COULD-NOT-EVALUATE  no .md reports under .ufo/waves/round-26/ at 0c92c2e6fbe18f2f3009504d87240b6a22ad3d5b
    EXIT=2
    ```

    The round-caused entry→lesson pointer is gone (`ea0bbe6`), but `carry_heading=0` and
    `checked_reports=0` remain: the lesson has no `## Seat-reported failures` section and no wave
    report is committed.

Source locations for the two behavioural claims the recipe encodes:
`tools/souji-landing-gate.py:474` — `raise EvalError("no .md reports under %s at %s" % (prefix, rev))`
(verbatim); `corpus/QUALITY.md:80` (Q31) — `in SKILL.md, SHONEN.md, SCORECARD.md, PROVINCE.md,
corpus/QUALITY.md, corpus/README.md, corpus/knowledge/*.md` (verbatim list of pointer sources;
`corpus/SOURCES.md` is not in it).

## Findings

1. **Round-caused dangling pointer: measured at e0f8dcd, closed at 0c92c2e by the lesson commit;
   the carry heading is what remains.** `corpus/knowledge/git-auto-maintenance-trigger-set.md:52`
   cites `corpus/lessons/round-26.md`, absent at `e0f8dcd` (`LG-DANGLING-PTR`, measured; findings
   2 → 1). `ea0bbe6` landed the lesson with a `## Gate` section, so the citation resolves at
   `0c92c2e`. Residual: that lesson has no `## Seat-reported failures` (`carry_heading=0`). If a
   later edit re-points the citation or moves the lesson, the pointer returns — re-run at the
   landing tip, do not assume the e0f8dcd delta is gone.

2. **The gate cannot evaluate the carry arm at either tip, and the carry burden is already 12
   paragraphs.** `checked_reports=0`, exit 2, `COULD-NOT-EVALUATE no .md reports under
   .ufo/waves/round-26/` — the `w1/*.md` reports (54 at the last read) are all untracked. A
   pre-commit run therefore reports pointer classes only; its `status_lines=0` is unexercised,
   never a pass. At `0c92c2e` the lesson exists but `carry_heading=0` (no
   `## Seat-reported failures`), so if the reports commit as they stand the carry arm reads
   `status_lines=39`, `checked_markers=12` (2 FAIL, 10 PARTIAL; measured with the gate's own
   `seat_failure_lines`, listed in `.ufo/waves/round-26/w1/landing-check.md` §F) and every one must
   be carried in `corpus/lessons/round-26.md` under `## Seat-reported failures`, whole-paragraph or
   cut at a physical line end plus ellipsis, or `LG-SEAT-UNCARRIED` fires once per uncarried line.

3. **Inherited dangling pointer blocks a findings=0 landing.** `corpus/QUALITY.md:141` (Q57) carries
   the token `corpus/lessons/round-24.md:232:S118`; `_trim_pointer_token`
   (`tools/souji-landing-gate.py:795-797`) strips only a trailing `:N`/`:N-M`, so a `:line:id` suffix
   floats and the whole token dangles. Present at base `0eca7c8`, at the r25 landing `728b2ce`, and
   at the r26 tip. It is not r26-caused, but it means the landing receipt must either repair the token
   or add a reasoned `corpus/pointer-exemptions.tsv` row — and an unused exemption itself becomes
   `LG-DANGLING-PTR-EXEMPT-STALE`. Reporting `findings=0` at the landing tip is otherwise impossible.

4. **`--fleet-root` is load-bearing for this lane's finding count.** Three hyaku citation tokens
   under `corpus/README.md:217` and `corpus/knowledge/jj-colocation-receipts.md:148` classify as
   `fleet` only when `/home/vgpnk/Projects/shokunin` is supplied; without it the gate reports 5
   findings at `e0f8dcd` (2 with) and 4 at `0c92c2e` (1 with). The recipe pins the flag so the
   landing receipt is comparable with r18/r21.

5. **`--base` is the only parse coverage for the new scripts.** `SKILL.md` is unchanged and cites
   neither `tools/souji-axis-check.py` nor `tests/fixtures/r26-axis-check.py`, so `checked_reg` stays
   50 at base and tip while `checked_changed=6` requires `--base`. Dropping `--base` leaves the two
   new tools, three counters and `make-spec.py` unparsed by the gate.

6. **`LOG.md` has no round-26 section at either tip** (0 matches at `e0f8dcd` and `0c92c2e`; no
   `LOG.md` diff from base). The gate's LOG arm therefore
   scans nothing for round 26, and the prereg's AMENDMENT RULES require amendments (1 and 2) to be
   logged in `LOG.md` + the round lesson. Location: `/home/vgpnk/Projects/shokunin/souji-shokunin/LOG.md`
   (no round-26 heading), `.ufo/waves/round-26/preregistration.txt` § AMENDMENT RULES.

7. **C2 receipts are partially landed** (advisory to the C2 owner, not my item): at `0c92c2e`
   `census/round-26/records/c2-after.tsv` is present, but `c2-k4-after.tsv` and `c2-gate.tsv`,
   named by the prereg's RECEIPTS paragraph, are still absent. The landing gate does not check them;
   the C2 kill rule does.

8. **Gate coverage boundary, disclosed not fixed.** `corpus/SOURCES.md` is modified this round but is
   not a pointer source (`tools/souji-landing-gate.py:916-932`), so the five new registry rows'
   `used-by` paths receive no pointer validation from this gate; C2 K3
   (`scripts/sources-census.sh validate`) is the instrument that covers them. The recipe lists this
   so a green gate is not mistaken for registry-path integrity.

## Attack log

None — this is a landing-readiness item. No predicate, target or case set was judged gameable here;
the one thing that looks like a pass but is not (`checked_reports=0`, exit 2) is reported as an
unexercised arm, per the gate's own contract.

## Scope / hygiene

Wrote only `.ufo/waves/round-26/w1/landing-check.md` and this report. No `git add/commit/jj`
mutation, no deletion, no fleet or `/home/vgpnk/Projects/shokuknow` access, no `.scratch/` or
operator-sweep contents read. Scratch `/var/tmp/souji-r26-ExecLandingCheck/` removed. No tool was
installed or upgraded. Not run here: `--selftest`, the axis fixture, any lane test or counter — those
belong to the integration gate.
