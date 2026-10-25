# W2C2Game — attack: how C2 reached 0

## Status
STATUS: PASS — the agreement is real, not gamed. C2 reaches 0 only through the new r24 F2 row (README:516), and that row affirms the capability. The `ground: F2` line is true and does not affect the count. Survives with three findings: one stale forward citation at the scored rev 778747e, one gameable counter class (not exploited here), and one wording nit.

## Evidence
Revisions: base a65fac98964b445758e94c805728c9a19d302ff8; after-state 778747eb671f8e85ef5387bc3d7023337b30467c; after-receipts ca7fc1cb6dd1333096c6f3bdbad304686691d126; `master` = c3ca7ad3f8722d5e92ba350e49b4ebb96e8bface. Scratch was `/var/tmp/souji-r24-W2C2Game/` and has been removed.

- `python3 -B tools/souji-coverage-agreement.py --root <lane> --rev <rev>`:
  - base a65fac9 gives `grounded=4 mapped=2 dangling=0 mismatches=2`. Both mismatches are `MISSING-FROM-MAP`, for `repo-size-census-readonly.md` and `count-objects-garbage-readings-r25.md`, with `map_rows_F2=3` (the three F2 rows are README :40, :68 and :217).
  - 778747e and ca7fc1c each give `grounded=6 mapped=6 dangling=0 mismatches=0`, exit 0.
- `souji-receipt-run.py verify` returns `verify=ok` for `c2-after`, `c2-control-base`, `c2-fixture-after`, `r13-recheck-receipt` and `c1-after`. `c1-after` stdout: `cases=8 pass=8 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED`.
- `python3 -B tests/fixtures/r24-coverage-agreement.py --tool tools/souji-coverage-agreement.py` (working tree at master) gives `cases=9 pass=9 control=FALSE-GREEN-REJECTED`, exit 0.
- Per-entry kill rule (amendment 1): all 4 entries grounded at base carry the same `F<k>` at tip (F2 ×2, F4 ×2). The tip adds `count-objects-linked-worktree-garbage.md` (F2, new file) and a `ground: F2` line on `git-repo-structure-readonly.md`. No entry was deleted or regrounded.
- Every backticked path in the F2 row's entries cell (README:516) exists at ca7fc1c: the four `knowledge/*.md` files, `tools/souji-size-census.py`, `tests/fixtures/r24-size-census.py` and `census/round-24/size-census-lane.txt`.
- The source IDs in that cell match each entry's `source:` lines: S035–S037, S115–S117, S118–S119, and S120–S123 for the new entry.
- Commit history (`git log --diff-filter=A`):
  - the three read-side entries landed at 6ed10a7 (r13) and 4765250 (r23), which matches "three entries, r13/r23";
  - `size-census-lane.txt` and `r13-recheck-receipt.tsv` were added in ca7fc1c and are absent at 778747e.

## Findings
1. **The ground line is true and does not change the count.** `corpus/knowledge/git-repo-structure-readonly.md:4` adds `ground: F2 — repository size census (structure census of refs-rooted reachable objects)`.
   - The same entry's body already said so at base, line 8: "Coverage-map ground: F2 repository size census. This entry closes the r12 deferred fixture prerequisite".
   - The entry has been mapped under F2 at README:68 since r13.
   - Scratch G3 (tip tree with only that line removed) gives `grounded=5 mapped=5 dangling=0 mismatches=0`. So the line raises `grounded` by one and leaves `mismatches` unchanged. It moves the count in the direction the kill rule protects.
   - Residual nit: the entry's front-matter `verified-at:` still reads "2026-10-20; host Git 2.55.0", while body line 49 records the 2.56.0 re-verification.
2. **The new F2 row does the work, and its status affirms the capability.** Scratch G4 (tip tree minus README:516) gives `mismatches=3` (readings-r25, linked-worktree-garbage, repo-size-census). The three entries are mapped by no other row, so 0 depends on README:516 alone.
   - Its status cell begins "frontier; read side (three entries, r13/r23) plus a write-safety debris census (r24 C1)". It disclaims nothing.
   - The status prose matches the tool at ca7fc1c:
     - `--git-dir=<common>` for `count-objects -v` (tools/souji-size-census.py:174);
     - `fsck --unreachable --no-reflogs --no-progress` (:190), with no `--lost-found`;
     - alternates counted from `alternate` lines (:202);
     - exit 2 for any argv other than `--repo PATH` (:125), for a non-repository (:136), and for partialClone / promisor config / `.promisor` packs (:155, :165, :170);
     - "8 frozen fixture cases" agrees with c1-after `cases=8 pass=8`;
     - "one lane-bound measurement, no fleet figure" agrees with `census/round-24/size-census-lane.txt` line 1 ("this repository only … not a fleet figure").
   - The routed-defect sentence (README:530-532, "which names every F2 entry in its entries column") is true at tip: 4 of 4 F2 entries are named.
