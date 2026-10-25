# Round 26 w1 — distilled findings (deduplicated across seats)

Source: 82 STATUS-bearing seat reports + 22 draft/deliverable files under
`/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-26/w1/` (104 `.md` at distill time).
Lane tip when distilled: `166baa1` (`git rev-parse HEAD`).
Severity: **attack** = a frozen predicate/target/case-set is wrong, gameable, or its evidence is
falsified; **finding** = a defect in landed or authored bytes that the L1 can fix; **observation** =
a measured fact with no defect.
Status of each finding as of the tip is stated; several were closed by the L1 mid-wave (marked
`RESOLVED@<rev>`) and are retained because the closing is itself evidence.

Reported by: **DistilFindings** (read-only distillation seat; no lane bytes written except these two
files).

---

## C3 — axis-of-surface instrument (operability)

1. **[attack]** R2's class vocabulary is unbounded: any `surface-class` outside the five mapped names
   passes on any axis. Reproduced at tip: `surface-class: garbage-typo` → `claims=1 flags=0`, rc 0.
   — RevC3Design F2 · also ExecAxisSelftest A1, CritClaims F4, CritAmendNeed F1, CritAdmissionHistory F1
2. **[attack]** R2 is defeated by a second `surface-class:` line (parser is last-wins): `bookkeeping-file`
   then `receipt-binding` → `claims=1 flags=0`, rc 0 at tip. — RevC3Design F3 · also CritClaims F4, CritKillRules F8
3. **[attack]** A decoy first `## MACHINE BLOCK` shadows the real one (`re.search` first-match,
   `tools/souji-axis-check.py:56`): all real claims become invisible. — RevC3Design F4
4. **[attack]** The frozen K2 suite is forgeable — case worlds are static committed strings and the
   counter reduces the run to `tail -n 1`; a tool with no rule implemented can score 12/12, and the
   control arm says nothing about the submitted tool. — CritKillRules F6, F7
5. **[attack]** The fixture's own case set cannot detect several survivor classes: R3 hardcoded, R2
   pairs `knowledge-entry`/`registry-append` unexercised, file-scoped `enumerate:` unenforced, retired-row
   counting untested. — MutC3Fixture F2–F6
6. **[attack]** The gate never resolves a `§` locator to a heading — `LOCATOR_RE` only requires a
   token to be present; line numbers and ranges are decorative; the Q54 heading set is a union over
   every named snapshot, not row-scoped. K2 green therefore does not evidence the C2 kill rule's Q54
   clause. — CritQ54Gate F1–F6 · also LabGateCheck F4, RevGateTool F3, LabSnapshotPlan A1–A2, MutEntryLocators F1–F2
7. **[finding]** The R2 rule reads no `claim text` and flags a universal word inside the `enumerate:`
   value — inverted relative to the frozen text. **RESOLVED@`c594901`** (R4 now scans raw claim text,
   only when `enumerate:` is absent) — RevC3Design F1 · also ExecAxisSelftest F4, CritClaims F3, axis-check-docs divergence 5
8. **[finding]** The landed fixture ran 11 cases against a frozen 12-case literal, with no `control=`
   field in normal mode and `--tool PATH` ignored. **RESOLVED@`c594901`** (wave 12-case fixture adopted;
   tip now prints `cases=12 pass=12 control=FALSE-GREEN-REJECTED`, rc 0) — ExecAxisFixture F5 · also ScribeGateDraft F5, RevC3Design F5, LabAxisRun F7, CritClaims F1–F2, SimpCounterCheck F10, ScribeLessonR26 F2, ScribeLogR26 F2, ScribeScorecardR26 F2
9. **[finding]** Two C3 tool candidates disagreed at 6/12 vs 12/12; the w1 draft skips any SCORECARD
   line containing the substring `retired` (`w1/souji-axis-check.py:142`), so the synthetic calibration
   row vanishes and R3 misfires. **RESOLVED** — the landed tool scores 12/12 (re-verified) — ExecAxisFixture F4 · also MutC3Fixture F1, ExecAxisTool F2, axis-check-docs
10. **[finding]** R3's tie-break is dict insertion order; with a tied minimum a claim on the other
    tied lowest axis is flagged. Latent (real table has a unique lowest). — ExecAxisSelftest F2 · also RevC3Design F7, CritClaims F8, RevToolSafety F8
11. **[finding]** The axes scan is not bounded to the axes table — `### Round NN measurements` rows
    between `## Axes` and the next `## ` are matched by the same table-row pattern. — ExecAxisSelftest F3 · also RevC3Design F8
12. **[finding]** `--selftest` does not exist on the committed tool (argparse exits 2); a 27-case
    spec was delivered instead. — ExecAxisSelftest F1
