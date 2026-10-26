# SwarmCritic26 — round 31 wave 2 — M1 carry audit (round-28, 19 entries)

## Status
STATUS: PARTIAL — M1's round-28 carry is structurally sound (19/19 quotes byte-exact, carried set equals the 19 non-PASS reports, UNCARRIED finds reach 0 at the tip) but three `resolved@` dispositions credit an uncommitted worktree revert to a named commit, two `open` dispositions are already resolved in-lane, and five reasons are refuted by bytes I opened this run.

## Evidence

Revisions: section at `corpus/lessons/round-28.md:54-82` @ c6108301cbf0ca0ad086ff0ece6b76adad6b74b6; tip 2c16d018e40db7c23420a2c3bb546b52957bcc25; base 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc.

Quotes and coverage (all 19 entries, read from committed report bytes at c6108301):
- every quoted span equals the whole cited line; `line.split(quote)` → `("", "")` for all 19; no prefix/suffix omitted.
- 68 reports committed under `census/round-28/waves/w1/`; exactly 19 carry a non-PASS STATUS; the carried (path,line) set equals that set (0 missing, 0 extra).

Disposition commits:
- `git merge-base --is-ancestor <h> 2c16d018` → YES for 765fe8b, ed270c4, 691dd29, fec846d.
- `git show --stat 765fe8b` → `.gitignore | 3 +` (`.ufo/waves/`, `census/operator-sweep-*/`, `__pycache__/`), `census/round-26/waves/manifest.sha256 | 1382`, `census/round-27/waves/*`, `census/round-28/records/searchlog-draft.md`, `corpus/knowledge/origin-record-{exclusivity,durability}-r28.md` (+52/+55), `corpus/SOURCES.md | 14 +-`, `tools/souji-wave-evidence-capture.sh | 203`.
- `git diff --name-only 765fe8b^ 765fe8b -- .ufo` → 0 paths.
- `git log --oneline 0c96332..2c16d018 -- .ufo/waves/round-26` → 0 commits; `git diff --name-only 50443f5 2c16d018 -- .ufo/waves/round-26` → 0 files.
- `git show ed270c4 -- corpus/SOURCES.md` → single row line replaced (S215 pin 65-hex → 64-hex).
- `git show --stat fec846d` → c1/c2/c3-after.tsv + SCORECARD 3 cells.
- `git show --stat 691dd29` → 1 file, 126 lines (spot-check lesson).

Re-derived measurements (read-only):
- base gate @ 9f17a1e `--round 28 --fleet-root /home/vgpnk/Projects/shokunin` → `findings=21` (19 UNCARRIED, 2 DANGLING); same command without `--fleet-root` (as the carry header prints it) → `findings=24` (19 UNCARRIED, 5 DANGLING) — the header's arithmetic reproduces under its own command.
- tip gate @ tip → `findings=0`; base gate @ tip → `findings=2` (dangling only). M1's per-round target holds.
- `sha256sum -c census/round-26/waves/manifest.sha256` at 765fe8b → 1228 OK, 152 "FAILED open or read", 2 improperly formatted, rc 1; tree d246d803 unchanged at ed270c4/691dd29/tip. r27: 124/124 OK, rc 0.
- round-28 gate checker over committed 765fe8b entries+snapshots → `entries=2 ok=2` (check1-check5; the scratch root stages no slice, so `fail=1` is `slice-missing`).
- S215 pins: 765fe8b carries two 65-hex occurrences; ed270c4 fixes the row only; tip has 64-hex at `corpus/SOURCES.md:160` and the 65-hex form at `:187`. sha256 of committed `git-fetch-zh-HANS-CN.html` = `a7f4742d99fd515f1811aabd830a61840939ebe3e12cf1e6792662181b574042`.
- `census/round-28/sources/SHA256SUMS` @ tip: three POSIX files only.
- `census/round-28/waves/{w1-results.json,w1-spec.json,w1-dispatch.json,w1.ready,w1-run.err}` equal the live `.ufo/waves/round-28/` files, 5/5 sha256.
- `census/round-30/records/d3-green-r28-wave-evidence-capture.txt` (df6afe8): `case-4: PASS`, `cases=15 pass=15 control=TAMPER-REJECTED`, `rc=0`.
- The landed section is byte-identical to the wave-1 delivery `census/round-31/waves/w1/deliver-m1-carry-r28.append.md` (19/19 bullets equal), so the header wording originates in wave 1 and was integrated unchanged.

