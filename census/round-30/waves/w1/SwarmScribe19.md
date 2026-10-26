# SwarmScribe19 — r30 w1 records-skeleton scribe

## Status

STATUS: PASS — all five requested skeletons drafted at the named delivery path from committed bytes; no counter, fixture or product file was run or edited by this seat.

Scope note: this seat drafted text only. Every `<after>`, `<commit>` and `<...>` in the delivery is an L1 fill slot; nothing in it is a measurement of mine.

## Evidence

Lane working tree at `/home/vgpnk/Projects/shokunin/souji-shokunin`, HEAD `df6afe817d096e4ad71ba2b9cc21a83f126eb658`; lane base `9420341d9a814cb6089c25fb03a4cc9b23dc0d1b`; prereg `d4928ec86b667e3d1ed0adb07fb088e500cf1631`; controls `bae103cba91884947a0557940e60c320f5512f75`.

1. Frozen contract read first. `/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-30/records/preregistration.txt:5,7,9` (raw reads; lines 6, 8, 10 are blank). C1 instrument and correction grammar at :5 — quote: "K1 = rows whose command, run in a private clone at REV, neither prints the stated literal"; targets: C1 `SUMMARY k1=0 k2=0 mismatches=0 rows=18 pointers=10`, C2 `SUMMARY reports=86 cne=0 dangling=0 ... fixture=ok redarm=ok regress=same` with exit 0, C3 `SUMMARY legs=9 fail=0 f1_entries=3`. C2 fixture contract D1-D7 and "N >= 7" at :7 — quote: "D7 a capture-only report with an uncarried `STATUS: FAIL` line yields LG-SEAT-UNCARRIED". C3 entry, receipt names (`census/round-30/records/jj-keep-expiry-run.txt`, `tests/fixtures/r30-jj-keep-expiry.sh`) and F1 map-row obligation at :9.
2. Control values copied verbatim from `/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-30/records/controls.tsv`:

   ```
   C1-do-nothing(base)  c1  SUMMARY k1=13 k2=0 mismatches=13 rows=18 pointers=10 rev=9420341d9a814cb6089c25fb03a4cc9b23dc0d1b
   C2-do-nothing(base)  c2  SUMMARY reports=0 cne=1 dangling=3 other=0 fixture=fail redarm=fail regress=same rev=9420341d9a814cb6089c25fb03a4cc9b23dc0d1b
   C3-do-nothing(base)  c3  SUMMARY legs=9 fail=8 f1_entries=2 rev=9420341d9a814cb6089c25fb03a4cc9b23dc0d1b
   ```

   Junk rows: C1 `k1=2`, `k1=1`, `k1=1`; C2 reaches `reports=86 cne=0 dangling=0` with `redarm=fail regress=differs`; C3 `legs=9 fail=5 f1_entries=3`.
3. Layout anchors: `grep -n` over `/home/vgpnk/Projects/shokunin/souji-shokunin/SCORECARD.md` returned line 299 (`### Round 29 measurements (2026-10-25; base 691dd29211c53d0ef94fa072394cb9c8a69fe92e; preregistration b8cb4b31…`), 309 (`### Round 29 capability rows (appended, not inserted: …)`), 316 (`### Planned (appended at round 29)`). `wc -l` → SCORECARD.md 318, LOG.md 1784. Table header at 301, separator 302, C1-C3 rows 303-305, owned-scores paragraph 307; capability header 311, separator 312, rows 313-314; planned bullet 318.
4. `sed -n '1,6p' census/round-30/c1-rows.tsv` — exclusion rule names base lines 147, 151, 159, 163, 164, 165, 168, 170; first data row `R01 152 6/6 bash tests/fixtures/r12-maintenance-guard.sh --selftest`.
5. `c1-before.txt:29` — quote: `SUMMARY k1=13 k2=0 mismatches=13 rows=18 pointers=10 rev=9420341d9a814cb6089c25fb03a4cc9b23dc0d1b`; the frozen target lacks the trailing `rev=`.
6. Instrument provenance: `git ls-tree -r --name-only 9420341d9a814cb6089c25fb03a4cc9b23dc0d1b | grep -i capab` printed nothing; `git ls-tree -r --name-only HEAD | grep -i 'capab\|round-30/c1'` printed `census/round-30/c1-rows.tsv` and `tools/souji-capability-agreement.py`. Working tree clean apart from one untracked path (finding 7).
7. Census/axis start: `tail -3 census/round-30/records/census-start.txt` → last two lines are the `ok` corpus line and `rc=0`; `cat census/round-30/records/axis-check-before.txt` → `claims=3 flags=0`, `rc=0`.
8. House style: `/home/vgpnk/Projects/shokunin/.ufo/reports/round-29/souji.md` lines 35-80 (measurement table, Verdicts paragraph, `## Sources & frontier`, `## Trend verdicts`, `## SHONEN`, `## Round shape, seats, extras` with `- Stale-lane:` and `- Tool installs:` bullets); `Cross-domain evidence encountered` section precedent at `/home/vgpnk/Projects/shokunin/.ufo/reports/round-10/protocol.md:350`.
9. Wave inputs observed: `ls -la .ufo/waves/round-30/w1/` at 01:45 showed 25 files plus `sources/` (C1 correction receipts, `deliver-souji-landing-gate.py`/`.diff`, `deliver-r30-landing-gate-discovery.py`, `deliver-c2-fixture-red-before.txt`, `receipt-c2-fixture-arms.txt`, `deliver-r30-jj-keep-expiry.sh`, `deliver-jj-keep-expiry-run.txt`, `receipt-SwarmExecutor06-keepref-mechanism.txt`, `deliver-fetch-receipts.tsv`, six seat reports, `swarm-registry.json`).

