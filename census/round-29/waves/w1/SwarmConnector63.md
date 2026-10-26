# SwarmConnector63 — cross-claim pattern finder (souji r29 w1)

## Status

STATUS: PASS — three cross-claim overlaps that the frozen counters measure as *breaking* were each
isolated, reproduced in a scratch clone of the lane base, and shown to be avoidable by a landing
order; one (the SCORECARD.md:23 K2 pin) is a **confirmed counter-breaking defect** in the
round-end edit as specified by `deliver-scorecard-log-skeleton.md`, and it holds under both the
frozen v1 counter and the stricter v2 amendment now in the lane worktree.

## Evidence

All commands are absolute-path, read-only against the lane except the scratch clone under
`/var/tmp/souji-r29-SwarmConnector63.XXXXXX/` (removed at seat end). Lane base
`691dd29211c53d0ef94fa072394cb9c8a69fe92e`, preregistration
`b8cb4b31ce80e2e3314b88e85d40ea9873180804`, branch `master`.

### E1 — base counters reproduce the frozen controls

```
$ python3 -B tools/souji-registry-agreement.py --root . --rev 691dd29211c53d0ef94fa072394cb9c8a69fe92e \
      --list-rev b8cb4b31ce80e2e3314b88e85d40ea9873180804
K1 used-by-no-cite S215 corpus/knowledge/git-auto-maintenance-trigger-set.md
K1 cited-not-in-used-by S075 corpus/knowledge/process-residue-observations.md
K1 cited-not-in-used-by S076 corpus/knowledge/process-residue-observations.md
K1 cited-not-in-used-by S022 corpus/knowledge/quarantine-origin-record-fields-r24.md
K1 cited-not-in-used-by S024 corpus/knowledge/quarantine-same-filesystem-rename.md
K1 cited-not-in-used-by S025 corpus/knowledge/quarantine-same-filesystem-rename.md
K2 uncorrected LOG.md:1758
K2 uncorrected SCORECARD.md:23
K2 uncorrected corpus/lessons/round-28.md:22
K2 uncorrected corpus/lessons/round-28.md:40
SUMMARY k1=6 k2=4 mismatches=10 rev=691dd29211c53d0ef94fa072394cb9c8a69fe92e
rc=1
```

```
$ python3 -B census/round-29/c2-counter.py --root . --rev 691dd29211c53d0ef94fa072394cb9c8a69fe92e
r26 records=1382 failed=152 uncovered=14 floor_violation=0
r27 records=124 failed=0 uncovered=0 floor_violation=0
r28 records=75 failed=0 uncovered=0 floor_violation=0
SUMMARY manifests=3 failed=152 uncovered=14 floor_violations=0 rev=691dd29211c53d0ef94fa072394cb9c8a69fe92e
rc=1
```

Both match the preregistration's stated base values (`k1=6 k2=4 mismatches=10`; `failed=152
uncovered=14`). The frozen counter's K2 rule is read at
`tools/souji-registry-agreement.py:150-158`: the phrase must still sit at `file:line` **and** the
file must carry, after that line, a line starting `R29-CORRECTION ` naming `file:line`.

### E2 — CONFIRMED DEFECT: the round-end SCORECARD edit breaks C1's K2 pin

`census/round-29/stale-statements.tsv` pins `SCORECARD.md:23` with the phrase
`2 malformed newline-path records`. The L1's own skeleton delivery
`.ufo/waves/round-29/w1/deliver-scorecard-log-skeleton.md:13` instructs:

> Insert directly above `### Round 28 measurements (2026-10-25; base 3a2a80d…)` at
> `SCORECARD.md:17`.

Line 17 is **above** line 23, so this insertion shifts the pinned statement. Measured on a scratch
clone of the prereg commit, three placement variants of the identical Round-29 table:

| placement of the Round-29 SCORECARD table | frozen v1 counter | v2 amendment (worktree) |
|---|---|---|
| insert above line 17 (as the skeleton says) | `K2 phrase-moved-or-edited SCORECARD.md:23` — `SUMMARY k1=0 k2=1 mismatches=1` rc 1 | `K2 rewrote-not-appended SCORECARD.md` + `K2 statement-moved-or-edited SCORECARD.md:23` — `mismatches=2` rc 1 |
| append at file end | `SUMMARY k1=0 k2=0 mismatches=0` rc 0 | `SUMMARY k1=0 k2=0 mismatches=0` rc 0 |
| insert after line 26 | `SUMMARY k1=0 k2=0 mismatches=0` rc 0 | (not separately re-run under v2) |

