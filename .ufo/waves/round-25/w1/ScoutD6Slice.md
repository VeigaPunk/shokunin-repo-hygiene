# ScoutD6Slice — D6 (R24-M22) slice-verdict table reconciliation (round 25, wave 1, scout)

## Status
STATUS: PASS — the row-by-row mapping is produced and holds at tip: under the gate-table header map, gate and detail tables agree 8/8. S118 is `accepted` in the gate table literally. In the detail table it is `accepted` only through that header map: the detail row says `present-via-mirror` and carries no S118 note. Four stale "7 accepted, 1 unverifiable" mentions, all written in the re-grade commit itself, are undocumented. Documentation alone has already failed once (R24-M22 is a recurrence of R23-M4), so a gate is warranted (ATTACKS A1–A7).

## Evidence
Revisions: read at lane `6e4737eab43d8fde1b85eb9f57023d29046705b4`. The tip moved during the run to `1814de5` and then `de736c2…` (two prereg amendments). `git diff --stat 6e4737e de736c2 -- census/round-24 .ufo/waves/round-24/assimilation corpus/lessons SCORECARD.md LOG.md corpus/README.md corpus/QUALITY.md tools/souji-gate-check.py tools/souji-record-agreement.py census/round-22` is empty, so the findings hold at `de736c2`. shokuknow HEAD is `8b94c5c12c0521e4cd9ed8e5b6939afd8518c715`; it was only read with grep/sed.

Table history: both TSVs were added at `778747e`. Commit `315422b` (round-24 final) changed the gate S118 row from `unverifiable` to `accepted`, added the gate header's vocabulary line, and added the detail-table footnote. `git blame` attributes round-24.md:232, :240, :352–353, SCORECARD.md:181 and LOG.md:1692–1693 to that same `315422b`.

Cross-table check (scratch `/var/tmp/souji-r25-ScoutD6Slice/xmap.py`). It reads both TSVs and the r22 TSV via `git show <rev>:<path>`, applies the header map {present, present-via-mirror, present-quote-needs-fix} → accepted, and compares the result with the gate class.
- tip: `rows=8 disagree=0 r22_disagree=3` (S118, S126, S138)
- mutant gate table, every class set to `unverifiable`: `rows=8 disagree=8`. The check discriminates where `souji-gate-check.py` does not; W2Slice F5 showed that class swaps stay rc 0 there.

K3 retarget (scratch copy of `tools/souji-record-agreement.py`, sha256 `41db9ca8…`, constants changed: `K3_RECEIPT` = r24 gate TSV, `K3_RECORDS` = round-24.md, SCORECARD.md, LOG.md). Command: `python3 -B k3r24.py --root <lane> --rev 1814de5… --no-worktree`. Result: rc=1, `keys=4 records=3 occurrences=30 mismatches=26`.
- Real round-24-scope hits:
  - `corpus/lessons/round-24.md:240` 7 accepted / 1 unverifiable
  - `SCORECARD.md:181` 7 accepted / 1 unverifiable
  - `LOG.md:1692` 7 accepted / 1 unverifiable
- Noise:
  - 16 rows at `LOG.md:1508–1541`. These are the r22 section, which legitimately carries r22 tallies.
  - `round-24.md:165` "131 accepted". This is `S131 accepted` matched because `TALLY_RE` has no leading word boundary.
  - 2 `class-absent` rows.

Baseline: the committed `tools/souji-record-agreement.py --root <lane> --rev de736c2… --no-worktree` gives `keys=4 records=4 occurrences=17 mismatches=0`, rc=0. The missing word boundary is latent there; no README or round-22.md text triggers it.

