# CritC2Coverage — C2's coverage credit, tested against the lane's own map

STATUS: FAIL

Scope: C2 only (coverage axis, SCORECARD 8). C1, the slice's quote content and the
tool selftest are other seats' items and are not judged here.
Read-only: no tool installed, no pacman transaction, no git/jj write, no cleanup,
no process signalling. Base `4edb25dfe262515d0da63224bbba71e02e36cba5`;
landing-gate comparison at `3216c1998fe04d7e23793ffd4e135bd37c3a11f4`.
Evidence: `.ufo/waves/round-22/attempt2/w1/evidence/CritC2Coverage.md`.

`[EXECUTED]` = seen in this session's output. `[INFERENCE]` = derived from source
bytes without running the check.

## Headline

The frozen counter passes `[EXECUTED]`:

```
entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0    exit=0
```

That proves the entries are *citable*: it checks a Gate exists, a URL was opened
on the round date, quotes appear verbatim in named snapshots, source ids resolve,
and ADMIT/REJECT are present. It does **not** test whether the ground is new,
whether the locator names the right section, or whether a lane-relative path in
the entry exists. All three fail below. The coverage credit is therefore not
established by the counter that is offered for it.

## Q1 — Is "no-clobber rename + per-item origin record" new ground?

**Verdict: fails (already held; the delta is evidentiary, not ground).**

Already covering it:

| half | file | status | the decisive bytes |
|---|---|---|---|
| per-item origin record (read side) | `corpus/knowledge/trash-spec-restorable-quarantine.md` | ADMITTED | §6 :20 "A filename in the `$trash/files` directory MUST NEVER be used to recover the original filename; use the info file"; :21 "The key "Path" contains the original location"; :19 no-overwrite; :10 info-first `O_EXCL` |
| no-clobber rename primitive | `corpus/knowledge/quarantine-same-filesystem-rename.md` | HELD (content present) | :28 `renameat2(…, RENAME_NOREPLACE) = 0` observed in its own trace; :10 "`mv --no-copy` turns the cross-device case into a hard failure (exit 1, source untouched): a fail-closed guard for staging" |

The adopted r24 entry's own load-bearing sentence — "which field a restore
actually consumes" — is the S022 §6 rule already quoted in the admitted entry at
:20–:21. The adopted r23 entry's primitive was already traced at :28 of the HELD
entry.

Delta the two adopted entries actually add `[EXECUTED: diffs against the staged
package and against the two existing entries]`:

1. r23: man7 section citations (S110/S111) and **one vendored observation** that
   five specific directories accept `RENAME_NOREPLACE` (S109, produced
   2026-10-23 by `corpus-expansion-1`, "not re-run in this lane"). That answers
   *availability on those five devices* — an upstream precondition — not the
   cross-device copy+unlink semantics K5 holds.
2. r24: `gio(1) trash --list/--restore` spellings (S112) and the `statx` field
   availability (S114). S114 is the only fact in either entry the lane did not
   already hold in any form.
3. No new consequence. r23: "No staging tool is changed by this entry"; r24:
   "still does not specify souji's record format". F4's frontier next step is a
   tool change by the operator (`corpus/README.md:46`), and it is untouched.

The claimed coverage-map effect is also a relabel: the map's "entries held" already
meant *held in corpus*, including an admitted entry (`corpus/README.md`, r13
correction: "F4's trash-spec entry [is] admitted. Only K5 … is HELD"). Before: 2
files, 1 admitted + 1 HELD. After: 4 files, 3 admitted + 1 HELD. Count +2; ground
+ one field-availability fact.

## Q2 — Is adapting a staged entry "coverage" or "import"?

**Verdict: fails as coverage; it is import with re-grounding.**