The pinned line moves from 23 to 32 under the insert-above-17 placement, confirmed directly:

```
$ git show <bad-commit>:SCORECARD.md | grep -n "2 malformed newline-path records"
32:| C3 evidence capture | operability 8 | dirty `.ufo/waves` `163`; r26/r27 manifests absent | …
303:R29-CORRECTION SCORECARD.md:23 the "2 malformed newline-path records" reading is superseded, not
```

Line 32 ≠ 23, so the phrase is no longer at the pinned line: `K2 phrase-moved-or-edited`. The
`R29-CORRECTION` marker at line 303 is present but cannot rescue the pin, because the counter
checks the phrase's *position* first and `continue`s.

This is a real counter failure, not a stylistic preference: the preregistration's C1 kill rule is
`mismatches>0` at the measured commit, and C3's own counter list requires that "the C1 counter at
the C3 landing commit still `mismatches=0`".

**Live lane state at the time of writing (22:40):** all four K2 pins are still intact — `sed -n
'23p' SCORECARD.md` still yields the `C3 evidence capture` row, `grep -n "2 malformed
newline-path records" SCORECARD.md` returns only line 23 and the correction marker at line 296,
and `sed -n '1758p' LOG.md` / `'22p'` / `'40p'` `corpus/lessons/round-28.md` still yield their
pinned lines. The C1 corrections have been appended at the **tail** of SCORECARD.md
(`### R29 append-only correction (round 29, C1)`), which is the safe placement. The Round-29
`SCORECARD.md` measurements table is **not yet written**. The defect therefore has not yet
materialised, and the L1's next SCORECARD.md write is where it can still be avoided: append the
Round-29 table at the file end, not above line 17.

**Safe fix: append the Round-29 SCORECARD table at the file end (or below line 23), never above
it.** Both LOG.md and `corpus/lessons/round-28.md` are unaffected because their pins are corrected
by tail-appends, which cannot shift a line above them.

### E3 — full ordered landing lands all three claims green

Applied in a scratch clone in the order **C1 → C2 → C3 → round-end edits (safe placement) →
r29 receipt** using the seats' own delivered files:

| step | counter | result |
|---|---|---|
| C1 (9 cell edits + 3 correction blocks) | `souji-registry-agreement.py` | `SUMMARY k1=0 k2=0 mismatches=0` rc 0 |
| C2 (new tool + r26 recapture) | `census/round-29/c2-counter.py` | `r26 records=1255 failed=0 uncovered=0 floor_violation=0` / `SUMMARY manifests=3 failed=0 uncovered=0 floor_violations=0` rc 0 |
| C3 (2 entries + S216-S219 + README row) | `souji-registry-agreement.py` at the C3 landing | `SUMMARY k1=0 k2=0 mismatches=0` rc 0 |
| C3 (same commit) | F3 entries / SOURCES rows / coverage | `2` / `143` / `grounded=15 mapped=15 dangling=0 mismatches=0` rc 0 |
| round-end edits, safe placement | `souji-registry-agreement.py` at the tip | `SUMMARY k1=0 k2=0 mismatches=0` rc 0 |
| r29 receipt captured | `census/round-29/c2-counter.py` at the final tip | `SUMMARY manifests=4 failed=0 uncovered=0 floor_violations=0` rc 0 |

Every frozen target in the preregistration is met exactly: `k1=0 k2=0 mismatches=0`,
`failed=0 uncovered=0 floor_violations=0`, `grounded F3 = 2`, `SOURCES rows 139 → 143`,
`grounded=15 mapped=15 dangling=0 mismatches=0`, and `manifests=4` at the tip.

### E4 — C3's rows were delivered twice with different cell text

`.ufo/waves/round-29/w1/deliver-sources-rows.md` and `.ufo/waves/round-29/w1/deliver-sources-append-block.md`
each deliver S216–S219, with **5 of 11 cells differing per row** (source/scope/anchor/teaches/
recheck). Example, S216 `source`:

