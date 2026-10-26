# SwarmScribe16 — D4 per-entry correction for `corpus/lessons/round-29.md` `## Gate`

## Status

STATUS: PASS — the D4 correction section is drafted as an append-only block naming the superseded row by line number, with one row per staged entry, each row carrying what the entry actually asserts (quoted, located) and the sound reject reason under `PROVINCE.md:69-70` plus the held entries that already cover the consequence. No lane byte was edited; the draft is a delivery file for the L1 to append.

## Evidence

All lane reads were read-only (`read`, `awk`, `grep`, `wc`, `git show`/`git diff`); no gate, fixture or counter was run and no execution is claimed.

- Frozen contract read first: `/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-30/records/preregistration.txt` (C1/C2/C3, lane base `9420341d9a814cb6089c25fb03a4cc9b23dc0d1b`).
- Superseded text, at the lane base rev:
  `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 9420341d9a814cb6089c25fb03a4cc9b23dc0d1b:corpus/lessons/round-29.md | wc -l` → `88`; line 17 begins
  `| staged \`near-duplicate-threshold-r28.md\`, \`near-duplicate-operating-point-r28.md\`, \`near-duplicate-relations-r29.md\`, …` and its evidence cell reads
  "each states a threshold, operating point or relation choice over documents"; line 21 reads "the four near-duplicate entries are rejected for adopting a method or number".
  `git -C … diff --stat 9420341d9a814cb6089c25fb03a4cc9b23dc0d1b -- corpus/lessons/round-29.md PROVINCE.md corpus/knowledge/` → empty, so the working-tree line numbers equal the rev's.
- Four staged entries opened (read-only, `/home/vgpnk/Projects/shokuknow/merge/souji/knowledge/corpus/knowledge/`): `near-duplicate-threshold-r28.md`, `near-duplicate-operating-point-r28.md`, `near-duplicate-relations-r29.md`, `near-duplicate-threshold-source-r34.md`.
- Held entries opened: `corpus/knowledge/dupe-finders-detect-then-act.md` (`:34` cmp rule, `:35` OPERATOR DECISION), `duplicate-verdict-identity.md` (`:35`, `:57`), `duplicate-verdict-byte-equality.md` (`:38`).
- Scope line: `PROVINCE.md:69-70` "F3 duplicate verdicts — byte-identical copies; a `duplicate` receipt class would be a taxonomy change (operator decision)."
- Routed defect: `corpus/lessons/round-29-verifier-spotcheck.md:107` (discernment row for the staged threshold entry) and `:128` (Routed defects item 3 / D4).
- Scout table row facts: `census/round-29/waves/w1/deliver-f3-scope-table.tsv` rows 7-10.
- Quote gate: a `python3 -B` check normalised whitespace in each source file and confirmed all 19 quoted strings are present verbatim, none contains a pipe character, and the longest is 17 words (`OK` for every row; one mismatch found and fixed — the ssdeep disclaimer is "does not mean the files are related", not "…that the files are related").
- No scratch tree was created (no clone, work tree, fixture or download was needed); nothing was left on disk outside the two delivery files. No tool was installed or upgraded.

## Findings

1. `corpus/lessons/round-29.md:17` — the evidence cell is false for `near-duplicate-threshold-r28.md`: the entry states no threshold, no operating point and no relation choice, and says so itself at `near-duplicate-threshold-r28.md:35` "It does not set a threshold and does not recommend one." The cell is also a characterization sitting in a quote column — the row names no located quote for any of the four entries. Correction row 1.
2. `corpus/lessons/round-29.md:17` applied to `near-duplicate-operating-point-r28.md` — the closure's parenthetical ("also sets no threshold") is right, but narrowly: the entry *does* state a published operating point (`:19-20` "64-bit simhash fingerprints and k = 3 are reasonable (S172)") while setting no threshold for the lane (`:41`). The correction keeps that distinction so the L1 does not overcorrect into "states no operating point", which would be false.
3. `corpus/lessons/round-29.md:17` applied to `near-duplicate-relations-r29.md` — "relation choice" is descriptively true (resemblance/containment), but the entry recommends no relation (`:42`) and its Broder half is already held, bounded, at `duplicate-verdict-identity.md:35` and `:57`; its ssdeep half is similarity-measure literature outside F3. Its Gate quote also needs rewording before any future admission: `census/round-29/waves/w1/deliver-f3-scope-table.tsv:8` records that "no obvious threshold" is not verbatim in the Roussev text.
4. `corpus/lessons/round-29.md:17` applied to `near-duplicate-threshold-source-r34.md` — it does state literature thresholds (t = 60, t = 40) and explicitly declines to transfer them (`:40-41`); its campaign row ids S216/S217 collide with the lane's S216-S219, so any future admission must re-point them by document.
5. `corpus/lessons/round-29.md:21` — "the four near-duplicate entries are rejected for adopting a method or number" is false as written: none adopts a method or a number. This second superseded sentence is named in the correction block alongside `:17`.
6. `census/round-29/waves/w1/deliver-f3-scope-table.tsv:2` (identity row) — says "claim 1 is similarity VOCABULARY (Broder)", but in `corpus/knowledge/duplicate-verdict-identity.md` the Broder material is numbered claim 3 (claims 1-2 are link(2) and statx(2)). The correction cites claim 3 by line (`:35`), not by the scout table's number. Recording-only: the row's substance (Broder is vocabulary-only, explicitly bounded) is correct.
7. `corpus/lessons/round-29.md` — no r30 correction exists at the base rev and none was added by me: the delivery file is the drafted text only, so the L1 remains the single integration owner of the append.
8. Provenance limit — the four staged entries are held outside the lane under `/home/vgpnk/Projects/shokuknow/` (read-only there, as required); the correction therefore cites them by filename plus line, not by a lane revision. Their byte pins (`sha256` in each `source:` line) were not re-fetched this run; no network probe was performed.

## Deliveries

- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-30/w1/deliver-r29-gate-correction.md` — the `## Round 30 correction (D4, append-only)` section (superseded-line preamble + 4-row per-entry table + what-stands line), ready to append after `corpus/lessons/round-29.md:88`.
- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-30/w1/SwarmScribe16.md` — this report.
