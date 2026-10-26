# SwarmReviewer46 — calibration of the lane's self-assessment (r29, read-only)

Lane: /home/vgpnk/Projects/shokunin/souji-shokunin
Base measured: `691dd29211c53d0ef94fa072394cb9c8a69fe92e` (master branch, `git rev-parse HEAD` = `b8cb4b31ce80e2e3314b88e85d40ea9873180804`, the preregistration commit; working tree carries 1 modified tracked file, see Finding 5).
Evidence medium: committed bytes at a named revision (`git show <rev>:<path>`, `git ls-tree`, `git cat-file`). No code symbol server is applicable: every measurement is against historical blobs, not the working tree, so `lsp` references/definitions cannot answer these queries; the working tree was never the object of measurement.

## Status

STATUS: PASS — every assigned observable was re-derived from committed bytes at base and the SHONEN/capability pointers resolve; the lane's self-assessment is accurate in its counters and arithmetic chain, with two low-severity record drifts (Finding 1, Finding 2) and three scope notes (Finding 3–5) that the frozen r29 counters do not measure. No edits, no git writes, no installs.

## Evidence

All commands run from the lane root with `python3 -B` (no `__pycache__` written); `R=691dd29211c53d0ef94fa072394cb9c8a69fe92e`, `P=b8cb4b31ce80e2e3314b88e85d40ea9873180804`.

**SOURCES census (CORPUS.md `### Census` block, spacing-tolerant forms).**

```
$ git show $R:corpus/SOURCES.md | grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'
139
$ ... awk ... NF!=13 ...            # malformed rows      -> 0
$ ... awk tier histogram ...       # A=132 B=5 C=2
$ ... awk status histogram ...     # mined=115 queued=15 rejected=9
$ ... duplicate ids                 # (no output)
$ ... enum violations/tier inflation # (no output)
```

**Knowledge entries and grounds.**

```
$ git ls-tree -r --name-only $R -- corpus/knowledge/ | grep -c '\.md$'
20
$ git grep -lE '^ground: F' $R -- corpus/knowledge/ | wc -l       # 13 files
$ git grep -hE '^ground: F' $R -- corpus/knowledge/ | sort | uniq -c
  2 ground: F1 ...   5 ground: F2 ...   6 ground: F4 ...           # F3=0, F5=0
```

Entries without a `ground:` header (7): `dupe-finders-detect-then-act.md`, `git-auto-maintenance-prunes-worktrees.md`, `git-grace-periods-and-expire-to.md`, `jj-colocation-receipts.md`, `process-residue-observations.md`, `quarantine-same-filesystem-rename.md`, `trash-spec-restorable-quarantine.md` (`for f in ...; do git show $R:$f | grep -qE '^ground: F' || echo $f; done`).

**Coverage-map agreement (counter named in the frozen C3 contract).**

```
$ python3 -B tools/souji-coverage-agreement.py --root . --rev $R
grounded=13 mapped=13 dangling=0 mismatches=0
rc=0
```

**Capabilities table.** 29 data rows (`awk '/^## Capabilities/{f=1;next} /^## Planned/{f=0} f&&/^\|/{n++} END{print n-2}'`). Every backticked evidence path resolves at `$R`; the two globs resolve to 2 files (`census/round-17/jj-receipts-*.txt`) and 6 files (`census/round-23/records/*.tsv`).

**SHONEN `[~]` pointers (base `$R`).**

| SHONEN line | pointer | resolution |
|---|---|---|
| 5-6 | `SKILL.md` Decision tables/Error patterns/Checklists/Gate registry; `corpus/SOURCES.md` S100-S103; `corpus/lessons/round-21.md` Gate | SKILL.md headings :42, :78, :147, :167; 4 rows S100-S103 (S100/S101/S102 mined, S103 rejected); round-21 `## Gate` :25 |
| 7-8 | `LOG.md:362` (96 pushed-receipt artifacts quarantined, second-checked, removed) | :362 is the section heading `## 2026-10-19 — operator sweep (execution)…`; the 96-artifact removal is at :368, the staging/second-check flow at :372-380 |
| 9-10 | `census/round-21/run-acceptance.py`; `accepted-matrix.json` (3/3 sources, each18/18); `remote-source-after.json` | all three files present; matrix `scenarios=3 replayed=3 summaries_equal=true`, every record `returncode=0 matched_command_count=18 all_matched=true` |
| 11-12 | `PROVINCE.md` Round21 privacy boundary; `.ufo/waves/round-21/w1/ConnSiblingOverlap.md`; `corpus/lessons/round-21.md` Boundaries | PROVINCE `### Round21 privacy boundary` :161; wave file tracked; lesson `### Boundaries and teaching` :38 |

All four resolve; none of the four is marked `[x]`.

**Saturation / axes consistency.** SCORECARD:226-228 "Saturation line: 8 per axis; stagnation window 3 rounds. Scores per the rows above: coverage 8, operability 8, calibration 7"; rows at :13-15 read coverage 8 / calibration 7 / operability 8. Consistent with the prereg ("saturation line 8, so the lowest-axis obligation stands") — calibration 7 is the lowest and is below the line.