- rows-delivery: `statx(2) — https://man7.org/linux/man-pages/man2/statx.2.html`
- append-block: `statx(2) — Linux man-pages 6.19 (2026-02-08) — https://man7.org/linux/man-pages/man2/statx.2.html`

Both parse as 13 fields / 11 cells, so the C1 counter cannot discriminate; the divergence is a
curation choice the L1 must make explicitly. The `used-by` cells agree between the two, so
whichever is chosen keeps K1 at 0.

### E5 — the r26 recapture rewrites 13 committed receipt files and renames 5

`git diff --name-status -M 691dd29211c5 <recapture> -- census/round-26/waves` in the scratch clone:
**28 added, 13 modified, 5 renamed, 0 deleted.** The renames are the nested rule files
(`…/vadv-49/.gitignore` → `…/vadv-49/.gitignore.captured`, and four siblings). The 13 modified are
`census/round-26/waves/manifest.sha256` plus 12 `census/round-26/waves/w1/*` copies. Committed r26
entries go 1245 → 1273; committed symlinks 14 → 17; manifest records 1382 → 1255 (floor 1230,
margin 25). The 11 `excluded.tsv` rows are 7 nested `.git` directories and 4 `__pycache__/*.pyc`
files — dropped, not silently (the tool refuses `.git` and accounts ignored names).

This is why the C1 correction blocks are rev-scoped: they state "measured at rev
691dd29211c53d0ef94fa072394cb9c8a69fe92e", which remains true after the recapture.

### E6 — C3's own entries and lesson would dangle pointers at the tip

The landing gate scans `corpus/knowledge/*.md` and `corpus/lessons/round-<N>.md` for path
pointers. Two C3 artifacts would each produce findings at `--round 29`:

1. The two admitted entries cite `census/round-29/sources/{statx.2.html,link.2.html,cmp.1.html,
   broder97resemblance.pdf,broder97resemblance.txt}`, which were only staged under
   `.ufo/waves/round-29/w1/sources/` (gitignored, never committed). Measured before committing
   them: **13 `LG-DANGLING-PTR` findings**. After committing the 6 snapshot files under
   `census/round-29/sources/`: `SUMMARY findings=0 checked_reg=52 checked_pins=13`.
2. The delivered lesson draft (`deliver-lesson-mistakes.md`) cites
   `.ufo/waves/round-29/w1/deliver-q60-q62-red-before.tsv` and `.ufo/waves/round-29/`.
   Measured with that draft landed as `corpus/lessons/round-29.md`: **3 `LG-DANGLING-PTR`
   findings** (`.ufo/waves/round-29/`, `.ufo/waves/round-29/w1/`,
   `.ufo/waves/round-29/w1/deliver-q60-q62-red-before.tsv`). The file does exist in the committed
   receipt at `census/round-29/waves/w1/deliver-q60-q62-red-before.tsv`.

Fix: commit the snapshots in the same commit as the entries, and cite
`census/round-29/waves/w1/<file>` in the lesson, never `.ufo/waves/round-29/w1/<file>`.

### E7 — pointer-gate scan scope is narrower than the whole lane

The gate's `check_pointers` (`tools/souji-landing-gate.py:918-940`) scans a fixed set: `SKILL.md`,
`SHONEN.md`, `SCORECARD.md`, `PROVINCE.md`, `corpus/QUALITY.md`, `corpus/README.md`,
`corpus/lessons/round-<N>.md`, `corpus/lessons/round-<N>-verifier-spotcheck.md`, and
`corpus/knowledge/*.md` at depth 2, plus the round-N H2 sections of `LOG.md`. A full sweep of
those 26 sources at base for `census/round-26/` pointers found only three, all still present after
the recapture: `census/round-26/c1-counter.sh`, `c2-counter.sh`, `c3-counter.sh` (cited from
`SCORECARD.md`). Nothing under `census/round-26/waves/` is cited by a scanned source.

`corpus/lessons/round-28-verifier-spotcheck.md:71` cites
`census/round-26/waves/assimilation/validate/tests/vault/vadv-49/.gitignore:fixture/` — a path C2
renames. It is **already** absent at base and already reported
(`LG-DANGLING-PTR … vadv-49/.gitignore:fixture/`, one of 3 findings at `--round 28`). C2 neither
creates nor clears it; it is pre-existing and outside the round-29 scan scope.