The distinguisher that the lane's own bar supplies: coverage requires an *in-lane*
observation or a *changed lane consequence* (QUALITY Q2 "installed behaviour
outranks prose … a committed fixture"; Q23 "capability wording matches the
exercised boundary"). Import is a claim authored elsewhere landing with
provenance/citation work.

Applied `[EXECUTED: diffs, package report]`:

- The adopted r24 claim is the staged r24 claim with one verb changed ("uses" →
  "consumes"); the staged text already conceded "The write-side contract and the
  layout are already held (S126, S022)".
- The adopted r23 entry keeps the staged package's five-device claim but *downgrades
  its provenance* from "measured, re-run" to "vendored, not re-run here". The
  empirical content stays the campaign's.
- In-round work that is genuinely this lane's: opening six snapshots, verifying
  quote spans, writing the Gate, re-pointing ids (S124→S109, S116→S110, S115→S111,
  S137→S112, S126→S113, S117→S114). That is citation/calibration work.
- The package's own rule for this situation is the test that decides it: "The
  operator should check that the staged row adds an aspect the held row does not
  already carry" (`MERGE-REPORT.md`). At source-row granularity S112–S114 do add
  aspects; at claim granularity the load-bearing statement is the S022 text the
  lane already holds.

So: import at the ground level, calibration at the citation level. Crediting it to
**coverage** double-counts a calibration gain as a coverage gain, in the same round
that C1 is credited for calibration.

## Q3 — Province scope

**Verdict: holds.**

`PROVINCE.md:3-4`: "**Domain:** fleet repository & workspace hygiene (掃除) —
receipt-gated removal of stale, duplicate, and already-preserved artifacts."
`PROVINCE.md:7-8` (`## Owns`): "the fleet root repo's hygiene surfaces: stray
checkpoint/scratch files, superseded config snapshots, **quarantine staging**."
`## Core / Frontier / Adjacent` lists "F4 restorable quarantine and file-system
semantics — trash layout, same-device rename vs copy+remove."

Both entries are F4 work on exactly those two surfaces. No overreach: the entries
study the reference implementation (`gio`) but r24 states "`gio trash` is not
necessarily the mechanism souji would use", and neither entry claims a tool, format
or deletion authority. Refuses-list surfaces (credentials, operator config, history)
are untouched.

## Q4 — S022 reference and duplicate-URL census finding

**Verdict: holds (no finding as executed), with the rule named.**

Census rule `[EXECUTED: source + run]` — `scripts/sources-census.sh`:
`E04 duplicate URL+scope (no supersedes)` (:25) and
`W04 same URL across scopes (warnings do not affect clean lanes)` (:33);
implementation :644–:649 keys on `url_of()` normalization + the row's `scope`
cell, E04 only when the earlier row in that URL+scope pair is non-rejected and the
new row's `teaches` does not say `supersedes S###`.

Run: `bash scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji`
→ 30 W04 rows, `souji ok corpus/SOURCES.md`, `exit=0`; 114 registry rows; S022
appears exactly once (`grep -c` → 1).

Why the S022 reference cannot fire it: the census parses only `corpus/SOURCES.md`
(:2, :7), never knowledge files, and the round cites S022 by id rather than
appending a row. The risk exists only if a *new* row is appended for the same URL:
same scope "restorable trash layout" → **E04 → exit 1** (the prereg Target would
fail); different scope → W04 warning only. S049/S036 is the existing precedent for
the allowed cross-scope shape.

Residual (not a census finding): S022's `used-by` cell still names only
`trash-spec-restorable-quarantine.md`, so the index row now understates its users.
E11/W03 do not fire on that, and the prereg's adopted-row rule does not require it,
but "an index row is a claim" (fleet floor) argues for adding the new path.

## Bounded findings

**F1 — BLOCKING, executed. The adopted r24 entry introduces a landing-gate
regression.**

`corpus/knowledge/quarantine-origin-record-fields-r24.md:47` cites
`corpus/knowledge/quarantine-origin-record-fields-r23.md`. That file exists in
neither the working tree nor any revision; it is the *staged package's* entry name,
which the lane chose not to adopt (the adopted origin entry is the `-r24` one).

```
gate @ 4edb25d → findings=4  exit=1
gate @ 3216c19 → findings=5  exit=1
  LG-DANGLING-PTR  corpus/knowledge/quarantine-origin-record-fields-r23.md
                   corpus/knowledge/quarantine-origin-record-fields-r24.md:47 cites path absent
```

Not exempted (`corpus/pointer-exemptions.tsv`, 4 rows). Extraction confirmed with
the gate's own `_pointer_paths`: `['corpus/knowledge/quarantine-origin-record-fields-r23.md']`;
`check_pointers` scans every `corpus/knowledge/*.md`. Q31 requires authority files
to cite only evidence that exists at the landing revision; the prereg's
"no axis may be harmed" makes this a calibration/operability harm, not a style nit.
Axes: calibration (harm), operability (harm).
*Smallest safe correction:* name the provenance without a lane-relative path
("the staged round-2 origin-record entry in the `corpus-expansion-1` package"), or
delete the sentence. Do not create a stub file: a placeholder entry would be a false
receipt and would itself fail QUALITY Q17's spirit.

**F2 — MAJOR, fixable, executed. The committed r23 Gate locator does not exist in
its own snapshot.**

Committed (HEAD): `ADMIT: "do not copy if renaming fails" — § OPTIONS --no-copy`.
Snapshot `man7-mv.1.txt`: heading list at :29 is
`NAME | SYNOPSIS | DESCRIPTION | AUTHOR | …` — no `OPTIONS`; the quoted line is at
:91 under `DESCRIPTION` (:60). A fix is drafted but **uncommitted**
(`git diff corpus/knowledge/quarantine-staging-no-copy-r23.md` →
"§ DESCRIPTION, option `--no-copy` — the page has no OPTIONS heading").

Root cause is in the frozen predicate itself: check 3 requires *a* locator token,
not a correct one. So `ok=2` cannot be read as "re-grounded"; at the admitted bytes
a reader following the Gate looks for a section the page does not have. Axes:
calibration (harm), coverage (weakens the re-grounding claim). Fix lands with the
drafted diff; the finding stands against the bytes at `3216c19`.

**F3 — MINOR, wording. Title overclaims relative to the entry's own disclosure.**
r23 title: "A no-clobber staging primitive exists on every device this fleet uses";
body: "vendored, point-in-time observation … produced by another lane … this lane
did not re-run the probe". Five directories on one kernel, run elsewhere, is not
"every device this fleet uses". Q23 asks capability wording to match the exercised
boundary. Correction: title → "exists on the five devices measured (vendored
observation)"; body stands.

