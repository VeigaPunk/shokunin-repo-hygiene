# ScoutD4Marker — W2 attack: README :40 D4 marker placement + coverage-map counter blindness

`STATUS: PASS`

Lane: /home/vgpnk/Projects/shokunin/souji-shokunin
HEAD measured: `6deb53561aace9aa14a399f88cf8150da4d4f4bd` (round-25 prereg amendment 3; corpus/README.md at HEAD carries no D4 marker). D4 marker is present in the working tree (`corpus/README.md:40`), uncommitted. After-state for the counter built in isolated scratch (per Host bounds), then removed.

## Findings

1. **Marker sits in the status cell only** — `corpus/README.md:40`, F2 row:
   - Old (HEAD) line 40: `| F2 repository size census | frontier, no entry (r12 candidate deferred, `lessons/round-12.md` `## Gate`; sweep: `ls corpus/knowledge \| grep -ciE 'size\|structure\|sizer'` → 0, 2026-10-19) | — |`
   - New (working tree) line 40: `| F2 repository size census | frontier, no entry (r12 candidate deferred, `lessons/round-12.md` `## Gate`; sweep: `ls corpus/knowledge \| grep -ciE 'size\|structure\|sizer'` → 0, 2026-10-19); superseded by Round 24 F2 row (:517) | — |`
   - `git diff HEAD -- corpus/README.md` shows a single one-line-in/one-line-out replacement; the only changed segment is inside the status cell (between `2026-10-19)` and the closing ` | — |`). Ground cell (`F2 repository size census`) and entries cell (`—`) are byte-identical.
2. **No literal `|` in the marker** — marker string is `superseded by Round 24 F2 row (:517)`; programmatic assertion confirmed it contains no pipe character.
3. **No physical line added** — the marker is appended inline; line 40 is one physical line in both HEAD and the working tree (536 vs 536 lines for the marker-affected region; the D4 hunk is `@@ -37,7 +37,7 @@`, zero add/delete). (`grep -n` finds the marker only on line 40, plus the appended Round-25 prose section which is a separate append.)
4. **Pointer targets the row at :517, not the heading at :504** —
   - `corpus/README.md:504` = `## Round 24 — F2 write-safety census, coverage-map agreement, receipt verify symmetry` (section heading).
   - `corpus/README.md:517` = the F2 row of the Round 24 coverage map (`| F2 repository size census | frontier; read side (three entries, r13/r23) plus a write-safety debris census (r24 C1): …`), the row the status cell supersedes. Marker text literally names `Round 24 F2 row (:517)`.
5. **Coverage-map counter is blind to the fix** — counter = `python3 -B tools/souji-coverage-agreement.py --root <repo> --rev <full40>` (r24 C2 / r25 C1 tool; reads only ground + entries cells). Before/after runs, identical tool bytes, same blueprint repo (scratch clone of the lane, D4-marker-only commit):
   - BEFORE (marker absent, `--rev 6deb53561aace9aa14a399f88cf8150da4d4f4bd`): `grounded=6 mapped=6 dangling=0 mismatches=0`, rc=0
   - AFTER (marker present, `--rev 29a67f121d41fdb0085f618e2c0349d9900fb1ef`): `grounded=6 mapped=6 dangling=0 mismatches=0`, rc=0
   - Outputs byte-identical; the counter cannot see a status-cell-only change (consistent with the r24 lesson: "C2 is green with :40 unchanged" and the W1 analysis that `map_rows` yields only `row[0], row[2]`).

## Attack log
- `git clone` lane → `/var/tmp/souji-r25-ScoutD4Marker/lane`; verified clone HEAD == lane HEAD (`6deb535…`), clean.
- Asserted old line 40 equals HEAD bytes; applied the exact marker line; committed as scratch-only `29a67f12…`; scratch `git status --porcelain` empty after commit.
- Ran counter at before/after revs in scratch; both rc=0 with identical counts line.
- Scratch removed after run.

## Notes
- The marker being uncommitted in the lane is expected: it lands with the C3 claim's commit (same-commit rule, Q56); this seat is read-only and made no lane edits.
