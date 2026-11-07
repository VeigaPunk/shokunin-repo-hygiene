## Status
STATUS: FAIL — axis-check refused the preregistration because its machine block delimiters do not match the required `## MACHINE BLOCK ... END` section.

## Evidence
- Command: `python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-axis-check.py --prereg /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-27/preregistration.txt --scorecard /home/vgpnk/Projects/shokunin/souji-shokunin/SCORECARD.md`
- Output: `souji-axis-check: refused: no \`## MACHINE BLOCK ... END\` section found`; exit code 2. Expected `claims=3 flags=0` was not produced; no flag lines are available.
- Frozen revision stated by preregistration: `e78ac7c4837b81b634db4a927605a751a7f006ba` (line 1); this check ran against the current preregistration and SCORECARD paths, without pinning a revision.
- Context comparison: preregistration lines 5–9 state C1 calibration (7), C2 coverage (8), C3 operability (8). Machine rows 12–14 name those same axes and corresponding counters/before-after values. However, the machine block is plain `MACHINE BLOCK` followed by three claims and has no `##` heading or `END` terminator, so parser validation is blocked.

## Findings
1. Machine block formatting prevents the requested machine check. Location: `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-27/preregistration.txt:11-14`. Quote: `MACHINE BLOCK`.
2. The three machine rows match the context claim axes and the principal declared counter shapes: C1 findings 2→0, C2 rows/grounded-F4 132/2→135/4, C3 absent→present. This is a text comparison only, not machine-validated. Location: `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-27/preregistration.txt:5-14`. Quote: `CLAIM C1 axis=calibration surface-class=self-assessment-file enumerate=findings counter=landing-gate-findings before=2 after=0`.

## Attack log
- No separate counter-predicate attack asserted. Reported the exact parser refusal; do not treat missing output as `claims=3 flags=0`.
