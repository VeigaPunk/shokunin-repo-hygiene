# Deliver — `corpus/lessons/round-29.md` `## Gate` D4 per-entry correction

Seat SwarmScribe16, round 30 wave 1. Lane base `9420341d9a814cb6089c25fb03a4cc9b23dc0d1b` (branch `master`); the lesson
is 88 lines at that rev and carries no r30 correction yet (`grep -n 'R30-CORRECTION' corpus/lessons/round-29.md` → no
match). Nothing in lines 1-88 is edited: the L1 appends the section below after line 88, matching the r29 correction
precedent at `corpus/lessons/round-28.md:47-52` (heading plus `R29-CORRECTION `-tagged lines, superseded sentences left
in place).

## Superseded text (named by line number)

- `corpus/lessons/round-29.md:17` — the grouped reject row's "Located quote / evidence" cell: "each states a threshold,
  operating point or relation choice over documents". It is a characterization in a quote column: no located quote
  exists for the four staged entries in that row, and the cell is false for one entry and not the reject reason for the
  other three.
- `corpus/lessons/round-29.md:21` — "the four near-duplicate entries are rejected for adopting a method or number".
  None of the four adopts a method or a number; each says so in its own "What this does NOT establish" section.

## Round 30 correction (D4, append-only)

R30-CORRECTION corpus/lessons/round-29.md:17 supersedes the grouped reject row's evidence cell and the :21 sentence
with the per-entry rows below. The four REJECT decisions stand; the recorded characterization and the "adopting a
method or number" sentence do not. Opened read-only on 2026-10-26: the four staged entries under
`/home/vgpnk/Projects/shokuknow/merge/souji/knowledge/corpus/knowledge/`, the held entries
`corpus/knowledge/dupe-finders-detect-then-act.md`, `duplicate-verdict-identity.md`,
`duplicate-verdict-byte-equality.md`, `PROVINCE.md:69-70`, and the r29 scout table
`census/round-29/waves/w1/deliver-f3-scope-table.tsv` rows 7-10. Every quote below is at most 25 words, copied from the
bytes named beside it, and contains no pipe character. F3 is byte-identical scope: `PROVINCE.md:69-70` "F3 duplicate
verdicts — byte-identical copies; a `duplicate` receipt class would be a taxonomy change (operator decision)."

| Staged entry | What it actually asserts (location) | Sound reject reason |
|---|---|---|
| `near-duplicate-threshold-r28.md` (S162, ssdeep usage page) | Reports that ssdeep's score is a match score and that its own page says a fuzzy match "does not mean the files are related"; concludes the lane's class stays `cmp` byte-equality and the threshold is an operator ruling. **It states no threshold, no operating point and no relation choice**: `near-duplicate-threshold-r28.md:35` "It does not set a threshold and does not recommend one." The row's clause is false for this entry. | Similarity-score documentation outside F3's byte-identical scope (`PROVINCE.md:69-70`); its only lane consequence is already held — `dupe-finders-detect-then-act.md:34` "`cmp` byte equality (not a hash) between candidate and a designated original" and `:35` "OPERATOR DECISION"; documents a tool the lane never runs (scout table row 9). |
| `near-duplicate-operating-point-r28.md` (S172, WWW '07) | States a **published** operating point: `:19-20` "64-bit simhash fingerprints and k = 3 are reasonable (S172)" over an 8-billion-page crawl, with precision and recall near 0.75; calls it "a precedent for HOW to state a threshold, not a number to adopt" (`:37`). So the clause is literally true here as description — but the entry sets no threshold for the lane: `:41` "It does not set, recommend or imply a threshold for souji." | Simhash over a web crawl is document similarity, never byte-identical files; no lane consequence beyond the held `cmp` rule (`dupe-finders-detect-then-act.md:34`) and `duplicate-verdict-byte-equality.md:38` "The near-duplicate class is a different object and is not decided here." The scout table row 7 records the reason as "entry itself says it sets no threshold". |
| `near-duplicate-relations-r29.md` (S178 Broder, S179 Roussev) | States the relation pair and a measurement: resemblance r(A,B) and containment c(A,B), only the first a metric, and a survey finding no usable ssdeep threshold. It recommends no relation and sets no threshold: `:42` "It does not set a threshold, and it does not recommend a relation." The clause is true only as description of literature. | Its Broder half is already held as bounded vocabulary — `duplicate-verdict-identity.md:35` "Resemblance and containment are vocabulary, not equality." and `:57` "Broder is document similarity, not byte equality."; its ssdeep half is similarity-measure literature outside F3. Its Gate quote also needs exact wording: the scout probe found "no obvious threshold" not verbatim (row 8). |
| `near-duplicate-threshold-source-r34.md` (campaign rows S216/S217, IFIP DF 2014) | States **literature** ssdeep thresholds: `:19` "The paper does set thresholds." — t = 60 and t = 40 for the match score — and says why choosing one is hard. It adopts none: `:40-41` "It does not establish a threshold for souji's `duplicate` receipt class" because "The paper's thresholds are properties of a measured corpus and a chosen measure", and the threshold stays an operator ruling (`:47-48`). | Similarity thresholds that are properties of another corpus and measure, outside F3's byte-identical scope (scout row 10). Its row ids are campaign ids: S216/S217 collide with the lane's S216-S219, so any future admission must re-point them by document. |

The ADMIT rows at `:11-:16`, the separate rejections at `:18-:19`, and every flip condition stand unchanged; the
superseded text at `:17` and `:21` stays in place for the audit trail.