## Findings

1. **Worktree revert recorded as commit-delivered** (`corpus/lessons/round-28.md:65`, `:69`, `:77`; burden: C3's capture/revert half and M1's own bookkeeping). 765fe8b's diff has 0 `.ufo` paths, and no commit after round-26 touches `.ufo/waves/round-26` (0 commits in `0c96332..2c16d018`; 0 files differ vs `50443f5`). The cited ranges are therefore empty by construction and cannot evidence a revert. Reviewer37 (`:77`) and Executor13 (`:69`) are graded WRONG-RESOLVED; Critic43 (`:65`) is WRONG-RESOLVED for the residue clause only (instrument and both receipt trees are genuinely at 765fe8b). Axis hit: calibration (7, lowest) — the carry is the round's durable record of what closed.
2. **Two `open` dispositions no longer reproduce** (`:71` MutationTester47, `:72` MutationTester49). At tip the round-28 gate baseline has 0 UNCARRIED findings and this section names all 19 non-PASS reports, so "never named, so they stay uncarried" is self-refuting. For 49, `census/round-30/records/d3-green-r28-wave-evidence-capture.txt` records the same fixture green (`cases=15 pass=15`), after the fixture was rewritten at b862007; "no recorded resolution" is false. Both are SHOULD-BE-RESOLVED. Axis hit: calibration (stale residual debt in the mined-mistake ledger).
3. **Receipt presented as durable while it refuses verification** (`:65` Critic43, `:78` Reviewer38, and the pinned `census/round-28/records/c3-after.tsv` behind `:81`). `sha256sum -c` on the committed r26 manifest: 152 of 1382 entries absent from the tree at the same commit, rc 1. The dispositions state presence only ("committed with manifest.sha256 and summary.tsv") and never surface rc 1; the defect is disclosed elsewhere (`corpus/lessons/round-28.md:40`, R29 corrections), so this is an omission in the closed-form disposition, not a hidden defect. Axis hit: operability (8) at the receipt layer, via the C3 receipt the carry calls durable.
4. **Reason for an `open` refuted by the gate** (`:64` Critic42). The round-28 gate checker over the committed entries and snapshots returns `entries=2 ok=2` (check1-check5; my scratch root stages no slice, so the slice leg reads `slice-missing`), and the landed Gate quotes are present in the whitespace-squashed snapshot bytes while the rejected draft quotes are absent. The Residuals entry cited (`:39`) records neither of the two defects named. `open` stands for the frozen target (139 rows vs 138); the stated ground does not. Axis hit: calibration.
5. **Duplicate pin left stale under a closed entry** (`:73` Reviewer31, `corpus/SOURCES.md:187`). ed270c4 repairs the row pin; the same page's pin in the S215 search prose keeps the 65-hex garbled form at tip. The disposition's "the S215 pin now reads <64-hex>" is true of one of two authorities for the same snapshot. Axis hit: coverage (8) — source-pin authority is single-valued per snapshot.
6. **False detail in a resolved reason** (`:80` Scribe22). `691dd29` contains no git-scm fetch; S215 is verified from the committed snapshot (`git show fec846d:... | sha256sum`), not live. The independent POSIX reopen is real. Axis hit: calibration.
7. **Pinned acceptance record not reproducible from its own revision** (`:81` Scribe27 → `census/round-28/records/c3-after.tsv`). The pin asserts `round26_sha256sum_check=rc0; 1380 OK`; committed bytes give rc 1 with 152 unreadable. The R29 append corrects the claim, but the M1 entry leans on that tsv as the round's acceptance evidence. Axis hit: calibration.
8. **Measurement basis differs between header and receipt** (`:58` vs `census/round-31/records/m1-red-before.txt`). Header prints the gate without `--fleet-root` and gets 24 (19+5); the receipt passes `--fleet-root` and gets 21 (19+2); the three extra dangling pointers are `../.ufo/waves/hyaku/...` citations at `corpus/README.md:217` and `corpus/knowledge/jj-colocation-receipts.md:148`. Both numbers are true; the carry does not say which basis it used. Axis hit: calibration (minor).
9. **Reason contradicted by the lesson body** (`:79` Reviewer39). `corpus/lessons/round-28.md:49` states a counting command with a SUMMARY literal (r29 c2-counter over r26/27/28 manifests). `open` survives only on the narrow "for the round-28 claim" reading; the sentence as written is false. Axis hit: calibration (minor).
10. **Carried `[WAIT]` closed on input arrival only** (`:82` Sentinel61). The census archive is byte-identical to the live wave files (5/5), so the substitution is faithful, but the seat's five-item sweep has no run record at tip. Not a verdict change; residual for the L1. Axis: calibration (minor).

