# deliver-m1-audit-r27 — audit of the round-31 M1 carry in corpus/lessons/round-27.md

Seat SwarmCritic25, wave 2 (falsification), attempt 1. Read-only. Lane
`/home/vgpnk/Projects/shokunin/souji-shokunin`, base `9f17a1ef571f3a510a51ac233d7cf50ac0c871fc`,
preregistration `1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525`, M1 landing
`c6108301cbf0ca0ad086ff0ece6b76adad6b74b6`, tip `2c16d018e40db7c23420a2c3bb546b52957bcc25`.

Object under audit: the appended section at `corpus/lessons/round-27.md:43-82` (heading at :43,
preamble :45-52, 29 bullets :54-82), landed by
`git show c6108301cbf0ca0ad086ff0ece6b76adad6b74b6` (diff base..c610830, +41 lines, no in-place edit).

## 1. Quote exactness — 29/29 exact, no ellipsis truncation

Method: parsed the 29 bullets (`^- \`census/round-27/waves/w1/<Name>.md\` line <N> — <disp>: <quote>$`),
read each report from the M1 commit, took the paragraph starting at the cited line and running to the
next blank line, and compared under the landing gate's own normalization — `norm_line`, pinned at
`tools/souji-landing-gate.py:354-363`: `unicodedata.normalize("NFC", text)`, drop `*` and backticks,
`re.sub(r"\s+", " ", ...)`, strip.

Result: 29 compared, **0 DIFF**. Every bullet reproduces its report paragraph exactly, including
`census/round-27/waves/w1/RevReportIntegrity.md:5` (716-byte paragraph; the bullet at
`corpus/lessons/round-27.md:73` is 778 bytes and ends "…amendment is needed."). No bullet relies on the
gate's prefix-plus-ellipsis carry arm (`carries()` clause (b), `tools/souji-landing-gate.py:487-504`):
the U+2026 count in the carry section is 0. The report bytes are unchanged base..tip
(`git diff 9f17a1ef 2c16d018 -- census/round-27/waves/w1` empty), so the quotes are honest at base, at
the landing commit and at tip.

Line numbers: every cited `line N` is the line where that report's STATUS paragraph starts (a wrong line
would have produced a DIFF in the comparison above). 29 bullets, 29 distinct paths.

Carry recognition (independent of the M1 receipt):

```
$ python3 -B tools/souji-landing-gate.py --root <clone> --rev 2c16d018e40db7c23420a2c3bb546b52957bcc25 --round 27 --fleet-root /home/vgpnk/Projects/shokunin
SUMMARY	findings=0	checked_reg=63	checked_changed=0	checked_pins=13	checked_measured=3	checked_markers=29	status_lines=79	carry_heading=1	checked_reports=94
$ python3 -B tools/souji-landing-gate.py --root <clone> --rev 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc --round 27
SUMMARY	findings=32	checked_reg=62	checked_changed=0	checked_pins=13	checked_measured=3	checked_markers=29	status_lines=79	carry_heading=0	checked_reports=94
# id breakdown of the 32: 29 LG-SEAT-UNCARRIED + 3 LG-DANGLING-PTR
# the 3 dangling are the pre-existing fleet pointers, not introduced by the carry:
#   ../.ufo/waves/hyaku/jj-w1/reports/JjAuditSouji.md (corpus/README.md:217)
#   ../.ufo/waves/hyaku/jj-w1/reports/JjTrialSouji.md (corpus/README.md:217)
#   .ufo/waves/hyaku/jj-w1/reports/ (corpus/knowledge/jj-colocation-receipts.md:148)
```

The preamble's numbers (`findings=32 ... checked_markers=29 ... carry_heading=0`) are exact.

## 2. Verdict per entry

Rule taken from the carry itself (`corpus/lessons/round-27.md:48-51`) and the wave-1 delivery's
"Disposition basis" header: `resolved@<commit>` iff the stated repo-state defect is absent from the
landed bytes and that commit removed it; `open` iff **any** stated defect or missing receipt still
stands at tip.