**Frozen before-values reproduced at base (the r29 records' own `Before` claims).**

```
$ python3 -B tools/souji-registry-agreement.py --root . --rev $R --list-rev $P
K1 used-by-no-cite S215 …; K1 cited-not-in-used-by S075, S076, S022, S024, S025
K2 uncorrected LOG.md:1758; SCORECARD.md:23; corpus/lessons/round-28.md:22; :40
SUMMARY k1=6 k2=4 mismatches=10 rev=691dd29…        rc=1
$ python3 -B census/round-29/c2-counter.py --root . --rev $R
r26 records=1382 failed=152 uncovered=14 floor_violation=0
r27 records=124 failed=0 uncovered=0 floor_violation=0
r28 records=75 failed=0 uncovered=0 floor_violation=0
SUMMARY manifests=3 failed=152 uncovered=14 floor_violations=0 rev=691dd29…   rc=1
$ F3 grounded = 0 ; SOURCES rows = 139
```

Exact match to `census/round-29/records/controls.tsv` rows `C1-do-nothing(base)`, `C2-do-nothing(base)`, `C3-do-nothing(base)`. The four K2 phrases sit at their stated `file:line` at `$R` (checked line-by-line; each contains its phrase).

**SCORECARD calibration row re-derived with its own pinned instrument** (`tools/souji-declared-evidence.py` sha256 `65817d0d…` == `census/round-22/attempt2/instrument-digests.txt`):

```
rev 4edb25d… (before): assertions=55 resolved=52 skipped=33 mismatches=3   rc=1
rev 9301d98… (after) : assertions=63 resolved=63 skipped=40 mismatches=0   rc=0
rev 691dd29… (base)  : assertions=164 resolved=145 skipped=223 mismatches=19 rc=1
```

The two pinned rows in SCORECARD:14 reproduce exactly. The base reading is decomposed in Finding 4.

**Scorecard measurement-table arithmetic (row counts / grounded F4).**

```
e78ac7c rows=132 f4=2 | 6cb22dc rows=135 f4=4 | de478b4 rows=139 f4=6
ed270c4 rows=139 f4=6 | 691dd29 rows=139 f4=6 | 89e0fce rows=127 f1=0
9a6e0f1 rows=132 f1=2 | eb1aa49 rows=119 | 31984f4 rows=33 tiers A=29 B=3 C=1 status mined=16 queued=15 rejected=2
```

Every number matches its SCORECARD row (:22, :32, :288, :289, :103, :151). The r26 C1 heading claim `headings 17 44 78` is exact at `07f83e6` (`### Round 25 measurements` :17, `### Round 24` :44, `### Round 23` :78).

**Fleet admission pointer.** `/home/vgpnk/Projects/shokunin/MANIFEST.json` `rounds[408]` = round 21, lane souji, `admitted: true`, verdicts calibration/operability/coverage improved — matches SCORECARD:13/:15; `rounds[402]` = round 20 admitted.

**Frozen instrument digests bind committed bytes.** 6/6 lines of `census/round-29/records/frozen-digests.txt` equal `git show $P:<path> | sha256sum` (registry-agreement `51131fe7…`, c2-counter `5ab641c4…`, stale-statements `dccc57f2…`, controls.sh `d08c5417…`, gate-check `d5ed0805…`, coverage-agreement `bb506469…`).

**Round-start census record.** `census/round-29/records/census-start.txt` at `$P`: 35 `W04` lines, 0 `error`, `exit=0` — matches the prereg's "rc 0, 35 W04, 0 errors". `axis-check-before.txt` reads `claims=3 flags=0`.

## Findings

1. **[low] A self-assessed row count is stale in the live corpus doc.** `corpus/README.md:32` — "`SOURCES.md` — where souji learns (contract v1): 33 rows — `grep -cE …` 2026-10-19". Observed at `$R`: **139** rows. The statement is date-stamped and SCORECARD:151 names 33 as the r13 *baseline*, but the file carries no append-only correction naming the current value; a reader of the coverage doc sees a 33-row registry. Scope limit: this statement is outside the four statements frozen in `census/round-29/stale-statements.tsv`, so C1's `mismatches=0` will not retire it.

2. **[low] Coverage-map "entries" columns name supersets of the grounded entries.** Map rows at base vs `^ground: F<k>` headers: `corpus/README.md:39` (F1) names **4** entries, grounded F1 = **2**; `:41` (F3) names **1**, grounded F3 = **0**; `:42` (F4) names **8**, grounded F4 = **6**; F2 names 1 (`:68`), 4 (`:517`), 5 (`:544`) against grounded F2 = **5**. The grounded→map direction is measured and clean (`mismatches=0`, Evidence); the map→grounded direction is not measured by any tool, so a row that reads "entries held" can overstate the grounded set by the pre-`ground:` r12/r13/r17 entries (`trash-spec-restorable-quarantine.md`, `quarantine-same-filesystem-rename.md`, `git-auto-maintenance-prunes-worktrees.md`, `git-grace-periods-and-expire-to.md`, `dupe-finders-detect-then-act.md`, `jj-colocation-receipts.md`, `process-residue-observations.md` — 7 unheaded of 20 `.md`).

3. **[note] One declared tool digest is tip-stale but revision-correct.** `SCORECARD.md:68` declares `tools/souji-coverage-agreement.py` sha256 `71b89eb3…`; committed bytes at `$R` hash to `bb506469…`. At the row's own measured commit `778747e` the blob hashes exactly `71b89eb3…` (the tool changed in `7e4dbef`, r25 C1: +67/−20). The row's measured-commit cell is correct, so this is a qualification risk, not a false claim; the pinned declared-evidence instrument reports it as `mismatch:digest` when run at the tip.

4. **[note] The pinned declared-evidence instrument reads 19 mismatches on SCORECARD at base; all 19 are instrument-scope artefacts, none a dangling path.** `164 assertions / 145 resolved / 223 skipped / 19 mismatches`. Breakdown: 15 unqualified paths (`c1-after.tsv` ×2, `c2-after.tsv` ×2, `c3-after.tsv` ×1, `w2/RevR3Counter.md` ×1, `count-objects-garbage-readings-r25.md`, `repo-size-census-readonly.md`, `git-repo-structure-readonly.md` ×3, `c1-control-stub.tsv`, `c2-fixture-after.tsv`, `git-auto-maintenance-prunes-worktrees.md`, `git-grace-periods-and-expire-to.md`) — each exists at its round-qualified path (`census/round-2{4,7,8}/records/…`, `corpus/knowledge/…`, `.ufo/waves/round-25/w2/…`), verified with `git cat-file -e`; 2 are truncated tool-digest prefixes read as revisions (`65817d0d`, `09bb8e0d`); 2 are the Finding-3 digests. Zero true path failures in the lane's self-assessment file at base.

5. **[observed] The working tree diverges from committed bytes on one tracked wave file.** `git status --porcelain` at HEAD `b8cb4b3` reports ` M .ufo/waves/round-26/w1/ScribeGateDraft.md`. The r26 manifest record expects `8f25ae21f6009a889f308cb690f9dda2a2932af7743bc4c68f1534b34071bac0`, which is exactly the committed blob at `$R`; the on-disk file hashes to `a7f30602248fc803eed8157f7a62d326152335e1936cc6bfaabf422cae9700dc`. Consequence for calibration: the r28-style disk-based receipt check would fail this record, the C2 committed-bytes surface passes it — a live instance of the defect C2 claims to close. Not touched (not this seat's file).

6. **[note] The three axis scores have no reproducible derivation; the lane says so itself.** SCORECARD:5-7 ("a 0–10 score only where a reproducible mapping from evidence to number exists") and `corpus/README.md:24-25` ("Numeric rubric: axis scores start at 0 with explicit counting commands; a calibrated numeric rubric is a standing gap") mean `calibration 7 / coverage 8 / operability 8` cannot be re-derived by a command; the saturation obligation ("lowest axis below the line of 8") is therefore a policy statement, not a measurement. The per-round evidence under each row (re-derived in Evidence above) is accurate; the numbers attached to it are unmapped. `SCORECARD.md:14` itself states calibration "record accuracy, not a scored axis move".

7. **[info] SHONEN pointer composition.** All four `[~]` pointers resolve (Evidence table). Item 1's cited set `corpus/SOURCES.md S100-S103` includes **S103**, which `corpus/lessons/round-21.md:34` records as rejected ("S103 rejected for the attempted scope"). The pointer is a registry reference, not an admitted-evidence set; as written it can be read as four supporting sources.

8. **[verified] No contradiction found between the frozen r29 before-values and committed bytes.** C1 `k1=6 k2=4 mismatches=10`, C2 `failed=152 uncovered=14 floor_violations=0`, C3 `F3 grounded=0 / rows=139` all reproduce at `$R` (Evidence); the C3 base `grounded=13 mapped=13` also reproduces. The four K2 stale phrases are present at their exact lines and no `R29-CORRECTION` line follows any of them.

## Verification gaps / unrun

- `sources-census.sh validate` and the r28 `souji-gate-check.py` / `souji-landing-gate.py` rows were **not run**: they require fleet-root write surfaces or round snapshot inputs outside this seat's write scope; their SCORECARD numbers are therefore reported as declared, not re-derived. `[INFERENCE]` they are unchanged since r28, where the row records rc 0 / `entries=2 ok=2 fail=0`.
- The r21 canary/oracle figures in SCORECARD:13 (`oracle 6/27→27/27`, `leaks 19→0`) and the r22 "wider span-inclusive 67/67/40/0" reading were not re-executed; only the two pinned declared-evidence readings at `4edb25d`/`9301d98` were re-derived.
- No tool was installed or upgraded (none needed), so there is no tooling record.
- Scratch used `/var/tmp/souji-r29-SwarmReviewer46/` and was removed.

## Deliveries

- `.ufo/waves/round-29/w1/SwarmReviewer46.md` (this report). No other file written.