## Findings

1. **Append anchors.** SCORECARD.md is 318 lines; the three r30 sections must append after 318 to keep K2/C1's append-only test satisfied. Round 29 measurement cells sit at 303-305 and the owned-scores paragraph at 307 — the skeleton mirrors that order. Location: `/home/vgpnk/Projects/shokunin/souji-shokunin/SCORECARD.md:299-318`.
2. **C1 target lacks the printed `rev=` suffix.** The counter's SUMMARY ends `pointers=10 rev=9420341…` (`census/round-30/records/c1-before.txt:29`) while the frozen target stops at `pointers=10` (`census/round-30/records/preregistration.txt:5`). The skeleton keeps the frozen literal and sends the suffix to `<disclosures>`, matching the r29 precedent; an L1 that "fixes" the target to include `rev=` would relax a frozen literal. Location: `census/round-30/records/preregistration.txt:5` vs `census/round-30/records/c1-before.txt:29`.
3. **C2 target is a partial literal by design.** `reports=86 cne=0 dangling=0 ... fixture=ok redarm=ok regress=same` places the ellipsis over `other=`, which the prereg calls "reported, not targeted" (`preregistration.txt:7`). The skeleton quotes the ellipsis and annotates `other=` as not-targeted so the after cell cannot be normalized to `other=0`. Location: `census/round-30/records/preregistration.txt:7`.
4. **C1 instrument is not in the base tree.** `tools/souji-capability-agreement.py` matches nothing in `git ls-tree -r --name-only 9420341…` and is present at HEAD. The C1 base row is therefore reproducible only with the r30 tool blob applied to a clone at base; no base-committed instrument exists. Not a defect — a provenance constraint for the base cell. Location: `tools/souji-capability-agreement.py` vs base `9420341d9a814cb6089c25fb03a4cc9b23dc0d1b`.
5. **Correction lines must keep base line numbers.** C1 enumerates base SCORECARD lines 147-175 and 313-314 (`census/round-30/c1-rows.tsv:1-6`), but r30 capability rows appended at the tip shift line 313-314 downward. Any `R30-CORRECTION SCORECARD.md:<line>` must name the base line, never a post-append line. Location: `/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-30/c1-rows.tsv:1-6`.
6. **SHONEN has exactly four boxes, all unchecked.** Boxes at lines 5, 7, 9, 11, each `[~]`; the report skeleton carries one line each and no promotion wording. Location: `/home/vgpnk/Projects/shokunin/souji-shokunin/SHONEN.md:5,7,9,11`.
7. **Untracked sibling artifact during this run.** `git -C /home/vgpnk/Projects/shokunin/souji-shokunin status --porcelain` printed only `?? corpus/lessons/round-30.md`; not created, read, or modified by this seat. Location: `/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/lessons/round-30.md`.
8. **Wave receipts pre-exist the skeleton.** 25 files plus `sources/` were already in the w1 directory; the delivery lists them as fill inputs and does not restate any count from them (no fixture line was re-run here). Location: `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-30/w1/`.
9. **No scratch tree.** No clone, work tree or fixture was created, so `/fast/scratch/hyaku/souji-r30/SwarmScribe19` does not exist (verified absent); nothing to `rm -rf`.

## Attack log

Not an attack seat; no attack log.

## Deliveries

- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-30/w1/deliver-records-skeleton.md` — sections (1) SCORECARD Round 30 measurements table, (2) Round 30 capability rows (C1, C2), (3) Planned r31 bullet, (4) LOG.md entry skeleton, (5) `/home/vgpnk/Projects/shokunin/.ufo/reports/round-30/souji.md` report skeleton; plus fill notes and the wave-input list.