### E8 — the old r28 fixture survives the new tool

`tests/fixtures/r28-wave-evidence-capture.sh` drives `tools/souji-wave-evidence-capture.sh` by
path. With the new tool installed at that path in the scratch clone, the old fixture still
prints `cases=6 pass=6 control=TAMPER-REJECTED`, rc 0. `SKILL.md` cites neither fixture path, so
the gate's registry check (`LG-MISSING-REG`) is unaffected.

### E9 — a stricter v2 C1 counter is now in the lane worktree

`git status --porcelain=v1` in the lane shows ` M tools/souji-registry-agreement.py` plus
untracked `census/round-29/c2-counter-v2.py` and
`census/round-29/records/stray-r26-scribegatedraft.diff`. The worktree v2 counter adds a
byte-prefix requirement (`K2 rewrote-not-appended`), a uniqueness check on the pinned line, and a
requirement that the `R29-CORRECTION` line carry the derived `records=`/`failed=` integers and a
resolvable derivation source. I re-ran both placements under it: the safe placement gives
`SUMMARY k1=0 k2=0 mismatches=0` rc 0; the insert-above-17 placement gives
`K2 rewrote-not-appended SCORECARD.md` + `K2 statement-moved-or-edited SCORECARD.md:23`,
`mismatches=2` rc 1. **E2's finding is unchanged and strictly worse under v2.** The v2 tool is
an amendment, so it is the L1's to log; I did not modify or land it. The stray `.diff` file and the
modified counter are untracked/modified lane state that the pre-report gate's clean check
(`tools/souji-pre-report-gate.sh:34`) will report as `check-clean=FAIL` — the L1 must resolve both
before the report gate.

## Findings

1. **[counter-breaking, confirmed]** The round-end SCORECARD edit as specified in
   `deliver-scorecard-log-skeleton.md:13` (insert the Round-29 table above `SCORECARD.md:17`)
   shifts the K2-pinned statement at `SCORECARD.md:23` to line 32 and makes the frozen C1 counter
   report `K2 phrase-moved-or-edited` (`mismatches=1` under v1, `mismatches=2` under the v2
   amendment). Fix: append the Round-29 table at the file end or below line 23.
   Location: `SCORECARD.md:17` / `SCORECARD.md:23`; `census/round-29/stale-statements.tsv`;
   `.ufo/waves/round-29/w1/deliver-scorecard-log-skeleton.md:13`.

2. **[cross-claim, measured]** C2's r26 recapture rewrites 13 committed files under
   `census/round-26/waves/` (manifest + 12 `w1/*` copies) and renames 5 nested `.gitignore` to
   `.gitignore.captured`; committed entries 1245 → 1273, manifest records 1382 → 1255 (floor 1230,
   margin 25). The C1 correction blocks are correctly rev-scoped to the base rev and survive this;
   but if the recapture lands *before* the C1 corrections are written against base bytes, the
   corrections would describe a receipt that no longer exists at the tip. Land C1 before C2's
   recapture, or keep the corrections explicitly rev-pinned (as delivered).
   Location: `census/round-26/waves/`, `census/round-29/c2-counter.py` `FLOORS`.

3. **[cross-claim, measured]** C3's two admitted entries and its lesson draft would each introduce
   landing-gate pointer findings at `--round 29` unless the snapshots are committed with the
   entries (13 findings before, 0 after) and the lesson cites the committed receipt path
   `census/round-29/waves/w1/…` rather than the gitignored `.ufo/waves/round-29/w1/…` (3 findings).
   Location: `.ufo/waves/round-29/w1/deliver-duplicate-verdict-identity.md:58-62`,
   `…-byte-equality.md:94-104`, `…/deliver-lesson-mistakes.md:8,10`.

4. **[single-writer, measured]** `corpus/SOURCES.md` is written by both C1 (6 rows, cell edits at
   lines 43/45/46/96/97/160) and C3 (4 appended rows after line 160). C3's append point is below
   every row C1 edits, so C1's cited line numbers do not move — verified by comparing row text at
   base and after the append. C1 and C3 may land in either order on this file, but only if the
   append stays below line 160.
   Location: `corpus/SOURCES.md:43,45,46,96,97,160`.

