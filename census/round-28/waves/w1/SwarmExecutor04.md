# SwarmExecutor04 — w1 C1 red-before proof (Q57/Q59 citation repair)

## Status
STATUS: PASS — red-before proven both in a minimal two-commit repo and on a
scratch clone of the real lane: unfixed Q57/Q59 → landing gate findings=2;
with the proposed fixes (sites-file refactor + Q59 reword) → findings=0.
No lane worktree touched; no commits/adds on the real lane; scratch under
/var/tmp/souji-r28-ExecC1RedBefore/ removed at the end.

## Evidence

### Frozen contract (read first)
- census/round-28/records/preregistration.txt:5: "Correct the stale Q57
  composite-site citations that the frozen landing-gate counter reports at
  base, without exemptions" — C1 counter: `python3 -B
  tools/souji-landing-gate.py --root <lane> --rev <full40> --round 28
  --fleet-root <fleet>` → SUMMARY findings=N; Before findings=2 at
  3a2a80d, After findings=0.

### Baseline on the real lane (read-only), base 3a2a80d0d18940a5e352ebc526da22a57dad83c4
```
$ python3 -B tools/souji-landing-gate.py --root \
    /home/vgpnk/Projects/shokunin/souji-shokunin --rev \
    3a2a80d0d18940a5e352ebc526da22a57dad83c4 --round 28 --fleet-root \
    /home/vgpnk/Projects/shokunin
LG-DANGLING-PTR	corpus/knowledge/registry	corpus/QUALITY.md:143 cites path absent at 3a2a80d0d189
LG-DANGLING-PTR	corpus/lessons/round-24.md:232:S118	corpus/QUALITY.md:141 cites path absent at 3a2a80d0d189
SUMMARY	findings=2	checked_reg=52	checked_changed=0	checked_pins=13	checked_measured=3	checked_markers=0	status_lines=0	carry_heading=0	checked_reports=0
EXIT=2
```
(EXIT=2 only because the pre-wave rev has no .ufo/waves/round-28/ .md
reports yet; the two pointer findings print independently.)

### Minimal repo (red-before), /var/tmp/souji-r28-ExecC1RedBefore/minimal
git init (absolute -C paths), commit A = copies of committed base blobs
(corpus/QUALITY.md lines 141+143; tests/fixtures/r25-slice-mapping.py,
r25-q57-check.sh; census/round-24/records/slice-verdicts.tsv; tools/souji-axis-check.py;
corpus/lessons/round-24.md, round-25.md, round-26.md;
.ufo/waves/round-24/assimilation/slice-verdicts.tsv) + minimal SKILL.md +
one benign w1 report. Commit B = A + fixes.

Unfixed commit A (0973e4e3b49b6dd05791e7117c3238f2653f5b74):
```
LG-DANGLING-PTR	corpus/knowledge/registry	corpus/QUALITY.md:2 cites path absent at 0973e4e3b49b
LG-DANGLING-PTR	corpus/lessons/round-24.md:232:S118	corpus/QUALITY.md:1 cites path absent at 0973e4e3b49b
SUMMARY	findings=2	checked_reg=0	checked_changed=0	checked_pins=0	checked_measured=0	checked_markers=0	status_lines=0	carry_heading=0	checked_reports=1
EXIT=1
```
Fixed commit B (3f023d6b7135b4df480aab8938cb8e064c3d36fa):
```
SUMMARY	findings=0	checked_reg=0	checked_changed=0	checked_pins=0	checked_measured=0	checked_markers=0	status_lines=0	carry_heading=0	checked_reports=1
EXIT=0
```

### Full repo shape (scratch clone), /var/tmp/souji-r28-ExecC1RedBefore/lane-clone
`git clone --no-local` of the lane (HEAD 0c96332932e6 = round-28 frozen
preregistration commit, child of base). Before state on clone HEAD:
```
LG-DANGLING-PTR	corpus/knowledge/registry	corpus/QUALITY.md:143 cites path absent at 0c96332932e6
LG-DANGLING-PTR	corpus/lessons/round-24.md:232:S118	corpus/QUALITY.md:141 cites path absent at 0c96332932e6
SUMMARY	findings=2	checked_reg=52	checked_changed=0	checked_pins=13	checked_measured=3	checked_markers=0	status_lines=0	carry_heading=0	checked_reports=0
EXIT=2
```
After applying the fixes plus a benign round-28 w1 report (commit
e372ec47e3ee424c50b1b05cc153779119dcba9e):
```
SUMMARY	findings=0	checked_reg=52	checked_changed=0	checked_pins=13	checked_measured=3	checked_markers=0	status_lines=1	carry_heading=0	checked_reports=1
EXIT=0
```
Checked_reg/pins/measured exercise the full gate (52/13/3) in both states, so
findings=0 is not an artifact of skipped checks.

### Fixes applied (both fixtures)
- QUALITY.md line 141 (Q57 check cell): replaced the inline enumerated-site
  command with `bash tests/fixtures/r25-q57-check.sh . census/round-24/records/slice-verdicts.tsv $(cat census/round-28/q57-sites.txt)`; dropped the
  `.ufo/waves/round-24/assimilation/slice-verdicts.tsv` copy and the
  `corpus/lessons/round-24.md:232:S118` pseudo-path token from the command;
  added committed `census/round-28/q57-sites.txt` (five site rows: round-25.md,
  round-24.md:240, round-24.md:232, LOG.md:1692, SCORECARD.md:181).
- QUALITY.md line 143 (Q59 criterion body): `corpus/knowledge/registry`
  reworded to `knowledge-registry`.

## Findings
1. Both target findings reproduce exactly: `corpus/lessons/round-24.md:232:S118`
   (QUALITY.md:141, Q57 check cell pseudo-path token) and
   `corpus/knowledge/registry` (QUALITY.md:143, Q59 criterion-body token) —
   identical on the real base 3a2a80d, minimal commit A, and clone HEAD
   0c96332932e6. The tracked `.ufo/waves/round-24/assimilation/slice-verdicts.tsv`
   exists in the tree and is NOT a finding; it is dropped anyway per the
   contract's command hygiene. Location: tools/souji-landing-gate.py
   check_pointers (lines 905-992), POINTER_PATH_RE (141-146).
2. The minimal-repo red-before required replicating every resolvable token of
   lines 141/143 (incl. corpus/lessons/round-26.md, which resolves at base);
   omitting it produced a spurious third finding, confirming the fixture must
   mirror the real tree's resolvable set (fixture includes it; final runs
   show exactly 2).
3. With the proposed fixes the landing gate goes green (findings=0, exit 0)
   in both the minimal repo and the full-repo clone. The fix wording is safe
   for the real gate: no new dangling pointers appear at the fixed rev.

## Attack log
None — this seat's item is the C1 red-before proof, not an attack. No
counter/predicate/target changes proposed.

## Notes
- Tool channel: no installs made (operator 2026-10-19 directive recorded; none
  required). Skills read: godspeed. Gate run with python3 -B.
- Scratch removed: /var/tmp/souji-r28-ExecC1RedBefore after this report.
- Real lane: read-only git plumbing only (show/ls-tree/clone source); never
  touched the lane worktree or index.
