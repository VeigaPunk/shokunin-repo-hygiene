# W2Slice — attack on the round-24 quarantine-slice verdicts (wave 2, FALSIFY)

## Status
STATUS: PARTIAL — the slice partly survives. Where the 8 gate classes are checked against round 22's class definitions, 6 hold. But:
- S118 `unverifiable` contradicts its own evidence cell, its scout's `present` and those definitions.
- S126 and S138 changed class (`present` → `accepted`) with no recorded reason.
- The detail table disagrees with the gate table on 7 of 8 rows.
- 3 gate evidence cells (S123, S131, S133) do not support a quote-class verdict.
- The gate cannot tell one class from another, so none of this shows up in its counts line.

## Evidence
Revisions: lane `master` = `c3ca7ad3f8722d5e92ba350e49b4ebb96e8bface`, which is the wave-1 reports commit on top of the after-receipts commit `ca7fc1c`. Both verdict files were added at `778747e`. `git cat-file -p 778747e:census/round-24/records/slice-verdicts.tsv | diff -` against the tip file is empty, so the file is unchanged at tip. shokuknow HEAD is `8b94c5c1…`, read-only, and `git status --porcelain lanes/souji/round{2,3}` is empty.

Tools: curl 8.23.0, pdftotext 26.08.0, git 2.56.0, run at 2026-10-25T09:40:44Z. Scratch was `/var/tmp/souji-r24-W2Slice/` and has been removed. No tools were installed.