Quotes (opened this run):
- `corpus/lessons/round-22.md:357-358`: "`accepted` = the quoted span is real and locates to a document, so the row is repairable by re-citing it"
- `corpus/lessons/round-22.md:359`: "`unverifiable` = the source cannot be read at all."
- `corpus/lessons/round-22.md:354`: "2 **present** (S126; S138), 1 **unverifiable** (S118 — DOI answers 202 with an"
- `census/round-24/records/slice-verdicts.tsv:1`: "gate classes accepted/unverifiable/refused/present follow census/round-22/attempt2/slice-verdicts.tsv; the detail table's present/present-via-mirror/present-quote-needs-fix all map to accepted"
- `census/round-24/records/slice-verdicts.tsv:4` (S118): "by round-22 definitions (unverifiable = source unreadable at all; accepted = span real, row fixable by re-citing) this is accepted with a re-cite"
- `.ufo/waves/round-24/assimilation/slice-verdicts.tsv:10`: "S123/S131/S133 register quotes match 0 times in their cited outputs"
- `corpus/lessons/round-24.md:240`: "Tally: 7 accepted, 1 unverifiable, 0 rejected"
- `SCORECARD.md:181`: "slice 7 accepted + 1 unverifiable (S118)"
- `LOG.md:1692`: "Quarantine slice 8 rows: 7 accepted, 1 unverifiable"
- `corpus/lessons/round-24.md:352`: "S118 re-graded `accepted` per round-22 definitions"
- `tools/souji-gate-check.py:48`: `CLASSES = {"present", "accepted", "unverifiable", "refused"}`
- `tools/souji-record-agreement.py:60`: `K3_RECEIPT = "census/round-22/attempt2/slice-verdicts.tsv"`
- shokuknow `.ufo/waves/corpus-expansion-1/absent-defect-register.md:14` (`unreachable` meaning): "the source could not be fetched, so the quote was never checked"
- same register, `:361` (souji S118, "NEVER CHECKED" table, reason column): "the cited source could not be fetched, so no quote was checked"
- `.ufo/waves/round-25/preregistration.txt:124-125`: "slice-verdict vocabulary mapping documented in the lesson (both tables, the class map, S118 re-classed accepted everywhere)"
- `.ufo/waves/round-25/preregistration.txt:146`: "the r24 quarantine-slice verdicts stand unchanged."

## Findings

1. **Row-by-row mapping at tip.** Ids are campaign register ids, keyed (souji, Sxxx), not lane registry ids. Sources: r22 = `census/round-22/attempt2/slice-verdicts.tsv`; register class = detail table column 2; detail verdict = detail column 3; gate = `census/round-24/records/slice-verdicts.tsv` column 2.

