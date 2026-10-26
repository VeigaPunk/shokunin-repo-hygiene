# SwarmExecutor10 — A1 REGRESS-FULL receipt (souji r31 w1)

## Status

STATUS: PASS — routed round-30 closure defect 3 reproduced and isolated: the r30 REGRESS-FULL `differs` at (68447af, 9420341) is caused solely by the tab-only tail strip, and a separator-normalized strip yields `same` with zero differing lines; both delivery files written and every quoted run was executed this session.

## Evidence

- Lane: /home/vgpnk/Projects/shokunin/souji-shokunin; base 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc (r31 prereg); r30 base 9420341d9a814cb6089c25fb03a4cc9b23dc0d1b; r30 C2 landing 68447afef62e4761249af55a2467657f04046537.
- Tooling: python3 3.14.8, git 2.56.0; no installs/upgrades. Scratch: /fast/scratch/hyaku/souji-r31/A1Regex/ (TMPDIR there; origin removed after every clone; removed after delivery).
- Pair 1, receipt script (rev 68447af, base 9420341):
  `python3 -B .ufo/waves/round-31/w1/deliver-a1-regress-full-check.py --root <lane> --rev 68447af... --base 9420341... --scratch /fast/scratch/hyaku/souji-r31/A1Regex`
  ```
  A1-BROKEN tools/souji-landing-gate.py rc=0/0 lines=66/66 differs
  A1-FIXED  tools/souji-landing-gate.py rc=0/0 lines=66/66 same
  A1-DIFF-COUNT tools/souji-landing-gate.py broken=2 fixed=0
  A1-BROKEN tests/fixtures/r16-landing-gate.py rc=0/0 lines=16/16 same
  A1-FIXED  tests/fixtures/r16-landing-gate.py rc=0/0 lines=16/16 same
  SUMMARY-A1 pair=68447af...9420341 broken=differs fixed=same
  ```
- Pair 2 (rev = base = 9f17a1e...), same script: `SUMMARY-A1 ... broken=same fixed=same`; both programs 66/66 and 16/16 `same` in both variants.
- Original counter, pair 1 (`census/round-30/c2-counter-v2.py --rev 68447af... --base 9420341... --fleet-root /home/vgpnk/Projects/shokunin --scratch .../c2v2-pair1`): `REGRESS-FULL tools/souji-landing-gate.py rc=0/0 lines=66/66 differs`, `REGRESS-FULL tests/fixtures/r16-landing-gate.py ... same`, `SUMMARY-V2 ... bind=fail ... regress_full=differs` (exit 1).
- Original counter, pair 2: `REGRESS-FULL ... tools/souji-landing-gate.py ... same`, `REGRESS-FULL ... r16 ... same`, `SUMMARY-V2 ... bind=ok ... redarm=fail regress_full=same` (exit 1).
- Full commands and outputs, including the direct gate probe: `.ufo/waves/round-31/w1/deliver-a1-regex-receipt.txt`.

## Findings

1. Defect confirmed at census/round-30/c2-counter-v2.py:69 — `re.sub(r"\terr=.*$", "", l)` — while tools/souji-landing-gate.py:1423 builds `detail = "exit=%d ids=%s paths=%s fleet=%s err=%s" % (` and :1437 prints `"CASE\t%s\t%s\t%s"`; the tail is ` err=` (space), so the strip never fires and `regress_full=same` is unreachable whenever the free-text message differs.
2. Pair 1 isolates the cause: with the v2 strip verbatim the gate output differs on exactly 2 of 66 lines, both CASE lines whose only delta is the reworded no-reports error (`no .md reports under %s at %s` → `no .md reports under %s or %s at %s`, cases `pointer-without-wave-reports` round 18 and `no-wave-dir-exit2` round 16); with the strip normalized on `[ \t]err=` there are 0 differing lines. No non-`err=` byte moved.
3. The v2 counter's exit 1 at pair 1 is not attributable to the regex: its BIND leg reports `dangling=1` from SCORECARD.md:322 citing `.ufo/waves/round-30/w1/deliver-c1-literal-history.tsv`, absent at 68447af and present from 393b011 (both trees verified with `git ls-tree -r --name-only`); that pointer is the only LG-DANGLING-PTR at 68447af and is gone at 9f17 (BIND `dangling=0`).
4. Pair 2's `redarm=fail` is inherent to a same-revision control (base clone and rev clone hold the same tool, so the red-before arm cannot distinguish); its REGRESS lines are trivially `same` in both variants and carry no evidence either way.
5. No round-30 file was edited; the receipt script is standalone and mirrors c2-counter-v2.py's clone discipline, TMPDIR handling, `norm()` and comparison order (c2-counter-v2.py:161-167).

## Deliveries

- `.ufo/waves/round-31/w1/deliver-a1-regress-full-check.py` — standalone receipt script: clones BASE and REV (`git clone --no-local`, origin removed, detached checkout), compares `tools/souji-landing-gate.py --selftest` and `tests/fixtures/r16-landing-gate.py`, and prints A1-BROKEN (v2 regex verbatim) / A1-FIXED (`[ \t]err=`) / diff counts / `SUMMARY-A1`.
- `.ufo/waves/round-31/w1/deliver-a1-regex-receipt.txt` — commands, outputs for both pairs and both counters, and the one-paragraph conclusion.
