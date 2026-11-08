# Round 89 — amendments to the frozen claims (pre-file falsification)

Written before the round report was filed. The frozen wording lives in `census/round-89/preregistration.txt`
(commit F) and is not edited here: each amendment records what the round's own artifacts falsified in that wording,
and the narrower sentence the round now puts its name to. Numbers are re-derived on committed bytes by non-author
seats and by the L1; records under `census/round-89/records/` and the wave's reports under
`.ufo/waves/round-89/w1/`.

Wave evidence root: `.ufo/waves/round-89/w1/`.

## A0 — instrument and chronology corrections (before or during data; not amendments to a claim)

- **A0.1 — the C2 fixture's KFF6/KFF7 checkers were fixed before freezing.** The first checkers asserted a substring
  (`"\\\\xff" in detail`) that the r88 (before) detail also contains, so KFF6 and KFF7 both passed on the before
  tool. The checkers now count backslashes with `chr(92)`: KFF6 requires exactly one backslash before `xff` and none
  doubled; KFF7 requires the doubled spelling with none bare. A pair check in the fixture's `main()` additionally
  requires the KFF6 and KFF7 details on the tool under test to be byte-different. Before the fix the before arm read
  `tool_pass=9 before_pass=9`; after it reads `tool_pass=8 before_pass=8` on the before bytes and `tool_pass=10
  before_pass=8` on the filed tool. The fix landed before the control/after receipts were filed.
- **A0.2 — the C2 numbers in the frozen prereg are `before_pass=8`, not 7; KFF7 passes on both arms.** The prereg's
  first draft said `before_pass=7` with KFF6/KFF7/KFF8 failing. Measured, KFF7 (the literal spelling) is byte-stable
  across the repair, so it passes on the before tool too; the delta is KFF6 + KFF8. The prereg was corrected before
  freezing and the frozen sentence names the stable case explicitly.
- **A0.3 — the C2 `200-character` bound is restated as a 200-RAW-BYTE window (escape-first vs raw-first).** The r88
  `_one_line` measured the bound on the ESCAPED text. The r89 `_one_line_bytes` bounds raw bytes first, so the escaped
  rendering of a control-heavy input can exceed 200 characters (each control byte costs four). The frozen prereg's
  stated limits say so. The r88 KFF3 case (a printable 400-character line) is still 1:1 and still within the old
  260-character detail bound.
- **A0.4 — a misrooted `write` of the preregistration landed at the fleet root** (`/home/vgpnk/Projects/shokunin/census/round-89/`);
  it was moved byte-exact into the lane and the fleet directory removed. No other fleet file was touched; the misroot
  sweep before the report confirms no further fleet write from this round's seats.
- **A0.5 — the C1 battery exceeds one 300 s cell.** Each pinned population costs a fresh fixture clone plus 53 counter
  runs per mutant. The C1 before run was therefore launched detached and its receipt filed from the detached log;
  the after run follows the same path once the wave's instruments are frozen.

## A1 — C1: LD2 does not bind the malformed-row guard, so the frozen kill count is 15, not 16

- **Artifact:** `.ufo/waves/round-89/w1/S89MutCounter.md` F1/§6 (counter matrix + load-bearing verdict),
  `S89Sentinel.md` §3.4/F-1, `S89Reviewer.md` §1, `S89Simplifier.md` F1 — four seats, same number.
- **Frozen wording falsified:** the prereg's "kills all SIXTEEN … killed_r88=12, killed_r89=16,
  killed_total=28, EXIT 0" and "LD2 binds the `_ledger` malformed-row guard". Measured with the prereg's own
  command: `SUMMARY mutants=16 sets=r88,r89 pristine_r88=ok pristine_r89=ok killed_r88=12 killed_r89=15
  killed_total=27`, battery EXIT 1; `m17c-no-malformed pop=r89 killed=no`.
- **Mechanism:** LD2 appends `P02\tABSENT` (2 columns), but `P02` is already a row of the frozen r77 ledger
  (`P02 ABSENT -`), so pristine refuses on `len(r) < 3` and `m17c` (which drops only that clause) refuses on
  `r[0] in ledger` — the same `LEDGER-REFUSED id=P02` marker and exit 1. The harness row stays green under
  `m17c`, so `m17c` survives and LD2 binds the duplicate clause a second time. The malformed clause is reachable
  — a 2-column row under an absent id (`ZZ9\tABSENT`) makes pristine refuse with `LEDGER-REFUSED id=ZZ9` and
  `m17c` raise `IndexError` with no marker — but the filed LD2 row does not exercise it.
- **Narrowed sentence:** *Three of the four r89 bindings verify: NF6h kills `m18b` (the slash predecessor),
  LD1b kills `m17b` (a duplicate with a different target) and NF6i kills `m18d` (the multi-occurrence loop).
  LD2 does not bind `m17c`: its appended `P02` is already in the frozen ledger, so `m17c` still refuses through
  the duplicate leg. The measured kill count on the frozen 57-row population is `killed_r89=15,
  killed_total=27`, battery EXIT 1 — C1's frozen target (16/28/EXIT 0) is NOT MET. The binding row for the
  malformed guard is `LD2b` (append `ZZ9\tABSENT`, an id absent from the frozen ledger), measured but not filed;
  it is carried to r90.*

