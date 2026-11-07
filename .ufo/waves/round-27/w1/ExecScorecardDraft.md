## Status
STATUS: PARTIAL — prepared the requested scorecard additions; all after-values remain EVIDENCE-PENDING because this seat did not measure a landing tip.

## Evidence
- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD` → `e78ac7c4837b81b634db4a927605a751a7f006ba`; matches frozen base.
- `python3 -B tools/souji-landing-gate.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev e78ac7c4837b81b634db4a927605a751a7f006ba --round 27 --fleet-root /home/vgpnk/Projects/shokunin` → `SUMMARY findings=2 checked_reg=50 checked_changed=0 checked_pins=13 checked_measured=3 checked_markers=0 status_lines=0 carry_heading=0 checked_reports=0` (also reports inability to evaluate reports at base). Revision: frozen base `e78ac7c4837b81b634db4a927605a751a7f006ba`.
- Draft written: `.ufo/waves/round-27/w1/scorecard-draft.md`.

## Findings
1. Draft includes the requested C1/C2/C3 measurement rows, with after results explicitly EVIDENCE-PENDING; append-only correction notes for both pointer-exemption tokens and no line mapping where no in-place references move; an r28 planned bullet; and the pre-report gate capability row. Existing shapes were taken from `/home/vgpnk/Projects/shokunin/souji-shokunin/SCORECARD.md` §§ Capabilities/Planned and Round 26 measurement table. Quote: “| claim | axis | before | after | counting command | measured commit |”
2. Frozen contract location: `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-27/preregistration.txt` lines 5-9. Quote: “Before: `findings=2` at e78ac7c.” C1 base measurement agrees; no tip measurement performed.
3. Pointer text basis: `/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/QUALITY.md` Q57 at line 141 and Q59 at line 143. Quote from Q59: “a corpus/knowledge/registry change is a coverage surface”.

## Attack log
- None.
