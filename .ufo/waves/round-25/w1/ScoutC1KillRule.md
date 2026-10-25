# ScoutC1KillRule — round 25 wave 1, C1 kill-rule recon

Seat: L1Souji25.ScoutC1KillRule-2 (scout, read-only). Lane HEAD 6e4737eab43d8fde1b85eb9f57023d29046705b4; base a6d2d157755ef36b1dd4b9d53ad6d5b2ad6a3afe. git 2.56.0, Python 3.14.8.
Scratch `/var/tmp/souji-r25-ScoutC1KillRule-2/` (own name, avoids sibling `ScoutC1KillRule` collision) — created, used, removed. No installs. No lane edits other than this report.

## Status
STATUS: PARTIAL — integration points and feasibility are fully mapped, and a prototype passes the r24 fixture 9/9. **A1:** the frozen real-run target `kill_tested=4` cannot be reached by a tool that follows the frozen spec, which yields 6 at base a6d2d15. An F2-only mutant that narrows scope hits 4 exactly and passes all frozen k1–k4 cases. The frozen target therefore rewards an under-scoped tool. The L1 must decide.

## Evidence
1. `git -C <lane> ls-tree a6d2d15 -- corpus/knowledge/` + per-entry front-matter grep (before the first `# ` line): six grounded entries at base — F2: `count-objects-garbage-readings-r25.md`, `count-objects-linked-worktree-garbage.md`, `git-repo-structure-readonly.md`, `repo-size-census-readonly.md`; F4: `quarantine-origin-record-fields-r24.md`, `quarantine-staging-no-copy-r23.md`. All 14 children are mode 100644.
2. Committed receipt `census/round-25/records/coverage-agreement-at-base.tsv` (in 6e4737e) stdout: `grounded=6 mapped=6 dangling=0 mismatches=0`, rc=0.
3. Scratch prototype (committed tool bytes plus a `--base-rev` arm; kill keys printed only when `--base-rev` is given), run read-only against the lane:
   `proto.py --root <lane> --rev 6e4737e… --base-rev a6d2d15…` → `grounded=6 mapped=6 dangling=0 mismatches=0 kill_tested=6 kill_violations=0` rc=0.
   Same command with mutant `f2-only` (checks only F2 grounds) → `… kill_tested=4 kill_violations=0` rc=0.
4. Committed r24 fixture `tests/fixtures/r24-coverage-agreement.py` (HEAD blob copy) `--tool proto.py` → `cases=9 pass=9 control=FALSE-GREEN-REJECTED` rc=0. The r24 counter is not harmed when the kill keys are conditional.
5. Scratch k-case harness (synthetic repos with one base-grounded `e.md` each; every case runs `--rev tip --base-rev base`). Pass counts over 8 cases (frozen k1–k4 plus scout extras k1b, k5, k6, k7):

| tool / mutant | k1 | k2 | k3 | k4 | k5 multi-partial | k6 extra-ground | k7 symlink | total |
|---|---|---|---|---|---|---|---|---|
| faithful prototype | pass | pass | pass | pass | pass | pass | rc 0 (spec-ambiguous) | 7/8 |
| `ignore` (accepts --base-rev, never checks) | FAIL | FAIL | pass | pass | FAIL | pass | FAIL | 3/8 |
| `exists-only` | pass | FAIL | pass | pass | FAIL | pass | FAIL | 5/8 |
| `any-retained` (one base F kept suffices) | pass | pass | pass | pass | FAIL | pass | FAIL | 6/8 |
| `f2-only` | pass | pass | pass | pass | FAIL | pass | FAIL | 6/8 |
| `exact` (tip set must equal base set) | pass | rows V=2 | pass | pass | pass | FAIL | FAIL | 5/8 |
| OLD tool a6d2d15 | rc 2 | rc 2 | rc 2 | rc 2 | rc 2 | rc 2 | rc 2 | 0/8 |

   Bad `--base-rev` (`<12-hex>`, `HEAD`, 39-hex+`z`) → rc 2 in the prototype. With base and rev swapped (k2 repo), the prototype reports rc=1 and `kill_violations=1`: there is no ancestry requirement.
6. Lane tool sha256 `71b89eb3…8f28897` equals `tool_sha256` in `census/round-25/records/c1-control-base.tsv`. That receipt records rc=2 with `refused: argv: unrecognized arguments: --base-rev …`.