13. **[finding]** `tools/souji-receipt-run.py` `COUNTS_RE` cannot match the proposed `selftest=N/N pass`
    spelling, so a counter echoing that line yields no counts line. — ExecAxisSelftest F7
14. **[finding]** R1's "non-retired" limb is vacuous — `OWNED_AXES` is exactly the three non-retired
    axes, so a retired owned axis is inexpressible. — ExecAxisSelftest F8
15. **[finding]** Four input-hygiene defects in the tool: no identical-path/alias refusal (a file
    containing both a MACHINE BLOCK and an Axes table self-validates), FIFO/character-device reads
    block or balloon, `UnicodeDecodeError` escapes as exit 1 (contract says exit 2), unbounded
    whole-file reads. — RevToolSafety F1–F4
16. **[finding]** The adopted fixture hardcodes another seat's scratch root
    (`/var/tmp/souji-r26-ExecAxisFixture`, `tests/fixtures/r26-axis-check.py:47–48`) — a wave-seat
    path now baked into a committed lane instrument. — own probe at tip (no seat reported it)
17. **[observation]** The 12-case suite's case 1 is the r25-C2-replica discriminator and case 12 is
    the always-green stub control, as frozen. — ExecAxisFixture F1–F2 · also ScribeGateDraft F5

---

## C2 — F1 trigger-set assimilation (coverage)

18. **[attack]** Entry B's headline is falsified by the fixture's own case bodies: the `pull` case
    runs `git fetch -q origin` and never `git pull`; the `merge`/`rebase` cases run a plain
    `git commit` before the named command, and a plain commit alone takes 2→1 (reproduced:
    `before=2`, `after_plain_commit=1`); the merge is a **fast-forward**, contradicting the fixture's
    own comment "A real, non-fast-forward merge" (reproduced: merge output `Fast-forward`). The landed
    entry still headlines "`fetch`, `merge`, `rebase` and `pull` auto-maintenance all prune". —
    CritEntryB F1–F3 · corroborated from source bytes by ScoutRegroundDocs F6–F8
19. **[attack]** S132's "0 prunable" fleet figure is stale at the tip: the live fleet repo holds 5
    registrations of which 4 are prunable (`worktree prune --dry-run --expire=now` lists 4). The
    landed entry asserts the fleet "is currently *not* exposed". — ScoutRegroundOwnwork F3 · also LabGitVersion F6
