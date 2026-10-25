# ScoutD5Ids — D5 disambiguation audit (round 25, wave 2)

STATUS: PARTIAL

Seat: L1Souji25.ScoutD5Ids (scout, leaf). Lane: souji-shokunin. Base: `a6d2d157755ef36b1dd4b9d53ad6d5b2ad6a3afe`; working tree vs HEAD `6deb535` (jj `@` = `604cd441c54d`).

## 1. Audit of the appended D5 note in `corpus/lessons/round-22.md`

**Finding 1 (primary): the D5 note is NOT appended to `corpus/lessons/round-22.md`.** `git diff HEAD -- corpus/lessons/round-22.md` is empty; the file is byte-identical to the round-25 base and ends at line 492 with the round-23 D6 correction section. There is no disambiguation section, no mention of "campaign", "staged" or "collision" in any appended block. The only artifact carrying the D5 note text is the wave-1 draft `.ufo/waves/round-25/w1/d5d6-drafts.md`, which states on its face: "Drafts only. The L1 integrates; no corpus file was edited by this seat." (verbatim, d5d6-drafts.md:3). The routed fix (prereg D5) has therefore not yet landed in lesson bytes; it exists only as a W1 draft. No W1 artifact claims the append was performed, so there is no false-green to reject — the residual is pending L1 integration after wave 2.

**Finding 2: the D5 draft correctly identifies all three designated bare sites plus two more.** The draft's table covers round-22.md L298/L351/L363, spot-check L199, and LOG.md L1509/L1538 as campaign-register ids, and names the colliding lane rows. That list is consistent with the round-24 hazard (`corpus/lessons/round-24.md:209-212`): "Hazard: the bare "S123" in `corpus/lessons/round-22.md` L298, L351, L363 and `round-22-verifier-spotcheck.md` L199 means the staged own-work row (`W2Collisions` F6). It needs a disambiguation note."

**Finding 3: the collision set is now wider than the draft's S123 focus.** Lane `corpus/SOURCES.md` rows S120–S123 exist since round 24 (lines 141–144), and rows S124–S126 were opened this round in the working tree (lines 145–147: S124 gitrepository-layout § commondir, S125 git-rev-parse § --git-common-dir, S126 git-worktree § DETAILS). Campaign/staged ids S123/S124/S126 exist in `.ufo/waves/round-22/attempt2/assimilation/staged-ids` (lines 15/16/18). So bare S123, S124 and S126 each name two different documents today; the draft itself notes ~S124 collides too" (L352/L363) once lane S124 lands — it has now landed in the working tree. W1 seats flagged the same: ScoutGateCensus F5 ("A bare "S124" written this round has the same ambiguity D5 is fixing for bare "S123""), ScoutSourcedClaimCheck attack 3 (lists eight bare-`S124` sites), ScribeReadme ("Whether `S124` is a bare ID is the same class of problem as the S123 disambiguation in D5").

## 2. Census of every S123/S124/S126 mention in lane-authored lessons