## Findings
**(a) Integration points** (committed `tools/souji-coverage-agreement.py` @ 6e4737e):
1. `main()` :140–157. Add `--base-rev` next to `--rev` (:143). Validate it the same way as `--rev` (:146–148: `FULL_REV.fullmatch` + `rev-parse --verify --quiet <rev>^{commit}`) **inside** the `try` (:145–152), so any base-side git failure is a `Refused` that exits 2 and never becomes a false rc 0/1.
2. The base read and the kill check belong after `measure()` (:149), still inside the `try`. Reuse the tip data from `measure()` rather than re-reading the tip. :120 already reads every tip `.md` blob: `ks = front_grounds(show(root, rev, f"{KNOWLEDGE}/{name}"))`. Exposing name→ks plus the `tree` from :97 avoids a second `git show` per entry. ExecC1's draft does this (`kill_rule(root, base_rev, tree, grounds)`, draft :113).
3. Counts: `counts` (:130–131) is an insertion-ordered dict printed at :155. Append `kill_tested`/`kill_violations` **after** `mismatches`, and **only when `--base-rev` is given**. Two consumers pin this:
   - The r24 fixture's `COUNTS` (fixture :53, `^grounded=(\d+) mapped=(\d+) dangling=(\d+) mismatches=(\d+)$`) is end-anchored. Always-printed keys would turn every r24 case into `counts_lines=0`. [INFERENCE from regex; the conditional variant measured 9/9, Evidence 4.]
   - `tools/souji-receipt-run.py` `COUNTS_RE` (:67–77) matches a prefix and is followed by a whitespace-or-end lookahead. Keys appended after `mismatches=` still match; keys inserted before `mismatches=` would break `run`/`verify` with `RECEIPT-COUNTS-ABSENT`. Its docstring (:95): "The last stdout line that STARTS with a counts line (anchored; stderr and prose never count)."
4. `mismatches` must stay map-only (DANGLING + MISSING). KILL-RULE rows count only in `kill_violations`. The frozen exit predicate names both keys separately (prereg :36–37). Rows: merge KILL-RULE into the sorted `MISMATCH` output (:153–154). Exit (:156) becomes `mismatches==0 and kill_violations==0`.
5. Fixture integration (`r24-coverage-agreement.py`):
   - `CLASSES` :52 / `COUNTS` :53 need a KILL-RULE class and a kill-suffixed counts form for k-cases only.
   - `score()` :307–324: the `len(rows) == mismatches` check becomes `== mismatches + kill_violations` for k-cases.
   - `run_tool()` :280–288 needs an optional `--base-rev`.
   - `build()` :109–123 returns all shas, so the base is `shas[0]`.
   - `CONTROL_SRC` :54–58 prints no kill keys.

**(b) Feasibility:** yes, with no new helpers. `knowledge_tree(root, base)` (:51–57), `show(root, base, path)` (:47–48) and `front_grounds()` (:85–93) apply unchanged to the base. Use the same `.md` + `blob` filter as :118 so base and tip agree on what counts as an entry. Read only `corpus/knowledge` at the base, never `corpus/README.md`, because the spec reads the knowledge tree only. Faithful prototype: 7/8 scout cases, lane real run rc 0.

