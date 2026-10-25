# ExecC1Surgery — C1 SCORECARD scaffold integration (round 26, w1)

## Status
STATUS: PARTIAL — the three draft files are delivered and verified (frozen counter on the draft:
`markers=0`, `headings=17 44 78`), but the landed tip `a529c76` violates amendment 2 item 5: both r24
capability rows are absent. Also: the brief's literal layout design contradicts the frozen K2 order;
I delivered the counter-correct order (r25 first) and document the conflict instead of implementing it.

## Evidence
| # | command | output excerpt | revision |
|---|---|---|---|
| 1 | `git rev-parse 89e0fce` + `git merge-base --is-ancestor 89e0fce HEAD` | resolves; IS ancestor (rc 0) | HEAD `4453128` |
| 2 | `git diff 0eca7c8 89e0fce -- SCORECARD.md` | empty → base bytes identical at lane base and frozen rev; base 254 lines, sha256 `b42a24f019b2dfa5084a5399dd750302e6ce11bf019820a81db78ada05229310` | `0eca7c8` / `89e0fce` |
| 3 | `bash census/round-26/c1-counter.sh` (committed instrument, run on base bytes in `/var/tmp` scratch) | `markers=2` / `headings=17 175 231 `, rc 0 | base |
| 4 | same counter on my draft bytes | `markers=0` / `headings=17 44 78 `, rc 0 | draft (sha256 `67998848d15f9c4e18100e9893eb79e7440f87cf0f280d8a04c8703845c72e33`) |
| 5 | same counter on the exact-span variant (230 lines) | `markers=0` / `headings=17 41 74 `, rc 0 | exact variant (sha256 `f8eaf485d995c895efeeeb5a49e37450a53d8d6d3cc228a1f03657831aa041bf`) |
| 6 | `git show a529c76:SCORECARD.md` then `grep -c 'debris census (r24)'` on it | `0`; file 233 lines, sha256 `a203bdcc4832802dd97ed879505ddc58f87dc02b1fb503817efe0e50232507f6`; headings 17 (r25), 44 (r24), 78 (r23) | `a529c76` |
| 7 | `cat census/round-26/records/c1-after.tsv` | `rev=a529c762…`, `tool=census/round-26/c1-counter.sh`, `rc=0`, stdout `markers=0` / `headings=17 44 78 ` | `4453128` |
| 8 | 15 span assertions (scratch python, byte equality) | 15/15 PASS: base 1-16; base 231-254 at 17-40; base 175-207 at 44-76; base 17-62 at 78-123; base 63-92 at 124-153; line 92 + R3 note at 153; base 93 at 154; base 213-214 at 155-156; base 94 at 157; base 95-137 at 158-200; base 225-226 at 201-202; base 138-169 at 204-235; separators at 41-43/77/203; 235 lines; zero marker lines | draft |
| 9 | payload round-trip from `c1-scaffold-extract.md` | payload 1 (33 lines), 2 (2), 3 (2) all equal the `git show 89e0fce:SCORECARD.md` bytes | `89e0fce` |

No tools installed or upgraded (nothing needed). Scratch `/var/tmp/souji-r26-ExecC1Surgery` removed.

## Findings
1. **True required ordering: Round 25 block, then Round 24, then Round 23** — r25 must be FIRST.
   The counter (`preregistration.txt:43`) prints `NR` in file order, so its triple is ascending; the
   prereg labels that triple `(n25, n24, n23)` and requires `n25 < n24 < n23`, which is only
   meaningful as heading-to-number mapping. Quote (`preregistration.txt:44-45`): "After condition:
   exactly three headings, ordered Round 25 < Round 24 < Round 23". The base file fails it
   (`17 175 231` = r23, r24-fenced, r25-last). Location: `SCORECARD.md:17,44,78` at `a529c76`.