| id | r22 gate (frozen) | register class | r24 detail verdict | map → | r24 gate | evidence status |
|---|---|---|---|---|---|---|
| S114 | accepted | payload-absent | present | accepted | accepted | supports: span on git-scm git-prune; `[1]` vs `(1)` markup is a checker false positive with a stated correction |
| S118 | unverifiable | `unreachable` (the cell holds the register's reason prose, see F4) | present-via-mirror | accepted | accepted (re-graded at `315422b`) | supports accepted under r22 boundary: DOI → IEEE 202 with 0 bytes twice; Crossref-linked IEEE staging abstract and Princeton PDF line 11 carry the span (W2Slice evidence); re-cite needed; venue cell wrong |
| S123 | accepted | payload-absent | present (false of bytes: 0 quote matches) | accepted | accepted | class supported by r22 cell (span in git-worktree(1) SYNOPSIS); the r24 gate cell is digest-only (`510722c1`) and does not support a quote class |
| S124 | accepted | payload-absent | present-quote-needs-fix | accepted | accepted | supports: digests `1634d206`/`11df88f1` match; quote drops `NOREPLACE_new=0(ok)` |
| S126 | **present** | payload-absent | present | accepted | accepted | span verbatim (gtk File.trash; register quote is a 120-char prefix, still a substring): r22 `present`; r24 `accepted` is the collapse with no reason stated |
| S131 | accepted | payload-absent | present (false of bytes: 0 matches) | accepted | accepted | as S123 (span in git-worktree(1) OPTIONS; gate cell digest-only `1ac71c4f`) |
| S133 | accepted | payload-absent | present (false of bytes: 0 matches) | accepted | accepted | as S123 (span in rename(2) 91–92; gate cell digest-only) |
| S138 | **present** | payload-absent | present | accepted | accepted | span at qiita markdown line 17 (r22 says line 11; [INFERENCE] the 6-line front-matter offset) — r22 `present`; collapse as S126 |

Tallies: r22 5 accepted / 2 present / 1 unverifiable / 0 refused (frozen). r24 gate 8 accepted / 0 / 0 / 0.

2. **S118 confirmation.**
   - Gate table: literally `accepted` (`census/round-24/records/slice-verdicts.tsv:4`). The cell cites the r22 boundary and "r24 W2Slice re-grade from unverifiable".
   - Detail table: `present-via-mirror`, which maps to `accepted` only through the gate header (`:1`). The detail row has no gate-class column, and its footnote (`:10`) covers S123/S131/S133 only.
   - Under r22 definitions (`round-22.md:357-359`) `accepted` holds: the span is real in reachable documents, and the source is not "unreadable at all". This is also the flip round 22 itself named: "the flip is a re-cite to that copy" (r22 TSV S118 cell).
   - The r22 TSV still reads `unverifiable`. That is correct as round-22's measurement, and it must stay: `tools/souji-record-agreement.py` K2/K3 derive the r22 tallies from that file.

3. **Undocumented disagreement remains, (b).**
   - (i) Stale S118/tally mentions, all written in `315422b`, the commit that re-graded S118. None carries a `superseded by` note.
     - `corpus/lessons/round-24.md:232`: the S118 row's gate-verdict cell reads `unverifiable`. The wave-2 note says `accepted`, but the cell is not corrected.
     - `corpus/lessons/round-24.md:240` (tally)
     - `SCORECARD.md:181`
     - `LOG.md:1692–1693`
   - (ii) S126/S138 `present`→`accepted`. The header asserts the map but gives no reason. The same header also claims the gate vocabulary, which includes `present`, "follow[s]" r22, while r22 classes these two `present`. W2Slice F4 is unanswered.
   - (iii) The detail `register_class` cell for S118 holds the register's "why not checked" prose, not a class token. The register class is `unreachable` (register `:14`, `:361`).
   - (iv) The S138 locator says line 17 in the r24 gate and line 11 in r22. No table states what the line count starts from (W2Slice F6).

   Partially documented:
   - S123/S131/S133 detail `present` is false of the bytes. The footnote `:10` documents this, but the verdict cells are unchanged.
   - Their gate cells are digest-only; this is noted in round-24.md:233 only.

4. **Bare-id hazard in the mapping statement.** Campaign S118 is the Broder DOI. Lane `corpus/SOURCES.md` S118 is the Qiita koseki page, cited in the S138 gate cell. ConnSiblings F4 witnesses a cross-lane S114 collision (chousa, souji and tabi rows). The lesson's mapping must key rows as (souji, Sxxx) campaign ids.

5. **(a) Authoritative mapping statement for the lesson (proposed text):**
   > Round-24 quarantine-slice verdicts are keyed by campaign register (lane, id) = (souji, Sxxx), not lane registry ids. `census/round-24/records/slice-verdicts.tsv` is the gate record. `.ufo/waves/round-24/assimilation/slice-verdicts.tsv` is the scouts' detail reading, mapped present / present-via-mirror / present-quote-needs-fix → `accepted`.
   >
   > The r24 gate vocabulary collapses round 22's two pass classes into one. r22 `present` (span verbatim in the cited document) and r22 `accepted` (span real in a reachable document; row repairable by correction or re-cite) are both r24 `accepted`. `unverifiable` and `refused` keep their round-22 meaning. S126 and S138 are r22 `present` and r24 `accepted` by this collapse, not by re-grade.
   >
   > S118 is the only re-grade: r22 `unverifiable` → r24 `accepted`, the flip round 22 named (re-cite to the Crossref-registered IEEE record or the mirror). Its register class is `unreachable`.
   >
   > For S123, S131 and S133, detail `present` records digest presence, not the quote predicate (0 matches in the cited payloads). Their `accepted` rests on the wrong-source span in git-worktree(1) and rename(2).
   >
   > Tally: r24 8 accepted / 0 present / 0 unverifiable / 0 refused. `census/round-22/attempt2/slice-verdicts.tsv` stays 5/2/1/0 as round 22's measurement. The "7 accepted, 1 unverifiable" at round-24.md:232/240, SCORECARD.md:181 and LOG.md:1692 is superseded by 8 accepted (R24-M22).

## Attack log
- **A1. Is documentation enough? No, on the record.**
  - R24-M22 is itself a recurrence of R23-M4, the single-site sweep (`round-24.md:170`).
  - The fix commit `315422b` claimed "the vocabulary mapping recorded" (`round-24.md:353`) and, in the same commit, wrote four mentions that contradict the re-grade (F3 i).
  - A lesson paragraph adds a fifth site to sweep and nothing that fails when a site is missed. **Gate needed.**
- **A2. Cheap discriminating gate exists.**
  - The cross-table map check (Evidence) gives 0/8 disagree at tip and 8/8 on a class-swap mutant.
  - Q57 should bind a counter: gate ⋈ detail on (lane, id) through a declared map → `disagree=0`, plus a red mutant.
  - Today `souji-gate-check.py` tests membership only (`:48`).
- **A3. A naive K3 retarget is not a usable gate.**
  - It flags the 3 real records but adds 21 noise rows.
  - Fixing that needs (i) section scoping (Round 24 sections only, K2-style, so append-only LOG/SCORECARD pass once a later `superseded by` line names the old tally), (ii) a `\b` before the count (`S131 accepted` → "131 accepted"), and (iii) `class-absent` relaxed to the classes the receipt actually uses.
  - The missing `\b` is latent in the committed K3 too; it is unexercised at tip.
- **A4. The map is degenerate.**
  - All three detail values map to `accepted`, and the detail vocabulary cannot express `unverifiable` or `refused`. So "agreement under the map" only catches gate-side flips.
  - A wrong detail reading still maps green: S123/S131/S133 `present` is false of the bytes.
  - To make detail-side error falsifiable, a gate needs a per-row quote-predicate datum: span in the cited payload yes/no, plus where the span is if no.
- **A5. "S118 re-classed accepted everywhere" (prereg :124-125) cannot be literal.**
  - The r22 TSV must stay `unverifiable` (it is round-22's measurement and the source of the r23 K2/K3 tallies).
  - LOG/SCORECARD are append-only, so they need appended `superseded by` notes, not edits.
  - The lesson should scope "everywhere" to round-24 records, with the r22 TSV frozen. This is a wording-scope ATTACK, not a predicate change.
- **A6. The gate header contradicts itself.** It names `present` as a gate class that "follow[s]" r22, yet maps detail `present`→`accepted`, which is exactly the S126/S138 drift. The prereg freezes the verdicts as unchanged (`:146`), so the collapse must be declared explicitly (F5 text). The alternative, re-classing S126/S138 to `present`, would change the frozen verdicts.
- **A7. Join-key scope (ConnSiblings F4 corroborated).** Any Q57 or D6 counter that joins by bare id across the r22, r24 or sibling tables admits a foreign row. The key must be (lane, id).

Scratch `/var/tmp/souji-r25-ScoutD6Slice/` (xmap.py, k3r24.py, gate-mut.tsv, k3.out, base.out) is removed after this report. No lane file other than this report was written. No git or jj mutation. No shokuknow writes. No tools installed.