**F4 — MINOR, evidence hygiene. Two id spaces in one round's evidence.**
`slice-verdicts.tsv` keys are campaign ids; the lane registry now holds S109–S114
for different documents (lane S114 = `statx(2)`; campaign S114 = the git-prune row
whose verdict text mentions `git-repack[1]`). The mapping lives only in the lesson
(M16), not in the TSV. No frozen rule is broken (the slice predicate is
id-space-agnostic), but a reader resolving S114 against the registry gets the wrong
document. Correction: a header line naming the space, or `campaign: S114` in the
pointer column.

**F5 — observation, judgment input for the canonical judge.**
The coverage-axis claim the round should be able to defend is "+2 admitted entries
carrying two previously uncited facts (S109 availability, S114 statx fields)"; it
should **not** be "F4 advanced". The frontier next step is unchanged and both
entries decline to change it. A judge may accept +2 entries as legitimate corpus
growth; it should not accept the assimilated package as new ground, because the
lane's own map already held both halves. This one is not fixable by wording — it is
a tradeoff: admitting the package is fine as consolidation, mislabeling it as
coverage is not.

## What I did not do

- Did not re-derive the seven slice rows' quote content (Slice*/RevSliceVerif seats)
  or the gate-check selftest (Mut*/AuditCap seats); I ran the frozen counter once,
  as the claim's own command.
- Did not run the gate-check on the post-fix working tree as a landing claim; the
  only landing-gate runs recorded here are at `4edb25d` and `3216c19`.
- Did not read `/proc`, credentials, private TSVs, `.tower`, or the operator sweep.