| # | report:line | chosen | verdict | evidence |
|---|---|---|---|---|
| 1 | CritC3Attack.md:2 | open | OK | Setup always writes report and prereg (`tests/fixtures/r27-pre-report-gate.sh:23-24`), so the four cases never exercise the `check-report`/`check-prereg` red paths. |
| 2 | CritCounterFidelity.md:5 | open | OK (basis partly false) | Fleet-root dependency reproduced: base gate round 27 = 32 findings without `--fleet-root`, 29 with. `c2-after.tsv` has no tool-digest column. Basis says the false-`gate_sha256` clause "is gone" — true only of `census/round-27/records/c1-before.tsv`; see finding F1. |
| 3 | CritErrorPatterns.md:2 | resolved@c973d1a | OK | `c1-after.tsv`, `c2-after.tsv`, `c3-after.tsv` all exist at `c973d1a` (`git show --stat`), none at `6cb22dc`; fixture at `6cb22dc`. |
| 4 | CritNoHarmAttack.md:2 | open | OK (basis count wrong) | Each `corpus/pointer-exemptions.tsv` row is path + reason text only: no finding identity, no expiry. Basis says "three rows"; the file has four rows at `1b811368` and at tip. |
| 5 | CritReportContract.md:5 | open | OK (basis false) | Item 2 stands: `git grep -l PENDING <tip> -- tools tests/fixtures` is empty, so no pre-filing residue check exists. Item 5 was in fact discharged: `corpus/lessons/round-27.md:37` (already at `c973d1a`) carries the wave shape, 79 seats, role split, dead-seat statement and "L1 performed the planner seat" — a lane commit, not only the fleet report. |
| 6 | ExecC1Counter.md:2 | resolved@c973d1a | OK | `census/round-27/records/c1-after.tsv` = `6cb22dc… 02b58f81… 2 52 2`, committed there. |
| 7 | ExecC3Counter.md:2 | resolved@6cb22dc | **WRONG-RESOLVED** (hash scope) | `git cat-file -e 6cb22dc:census/round-27/records/c3-after.tsv` → "exists on disk, but not in '6cb22dc…'". The receipt the basis cites was added in `c973d1a` (`git show --stat c973d1a`). Resolution is real at tip; the named commit does not contain it. |
| 8 | ExecCensusAfterScript.md:2 | open | OK | `census/round-27/records/` holds no census-after receipt (only `sources-census-after.out`, a SOURCES census), and `w1/census-after.sh` has no committed run. |
| 9 | ExecKnowledgeMechanism.md:2 | resolved@6cb22dc | OK | `census/round-27/sources/{glocalfile.c,gfileutils.c,SHA256SUMS}` and `census/round-27/assimilation/*` present there; recomputed sha256 `66b588c4…` and `5161ae43…` equal the entry pins. |
| 10 | ExecPycacheFix.md:2 | open | OK | `census/round-10/__pycache__/S13-candidate-battery.cpython-314.pyc` still tracked at tip. |
| 11 | ExecScorecardDraft.md:2 | resolved@c973d1a | OK | Round-27 measurement block at `SCORECARD.md:27-35` (tip numbering), `PENDING` count 0. |
| 12 | LabGitIgnoreProbe.md:4 | open | OK | 5 tracked `__pycache__` blobs at tip, the r10 `.pyc` among them. |
| 13 | LabSliceFetch.md:2 | open | OK | DOI clause stands (`corpus/lessons/round-27.md:14`: S118 unverifiable, no payload). The S114 clause was fixed at `6cb22dc`: `slice-verdicts.tsv` row S114 = accepted with a located quote. |
| 14 | RevC2Entries.md:2 | resolved@6cb22dc | OK | Both entries carry `## Gate` with `opened: 2026-10-25` and ADMIT lines; `corpus/README.md:42` lists both. |
| 15 | RevC2Rows.md:4 | resolved@6cb22dc | OK | `corpus/SOURCES.md:154` (S152) contains no S146; tip gate `--round 27 --fleet-root` = findings 0, so no `LG-DANGLING-PTR`. |
| 16 | RevC3Fixture.md:4 | resolved@6cb22dc | OK for the stated defect (residual, F2) | Deleting the case-2 block now prints `cases=4 pass=3 … failures=0` and exits 1. Replacing case 2 with a duplicate of case 1 still prints `cases=4 pass=4 control=FALSE-GREEN-REJECTED` rc 0. |
| 17 | RevC3Gate.md:4 | open | OK | Reproduced a live false PASS: with `GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=core.excludesFile`, an untracked `stray.txt` yields `check-clean=PASS` and rc 0; without the env, `check-clean=FAIL`, rc 1. |
| 18 | RevMistake.md:2 | resolved@c973d1a | OK | `corpus/lessons/round-26-verifier-spotcheck.md:13` is the routed Leftovers defect; the four-case fixture is committed at `6cb22dc`. |
| 19 | RevNoHarm.md:7 | resolved@6cb22dc | OK | `c1-after.tsv` records `findings=2` (not 3); tip gate round 27 = 0 findings, so no staged `corpus/` pointer landed. |
| 20 | RevReportIntegrity.md:5 | open | OK (basis false) | Two clauses stand: no zero-`[PENDING]` check in `tools/`/`tests/fixtures/`, and the lesson carries no `ls-remote` lane-tip line. The wave-shape clause was discharged at `corpus/lessons/round-27.md:37` — the basis's "only in the fleet report" is false there. |
| 21 | ScoutScorecardState.md:4 | resolved@c973d1a | **WRONG-RESOLVED** (substantive) | Clause (ii) still stands at tip: `census/round-27/waves/records/c1-before.tsv` column `gate_sha256` = `e67810d130817879fddd71c5ceeb5d5fd37e6ea8`, which is `git rev-parse e78ac7c:tools/souji-landing-gate.py` (a 40-hex git blob SHA-1), not a sha256. The file was committed at `765fe8b` and is unchanged at tip. The basis recomputed the *other* file, `census/round-27/records/c1-before.tsv` (`02b58f81…`, 64 hex), which never had the defect. |
| 22 | ScribeInvariant.md:2 | resolved@6cb22dc | **WRONG-RESOLVED** (hash scope) | The SKILL.md `+1/-1` at `6cb22dc` is real (row at `SKILL.md:226`), but the second clause ("C3 delivery/test claims remain unverified") is discharged only by `c3-after.tsv`, which exists only from `c973d1a`. |
| 23 | ScribeLOG.md:2 | resolved@c973d1a | OK | `LOG.md:1743` = "## 2026-10-25 — Round 27 attempt 2: F4 source admission, pre-report gate, honest stop", followed by the C1/C2/C3 outcomes. |
| 24 | ScribeLessonGate.md:2 | resolved@c973d1a | OK | `corpus/lessons/round-27.md:3-14` Gate with ADMIT S152/S210/S211, located line numbers and the S119 REJECT. |
| 25 | ScribePrereg.md:2 | resolved@6cb22dc | OK | In the clone checked out at `6cb22dc`: `python3 -B tools/souji-axis-check.py --prereg census/round-27/records/preregistration.txt --scorecard SCORECARD.md` → `claims=3 flags=0`, rc 0 (`MACHINE BLOCK` at :11, `END` at :24). |
| 26 | ScribeReport.md:2 | open | OK | The lesson has no Trend verdicts and no stale-lane section (only `Findings`/`Residuals`/`Receipts`/`Mistakes`). |
| 27 | ScribeScorecard.md:2 | resolved@c973d1a | OK | Same block; `[PENDING]` landing-tip values replaced by values measured at `6cb22dc`. |
| 28 | SimplExistingTools.md:2 | open | OK | `## Residuals` (`corpus/lessons/round-27.md:29`) keeps the 36 inherited r26 wave files in place; no removal in the landed record. |
| 29 | SimplWaveSpec.md:2 | open | OK | `census/round-27/waves/w1-spec.json` still contains `80-item` at tip while the record counts 79 seats. |