Re-fetched web row: S118 (plus S138's locator).
- `curl -L https://doi.org/10.1109/SEQUEN.1997.666900`, run twice. Both times: `302` → `301` → `HTTP/2 202`, `content-length: 0`, `x-amzn-waf-action: challenge`, body sha256 `e3b0c442…` (empty).
- `api.crossref.org/works/10.1109/SEQUEN.1997.666900` → 200.
  - container: `Proceedings. Compression and Complexity of SEQUENCES 1997 (Cat. No.97TB100171)`
  - page: `21-29`
  - author: Broder
  - link: `http://xplorestaging.ieee.org/ielx4/5423/14659/00666900.pdf?arnumber=666900`
- That Crossref link → 200, 45196 B (sha256 `ea229c16…`). Its JSON `"abstract"` (646 chars) contains: `the informal notions of \"roughly the same\" and \"roughly contained.\"`
- The Princeton PDF mirror → 200, 254930 B (sha256 `da122799…`).
  - line 11: "the informal notions of “roughly the same” and “roughly contained.”"
  - line 71: "2    Definitions as set intersection problems"
- `qiita.com/koseki/items/f1af58f1ec1693f0536a.md` → 200, 4047 B (sha256 `4d1991a3…`). `grep -n` gives `17:## gc.auto (6700)`. Lines 1–6 are YAML front matter (`---` … `---`).

Re-checked own-work row: S133 (plus quote-in-payload counts for S123 and S131, and S124's lane copy).
- `sha256sum` matches the named prefixes:
  - `lanes/souji/round3/evidence/r24-renameat2-probe.out` = `a53f1e30…`
  - the probe `.py` = `a4506492…`
  - also matching: `510722c1…` (S123), `1ac71c4f…` (S131), `1634d206…` (S124)
- The `.out` has 8 mount lines, and `awk '{print $1}' | sort | uniq -c` shows 7 distinct paths, because `/fast` appears twice (btrfs and xfs). Line 11 is `SUMMARY: every writable mount implements RENAME_NOREPLACE`.
- `grep -c -F` of each register quote against its cited payload returns `0` in all three cases:
  - S133: `RENAME_NOREPLACE Don't overwrite newpath of the rename.` in r24-renameat2-probe.out
  - S123: `git worktree prune [-n] [-v] [--expire <expire>]` in r23-trigger-prune.out
  - S131: `With prune, do not remove anything` in r23-worktree-census.out
- The S133 span is real in `man 2 rename | col -b`, line 91–92: `RENAME_NOREPLACE` / `Don't  overwrite newpath of the rename.`
- S124's lane copy `census/round-22/attempt2/sources/vendor-noreplace-probe.out` is tracked and has sha256 `1634d206…`, identical to the shokuknow payload.

Gate and receipt:
- `python3 -B tools/souji-receipt-run.py verify --root . census/round-24/records/gate-check-r24-entry.tsv` → `verify=ok rev=778747eb… tool_sha256=d5ed0805…`, rc=0.
- Class mutation (scratch verdict files, same ids, every class replaced): an all-`unverifiable` file and an all-`refused` file each give `entries=1 ok=1 slice_verdicts=8 slice_total=8 fail=0`, rc=0.
- Tallies (`cut -f2 | sort | uniq -c`):
  - r24 gate: 7 `accepted`, 1 `unverifiable`
  - r22: 5 accepted, 2 present, 1 unverifiable

Lane holdings cited by the detail table's `appended_r24` column, from `corpus/SOURCES.md`: S117 is git-prune(1) at line 137, S118 is the Qiita koseki page at line 138, and S113 is the GLib `g_file_trash()` reference at line 133. All three claims hold.

## Findings
1. **S118 `unverifiable` is not consistent with its scout and contradicts its own evidence** (medium, calibration).
   - Gate: `census/round-24/records/slice-verdicts.tsv` row S118 has class `unverifiable`, but its own evidence cell says "quote present in IEEE staging record and a PDF mirror".
   - Detail: `.ufo/waves/round-24/assimilation/slice-verdicts.tsv` row S118 says `present-via-mirror`.
   - Scout: `.ufo/waves/round-24/w1/ScoutSliceWeb.md` Findings table, S118 row, says `present` (the cited URL itself is unreachable).
   - Round 22's class definitions (`corpus/lessons/round-22.md`, register-slice paragraph): "`accepted` = the quoted span is real and locates to a document, so the row is repairable by re-citing it" and "`unverifiable` = the source cannot be read at all".
   - My re-fetch read the work at the DOI's own Crossref-registered IEEE link and at the mirror. So the source can be read, the span is real, and under those definitions the row is `accepted`, to be fixed by re-citing (round 22's own S118 cell already said "the flip is a re-cite to that copy").
   - Defence that does not fully rescue the class: the register's `unreachable` instruction (shokuknow `absent-defect-register.md`, class table) reads "re-fetch, or mark the row unverifiable". The re-fetch succeeded through the Crossref link, so the first branch applies. The class only fits if "source" means the literal DOI URL, and no record states that reading.
   - No downstream harm: the row is not appended and the gate does not read classes (finding 5).
2. **The detail and gate tables disagree on 7 of 8 rows, and no mapping is documented** (medium, the round-23 R23-M4 class of single-site sweep).
   - Detail `present` vs gate `accepted`: S114, S123, S126, S131, S133, S138.
   - Detail `present-via-mirror` vs gate `unverifiable`: S118.
   - Only S124 (`present-quote-needs-fix` → `accepted`) maps without contradiction.
   - The gate file's header points readers to the detail table as its authority, but nothing defines the vocabulary used in the detail file.
3. **Detail `present` for S123, S131 and S133 is unsupported, and the matching gate evidence cells do not support the class** (medium).
   - The register's quotes are absent from the cited payloads (my `grep -c` returns 0, 0, 0). Round 22 classed these as wrong-source citations whose span is real elsewhere, and its S123 cell reads "0 matches in the cited fixture output".
   - ScoutSliceOwnWork's `present` measured a different predicate, namely that the row's figures and digests are in the bytes (its Findings 1, 3 and 4). That is not the register's quote predicate.
   - The gate class `accepted` is right. But the evidence cells for these three rows only report digest matches, for example S123 "output sha256 510722c1 matches". They never say where the quoted span actually lives (git-worktree(1) SYNOPSIS or OPTIONS, rename(2)). A digest match cannot support a quote-class verdict.
4. **S126 and S138 drifted from `present` to `accepted` with no recorded reason** (low).
   - Round 22 (`census/round-22/attempt2/slice-verdicts.tsv`) has S126 and S138 as `present`, and so do this round's scout and detail table.
   - Re-checked: the S138 span is verbatim at line 17 of the markdown source. The S126 register quote is a truncated but verbatim prefix ("…emptying t"), which is still a substring. Under round 22's definitions both are `present`.
   - The gate tally moved from 5/2/1/0 to 7/0/1/0 without a stated reason.
5. **ATTACK, residual: the gate cannot see verdict classes.** `souji-gate-check.py` `check_slice` only tests membership in `CLASSES = {"present", "accepted", "unverifiable", "refused"}` and that each id has a row. Swapping every class to `unverifiable`, or to `refused`, still prints the same green counts line with rc 0 (see Evidence). So `slice_verdicts=8 slice_total=8` shows coverage only. Whether any verdict is correct rests entirely on hand checks like this seat's. That is why findings 1–4 do not move any counter.
6. **S138's locator is ambiguous, but not wrong** (info).
   - The gate says "markdown line 17", which I confirmed on the `.md` endpoint. Round 22 said "markdown line 11".
   - [INFERENCE] Round 22 counted from after the 6-line front matter (17 − 6 = 11).
   - The locator should state what it counts from.
7. **The admitted entry's REJECT reason has a stale clause** (low).
   - `corpus/knowledge/count-objects-linked-worktree-garbage.md` line 150 rejects the staged r23 entry partly because "S131 is quarantined payload-absent". This round's own verdict for S131 is `accepted`: the class is a register false positive, and the span is real in git-worktree(1).
   - The reject still stands on its other reasons (fleet claims, id collisions), but this clause is contradicted by the slice verdict.
8. **Survives:**
   - S114 (lane holds git-prune(1) as S117).
   - S124: digests match, the lane copy is byte-identical and tracked, and the `NOREPLACE_new=0(ok)` correction note stands.
   - S133: confirmed as 8 mounts and 7 distinct paths.
   - S118: the venue defect is confirmed by Crossref.
   - Every `appended_r24=no` holding claim.
   - The gate receipt (`verify=ok`).

## Attack log
- A1, S118 class vs scout: falsified (finding 1). The gate class is unsupported under round 22's definitions, and the register's own instruction points to re-fetch, which succeeded.
- A2, two-record agreement: falsified (finding 2), 7 of 8 rows disagree.
- A3, own-work quote predicate: falsified for the detail table (finding 3). The gate class survives, but its evidence is non-supporting.
- A4, class drift against round 22: falsified, low severity (finding 4).
- A5, gate sensitivity: the mutation passes green (finding 5). This is a residual, not a defect in a row.
- A6, re-fetching S118 and S138 and re-checking S133: the scouts' byte claims survive (Evidence).
- No lane file other than this report was written. No git or jj mutation. No shokuknow writes. Scratch has been removed.
