# SwarmCritic23 — attack on the round-29 lesson append (936efc8), its D4 correction, and the r29 instruments

Seat: critic, round 30 attempt 1, wave 2. Lane `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Base `9420341d9a814cb6089c25fb03a4cc9b23dc0d1b`, frozen prereg blob `d4928ec8…`, amendments A1-A3 `02aea48`.
All lane reads are `git -C` against committed bytes in a private clone (`/fast/scratch/hyaku/souji-r30/SwarmCritic23/c`, origin
dropped) plus read-only `git`/`cat` against the lane and `/home/vgpnk/Projects/shokuknow`. No lane byte written except this
report and its receipts.

## Status

STATUS: PASS — the attack ran on every assigned question (byte prefix, the seven paragraph texts, the `open` dispositions, D4 against the four staged entries, and five instruments at `936efc8` and the tip); the append and D4 hold on bytes, one of seven `open` dispositions does not.

## Evidence

- Append-only: `git cat-file -p 76c94eb…:corpus/lessons/round-29.md` (88 lines, 17978 B) vs `936efc8…` (126 lines, 27244 B); `cmp` on the first 17978 bytes → rc 0 (`PREFIX-IDENTICAL`); `git diff --stat` = "1 file changed, 38 insertions(+)". Nothing pins the whole file: `census/round-29/records/frozen-digests.txt` has no `round-29.md` line, and no `tests/fixtures/*expected.json` names it.
- The seven paragraphs: exact join-match against the committed reports at `df6afe8` for all seven (`qlen == paralen` in every case; paragraph line counts 4,1,6,5,8,1,8). Report blobs are identical at `de874ee`, `df6afe8`, `76c94eb`, `936efc8`, `9dcd367` (blob prefixes `c87176a fa8ee13 957ee58 e0a9f2c 13b7ee2 f0df316 5979e4e`).
- Completeness: 86 `.md` under `census/round-29/waves/`, all in `w1`; 69 `STATUS:` lines = 62 `PASS` + 6 `PARTIAL` + 1 `FAIL`; the gate prints `status_lines=69 checked_markers=7` both before and after the append.
- Carry effect: gate `--round 29` at `76c94eb` → `findings=10` (7 `LG-SEAT-UNCARRIED` + 3 `LG-DANGLING-PTR`), `carry_heading=0`; at `936efc8` and at the tip → `findings=3` (0 uncarried), `carry_heading=1`. r30 C2 counter: `76c94eb` → `other=7`, `936efc8` → `other=0`, every other leg identical (`reports=86 cne=0 dangling=0 fixture=ok redarm=ok regress=same`).
- r29 instrument named in the seat: `python3 -B tools/souji-registry-agreement.py --root … --rev 936efc8… --list-rev b8cb4b31…` → `SUMMARY k1=0 k2=0 mismatches=0`, rc 0 (identical from the clone and from the prescribed lane root; identical at the tip `9dcd367`).
- D4: 14/14 quoted spans occur verbatim at the cited lines of the bytes named beside them; 16 double-quoted spans in the six table rows, none over 25 words, none containing a pipe.

## Findings

1. **Append-only holds byte-exactly** (`corpus/lessons/round-29.md` at `936efc8`). The 17978-byte base prefix is untouched; the commit is 38 added lines, no modification, no reflow of the r29 text. Located: `/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/lessons/round-29.md:89-126`.
2. **"verbatim (bytes as committed …)" is over-claimed, not wrong in content** (`corpus/lessons/round-29.md:94-95`). The lesson says each entry quotes the STATUS paragraph "Each entry quotes that report's STATUS paragraph verbatim (bytes as committed at lane tip". The reports hard-wrap at ~80 columns; the append joins those lines with single spaces, so the text is verbatim only after whitespace normalization (all seven: `exact_join_match=True`, joined length == quoted length). The lane's own carry test collapses whitespace, so the carry is legitimate — but the word "bytes" is a byte-equality claim the artifact does not satisfy. r16 already named this: `.ufo/waves/round-16/w2/ConnQuality2.md:43` "Spell the normalization in the clause." Smallest safe correction: say "verbatim after whitespace normalization" (or name `de874ee` and the wrap rule).
3. **Seven is the whole set, not a sample.** Verified by two independent readings: every failure-form STATUS line in the committed r29 capture is one of these seven (6 `PARTIAL` + 1 `FAIL` over 86 reports), and the r29 gate flagged exactly these seven as `LG-SEAT-UNCARRIED` once discovery worked at `68447af` (`checked_markers=7`). No eighth failure line exists outside `w1` — all 86 `.md` are under `w1`.
4. **`open` is not honest for one of the seven: `SwarmExecutor17`** (`corpus/lessons/round-29.md:101` vs `:83`). The item's substance was dispositioned at the round-29 landing by an artifact change in the same lesson: `:83` records it — "the seat restored the ref with a compare-and-swap and disclosed it (its report, Finding 1)" — and the carried STATUS paragraph itself ends with the repair. The lane's close rule is `.ufo/waves/round-16/w2/ConnLessonCarry.md:68` "The honest close is a change in the artifact (code, fixture, README, SCORECARD, lesson, or SOURCES row) followed by `resolved@<landing-hex>`": the lesson row at `de874ee` (verified ancestor of `936efc8`) is that change, so `resolved@de874ee8` was available and `open` re-opens a closed item. The append's test cannot see this because it is a token test — "no `resolved@` receipt for any of them exists in `corpus/lessons/round-29.md` or `census/round-29/records/controls.tsv`" — and, after the append, the string `resolved@` now *does* occur in that file (at `:95`, in that sentence), so the stated check is no longer re-runnable as a plain grep. For `SwarmCritic51` (`:99`) `open` stays defensible: `:82` records A1-A4 as the remedy, but A1 is a format condition while Critic51's claim is "satisfiable without any true correction"; the append should still name the partial closure rather than leave it implicit. Impacted axis: calibration (self-assessment records).
5. **"lane tip `df6afe8`" is a stale label** (`corpus/lessons/round-29.md:94-95`). At the landing commit the lane tip is `936efc8`; the rev that committed the r29 capture and lesson is `de874ee`; `df6afe8` is the round-30 D3 commit ("routed r29 defect D3 …") and was the tip only when wave 1 drafted the block — `census/round-30/waves/w1/deliver-r29-carry-block.md:7` "Lane state read this run: HEAD `df6afe817d096e4ad71ba2b9cc21a83f126eb658`". The quoted bytes are identical at all five revs I checked, so the content stands; the label would send a verifier to a rev that neither wrote nor is the tip. Smallest safe correction: cite `de874ee86fcaee212bbf4a9bfa4bf49d953ccb8b`.
6. **D4 per-entry correction is accurate against the four staged entries** (`corpus/lessons/round-29.md:106-126`). All quotes resolve at the cited lines: `near-duplicate-threshold-r28.md:35` "It does not set a threshold and does not recommend one."; `:19-20`, `:37`, `:41` of the operating-point entry; `:42` of the relations entry; `:19`, `:40-41`, `:47-48` of the r34 entry. The superseded text and the untouched rows are cited correctly (`:11-:16` ADMIT, `:17` grouped reject, `:18-:19` separate rejections, `:21` the "adopting a method or number" sentence), `PROVINCE.md:69-70` is quoted exactly, and the scout rows are 7-10 with the content the table attributes to them (row 9 "documents a tool the lane never runs", row 7 "entry itself says it sets no threshold", row 8 the `no obvious threshold` probe, row 10 the r34 entry). The S216/S217 collision with the lane's S216-S219 is real: the staged r34 entry's `source:` lines name S216 (the chapter) and S217 (the Unpaywall record), while lane S216/S217 are `statx(2)`/Broder.
7. **D4 provenance is uneven across the four entries** (same rows). Three are tracked in `shokuknow` with last commits on `2026-10-24` (`9b707a72`, `9e91e504`, `d15c3d7d`) — before the r29 reject was recorded on 2026-10-25, so the bytes the correction attacks predate the judgment. `near-duplicate-threshold-source-r34.md` is untracked there (`??`), so its quoted lines rest on a working-tree file (mtime `2026-10-24 23:33:20`) with no history; a `sha256` in that row would make it re-checkable from the lane alone. Non-fatal.
8. **No r29 instrument is disturbed; the one that was broken is repaired.** Registry-agreement `k1=0 k2=0` at `936efc8` and at the tip. r29 C2 v1/v2 unchanged at `936efc8` (`failed=0 uncovered=0`, `lost=0 fidelity=0`, `manifests=5` because the r30 capture landed earlier). r29 C3 integrity is identical at `76c94eb` and `936efc8` (`SUMMARY legs=9 fail=1`, `L2 FAIL rows=145`): that red appears at C3's own landing, where r30 added S220/S221 to a leg pinned to 143, and pre-dates the append. The append's only measurable effect is on the channel it exists to fix: r29 gate `findings 10 → 3` (7 uncarried → 0) and C2 counter `other= 7 → 0`.
9. **The three findings left at the tip are the base's own jj pointers, not the append's.** `LG-DANGLING-PTR` for `../.ufo/waves/hyaku/jj-w1/reports/JjAuditSouji.md`, `…/JjTrialSouji.md` (`corpus/README.md:217`) and `.ufo/waves/hyaku/jj-w1/reports/` (`corpus/knowledge/jj-colocation-receipts.md:148`) are already present at `7b16731` and are exactly the base control's `dangling=3`; under `--fleet-root` the C2 counter reads `dangling=0`. Recorded for the operability seat, not filed against this commit.

## Attack log

| attacked item | verdict |
|---|---|
| append is a byte prefix of the base file | HOLDS |
| seven STATUS paragraphs complete, correct line numbers (5,7,5,3,3,5,5) | HOLDS |
| seven STATUS paragraphs byte-verbatim as the lesson words it | DEFECT-NOT-FATAL (wraps joined; whitespace-normalized, not bytes) |
| the seven are the whole failure set | HOLDS |
| `open` for `SwarmCritic49/51/53`, `SwarmReviewer40/42/43` | HOLDS (no `resolved@` receipt for them; A1 does not close Critic51's truth claim) |
| `open` for `SwarmExecutor17` | BROKEN (closed in substance at `:83`/`de874ee`; `resolved@` was available) |
| "lane tip `df6afe8`" | DEFECT-NOT-FATAL (stale label; bytes correct at all five revs) |
| D4 reasons vs the four staged entries | HOLDS |
| D4 quote length (≤25 words) and no-pipe rule | HOLDS (16/16 spans) |
| D4 line citations (`:11-:16`, `:17`, `:18-:19`, `:21`, `:82`, `:83`, `PROVINCE.md:69-70`, scout 7-10) | HOLDS |
| D4 provenance of `near-duplicate-threshold-source-r34.md` | DEFECT-NOT-FATAL (untracked in shokuknow) |
| r29 instrument `souji-registry-agreement.py` at `936efc8` / tip | HOLDS (`k1=0 k2=0`) |
| r29 C2 counters and r29 C3 integrity at `936efc8` | HOLDS (unchanged; C3 L2 red predates the append) |
| r29 landing-gate carry channel | HOLDS (10 → 3 findings; 7 uncarried → 0; rc stays 1 on the 3 fleet pointers) |
| C1 calibration counter at `936efc8` / tip | HOLDS (`k1=0 k2=0 mismatches=0 rows=18 pointers=10`) |

Impacted axes: calibration — finding 4 (a self-assessment record marks a closed item open); operability — positive, the round-29
carry channel closes and no operand moved; coverage — D4 is documentation over already-rejected entries, no F3/F1 surface moved.
No frozen target, predicate, counter or kill rule was touched by this review, and none is proposed to change.

## Deliveries

- `.ufo/waves/round-30/w2/SwarmCritic23.md` (this report)
- `.ufo/waves/round-30/w2/SwarmCritic23-receipts.txt` (13 sections: prefix `cmp`, report blob stability, STATUS census, seven-quote
  verification, gate before/after, C2 counter before/after, registry-agreement clone + lane root + tip, r29 C2 v1/v2, r29 C3 L2
  attribution, D4 quote/line verification, staged-entry provenance, lesson line map, C1 at `936efc8` and tip)
- Scratch `/fast/scratch/hyaku/souji-r30/SwarmCritic23/` removed after the receipts were copied.
- Tooling: no install or update this run; `git 2.x`, `python3 -B` from the host as provided. No pacman call.