Tally: **26 OK, 3 WRONG-RESOLVED, 0 SHOULD-BE-RESOLVED, 0 MISQUOTED.**

## 3. Findings

**F1 — WRONG-RESOLVED, entry 21 (`corpus/lessons/round-27.md:74`).** The seat's mislabel finding is
true of the wave receipt and that receipt is part of the lane at tip; `resolved@c973d1a` is displaced to
a different file. Reproduce:

```
$ git -C <lane> show 2c16d018…:census/round-27/waves/records/c1-before.tsv
rev	gate_sha256	findings	checked_reg	rc
e78ac7c4837b81b634db4a927605a751a7f006ba	e67810d130817879fddd71c5ceeb5d5fd37e6ea8	2	50	2
$ git -C <lane> rev-parse e78ac7c4837b81b634db4a927605a751a7f006ba:tools/souji-landing-gate.py
e67810d130817879fddd71c5ceeb5d5fd37e6ea8
$ git -C <lane> log --oneline --diff-filter=A -- census/round-27/waves/records/c1-before.tsv
765fe8b round-28: repair pointers, curate F4 primitives, capture wave evidence
```

Axis it would harm: **calibration** (a receipt column labelled `gate_sha256` holds a SHA-1, and the M1
carry records the opposite of what the bytes say). Correction: change entry 21 to `open`, or name
`c973d1a` **and** drop the claim that clause (ii) is discharged (it is not), or fix the wave
receipt — out of this seat's write scope.

