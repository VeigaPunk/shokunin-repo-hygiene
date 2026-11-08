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

## A1 — C1: (pending wave)

## A2 — C2: (pending wave)

## A3 — Sources: (pending wave)
