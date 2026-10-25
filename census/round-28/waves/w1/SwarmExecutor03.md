# SwarmExecutor03 — souji round 28, C1 counter wrapper (lane: fleet repo & workspace hygiene)

## Status
STATUS: PASS — delivered `census/round-28/c1-counter.sh` (frozen C1 counter wrapper), ran it at base
3a2a80d0d18940a5e352ebc526da22a57dad83c4: SUMMARY `findings=2`, `checked_reg=52`, rc 2; receipt
`census/round-28/records/c1-run-base.tsv` byte-identical to the frozen preregistration `c1-before.tsv`.
Deterministic (python3 -B, LC_ALL=C, no network; double-run sha256 identical). No tools installed.

## Evidence
Command (exact):
```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && ./census/round-28/c1-counter.sh 3a2a80d0d18940a5e352ebc526da22a57dad83c4 run-base; echo wrapper_exit=$?
```
Output:
```
SUMMARY	findings=2	checked_reg=52	checked_changed=0	checked_pins=13	checked_measured=3	checked_markers=0	status_lines=0	carry_heading=0	checked_reports=0
c1_rc=2
wrapper_exit=2
```
Receipt `census/round-28/records/c1-run-base.tsv`:
```
LG-DANGLING-PTR	corpus/knowledge/registry	corpus/QUALITY.md:143 cites path absent at 3a2a80d0d189
LG-DANGLING-PTR	corpus/lessons/round-24.md:232:S118	corpus/QUALITY.md:141 cites path absent at 3a2a80d0d189
SUMMARY	findings=2	checked_reg=52 ...
COULD-NOT-EVALUATE	no .md reports under .ufo/waves/round-28/ at 3a2a80d0d18940a5e352ebc526da22a57dad83c4
c1_rc=2
```
`diff` vs `census/round-28/records/c1-before.tsv` = identical (findings=2, checked_reg=52, rc=2 exactly
as frozen). Rerun determinism: sha256 `f6475151e574b0a85f9d5813d4824c5a70d6cadb6b2619d36d5b15e70084ed31` before
and after identical. `bash -n census/round-28/c1-counter.sh` = ok. Base rev verified: `git cat-file -t
3a2a80d0d18940a5e352ebc526da22a57dad83c4` = commit; ancestor of HEAD (0c963329). Wrapper exits with the
gate's rc (0/1/2) and prints it as `c1_rc=`.

## Findings
1. `census/round-28/c1-counter.sh` (new, mode 755): takes `<full40-rev>` + optional label, cd's to the lane,
   runs the frozen command verbatim (`python3 -B tools/souji-landing-gate.py --root … --rev <full40> --round 28
   --fleet-root …`), prints the SUMMARY line and the exit code, writes `census/round-28/records/c1-<label>.tsv`
   (stdout findings+SUMMARY, then stderr, then `c1_rc=`), deterministic.
2. `census/round-28/records/c1-run-base.tsv` (new): base run receipt, byte-identical to frozen `c1-before.tsv`
   — matches the frozen C1 "Before" row (findings=2, checked_reg=52). Kill-rule baseline holds: no exemption row
   used; findings are exactly the two stale citation pointers (Q57 round-24.md:232:S118, Q59 knowledge/registry).
3. No tool installs needed (no install/update record). No network: gate runs with its pinned GIT_ENV
   (NO_LAZY_FETCH/NO_REPLACE_OBJECTS).

## Attack log
None — counter output matches the frozen preregistration expectations exactly; no mis-count observed.