**F2 — WRONG-RESOLVED, entries 7 (`:60`) and 22 (`:75`), hash scope.** Both bases lean on
`census/round-27/records/c3-after.tsv`, absent at `6cb22dc`, added at `c973d1a`
(`fatal: path … exists on disk, but not in '6cb22dc…'`). The dispositions are true at tip; the named
commit is wrong. Axis: **calibration** (a reader replaying `git show --stat 6cb22dc` cannot find the
cited receipt). Correction: `resolved@c973d1a1c2d8aa1679adc61b2c76634d50e0c1c0` for entry 7 and 22, or
cite `6cb22dc` only for the installed tool/fixture half.

**F3 — basis displacement (entry 2, `:55`).** Same artifact swap as F1 in the wave-1 delivery's basis
row 2 ("the false-`gate_sha256` clause is gone"), while the entry stays `open`. Axis: **calibration**
(evidence quality of the disposition basis). Correction: state that the wave receipt is still mislabelled.

**F4 — residual in the installed r27 fixture (entry 16), `tests/fixtures/r27-pre-report-gate.sh:76-78`.**
The frozen line keys on `passes == 4`, not on case identity, so a substituted case keeps it green:

```
# case-2 block replaced by a duplicate of case 1 under label clean-pass-again
cases=4 pass=4 control=FALSE-GREEN-REJECTED
rc=0
```

The seat's exact F1 reproduction (delete the case-2 block) is fixed (now `passes=3`, rc 1), so entry 16
stays OK; the count-based class survives. Axis it would harm: **operability** (round 27's C3 evidence
`cases=4 pass=4` can be printed with the remote-mismatch path untested). Not introduced by round 31.

**F5 — false statements in the basis (entries 4, 5, 20).** (a) `corpus/pointer-exemptions.tsv` has four
rows at `1b811368` and at tip, not three. (b) Basis rows 5 and 20 assert the wave-shape/planner record
exists only in the fleet report; `corpus/lessons/round-27.md:37` carries it in the lane from `c973d1a`
("one v2 wave, 79 seats … L1 performed the planner seat"). Verdicts remain `open` on their other
clauses. Axis: **calibration**.

**F6 — inconsistent open/resolved rule (entries 13 vs 21).** Entry 13 stays `open` although one of its
two defect clauses (S114 quote absent) was fixed at `6cb22dc`; entry 21 is `resolved` although one of its
clauses stands. One of the two applications of the "any clause" rule is wrong; F1's correction (entry 21
→ `open`) makes both consistent without touching a target.

## 4. Not verified here / limits

- No network fetch was needed: every claim above is a lane-byte or lane-commit fact.
- I did not audit the round-26 or round-28 carries (out of this seat's assignment).
- The M1 after-receipt's own readings were spot-checked for round 27 only (`findings=0` at tip,
  `findings=32` at base reproduced).