No finding touches C1, C2 or C3's own counters, and M1's frozen per-round target (UNCARRIED → 0) holds at the tip for round 28.

## Attack log

- Quoted-span attack: tried to find any bullet whose quote is a partial or edited span. Result: 19/19 equal the full cited line; no MISQUOTED.
- Coverage attack: enumerated all round-28 reports independently of the gate and compared STATUS sets. Result: carried set equals non-PASS set; no gap.
- Vacuous-evidence attack on the r26 revert: tested whether the empty commit-range diff could be non-empty. Result: no commit in the range touched `.ufo/waves/round-26`, so the evidence is structurally empty — attack succeeded (findings 1).
- Provenance attack on `765fe8b` as the delivering commit: `git diff --name-only 765fe8b^ 765fe8b -- .ufo` → 0. Attack succeeded for Executor13/Reviewer37/Critic43.
- Receipt-verification attack: extracted the committed r26/r27 waves trees and ran `sha256sum -c`. Result: r26 rc 1 (152 unreadable), r27 rc 0 — attack succeeded for the "durable receipts" wording, failed for r27.
- Header-arithmetic attack: initial runs with `--fleet-root` gave 21, so I first read the header's 24 as fabricated; re-running the header's own command (no `--fleet-root`) reproduced 24 = 19+5 exactly. Attack withdrawn; replaced by finding 8 (basis mismatch).
- Open-disposition attack: grepped for later resolutions of each open item. Succeeded for MutationTester47 (tip gate findings=0) and MutationTester49 (round-30 green record); failed for Critic45, Reviewer33 (SHA256SUMS still 3 files at tip), Reviewer39.
- `resolved@` commit attacks: for each of the four hashes, verified ancestry, stat, and the specific hunk. Failed to falsify 765fe8b for Executor10/12/19/Reviewer32/35/38, ed270c4 for Reviewer31/Sentinel61, 691dd29 for Scribe22, fec846d for Scribe27.
- Fetched-source substitution attack on Sentinel61: compared the five census-archived wave files with the live `.ufo` files. Attack failed (all sha256 equal).
- Not attempted (out of scope by seat bound): re-running jj/git live fetches of the POSIX or git-scm pages, and any write inside the lane.

## Deliveries
- `.ufo/waves/round-31/w2/deliver-m1-audit-r28.md` — per-entry verdict table, quote-exactness control, per-entry evidence.
- `.ufo/waves/round-31/w2/SwarmCritic26.md` — this report.