3. **Superseded rows are marked, not left silent.** README:40 still reads "frontier, no entry (r12 candidate deferred", but:
   - README:64 has been headed "Round 13 current coverage (supersedes the r12 F2 row)" since r13;
   - README:506-507 states "For the entries column only, this table supersedes the F2 rows at :40 (r12 map) and :68 (Round 13); their status prose stays as history."
   - The line references :40, :42, :68, :205-211 and :233-234 all land on the cited rows at tip. :41 of `lessons/round-23-verifier-spotcheck.md` is the routed defect.
   - Neither :40 (entries cell `—`) nor :217 contributes any name to the mapping at tip.
4. **DEFECT (fixable, not a game): forward citation at the scored rev.** At 778747e, the rev that `c2-after` scored, README:516 names `../census/round-24/size-census-lane.txt`, which does not exist until ca7fc1c.
   - This breaks the row's own landing condition at README:509-511: "otherwise its cells name only the files present at that commit."
   - The C2 counter cannot see this, because `DANGLING-MAP-PATH` checks only spans ending in `knowledge/<name>`. `../` paths are unchecked.
   - The same applies to `git-repo-structure-readonly.md:49`, which at 778747e cites `census/round-24/records/r13-recheck-receipt.tsv` (added in ca7fc1c) and `.ufo/waves/round-24/w1/ReviewRepoStructureFixture.md` (committed only at c3ca7ad).
   - Everything resolves at the lane tip. Impacted axis: calibration (a claim committed before its evidence).
5. **Wording nit.** README:509-510 says the F2 row "lands only in the same commit as" the entry, the tool and the fixture. The tool and fixture were added in 1efe406, not 778747e; they were present, not co-committed. Read as "present at", it holds.

## Attack log
- **A1: map an entry through a row that disclaims the capability.** Scratch G1: base tree plus the two missing entries appended to the README:217 entries cell (`F2 caveat … — no F2 capability claimed`). Result: `grounded=4 mapped=4 dangling=0 mismatches=0`, exit 0. **The counter accepts this.** The C2 fixture pins this behaviour: its case 6 has `F2 caveat` count as F2 (tests/fixtures/r24-coverage-agreement.py:240-249). Not exploited at tip (G4 shows README:516 is the only carrier). Report as an ATTACK on the frozen counter, not a defect in the landed bytes.
- **A2: map entries through the "frontier, no entry" row.** Scratch G2: base tree with README:40's `—` replaced by the two entries. Result: `mismatches=0`, exit 0. **The counter accepts this.** It reads no status column, so "no entry" next to named entries goes unnoticed. Not exploited at tip.
- **A3: ground line as an inflation game.** Scratch G3 (shown in Finding 1): removing the line leaves `mismatches=0`. The line does not change the count. **Survives.**
- **A4: the F2 row's prose against the landed bytes.** Every claim was checked against tools/souji-size-census.py and the c1-after receipt (Finding 2). **Survives.**
- **A5: a superseded row left unmarked.** README:40 is marked by :64 and :506-507 (Finding 3). **Survives.**
- **A6: dangling `../` paths.** Fails at 778747e (Finding 4); survives at ca7fc1c.

Verdict: **real agreement** (README:516 maps all four F2 entries; `git-repo-structure-readonly.md:4` is true and does not change the count). Defects: Finding 4 (forward citation at 778747e) and the counter gaps A1 and A2.

Smallest safe corrections:
- **Finding 4:** disclose that the C2 after-receipt rev 778747e cites `size-census-lane.txt` before it existed. Do this in an appended correction, not by editing the scored row.
- **A1 and A2:** carry them as a named counter limit ("a row whose status cell disclaims the capability still maps"). A future round's counter could exclude rows whose status contains `no entry` or `not claimed`. That would be a new preregistered predicate, not an r24 edit.

Tools installed: none.