20. **[attack]** `verified-at:` conflates "campaign measured" with "this lane measured" — the field a
    calibration reader scans; the campaign run date is 2026-10-23. The honest qualifier sits 55 lines
    away, and the Gate reason actively misattributes campaign output to this lane ("the lane's
    re-runnable gate output"). — CritEntryB F4–F5
21. **[attack]** C2's coverage credit is a deepening, not an expansion: the base F1 row already says
    "frontier, entries held" with two entries, and the row still says so at the tip. K1's `0 → 2`
    counts front-matter labels on already-held entries; K4 unions map rows per ground token, so the
    F1 row `:39` is not even required. — CritCoverageCredit F1–F3 · also LabReadmeF1 F2–F3
22. **[attack]** The build spec presumes the credit under test: "Deliver the gap list that grounds the
    C2 expansion claim". — CritCoverageCredit F7
23. **[attack]** "Every cited source is re-opened THIS round" is not mechanically checkable — the gate
    compares quotes only against snapshots written by the same seat; fabricating both sides is green. —
    CritKillRules F3
24. **[attack]** K1 counts FILES with any `^ground: F1` line, not front-matter ground; a body-example
    line in a non-grounded file counts for grep but not for the tool (`grounded_f1=2` vs
    tool-grounded=1). The `corpus/knowledge/*.md` glob also admits any stray draft. —
    MutCounterStub F3–F4 · also SimpCounterCheck F5
25. **[attack]** The c2 counter substitutes a working-tree glob for the frozen rev-scoped grep and
    swallows errors: an untracked `corpus/knowledge/zz-untracked-probe.md` raised `grounded_f1` to 3,
    and `2>/dev/null` makes a missing tree print the red-before literal `grounded_f1=0`. —
    SimpCounterCheck F5–F6
26. **[attack]** `verify=ok` is byte-binding, not truth: it re-hashes the tool blob, checks the argv
    string and the presence of a `COUNTS_RE` line — it never re-runs the counter, never compares the
    recorded counts to the tip tree, and never inspects `rc=`. A counter that failed and a counter
    whose data later flipped both verify `ok`. — MutCounterStub F1
27. **[attack]** The prereg's own frozen red-before command is not runnable: `run` has no `--label`
    (it is `--tool`), and `census/round-26/c*-counter.sh` does not exist at the named base `0eca7c8`
    (the counters exist only from `12fd90b`). — LabReceiptVerify F7 · also CritClaims F7, SentBounds F2, ScribeScorecardR26 F4, CritKillRules F10
28. **[attack]** Five of the nine committed receipts refuse `verify` with `RECEIPT-COUNTS-ABSENT`
    (re-verified at tip: c1-before, c1-after, c2-before, c2-after, c3-before), while the prereg says
    "each `verify=ok`" and the lesson says "all verify=ok". Cause: the counters print
    `markers=`/`grounded_f1=`/`registry_rows=`/`axis_check_tool=`, none of which `COUNTS_RE` matches. —
    LabReceiptVerify F1, F5 · also ExecReportAssemble F1, ExecVerifyLoop F2, CritKillRules F10, CritCoverageCredit F6, SentBounds F4, ScribeLogR26 F4
29. **[attack]** Two "before" receipts were re-emitted after the after-data existed (`c2-before`
    utc 17:29:54Z, `c3-before` 17:29:28Z, committed in `e0f8dcd`/`d6c13b0`); the original pre-data
    copies survive only at `89e0fce`. — LabReceiptVerify F6 · also MutFreezeOrder F3, RevPreregFreeze F5, RevMirrorGate F4, CritKillRules F10
30. **[attack]** The amendment-ordering rule is prose only: no frozen predicate compares a receipt's
    `utc` against the amendment commit time, so a seat that produced green data before the amendment
    and committed red receipts afterwards fails no rule. — MutFreezeOrder F2
31. **[attack]** The frozen C3 counter was mutated after the freeze (a `--stub` arm added at
    `d2e6253`), so the red and green receipts bind different instrument bytes; no amendment records
    the edit. — SentBounds F8 · also SimpCounterCheck F9, CritKillRules F10
32. **[attack]** The §2b attestation was dropped between the wave drafts and the landing: the lesson
    Gate names S128–S132 in prose with no per-row access date and no per-row located quote (r25's Gate
    has 3 `Quote (` occurrences; r26 has 0), and the registry has no round-26 provenance paragraph. —
    CritSourcedClaim F3–F4 · also ScoutRegroundDocs F9
33. **[attack]** The committed entries' Gates carry no `§ <NAME>` locator, so the Q54 heading-resolution
    clause of the C2 kill rule is vacuous on both admitted entries (`locators=0`). — ScoutRegroundDocs F3
34. **[finding]** Both committed entries lacked a `## Gate` section, so the frozen K2 was red at every
    tip through `ba8b54b` (`entries=2 ok=0 fail=2`, rc 1). **RESOLVED@`33e6807`** (Gate sections landed;
    `c2-gate.tsv` now `entries=2 ok=2 fail=0`, rc 0, `verify=ok`) — RevGateTool F5 · also LabGateCheck F1, ScribeGateDraft F1, ScribeEntryA F4, ScribeEntryB F7, CritSourcedClaim F2, CritCoverageCredit F4, RevAssimRules F1, LabGitVersion F7, ScribeLessonR26 F1, ScribeLogR26 F1, ScribeScorecardR26 F1, MutEntryLocators F3
35. **[finding]** `c2-k4-after.tsv` and `c2-gate.tsv` (named by the prereg RECEIPTS block) were absent
    through `0c92c2e`. **RESOLVED@`9a6e0f1`** (both present, both `verify=ok`) — ScribeGateDraft F2 · also SonicSourcesGrep F8, ScribeEntryB F7, RevAssimRules F2, RevMirrorGate F2, CritSourcedClaim F5, LabGitVersion F8, ScribeLessonR26 F6
36. **[finding]** After-receipts bind non-tip revisions (`c1-after` rev `07f83e6`, `c2-after` rev
    `e0f8dcd`, `c3-after` rev `c594901`) against tip `166baa1`. — ExecReportAssemble F2 · also ScribeReportDraft F2, RevAssimRules F4, SimpCounterCheck F12, CritCoverageCredit F5
37. **[finding]** `registry_rows=132` is a count-only proxy (a delete plus an add keeps 132) and the
    fleet validator has no receipt (`c2-k3.tsv` absent), so a red validate can pass every named
    receipt. — SimpCounterCheck F7 · also CritKillRules F5
38. **[finding]** The c3 counter always exits 0 (its last command is `printf`), so present-pass,
    present-flag and tool-absent are rc-identical. — SimpCounterCheck F8
39. **[finding]** Commit `0833de9`, subject "round-26 C3: …", lands the entire C2 surface (both
    entries, `corpus/SOURCES.md` +5 rows, the README F1 row, seven snapshots). — LabReadmeF1 F6 · also ScribeLogR26 F3, ExecCensusTables F1, RevMirrorGate F5
40. **[finding]** The scratch-mirror gate ran at `/var/tmp/souji-r26-mirror` (already occupied by
    another seat's build) instead of the prereg path `.ufo/waves/round-26/assimilation/validate/`, which
    still does not exist; the mirror also validated the pre-enrichment entry bytes, while the landed
    entry differs. — RevMirrorGate F2–F3 · also RevAssimRules F3, ExecScratchMirror F3, SentBounds F5
41. **[finding]** Staged S131's `used-by` named a file this round does not admit
    (`corpus/knowledge/count-objects-garbage-semantics-r23.md`); 5/5 staged rows also fail the E09
    recheck schema (prose tail after the cadence). Repaired in the landed rows. — ExecRenumberMap F4 · also MutC2Rows F1–F2, ScribeSourceRows F5, SonicRowSchema F3
42. **[finding]** S131's `used-by` under-counts: the landed entry A carries a literal `(S131)` at
    `corpus/knowledge/git-auto-maintenance-trigger-set.md:45`, but S131's `used-by` lists entry B only;
    E11 checks path existence only, so K3 cannot see it. — ExecRenumberMap F6 · also RevCensusSchema F3
43. **[finding]** E04/W04 cannot see own-work rows — `url_of()` extracts only `https?://`, so local
    paths yield an empty duplicate key. — ExecRenumberMap F2 · also ConnCrossSource F4, renumber-map §2c
44. **[finding]** Five registry rows break the `status`/`used-by` contract (S022, S075, S076, S024,
    S025) and no arm of the frozen census can see it. Pre-existing, not r26-caused. — LabSourcesCensus F1
45. **[observation]** S129's front matter cites the tree URL while row S129 cites the blob URL; no
    validator failure. — ExecRenumberMap F8 · also ConnCrossSource F5, RevCensusSchema F4
46. **[observation]** Two of the five new `teaches` cells are tightened rather than verbatim staged
    (S128 appends "; the switch is default-on", S129 narrows the "ignore errors" scope). —
    ScribeSourceRows F4

---

## C1 — SCORECARD scaffold census (calibration)

47. **[attack]** K1 counts two marker prefixes only: deleting or rephrasing those two lines while the
    fence, instructions and payload copies survive still scores `markers=0`. — RevC1Counter F1 · also ExecC1Surgery A2
48. **[attack]** K2's printed triple is unlabeled and ascending by construction, so the literal
    `n25 < n24 < n23` predicate holds for *any* heading order; the base itself prints `17 175 231`
    (Round 25 last) and satisfies it. Only the heading-to-number mapping discriminates, and the
    committed counter prints numbers with no mapping. — ExecC1Surgery A1 · also RevC1Counter F2, SimpCounterCheck F1, CritKillRules F1, MutC1Surgery
49. **[attack]** The counter measures no payload: a file can drop both r24 capability rows and both
    planned bullets, keep the heading triple, and still score `markers=0`. The landed tip demonstrated
    exactly that. — ExecC1Surgery A3 · also ScribeC1Note F4, MutC1Surgery F3, ExecC1Verify F3
50. **[attack]** Amendment 2 is a pre-data *relaxation* of the C1 kill predicate, not a clarification:
    base lines 1–171 forbid any byte change other than planned bullets, yet the landed R3 note and the
    two capability rows land inside that region while the amendment text claims "no predicate … changed";
    its enforcement sentence is also unsatisfiable for region 5, which item 5 itself mandates. —
    CritClaims F6 · also CritAmendNeed F2
51. **[finding]** The first landing `a529c76` omitted both r24 capability rows that amendment 2 item 5
    requires, while K1/K2 scored green (no kill-rule arm exists for it). **RESOLVED@`07f83e6`** (rows
    now `SCORECARD.md:155–156`, `c1-after` regenerated) — ExecC1Verify F3 · also ExecC1Surgery F3, LabC1AfterSim F2, ScribeC1Note F3, ScribeLessonR26 F4
52. **[finding]** The five `superseded by SCORECARD.md:<n>` refs remain stale position literals: at the
    tip `:181`/`:180`/`:92`/`:224`/`:225` resolve to unrelated prose. Amendment 2 protects those bytes,
    so the defect is displaced, not closed. — ExecC1Verify F4 · also ExecC1Surgery F5, ScribeLessonR26 F5, ScribeC1Note F1
53. **[finding]** The landed append-only mapping note is itself one commit stale: its "post-C1
    `a529c76`" column gives the planned bullets as `:199`/`:200`, but at tip `166baa1` they are `:201`/
    `:202` (two capability rows were inserted above them at `07f83e6`). — ScribeC1Note F2 · also CritNoHarm F3
54. **[finding]** Bytes outside every named span survive the landing: the `---` separator at
    `SCORECARD.md:42` is byte-identical to base line 229, which amendment 2 lists among deleted scaffold
    content; no frozen counter and no protected span observes it. — LabC1AfterSim F3 · also ExecC1Verify F5, ExecC1Surgery F4
55. **[finding]** K2 is fence-blind (a fenced duplicate heading counts toward "exactly three"), and the
    counter prints a trailing space absent from the frozen literal; a missing `SCORECARD.md` is a silent
    pass. — SimpCounterCheck F2–F4
56. **[finding]** The literal edit recipe (delete base 170–229, insert the r24 table above Round 23)
    cannot satisfy K2 — it yields `17 50 204` with Round 25 last; the amendment-2 span order was
    required. — ExecC1Verify F2 · also ExecC1Surgery F2, LabC1AfterSim F1, MutC1Surgery F1
57. **[finding]** The R3 note landed as a fifth cell on a four-column table (schema-inconsistent,
    counter-inert). — LabC1AfterSim F4
58. **[finding]** The round's own Round 26 measurements block was appended *below* Round 23
    (`SCORECARD.md:264`), giving heading order 25/24/23/26 — neither newest-first nor the file's
    observed history — and the frozen K2 cannot see it because it counts only rounds 23/24/25. —
    CritNoHarm F1
59. **[observation]** The C1 counter measures file layout (markers + heading positions), not
    "self-assessment entries match observed repo state" as AXES defines calibration — the axis family is
    right, the measurement is a format lint. — CritClaims F9
60. **[observation]** The round-24 measurement block landed verbatim with no payload loss; the 12 absent
    base lines are fence markers and instruction prose. — CritNoHarm F1 · also LabC1AfterSim F1

---

## Round-level / contract / process

61. **[attack]** The R2 escape hatch can only be closed by changing frozen fixture cases 3, 7 and 10,
    which use `surface-class: measurement` as filler — so the hole cannot be closed this round without
    breaching the frozen case set; an amendment-3 scope disclosure is the only strict path. —
    CritAmendNeed F1
62. **[finding]** `LOG.md` has no Round 26 entry (0 matches for "round 26"/"round-26"), while the
    prereg's AMENDMENT RULES require amendments "logged in LOG.md + the round lesson". —
    ScribeLessonR26 F7 · also RevMirrorGate F6, ScribeLogR26, ExecReportAssemble F4, ScribeReportDraft F6, ScribeQ58Note F4
63. **[finding]** The landed lesson has no `## Seat-reported failures` heading (`carry_heading=0`), and
    18 committed STATUS lines are FAIL/PARTIAL — the landing gate's carry arm cannot evaluate while
    the wave reports are untracked (`checked_reports=0`, exit 2). — ExecLandingCheck F1–F2
64. **[finding]** An inherited dangling pointer (`corpus/QUALITY.md:141` carries
    `corpus/lessons/round-24.md:232:S118`) blocks a findings=0 landing and must be repaired or exempted. —
    ExecLandingCheck F3
65. **[finding]** The tip commit `166baa1` landed a syntactically broken `verify-loop.sh`
    (`bash -n` → `unexpected EOF while looking for matching '"'`), which the landing gate reports as
    `LG-PARSE-CHANGED`. — ExecVerifyLoop F1
66. **[finding]** The adopted QUALITY row Q59 landed *inside* the `## Round 25 criteria` block with no
    `## Round 26 criteria` heading, attributing a round-26 criterion to round 25. — DistillPlanCheck F2 · also axis-check-docs placement note
67. **[finding]** Q59's check column names an executable carrier that does not exist ("the r25-C2
    replica … exits 1 with an R2 FLAG line"); the only committed carrier is the fixture's case 1, which
    was 11-case at the time. The `round-26.md R26-M1` motivating-evidence anchor was dangling (the
    mistakes row has since landed at `166baa1`). — RevQ59Text F1–F2
68. **[finding]** `census/round-26/sources/SHA256SUMS` verifies 7/7 but is not in `LC_ALL=C` order
    (`sort -c` reports disorder at line 5); "sorted" is a new, stricter convention not held by r24 or
    r25 either. — ExecSh256Sums F2–F3 · also sha256sums-recipe.md §6
69. **[finding]** The recorded verify command in `corpus/lessons/round-25.md:78` does not reproduce from
    the lane root (bare names resolve against cwd); the working form is `cd` into the sources dir. —
    ExecSh256Sums F4
70. **[finding]** The manual census in `/home/vgpnk/Projects/shokunin/CORPUS.md` is column-zero-only,
    so a row indented 1–3 spaces is invisible to it while the maintained parser accepts it; the
    lane-local `CORPUS.md` path named by several briefs does not exist at any revision. —
    MutC2Rows F4 · also LabSourcesCensus (status), ExecCensusTables F3
71. **[finding]** `census-before.txt` carries no row count, so byte-identity with it cannot witness the
    C2 127→132 literal; only the counter receipt does. — ScoutCensusBefore F3
72. **[observation]** Untracked `tools/__pycache__/` and `tests/fixtures/__pycache__/` remain in the
    lane tree (a `git add -A` would land bytecode); no root `.gitignore` exists. — ExecAxisTool F3 · also LabAxisRun F8, ScribeEntryA F8, ScribeEntryB F8, ScribeGateDraft F7, SonicToolsList F4, SimpCounterCheck F13, ScribeLessonR26 F8, SentBounds F9
73. **[observation]** The lane is detached from its branch at every sample (reflog: `export from jj`) while
    the prereg header says "branch master, ahead=0"; the lane's loose objects now exceed the stock
    `gc.auto=6700` threshold. — LabGitVersion F3–F4 · also LabReadmeF1 F5, SonicToolsList F6
74. **[observation]** The prereg names `89e0fce` as "this file's landing commit" for the freeze, but
    `89e0fce` is amendment 1; the freeze commit is `12fd90b`. — ScribeQ58Note F1
75. **[observation]** The wave spec's routable-share bar (44/87 = 50.57%) is met by exactly one seat, and
    13 seats (14.94%) sit in neither tracking set. — SonicSpecCount F1–F4
76. **[observation]** Sibling-lane overlap scan across 21 rostered lanes is clean — every verdict
    `routed`/`report`, zero collision on F1 auto-maintenance, prereg-gating or SCORECARD surgery. —
    ConnSiblings
77. **[observation]** The three claims are causally separable: each counterfactual reversion leaves the
    other claims' frozen counters byte-identically re-derivable. — RevClaimSeparation F1–F4
78. **[observation]** All six base/tip counter literals reproduce the committed receipts exactly, and the
    freeze/amendment ordering holds on all three edges (freeze → amendment+red receipts → wave). —
    RevPreregFreeze F1–F4 · also MutFreezeOrder F1, ExecC1Verify F1, ScribeLessonR26 F9
79. **[observation]** The C1–C3 axes are each distinct from every prior admitted claim; C2 and C3 extend
    previously routed-but-unclaimed items. — DistillPlanCheck F1–F3

---

## Late additions (verified against the lane at tip `e78ac7c`, after the integrator's spot-check)

80. **[attack]** The landed entry Gates carry **no** `§ <NAME>` locator at all, so the C2 kill rule's
    Q54 clause is vacuous: `python3 -B tests/fixtures/r23-locator-heading.py --entries
    corpus/knowledge/git-auto-maintenance-trigger-set.md corpus/knowledge/git-auto-maintenance-trigger-set-r23.md
    --snapshot-dir census/round-26/sources` → `entries=2 locators=0 locators_bad=0` (re-run by this
    seat). The `§ OPTIONS` string lives in the *registry row* S128, not in either entry Gate. The
    integrator's spot-check reads the row's locator, not the entries'. — ScoutRegroundDocs F3, re-verified
    by DistilFindings
81. **[finding]** The landed entry A Gate quotes `"struct child_process cmd = CHILD_PROCESS_INIT;"`
    from `git-builtin-pull.c lines 390-391` — a generic boilerplate line that appears at pull.c:390,
    527 and 753, and that does not evidence S130's claim (the fetch spawn at pull.c:392). —
    ScoutRegroundDocs F5
82. **[finding]** The landed entry B Gate quotes `"run_auto_maintenance(the_repository, verbosity < 0);"`
    against `git-builtin-merge.c lines 506-509` and `git-builtin-fetch.c line 2926` — the merge.c
    locator points at the *comment* span, not the call at merge.c:509, and the same quote string is
    reused for two different rows. — ScoutRegroundDocs F5, extended by DistilFindings (line-number read
    at tip)
83. **[finding]** The landed lesson Gate has **0** `Quote (` occurrences and **0** `accessed` dates,
    against r25's convention of 3 per-row quoted attestations — the §2b per-row quote/access-date
    attestation is absent from the landed lesson, not only from the wave drafts. — ScoutRegroundDocs F9,
    re-verified by DistilFindings (`grep -c 'Quote (' corpus/lessons/round-{25,26}.md` → 3 vs 0)
84. **[attack]** The integrator's spot-check (lane tip `e78ac7c`, non-author) reached **"expansion —
    improved"** on the basis that "two admitted entries on F1 frontier ground not previously held",
    while the base F1 row already read "frontier, entries held" with two entries and the tip row still
    reads "frontier, entries held" with four. The spot-check's own C2 section records
    `corpus/README.md:39` naming both new entries as the only map change. On the bytes, the two
    new entries are a *deepening* of an already-held F1 frontier — the same reading CritCoverageCredit
    reached. This is a live disagreement between the closure verdict and the lane's own map state. —
    CritCoverageCredit F1–F3 vs `corpus/lessons/round-26-verifier-spotcheck.md:54`, re-verified by
    DistilFindings (`corpus/README.md:39` at base `0eca7c8` and at tip)
85. **[finding]** The spot-check's "no owned axis harmed" reading omits the Round 26 measurements block
    the round itself appended below Round 23 (`SCORECARD.md:264`), leaving the file's heading order
    25/24/23/26 — a calibration-axis shape the frozen K2 cannot see and the spot-check's diff summary
    describes only as "r26 measurements/corrections/planned adds". — CritNoHarm F1, extended by
    DistilFindings (heading scan at tip)
86. **[finding]** The spot-check records a **disagreement with the round's own refusal reason**: the
    zh-Hans `git-fetch` page now carries "git-fetch last updated in 2.56.0" and the `--auto-maintenance`
    switch, so the recorded reason ("version alignment unprovable, build stamps ambiguous") does not
    reproduce today. The reject outcome survives; the recorded rationale is time-fragile and was routed
    to r27. This is the same fragility ScribeGateDraft F4 raised from the other direction (the lesson
    states a reason the prereg did not freeze). — `corpus/lessons/round-26-verifier-spotcheck.md:47`,
    corroborated by ScribeGateDraft F4
87. **[finding]** `corpus/lessons/round-26-verifier-spotcheck.md` is the only lane artifact naming the
    S1–S5 residual class the wave raised, and it routes three items to r27 (trailing uncommitted wave
    outputs, S-language edition snapshot pinning, `__pycache__`/`.gitignore`) without carrying the
    round's own strongest attack findings — the falsified Entry B measurement (F18), the stale S132
    figure (F19), the five unverifiable receipts (F28) and the gameable K2 (F4) are not named in it.
    The closure record therefore does not carry the wave's calibration-debt findings. —
    `corpus/lessons/round-26-verifier-spotcheck.md:60-66`, observed by DistilFindings

---

## Seats that disagree on the same fact

**D1 — Which C3 tool implementation should be installed.** ExecAxisTool F2 reports its draft as the
deliverable and instructs the L1 to "copy to `tools/souji-axis-check.py`"; ExecAxisFixture F4 and
ScribeAxisDocs measure that *same draft* at **6/12** on the frozen case set (root cause
`w1/souji-axis-check.py:142`, the `retired` substring skip) while the already-landed tool scores
**12/12**. Resolution on the bytes: the landed tool (and the wave 12-case fixture) is the correct pair;
ExecAxisTool's instruction is unsafe. Landed pair adopted at `c594901`.

**D2 — Entry B's source-line citation.** RevEntryDrafts F2 reports a defect: entry B "does not cite
the required S132 census at the source-line level". ScribeEntryB F2 reports the re-point is done. The
bytes settle it: `corpus/knowledge/git-auto-maintenance-trigger-set-r23.md:5` at the tip reads
`source: S132 — lanes/souji/round2/evidence/r23-worktree-census.out`. RevEntryDrafts F2 is wrong on
the landed bytes; its residual point (the *body* citation was the object of the re-point) is carried by
ScoutRegroundDocs F9 instead.

**D3 — Is the C3 counter gameable?** RevToolSafety (Status) declares "the frozen C3 counter (K1
self-hosting + K2 12-case fixture) is not gameable; no attack vector found", while CritKillRules F6–F7
shows the K2 green is forgeable (static case worlds, `tail -n 1` reduction) and the control arm is not
evidence about the submitted tool, and MutC3Fixture F2–F6 shows five survivor classes. On the bytes
CritKillRules/MutC3Fixture are right: the fixture reads committed static strings and the counter
reduces the run to the last line. RevToolSafety's own F1–F4 (four input-hygiene defects) are a
different, compatible class.

**D4 — Does K2 certify the heading ordering?** ExecC1Verify F2 and LabC1AfterSim F1 report the landed
`17 44 78` as satisfying the frozen predicate; RevC1Counter F2, ExecC1Surgery A1 and SimpCounterCheck
F1 show the counter's emitted triple is unlabeled and ascending for any order, so the counter alone
certifies nothing. Both readings can hold — the landed file *is* newest-first — but only via the
heading-to-number mapping, which the counter does not print. Treat "K2 green" as insufficient
evidence of ordering.

**D5 — Is C2 a coverage expansion?** The prereg, the lesson and the wave seats' PASS verdicts treat
C2 as the round's coverage claim; CritCoverageCredit F1–F3 finds F1 was already held ground at base
and the credit is a deepening. On the bytes: `corpus/README.md:39` reads "frontier, entries held"
with two entries at base and four at the tip, and no status transition. Not a counter failure — a
credit-attribution question the L1 must answer.

**D6 — Reason recorded for the staged language-edition refusal.** The prereg freezes the reason as
"peripheral corroboration, not load-bearing for the claim"; the landed lesson Gate states a different
reason ("version alignment with 2.56.0 on the mirrors was not provable and the pages' own build
stamps were ambiguous"). ScribeGateDraft F4 reports the conflict and quotes both. The prereg text
also requires the refusal's reason *and flip* to be recorded in the round lesson Gate — the flip is
recorded, the reason differs.

**D7 — Provenance of the +1 staleness in the five `superseded by` refs.** `c1-line-map.md` attributes
the shift to "r25 inserted the scaffold"; ScribeC1Note F1 attributes it to r25's planned bullet at
`:136`. `git log -S` at the tip shows the scaffold entered at `315422b` (round 24) and the r25 planned
bullet at `728b2ce` — the shift is r25's, the scaffold's origin is r24's. The two agree on the
numbers.

**D8 — Two readings of the five refs, and which one landed.** `c1-line-map.md` resolves the literal
numbers against base `89e0fce` (so `:181` names the C3 row, `:180` the C2 row); `c1-append-note.md` and
the landed note resolve them semantically against the r25 base `a6d2d15` (so `:181` names the
assimilation row → tip `:51`, `:180` the C3 row → tip `:50`). Both are internally consistent; the
landed note uses the semantic reading, and its "post-C1" column is now stale at the tip (see F53).

**D9 — S132 currency.** ScoutRegroundOwnwork F3 and LabGitVersion F6 measure the live fleet as
4-of-5 prunable; the landed entry and row S132 state "0 prunable / 5 registrations" and "the fleet is
currently not exposed", and ScribeEntryB F2 reports the census row as re-grounded clean. The re-ground
is byte-exact against the 2026-10-23 evidence file; the *claim built on it* is stale. The bytes support
ScoutRegroundOwnwork's measurement.

**D10 — Round 26's own SCORECARD placement.** CritNoHarm F1 reports that appending the Round 26
measurements block below Round 23 breaks the file's newest-first contract; the L1's C1 work and
ExecC1Verify F2/LabC1AfterSim F1 report C1 green on `17 44 78`. Both are true: C1's counter is green
and the file's ordering is not. The frozen K2 is blind to it by construction.

**D11 — The closure verdict's coverage credit.** The integrator's spot-check (`e78ac7c`, the
non-author closure) records "expansion — improved" and "two admitted entries on F1 frontier ground not
previously held"; CritCoverageCredit F1–F3 records that F1 was *already held* at base and the credit
is a deepening. Both read `corpus/README.md:39`: the base row reads "frontier, entries held" with two
entries and the tip row reads "frontier, entries held" with four — no status transition, no new `F<k>`
row, no Core marking. The spot-check's own C2 section cites that row as the only map change, so its
two statements are in tension. This is the round's live axis-credit question.

**D12 — Where the `§ OPTIONS` locator lives.** The integrator's spot-check records S128's quote as
"located (`§ OPTIONS`)", which is true of the *registry row* (`corpus/SOURCES.md:149`). It is not true
of either admitted *entry* Gate: re-running Q54 at the tip yields `entries=2 locators=0
locators_bad=0`, so the C2 kill rule's "every snapshot § locator resolves to a heading line" clause
resolves nothing. ScoutRegroundDocs F3 is the reading the bytes support; the spot-check's S128 row
check and the entries' Q54 clause are different objects.

**D13 — The refusal reason for the staged language-edition rows.** The prereg froze "peripheral
corroboration, not load-bearing for the claim"; the landed lesson states "version alignment with
2.56.0 on the mirrors was not provable and the pages' own build stamps were ambiguous"; the
integrator's spot-check finds that reason no longer reproduces (the zh-Hans page now says "git-fetch
last updated in 2.56.0"). Three different rationales for one refusal across three artifacts, and the
frozen one is not the landed one.

---

## Residual unknowns (not resolved by any seat, verified open at the tip)

- Whether `c2-gate.tsv` and `c2-k4-after.tsv` were produced by a run at the tip they name or
  reconstructed from a draft (both bind `rev=33e6807`; the entries are byte-identical to the tip's).
- Whether the `## Seat-reported failures` carry text will exist before the landing gate runs.
- Whether the five `verify=ok`-refusing receipts can ever satisfy the prereg's "each `verify=ok`"
  sentence without a counter change (the `COUNTS_RE` grammar is frozen in `tools/souji-receipt-run.py`,
  whose bytes are unchanged since `12fd90b`).
- Whether the operator's `shokuknow` vs `shokuknow` bound-text spelling (SentBounds F1) reaches the
  lane's own machinery: the prereg and `w1-spec.json` both name the path that exists on disk and
  holds `merge/souji`, so no lane artifact is affected.