Scope: `corpus/lessons/round-{1..24}.md` (lane-authored). `*`verifier-spotcheck.md` files are non-author-owned and counted separately (§3). Grep `\bS12[346]\b` across the lessons directory returns mentions only in round-22.md and round-24.md (rounds 1–21, 23: zero).

Tokens, by class:
- **DI** = disambiguated inline (explicit prefix/section/convention in the same text unit)
- **BR** = bare but resolvable by document content
- **BA** = bare and ambiguous (two live spaces, no inline resolution) — the D5 target class

### round-22.md — 11 tokens in 9 lines (all campaign-intended)

| line | token(s) | class | basis |
|---|---|---|---|
| 298 | S123 | BA | M14: "Rows S123/S131/S133 quote man-page prose" — bare; register-slice context only |
| 323 | S124 | DI | explicit prefix: "campaign S124→S109" |
| 324 | S126 | DI | same mapping sentence as L323 ("campaign" governs the list) |
| 351 | S123 | BA | Register slice: "(S114 markup …; S123 and S131 man-page spans…)" |
| 352 | S124 | BA | same paragraph: "S124 intervening `NOREPLACE_new` field" |
| 354 | S126 | BA | same paragraph: "2 **present** (S126; S138)" |
| 360 | S126 | DI | explicit: "false positives of the campaign checker (S114, S126, S138…)" |
| 363 | S123, S124 | BA | "four are genuine wrong-source citations … (S123, S124, S131, S133)" |
| 432 | S124, S126 | DI | M21 map sentence: "the document map is the disambiguator (S124→S109 … S126→S113 …)" |

BA tokens: **6** (S123 ×3 at L298/L351/L363; S124 ×2 at L352/L363; S126 ×1 at L354). DI tokens: **5**.

### round-24.md — 16 tokens in 16 lines (6 lane, 9 campaign, 1 meta)

| line | token(s) | class | basis |
|---|---|---|---|
| 168 | S123 | BR | lane (entry citation, § REFS/§ DETAILS anchors match lane row) |
| 170 | S126 | BR | campaign (slice-verdict tables subject) |
| 186 | S123 | BR | lane (row definition: "S123 mined — https://git-scm.com/docs/git-worktree § REFS") |
| 198 | S123 | DI | explicit "Lane S120–S123" |
| 199 | S123 | DI | explicit "staged S120–S123" |
| 207 | S123 | DI | table column header "lane" |
| 209 | S123 | DI | meta: hazard statement quoting the bare token as an object |
| 216 | S123 | BR | lane (ADMIT re-sourcing to S120–S123) |
| 233 | S123 | DI | slice table under header "campaign register ids" (L227) |
| 234 | S124 | DI | same table header |
| 235 | S126 | DI | same table header |
| 236 | S123 | DI | slice table "as S123" cell under the "campaign register ids" header (L227) |
| 237 | S123 | DI | same |
| 238 | S126 | DI | slice table "as S126" cell under the same header |
| 354 | S123 | BR | lane (used-by update: "S123's scope widened to the § DETAILS sentence") |
| 383 | S126 | DI | new D6 append (working tree): same block carries the convention sentence "Campaign ids are keyed by lane plus id, never as bare S-numbers." (L385) |

DI: **11**; BR: **5**; BA: **0** in round-24.md.

## 3. Non-author spot-check files (must NOT be edited; verified unmodified)

`git status` shows neither spot-check file in the modified set — they are byte-identical to HEAD.

- `round-22-verifier-spotcheck.md:199` — "1 present, 1 refused (S123)" — **1 BA campaign token**. This is the round-24-designated second site; per D5 it is remediated by the lesson/report note, not by editing the file.
- `round-24-verifier-spotcheck.md` — L55/L62/L74: 3 lane tokens (resolvable: they name the git-worktree § REFS row and its URL); L99: the D5 hazard statement itself (meta). No BA campaign tokens.

## 4. Report/lesson citations disambiguate rather than editing non-author spot-check files

- **Lesson/bytes so far:** the only committed lesson-side disambiguation is structural: round-24.md § Id collisions and renumbering (L195–212, including the hazard and by-document map), the M16/M21 maps in round-22.md (L317–325, L424–435), and the slice-table header "campaign register ids" (round-24.md:227). The working tree adds the D6 append's convention sentence (round-24.md:385) and README/SCORECARD pointer text ("rows are joined by (souji, campaign-id), never bare S-id" — corpus/README.md uncommitted append; SCORECARD.md uncommitted append).
- **New C3 writes follow the convention:** the knowledge entry `corpus/knowledge/git-repo-structure-common-dir.md` (untracked, working tree) writes "source: S124 — https://git-scm.com/docs/gitrepository-layout — § commondir" and "SOURCES S124/S125/S126 opened live" (lines 1–5), i.e. name the registry and the document anchor rather than bare S-numbers. This matches ScoutGateCensus F5's recommendation.
- **No spot-check file was edited** (verified above). The D5 draft's cover line documents why and routes the note to lesson + report (d5d6-drafts.md:11-17).
- **Residual:** no round-25 report exists yet and the lesson note is still only a draft (§1) — the "report/lesson" half of the D5 fix is not yet delivered.

## 5. Counts and residuals

Counts (current working tree):
- Lane-authored lessons: 27 tokens total (round-22.md 11; round-24.md 16). DI 16, BR 5, BA 6.
- Non-author spot-checks: 5 tokens (round-22 spot-check 1 BA; round-24 spot-check 4, all lane/meta).
- Designated D5 bare sites still uncovered by any inline note: round-22.md L298/L351/L352/L354/L363 (6 tokens, 5 lines) + spot-check L199 (1 token) + LOG.md L1509/L1538 (2 tokens, verified bare campaign S123 in the r22-attempt2 tally and the r23 correction block).

Residuals:
1. D5 note absent from `corpus/lessons/round-22.md` (and from any committed report); only W1 draft `d5d6-drafts.md` exists — integration pending.
2. 6 BA tokens remain in round-22.md until the note lands.
3. Spot-check L199 and LOG L1509/L1538 remain bare; covered only by the draft note's promise, not by bytes.
4. Collision set newly extended to S124/S125/S126 (lane rows opened this round); any future bare S124/S125/S126 writes must follow the "SOURCES S<id>" convention — the C3 entry, SCORECARD and README drafts already do.

## Attack log

- `git diff HEAD -- corpus/lessons/round-22.md` → empty (note absent). `wc -l` = 492; tail = round-23 D6 correction block.
- Grep `\bS12[346]\b` over `corpus/lessons/` → only round-22.md / round-24.md / both spot-checks.
- `grep -nE '\| S12[0-3] |\bS12[456] ' corpus/SOURCES.md` → lane S120–S126 rows confirmed (lines 141–147).
- `grep -nE 'S12[346]$' .ufo/waves/round-22/attempt2/assimilation/staged-ids` → staged S123/S124/S126 confirmed.
- `grep -nE '\bS12[346]\b' LOG.md` → 1507 (map context), 1509, 1538, 1690; `sed -n '1500,1545p'` read confirms 1509/1538 are bare campaign S123.
- `git status --short` → no spot-check file modified; round-22.md unmodified; round-24.md carries the uncommitted D6 append; `corpus/knowledge/git-repo-structure-common-dir.md` untracked.
- No scratch created; no installs/updates (no tool installed this session).