## A2 — C2: the detail is not injective on the bytes for the 0x85/NEL pair; the window is 202 raw bytes, not 200

- **Artifact:** `.ufo/waves/round-89/w1/S89ExecC2.md` §6 (reproducer `S89ExecC2/r89-c2-collision.py`),
  `S89Critic.md` C2-a/C2-d, `S89Scribe.md` F1. Seat `S89Sentinel.md` §F-2 confirms the prereg's enumerated
  sentence set otherwise holds.
- **Frozen wording falsified (in part):** the title "injective on the bytes" and the sentence "A stderr carrying
  byte 0xFF and a stderr carrying the literal characters `\\xff` produce DIFFERENT detail cells". The pair
  KFF6/KFF7 (0xFF vs literal) IS injective — the frozen kill rule's enumerated check passes — but the composed
  decode+escape pipeline is injective only on that pair: raw byte `0x85` and the UTF-8 encoding of U+0085
  (`b'\\xc2\\x85'`, NEL) both render `\\x85` (the surrogate `\\udc85` and the real character take the
  same `o == 0x85` branch). The r88 tool distinguished them (`\\x85` vs `\\x85` differ in the r88 spelling);
  the r89 repair traded the 0xFF collision for this one.
- **Frozen wording falsified (in part):** "ONE physical line whose RAW window is at most 200 bytes". The truncated
  window is `raw[:100] + "…".encode() + raw[-99:]` = 100 + 3 + 99 = **202 raw bytes** (199 content + a 3-byte
  U+2026), and the K4 cell adds a 59-character wrapper. The head/tail arithmetic the prereg states elsewhere
  is accurate; the "at most 200" summary is not.
- **Narrowed sentences:** *The FLAGFAIL detail is injective on the bytes for the KFF6/KFF7 pair (a byte that
  is not valid UTF-8 renders as `\\xNN` with its value while the literal spelling doubles its backslash),
  and its truncated raw window is 202 bytes (head-100 of raw content, a three-byte U+2026, tail-99 of raw content).
  It is NOT injective on the 0x85/U+0085 pair: a raw byte 0x85 and the NEL character render identically.
  A stderr that differs from another only inside the elided middle also renders identically, which no bound can
  avoid.* The falsifying pair and the window arithmetic are the reasons C2's verdict below is
  "verified under the kill rule, headline narrowed".

## A3 — Sources: S351 admits, S352 is redundant with the standing S349 reject, and the captures are the 3.15.2 pages

- **Artifact:** `.ufo/waves/round-89/w1/S89ScoutSources/sources-candidates.md` (§§1-3) and
  `.ufo/waves/round-89/w1/S89Scribe/draft-sources-rows.md` (§§0-2).
- **S351 (ADMIT):** the `surrogateescape` entry is the exact scope S253 excludes ("not the `ignore` or
  `surrogateescape` handlers"), so it is a scope-narrowing row on a held URL, not a duplicate. The scout's
  live re-fetch of `/3/library/codecs.html` reproduces the lane's filed capture byte-for-byte, so the capture is
  honest; the sentence is byte-identical on the 3.14 book too, so the row is version-robust.
- **S352 (REJECT, not filed):** S349 already holds that exact scope, quote, rejection and flip on the versioned
  URL, and its quote re-verifies `True 15` on both the 3.14 and the 3.15.2 captures. Filing S352 would add
  registry weight, not a decision. It is recorded as the round's reject sample in the lesson Gate, re-using the
  standing S349 reject, exactly as S89Scribe F6 recommends.
- **Version note:** the lane's captures carry the 3.15.2 book ("Python 3.15.2 documentation") while the host
  interpreter is 3.14.8. The scout's 3.14 fetches and the 3.15.2 captures agree on both quoted sentences
  byte-for-byte, so no count changes; the S351 row names 3.14 in its title (the S348 precedent) while citing the
  filed capture, and the version drift is recorded here rather than re-fetched.

## A0.6 — NF6i's first draft carried the token once, not twice (instrument fix after F)

**Artifact:** L1's own pristine run (`ARM pristine pop=r89 rows=57 mismatches=1`, `NF6i … got=REFUSED rc=1 match=no`).
**Frozen wording falsified:** the prereg's NF6i design said the R12 declaration "carries the L06 token twice in one
line — first as a suffix of `xtests/.../.git`, later whole". The filed line carried it once: the only occurrence
was the `xtests/` suffix, and the quarantine slot's target path does not contain the token. Pristine `_whole`
returned False and the expected QUARANTINED verdict was REFUSED, so the population was not green and every mutant
was unscoreable (battery EXIT 2, INVALID).
**Narrowed sentence:** *NF6i's declaration is `- retired copy: xtests/vault/.../.git and tests/vault/.../.git;
quarantine slot `<q6>twice-stub`.` — the token occurs twice, first as a suffix of the longer path, then whole — so
pristine's `_whole` loop accepts it and m18d's first-occurrence-only edit refuses it.* The harness sha moved
(`6165eade…`); the population and mutant pins do not (rows and `old` strings unchanged). The fix landed as commit
`a3c7cb1` after F and before the after run; the C1 before receipt predates it (the before arm scores the r88
population, which has no R12 row, so the fix does not affect the control).