5. **[single-writer, unresolved]** S216–S219 were delivered twice with different cell text
   (5 of 11 cells per row). Both variants are schema-valid, so the counter cannot choose. The L1
   must pick one; landing both is impossible (duplicate ids).
   Location: `.ufo/waves/round-29/w1/deliver-sources-rows.md` vs
   `.ufo/waves/round-29/w1/deliver-sources-append-block.md`.

6. **[pre-existing, not caused by C2]** `corpus/lessons/round-28-verifier-spotcheck.md:71` cites a
   `.gitignore` path that C2 renames, but the citation is already dangling at base and already
   reported at `--round 28`; it is outside the `--round 29` scan scope. Do not attribute it to C2.
   Location: `corpus/lessons/round-28-verifier-spotcheck.md:71`.

7. **[lane state, L1 action]** The lane worktree currently has a modified frozen counter
   (` M tools/souji-registry-agreement.py`), an untracked `census/round-29/c2-counter-v2.py`, and
   an untracked `census/round-29/records/stray-r26-scribegatedraft.diff`. The pre-report gate's
   clean check reports any of these as `check-clean=FAIL`. The v2 amendment must be logged
   (`census/round-29/records/amendments.txt` is referenced by the v2 docstring but does not yet
   exist) and the stray file resolved before the report gate.
   Location: `git status --porcelain=v1 --untracked-files=all` in
   `/home/vgpnk/Projects/shokunin/souji-shokunin`.

## Recommended landing order

**C1 → C2 → C3 → round-end edits → r29 receipt capture.** Each dependency, with its reason:

1. **C1 first.** Its K2 corrections are rev-scoped to the base rev; landing them before C2's
   recapture keeps the text they assert true at the tip (finding 2). It also fixes the K1 rows
   whose `used-by` cells C3's new entries depend on, and it must be measurable at 0 before C3's
   landing commit, because C3's own counter list requires "the C1 counter at the C3 landing commit
   still `mismatches=0`".
2. **C2 second.** The recapture must precede the final r29 capture so the tool that produces the
   r29 receipt is the committed one, and it must precede the r29 capture because the r29 receipt
   is produced by the improved tool.
3. **C3 third.** Its four rows and two entries must land in one commit (the `used-by` paths must
   exist at the same rev, or K1 reports them missing), and the six source snapshots must land in
   that same commit or an earlier one (finding 3).
4. **Round-end edits fourth, with the SCORECARD table appended at the file end.** This is the
   step that breaks C1 if done as the skeleton says (finding 1). The `R29-CORRECTION` blocks are
   themselves part of step 1's commit; the Round-29 SCORECARD table and LOG entry are appended
   after them.
5. **r29 receipt capture last.** It produces the fourth manifest, giving `manifests=4` at the tip,
   and it must come after all wave evidence exists.

## Attack log

No attack filed. I did not propose changing any counter, target, predicate or case set. The v2
counter amendment found in the lane worktree (finding 7) was tested but not authored, modified or
landed by me; I report its effect on the landing order as an observation.

## Deliveries

- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-29/w1/deliver-overlap-map.tsv` —
  11 overlap rows (O1–O11): the touched claims, the byte-level interaction, the measured effect,
  how it was verified, the required order, and the constraint. Includes the SCORECARD.md:23 pin
  collision (O1), the SOURCES.md single-writer geometry (O4), the duplicated S216–S219 rows (O5),
  and the two C3 pointer-dangle surfaces (O9, O10).

## Notes for the L1

- The one defect that will actually cost the round is finding 1: it is a one-line placement
  decision (append the Round-29 SCORECARD table at the end of the file, not above line 17), and
  it is invisible unless the C1 counter is run at the tip.
- Finding 3 is a one-line citation rewrite in the lesson (`.ufo/waves/round-29/w1/…` →
  `census/round-29/waves/w1/…`) plus committing the six snapshots with the two entries.
- Finding 5 needs an explicit pick between two delivered row texts; the `used-by` cells agree, so
  either keeps K1 at 0.
- Scratch `/var/tmp/souji-r29-SwarmConnector63.*` removed at seat end. No lane file was modified;
  the only lane writes are this report and the delivery TSV above. No tools were installed or
  upgraded.