2. **The brief's design (b) is counter-incompatible and was not implemented.** Inserting r24 above
   r23 while leaving r25 at the file end produces r23 < r24 < r25 and fails the frozen condition.
   My `c1-new-scorecard-head.md` carries the counter-correct order (landed `a529c76` already uses it).

3. **Landed integration omits payload 2 (both r24 capability rows).** Amendment 2 item 5
   (`preregistration-amendment-2.txt:23-24`) requires "the base `## Capabilities` section (63-94)
   with exactly the two r24 capability rows appended". At `a529c76` lines 154-156 are the
   `record agreement audit (r23)` row, a blank, then `## Planned`; `grep -c 'debris census (r24)'`
   is 0. My draft inserts base 213-214 verbatim at lines 155-156 — the applied delta is a pure
   2-line insertion after line 154. Independently found by sibling seats in this wave
   (`w1/c1-append-note.md` calls it "the two r24 capability rows are absent"; `w1/c1-verify.md`
   byte-diffs the same fragments) — three seats, same gap.

4. **Landed integration carries 5 lines outside the seven amendment-2 spans:** `a529c76` lines
   41-43 (blank, `---`, blank), 77 (blank), 203 (blank). Amendment 2 lists seven content spans and
   deletes everything else from base 170-230, but its stated enforcement (per-span byte-diff) cannot
   see extra bytes *between* spans. Disclose them or apply the 230-line exact variant (sha256
   `f8eaf485…`), which removes all three separators and still scores `markers=0`.

5. **The five `superseded by` refs resolve against the r25-BASE layout, not the current file.**
   They were computed at `a6d2d15` (the r25 base): 92 = blob row, 180 = C3 row, 181 = assimilation
   row, 224 = r24 planned bullet, 225 = r25 planned bullet. `a6d2d15:SCORECARD.md` is byte-identical
   to the r24-tip file (`git diff 315422b a6d2d15 -- SCORECARD.md` empty, 228 lines). After the r25
   scaffold landing (`a877325`, 254 lines) four of the five are +1 stale: 180 = C2 row, 181 = C3 row,
   224 = fence opener, 225 = r24 bullet; only `:92` still resolves, and only because `## Capabilities`
   never shifted — the same never-integrated rows as Finding 3. Literal and semantic maps for
   landed / draft / exact are in `c1-line-map.md` (draft literal 50, 49, 153, 201, 201; draft
   semantic 50, 51, 153, 201, 202).

6. **Deliverables** (all in `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-26/w1/`):
   `c1-scaffold-extract.md` (three verbatim payloads + deleted-machinery table),
   `c1-new-scorecard-head.md` (required ordering, span map, apply-ready 235-line file, exact-variant
   note), `c1-line-map.md` (literal + semantic ref maps).

## Attack log
- **A1 — K2 as written is gameable (tautological).** The awk emits `NR` ascending, so any file with
  exactly three matching headings prints a strictly increasing triple; the literal predicate
  `n25 < n24 < n23` therefore holds for *any* heading order. Evidence: base bytes score
  `headings=17 175 231`, rc 0 — numerically increasing, semantically r25-last (the exact violation
  K2 exists to catch). Only the heading-to-number mapping discriminates, and the committed counter
  prints numbers with no mapping. Logged only; no predicate change proposed.

- **A2 — K1 is two marker lines wide.** Deleting only base lines 172 and 217 scores `markers=0`
  (`headings=17 174 229`, rc 0) while the whole fenced block survives, r24 still only a fenced copy.
  K1 cannot distinguish marker deletion from integration; K2 caught this instance only because r25
  would still be last.

- **A3 — the payloads are uncounted, which is how Finding 3 landed.** `c1-after.tsv` binds only
  markers + headings. A file can drop both capability rows and both planned bullets, keep the
  correct heading triple, and still score `markers=0`; the landed tip demonstrates the capability-row
  half. Stricter-only remedy for a future round: have the C1 receipt also emit the appended
  capability-row and planned-bullet counts (or byte-diff all seven amendment-2 spans).