**(c) Hazards:**
1. Abbreviated revs: `--base-rev` needs the same full-40 + `^{commit}` refusal as `--rev`. The frozen case set has **no bad-`--base-rev` case**, so this refusal surface is uncovered by the counter. A full-40 annotated-tag object id passes `^{commit}`, and `ls-tree`/`show` peel it. [INFERENCE from git semantics; not executed.]
2. Merge commits / non-ancestor base: the check reads two trees and never walks history. A merge base, or a base that is not an ancestor, works (reversed-order run measured, Evidence 5). No `merge-base` is needed. The spec does not require ancestry, so the tool must not add that requirement.
3. Entries added between base and tip (C3's `git-repo-structure-common-dir.md`, ground F2) are not base-grounded. They raise `grounded` (6→7) and leave `kill_tested` unchanged. An entry renamed between base and tip (`git mv`) counts as a deletion (KILL-RULE). Entries that are ungrounded at base and grounded at tip are ignored.
4. Multiple F<k>: emit one row per (entry, lost F) to mirror MISSING-FROM-MAP's per-k rows (:126–128). The prereg does not freeze whether `kill_violations` counts rows or entries. For the k-cases (one F lost, or a deletion of a single-F entry) both readings give 1. Deleting a two-F entry gives V=2 under rows and 1 under entries; no frozen case pins this.
5. Symlinks: `ls-tree` reports mode 120000 as type `blob`. The spec says "still exist as a blob", so a symlink at tip whose target text parses as `ground: F2` passes (k7, rc 0). The committed `measure()` already treats symlinks as entries, so this is consistent but unstated. Not a fixture case.
6. Heading cut-off: `front_grounds` stops at the first line starting `# `. A tip edit that moves the ground line below the title heading reads as a re-grounding/removal (a KILL-RULE row). This is correct per the spec, but no case covers it.
7. Fixture repo shape: `base_files()` (fixture :155–160) carries two grounded entries (`a-f2.md` F2, `b-f3.md` F3). k-case repos built from it would give `kill_tested=3`, against the frozen k3 `kill_tested=1`. The ExecC1 draft avoids this: "Each kill repo has exactly one base-grounded entry `e.md`" (draft r25 fixture :37–38).
8. k1 tip map state is unfrozen. If the map still lists the deleted E, DANGLING-MAP-PATH also fires (k1b: `dangling=1 mismatches=1 kill_violations=1`). The fixture must pin which form it builds.

**(d) Attacks** — see the Attack log.

## Attack log
- **A1 (HIGH — frozen target inconsistent with frozen spec; rewards an under-scoped tool).**
  - What the prereg says: :33 "collects every entry carrying a front-matter `ground: F<k>` line there". :53 "prints grounded=G mapped=M dangling=0 mismatches=0 kill_tested=4 kill_violations=0, rc 0". :139–140 "kill_tested stays 4 because C3's entry is not base-grounded".
  - What the base holds: six base-grounded entries (4×F2 + 2×F4, Evidence 1–2). A faithful tool prints `kill_tested=6`. ExecC1's draft defines N as "entries grounded at base" (draft :13–14), so it prints 6. Only `f2-only` prints 4, and it also passes every frozen k1–k4 case (Evidence 3, 5).
  - Consequences: if the after-target is read literally, a correct tool fails C1. Alternatively the executor narrows the scope to fit, which is gaming the counter.
  - [INFERENCE] The author appears to have counted only F2 entries (there are exactly 4).
  - This needs an L1 decision recorded as a prereg defect, not as a post-data edit.
- **A2 (MEDIUM — k1–k4 do not separate the spec from `any-retained` or `f2-only`).** Both mutants pass all four frozen kill cases. Only a multi-F partial-removal case catches them: base F2+F3 → tip F2 only → KILL-RULE rc 1 (scout k5). The spec explicitly makes this a violation (:35 "removal or re-grounding to another F is a violation"), but no frozen case tests it.
- **A3 (MEDIUM — the `exact` mutant survives if V is not pinned).** A tool that forbids extra ground lines passes k1/k3/k4. On k2 it emits 2 rows (lost F2 + extra F1), so it is caught only if the fixture asserts `kill_violations == 1` or the row multiset. Frozen k2 says only "KILL-RULE, rc 1". The spec's "extra ground lines are allowed" clause has no frozen case (scout k6: base F2 → tip F2+F3, mapped → rc 0).
- **A4 (MEDIUM — the do-nothing control is not adequate for the kill rule).**
  - k0 is frozen as "an always-zero emitter must fail >=1 case". The always-zero emitter already fails r24 cases 2–7 and 9, so k0's verdict says nothing about k1–k4.
  - The red arm (the OLD tool fails k1–k4) discriminates only on argparse: rc 2 on an unknown flag (Evidence 5, OLD row; receipt c1-control-base.tsv).
  - The informative control is an accept-and-ignore emitter (parses `--base-rev`, prints `kill_tested=N kill_violations=0`). It fails k1/k2 (Evidence 5, `ignore` row), but no frozen control requires that.
  - The ExecC1 draft's `CONTROL_SRC` appends kill keys under `--base-rev` (draft :68–69). That is a step toward this control, but it still prints `kill_tested=0`, so it fails k3 on the count, not on the violation logic.
- **A5 (LOW — C is not pinned).** The after-target says `cases=C pass=C` with no number (r24's 9 + k1–k4 = 13). Only the kill-rule sentence ("no case is dropped") prevents shrinkage. Pinning `cases=13` would make dropping a case visible from the counter alone.
- **A6 (LOW–MEDIUM — separability from C3 and D4 is one-way).**
  - C1's frozen kill rule is "mismatches>0 at tip -> C1 not verified". If C3 lands `git-repo-structure-common-dir.md` (ground F2) without a matching entries-cell span in some F2 row, C1 fails on MISSING-FROM-MAP. A C3 defect kills C1, even though prereg :134–137 says each counter runs without the others' files.
  - D4 appends to the README :40 F2 status cell, which already contains escaped `\|` (base README :40). An unescaped `|` in the marker would shift the cells: entries `—` becomes status text, and the following text becomes the entries cell. Any `knowledge/` span there would then count as mapped or dangling. [INFERENCE from `cells()` :60–64 / `CELL_SPLIT` :28.]
  - `kill_tested` itself is insensitive to C3/D4, because the base is fixed.
- **A7 (LOW — the bad-`--base-rev` refusal is unpinned).** There is no fixture case analogous to r24 case 9 for `--base-rev`. A tool that silently treats a bad base as an empty tree would print `kill_tested=0` with rc 0 on the real run and pass every frozen case except the real-run `kill_tested` target.

## Remaining unknowns
- Whether `kill_tested` counts entries or (entry, F) pairs. At a6d2d15 both readings give 6, so A1 holds under either.
- The ExecC1 r25 fixture draft was mid-write when grepped (k-case `Case(...)` lines absent at :225–285). It was not scored against these mutants.
- Tooling note: the Read tool refused the 15459-byte `r24-coverage-agreement.py` with "exceeds maximum allowed characters (100000 characters)". The file was read from its committed blob via `git show` instead.
