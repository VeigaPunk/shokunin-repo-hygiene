# RevAssimRules — C2 §10 assimilation review (round 26, w1)

## Status
STATUS: FAIL — C2's frozen K2 gate is RED at the committed tip: `entries=2 ok=0 fail=2`, exit 1.
The admitted entries as committed (0833de9) carry no `## Gate` section; the gate passes only on
uncommitted worktree bytes. Required receipts `c2-gate.tsv` and `c2-k4-after.tsv` are absent from
`census/round-26/records/`. All other §10 rules are satisfied by evidence below.

## Evidence
- Append commit `0833de9` (2026-10-25 14:27:56) added registry rows S128–S132 and the two entries;
  committed entries contain no `## Gate` (headings end at `## Freshness`: entry A :62, entry B :89).
- K2 run at committed tip (exact prereg command, `python3 -B`, read-only):
  `FAIL corpus/knowledge/git-auto-maintenance-trigger-set.md check1-no-gate: corpus/knowledge/git-auto-maintenance-trigger-set.md`
  `FAIL corpus/knowledge/git-auto-maintenance-trigger-set-r23.md check1-no-gate: …`
  `entries=2 ok=0 slice_verdicts=0 slice_total=0 fail=2` → `GATE_RC=1`.
- Same K2 run against the working tree (Gate sections appended, uncommitted, `git status` shows
  `M corpus/knowledge/git-auto-maintenance-trigger-set{,-r23}.md`): `entries=2 ok=2 slice_verdicts=0 slice_total=0 fail=0` → `GATE_RC=0`.
- K4 at tip `ba8b54b`: `grounded=9 mapped=9 dangling=0 mismatches=0 kill_tested=7 kill_violations=0`, rc=0 (matches the amendment-1 after-literal exactly).
- `find . -name 'c2-gate*' -o -name 'c2-k4-after*'` → none (only c1/c2-before/c2-after/c3 receipts in `census/round-26/records/`).
- Mirror gate: `/var/tmp/souji-r26-mirror/validate.out` (mtime 14:22) ends `file ok /var/tmp/souji-r26-mirror/corpus/SOURCES.md` plus W04 duplicate-url warnings only; append commit 0833de9 at 14:27:56, so validate predates the first real append. Prereg-named path `.ufo/waves/round-26/assimilation/validate/` does not exist.
- Rows 149–153 (`corpus/SOURCES.md`): NF=13 (11 cells), no literal/escaped `|` in any cell, `opened`=2026-10-25, `recheck` cadence only (`on-release`/`90d`), `status`=mined, `used-by` = admitted entries only.
- Citation cross-check: entries cite S128×2, S129×2, S130×2, S131×1, S132×1; landed rows cited identically; every cited row is appended (mirror-build E-check also enforces).
- Own-work re-grounding: entry B `verified-at` logs fixture sha256 11c136aa…, evidence 510722c1…, census 1ac71c4f…; campaign files exist (`ls` in renumber-map §4) with matching prefixes; lane did not re-execute the fixture (disclosed).
- Rule 10: `SOURCES.append.md`/`MERGE-REPORT.md` mtimes are 2026-10-24 23:33 (untouched); no file under `/home/vgpnk/Projects/shokuknow/merge/souji/` newer than 2026-10-25 08:00.

## Findings
1. **[BLOCKER] K2 kill rule red at committed tip** — `tools/souji-gate-check.py:74` (`check1-no-gate`) fails both entries at HEAD; the fix (`## Gate` sections, w/drafts) exists only as uncommitted worktree bytes. Commit the Gate sections and re-run K2; the green receipt must be committed from the landed bytes.
2. **[HIGH] Missing frozen receipts** — `census/round-26/records/c2-gate.tsv` (K2) and `c2-k4-after.tsv` (K4) are required by the prereg receipt list; neither exists. K4 itself runs clean at tip, so only the receipt file is missing; commit d6c13b0's message claims "real gate rc=0" but no gate receipt was committed with it.
3. **[MEDIUM] Scratch-mirror gate path deviation** — the gate ran (exit 0, warnings allowed) at `/var/tmp/souji-r26-mirror` (14:22) before the append (14:27:56), satisfying the timing predicate, but the prereg-named mirror path `.ufo/waves/round-26/assimilation/validate/` is absent, so the gate evidence is not committed in-lane (mirror also lacks the `.souji-mirror-build` marker; trust rests on /var/tmp bytes).
4. **[LOW] `c2-after.tsv` rev predates the landing tip** — receipt says `rev=e0f8dcd` (parent of the receipts commit), not the tip at which the counter ran. `registry_rows=132`, `grounded_f1=2` are stable at later tips, so value-wise fine; label provenance is off.
5. **[ADJACENT, outside C2] stale lesson text** — `corpus/lessons/round-26.md` describes a "11-case" C3 fixture; the adopted/wave fixture is 12-case (commit c594901). Text written at ea0bbe6 before the adoption; update in the lesson or leave as historical (C3's concern).

## §10 rule map (artifacts)
| Rule | Satisfied by | Status |
|---|---|---|
| 1 one theme, 1–3 entries | entry-git-auto-maintenance-trigger-set{,-r23}.md — F1 trigger-set theme, round1+round2 staged packages, 2 entries | OK |
| 2 PROVINCE scope F1 | PROVINCE.md:63-65 F1 def; both entries `ground: F1` (K1=2 at tip) | OK |
| 3 QUALITY bar per entry | souji-gate-check.py checks 1–6 (Gate, URL+opened, ≤25-word located quotes, verbatim-in-snapshot, source-id resolution, ADMIT/REJECT) — passes only on uncommitted bytes | OPEN (finding 1) |
| 4 expansion credit ground | README.md:39 F1 row lists both new entries; :46 next-step names them + S128–S132; K4 grounded=9 mapped=9 | OK |
| 5 renumber BY DOCUMENT | renember-map.md §2b/2d URL/path greps vs base+HEAD; mapping matches frozen prereg literal; 0 within-scope duplicates (E04 silent for own-work — manual path check done) | OK |
| 6 scratch mirror + census --file before append | /var/tmp/souji-r26-mirror validate.out exit 0 at 14:22 < append 14:27:56 | OK functionally; finding 3 (path/evidence) |
| 7 rows normalized | rows 149–153: 11 cells, no pipes, recheck cadence, opened 2026-10-25, used-by=admitted entries | OK |
| 8 Gate ≥1 admit + ≥1 reject | lesson Gate (round-26.md ## Gate) + both entry Gates | OK (once committed) |
| 9 own-work rows re-grounded | entry B verified-at sha256 + campaign file existence | OK |
| 10 nothing written into shokuknow | mtimes unchanged; no merge/souji writes today | OK |

## Residual risk
- Landing only the worktree Gate bytes and the two receipts turns K2 green under exactly the tested bytes; a future edit diverging from those bytes would need a fresh gate run (receipt binds bytes, not just structure).
- Mirror-gate evidence is uncommitted; without a committed validate output the pre-append gate rests on /var/tmp bytes (sibling attack A1/A2 in ExecScratchMirror.md apply).
